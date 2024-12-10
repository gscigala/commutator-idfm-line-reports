import sys
import argparse
import signal
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from commutator_idfm_line_reports.idfm_line_reports_data import IdfmLineReportsData
import logging

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

def signal_handler(signum, frame):
    print("SIGINT received, stopping the service...")
    idfm_line_reports_data.stop_auto_update()
    loop.quit()

def main():
    parser = argparse.ArgumentParser(description='IDFM line reports Data Service')
    parser.add_argument('--session', action='store_true', help='Use DBus session bus instead of system bus')
    parser.add_argument('--token', type=str, required=True, help='PRIM token')
    parser.add_argument('--update-interval', type=int, default=300, help='Update interval in seconds (default: 300)')
    args = parser.parse_args()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus_name = dbus.service.BusName('com.commutator.IdfmLineReports', dbus.SystemBus() if not args.session else dbus.SessionBus())
    global idfm_line_reports_data
    try:
        idfm_line_reports_data = IdfmLineReportsData(bus_name, token=args.token, update_interval=args.update_interval)
    except Exception as e:
        _LOGGER.error("Unable to initialize")
        sys.exit(1)

    global loop
    loop = GLib.MainLoop()

    signal.signal(signal.SIGINT, signal_handler)

    loop.run()

if __name__ == "__main__":
    sys.exit(main())
