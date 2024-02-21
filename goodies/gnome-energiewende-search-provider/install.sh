#!/bin/sh
install -Dm 0755 search_provider.py /usr/lib/energiewende_search_provider/search_provider.py
install -Dm 0644 config/org.gnome.Energiewende.SearchProvider.ini /usr/share/gnome-shell/search-providers/org.gnome.Energiewende.SearchProvider.ini
install -Dm 0644 config/org.gnome.Energiewende.SearchProvider.desktop /usr/share/applications/org.gnome.Energiewende.SearchProvider.desktop
install -Dm 0644 config/org.gnome.Energiewende.SearchProvider.service.dbus /usr/share/dbus-1/services/org.gnome.Energiewende.SearchProvider.service
install -Dm 0644 config/org.gnome.Energiewende.SearchProvider.service.systemd /usr/lib/systemd/user/org.gnome.Energiewende.SearchProvider.service
echo "Installation successful."