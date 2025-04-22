import logging
import requests
import threading
import json
import dbus
import dbus.service
import http
import sdnotify

from .idfm_line_reports_line import IdfmLineReportsLine
from .idfm_line_reports_dbus_object import IdfmLineReportsDBusObject

from requests.auth import HTTPBasicAuth

_LOGGER = logging.getLogger(__name__)

REQUEST_INIT_METRO = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3AMetro/lines?'
REQUEST_INIT_RER = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3ARapidTransit/lines?'
REQUEST_INIT_TRANSILIEN = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3ALocalTrain/lines?'

REQUEST_METRO = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3AMetro/line_reports?'
REQUEST_RER = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3ARapidTransit/line_reports?'
REQUEST_TRANSILIEN = 'https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/physical_modes/physical_mode%3ALocalTrain/line_reports?'

class IdfmLineReportsData:
    """The class for handling the data retrieval."""

    def __init__(self, bus_name, token, update_interval):
        """Initialize the data object."""
        self.bus_name = bus_name
        self.token = token
        self.timer = None
        self.line_dbus_list = []
        self.update_interval = update_interval
        self.quit_program = False

        try:
            self.init_line(REQUEST_INIT_METRO, 'Metro')
            self.init_line(REQUEST_INIT_RER, 'RapidTransit')
            self.init_line(REQUEST_INIT_TRANSILIEN, 'LocalTrain')
        except Exception as e:
            _LOGGER.error("init_line error: {}".format(e))
            raise ConnectionError("Failed to connect to the resource")

        self.auto_update()
        sdnotify.SystemdNotifier().notify("READY=1")

        _LOGGER.info("Init succeed")

    def init_line(self, request, lineType):
        try:
            url = request
            headers = {'Accept': 'application/json','apikey': self.token}
            req = requests.get(url, headers=headers, timeout=10)

        except Exception as e:
            _LOGGER.error("Connection error: {}".format(e))
            raise ConnectionError("Failed to connect to the resource")

        _LOGGER.debug('Status: {}'.format(req))

        if req.status_code == http.client.UNAUTHORIZED:
            raise ConnectionError("Invalid token")

        data = json.loads(req.content)

        lines = data.get("lines", [])
        for line in lines:
            identifier = line.get("id")
            name = line.get("name")
            color = line.get("color")
            text_color = line.get("text_color")

            new_line = IdfmLineReportsLine(identifier, name, lineType, color, text_color)

            object_path = f'/com/commutator/IdfmLineReports/{lineType}{name}'
            new_line_dbus = IdfmLineReportsDBusObject(self.bus_name, object_path, new_line)
            self.line_dbus_list.append(new_line_dbus)

    def auto_update(self):
        """Update the data and restart the timer."""
        try:
            self.update()
        except Exception as e:
            _LOGGER.error("Error in auto_update: {}".format(e))
        finally:
            if not self.quit_program:
                self.timer = threading.Timer(self.update_interval, self.auto_update)
                self.timer.start()

    def stop_auto_update(self):
        """Stop the auto-update timer."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
            self.quit_program = True

    def disrupted(self, identifier, effect, color):
        for line_dbus in self.line_dbus_list:
            if line_dbus.line.identifier == identifier:
                line_dbus.line.tmp_new_severity_effect = effect
                line_dbus.line.tmp_new_severity_color = color

    def update_line(self, request):

        try:
            url = request
            headers = {'Accept': 'application/json','apikey': self.token}
            req = requests.get(url, headers=headers, timeout=10)

        except Exception as e:
            _LOGGER.error("Connection error: {}".format(e))
            raise ConnectionError("Failed to connect to the resource")

        _LOGGER.debug('Status: {}'.format(req))

        data = json.loads(req.content)

        disruptions = data.get("disruptions", [])
        for disruption in disruptions:
            status = disruption.get("status", [])
            if status == "active":

                severity = disruption.get("severity", [])
                effect = severity.get("effect", [])
                color = severity.get("color", [])

                impacted_objects = disruption.get("impacted_objects", [])
                for impacted_object in impacted_objects:
                    pt_object = impacted_object.get("pt_object", [])
                    identifier = pt_object.get("id", [])
                    severity = ""

                    self.disrupted(identifier, effect, color)

    def update(self):

        # Reset status
        for line_dbus in self.line_dbus_list:
            line_dbus.line.tmp_new_severity_effect = "NO_PROBLEM"
            line_dbus.line.tmp_new_severity_color = "#FFFFFF"

        try:
            self.update_line(REQUEST_METRO)
            self.update_line(REQUEST_RER)
            self.update_line(REQUEST_TRANSILIEN)
        except Exception as e:
            _LOGGER.error("update_line error: {}".format(e))
            raise ConnectionError("Failed to connect to the resource")

        for line_dbus in self.line_dbus_list:

            line = line_dbus.line
            changed_properties = {}

            if (line.tmp_new_severity_effect != line.severity_effect) and (line.severity_effect != "NO_SERVICE"):
                line.severity_effect = line.tmp_new_severity_effect
                line.tmp_new_severity_effect = ""
                changed_properties['severity_effect'] = line.severity_effect
                _LOGGER.info(f'new severity_effect for {line.lineType} {line.name}: {line.severity_effect}')

            if (line.tmp_new_severity_color != line.severity_color) and (line.severity_effect != "NO_SERVICE"):
                line.severity_color = line.tmp_new_severity_color
                line.tmp_new_severity_color = ""
                changed_properties['severity_color'] = line.severity_color
                _LOGGER.info(f'new severity_color for {line.lineType} {line.name}: {line.severity_color}')

            if changed_properties:
                line_dbus.properties_changed(changed_properties)
