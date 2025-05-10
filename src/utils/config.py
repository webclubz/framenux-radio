#!/usr/bin/env python3
import os
from pathlib import Path

# Application data directory
APP_DIR = os.path.join(Path.home(), ".framenux-radio")
os.makedirs(APP_DIR, exist_ok=True)

# Paths to data files
STATIONS_JSON_PATH = os.path.join(APP_DIR, "stations.json")
FAVORITES_PATH = os.path.join(APP_DIR, "favorites.json")

# Station images directory
STATION_IMAGES_DIR = os.path.join(APP_DIR, "station_images")
os.makedirs(STATION_IMAGES_DIR, exist_ok=True)

# Default image for stations with no logo
DEFAULT_STATION_IMAGE = os.path.join(Path(__file__).parent.parent.parent, "assets", "music.png")

# UI Constants
STATION_IMAGE_SIZE = 180  # Size of the station logo image
PAGE_SIZE = 50  # Number of stations to load at once

# API URLs
STATIONS_API_URL = "http://162.55.180.156/json/stations/topvote"