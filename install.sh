#!/bin/bash

# Create directories if they don't exist
mkdir -p /usr/share/framenux-radio/assets
mkdir -p /usr/share/applications
mkdir -p /usr/bin
mkdir -p /usr/lib/framenux-radio/src
# Create icon directories
mkdir -p /usr/share/icons/hicolor/256x256/apps
mkdir -p /usr/share/pixmaps

# Copy the application files
cp -r src/* /usr/lib/framenux-radio/src/
cp assets/* /usr/share/framenux-radio/assets/
cp framenux_radio.py /usr/lib/framenux-radio/

# Create __init__.py in the framenux-radio directory to make it a proper package
touch /usr/lib/framenux-radio/__init__.py
touch /usr/lib/framenux-radio/src/__init__.py

# Install the app icon to standard icon locations
cp assets/framenux.png /usr/share/icons/hicolor/256x256/apps/framenux-radio.png
cp assets/framenux.png /usr/share/pixmaps/framenux-radio.png

# Create launcher script with fixed Python path
cat > /usr/bin/framenux-radio << 'EOL'
#!/usr/bin/env python3
import sys
import os

# Add the application directory to the Python path
sys.path.insert(0, '/usr/lib/framenux-radio')
os.chdir('/usr/lib/framenux-radio')  # Set the working directory to ensure relative imports work

# Run the application
from framenux_radio import main
main()
EOL

# Make the launcher executable
chmod +x /usr/bin/framenux-radio

# Install desktop file
cat > /usr/share/applications/framenux-radio.desktop << 'EOL'
[Desktop Entry]
Name=Framenux Radio
Comment=Internet Radio Player
Exec=framenux-radio
Icon=framenux-radio
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Player;GTK;
Keywords=Radio;Music;Stream;Internet;
EOL