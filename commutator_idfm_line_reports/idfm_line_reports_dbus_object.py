import dbus
import dbus.service

class IdfmLineReportsDBusObject(dbus.service.Object):
    def __init__(self, bus_name, object_path, line):
        self.line = line
        self.object_path = object_path
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.signal('org.freedesktop.DBus.Properties', signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
        pass

    def properties_changed(self, changed_properties):
        interface_name = f'com.commutator.IdfmLineReports.{self.line.lineType}{self.line.name}'
        self.PropertiesChanged(self.object_path, changed_properties, [])

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        return {
            'id': self.line.identifier,
            'name': self.line.name,
            'color': self.line.color,
            'text_color': self.line.text_color,
            'severity_effect': self.line.severity_effect,
            'severity_color': self.line.severity_color
        }

    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        return getattr(self.line, property_name)
