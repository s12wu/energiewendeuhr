import os
import subprocess
import requests

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
import dbus.service

from gi.repository import GLib

sbn = dict(dbus_interface='org.gnome.Shell.SearchProvider2')

class SearchService(dbus.service.Object):
    bus_name = "org.gnome.Energiewende.SearchProvider"
    object_path = "/" + bus_name.replace(".", "/")

    ew_downloaded = False
    ew_stati = "not called yet  /  "

    def __init__(self):
        self.session_bus = dbus.SessionBus()
        self.is_with_argument=False
        bus_name = dbus.service.BusName(self.bus_name, bus=self.session_bus)
        dbus.service.Object.__init__(self, bus_name, self.object_path)

    @dbus.service.method(in_signature='sasu', **sbn)
    def ActivateResult(self, id, terms, timestamp):
        os.system(f"xdg-open https://wieland.srvx.de/energiewende/")

    @dbus.service.method(in_signature='as', out_signature='as', **sbn)
    def GetInitialResultSet(self, terms):
        self.ew_downloaded = False
        return self.GetSubsearchResultSet([],terms)

    @dbus.service.method(in_signature='as', out_signature='aa{sv}', **sbn)
    def GetResultMetas(self, ids):
        return [dict(id=id, name=id, description=self.ew_stati[:-5]) for id in ids]

    @dbus.service.method(in_signature='asas', out_signature='as', **sbn)
    def GetSubsearchResultSet(self, previous_results, new_terms):
        if self.ew_downloaded:
            results = previous_results

        elif "ew" in new_terms:
            print("Downloading...")
            
            req = requests.get("https://wieland.srvx.de/energiewende/rawvalues.php")
            data = req.text.split(",")
            ew_fraction = int(float(data[0]) * 100.0)
            ew_color_numbers = []  # for example: [1, 1, 3, 4, 4, 4]
            for i in range(6):
                ew_color_numbers.append(int(data[i+1]))

            colors = ["error", "red", "orange", "yellow", "green"]
            times = ["now", "1h", "2h", "3h", "4h", "5h"]

            self.ew_stati = ""
            for i, index in enumerate(ew_color_numbers):
                s = f"{times[i]}: {colors[index]}  /  "
                self.ew_stati += s

            energiewende = f"Energiewende: {ew_fraction}%"
            results = [energiewende]
            self.ew_downloaded = True

        else:
            results = []

        return results
                
    @dbus.service.method(in_signature='asu', terms='as', timestamp='u', **sbn)
    def LaunchSearch(self, terms, timestamp):
        pass

if __name__ == "__main__":
    SearchService()
    GLib.MainLoop().run()
