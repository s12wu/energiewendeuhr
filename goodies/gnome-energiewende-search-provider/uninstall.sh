#!/bin/sh
rm /usr/lib/energiewende_search_provider/search_provider.py
rm /usr/share/gnome-shell/search-providers/org.gnome.Energiewende.SearchProvider.ini
rm /usr/share/applications/org.gnome.Energiewende.SearchProvider.desktop
rm /usr/share/dbus-1/services/org.gnome.Energiewende.SearchProvider.service
rm  /usr/lib/systemd/user/org.gnome.Energiewende.SearchProvider.service
echo "Removing successful."