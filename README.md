# Framenux Radio

Framenux Radio is a simple and elegant internet radio player that allows you to listen to thousands of radio stations from around the world. It features a clean GTK3 user interface, station search capabilities, and favorites management.

![Framenux Radio](assets/framenux.png)

## Features

- Access to approximately 54,000 online radio stations
- Search stations by name, country, or language
- Favorite stations for quick access
- Volume control
- Station images caching with clear cache option
- Clean and intuitive GTK3-based user interface

## Requirements

- Python 3
- GTK3 (GObject Introspection)
- GStreamer (for audio playback)

## Installation

### Option 1: Install from DEB package

```bash
sudo apt install ./framenux-radio_1.0.0-1_amd64.deb
```

### Option 2: Run directly from source

```bash
# Install dependencies
sudo apt install python3 python3-gi gir1.2-gtk-3.0

# Run the application
python3 framenux_radio.py
```

## Usage

1. Upon first launch, the application will prompt you to download the radio station list
2. Once downloaded, you can browse through the available stations
3. Use the search box to find stations by name
4. Use the filter dropdown to browse stations by country, language, or favorites
5. Click on a station to start playing
6. Use the controls to play/pause, stop, adjust volume, and add to favorites

## Creating a DEB Package

If you want to create your own DEB package from source, follow these steps:

1. Ensure you have the necessary build dependencies:

```bash
sudo apt install debhelper devscripts
```

2. From the project root directory, run:

```bash
dpkg-buildpackage -us -uc -b
```

3. The DEB package will be created in the parent directory

Alternatively, you can use the provided install.sh script:

```bash
./install.sh
```

## Directory Structure

- `src/` - Main source code
  - `ui/` - User interface components
  - `utils/` - Utility functions and configuration
  - `player.py` - Radio player implementation
- `assets/` - Application images and resources
- `debian/` - Debian packaging configuration

## License

This project is licensed under the terms of the MIT license.

## Disclaimer

This software is provided "as is" without warranty of any kind, either express or implied. The user assumes all responsibility and liability for using this software. The authors and contributors do not accept any responsibility for any damage that may occur to your computer system or other devices as a result of using this software. Use at your own risk.