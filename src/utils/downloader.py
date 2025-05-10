#!/usr/bin/env python3
import os
import json
import threading
import urllib.request
import tempfile
import shutil
from gi.repository import GLib

from ..utils import config

class StationDownloader:
    """Handles downloading the stations list and station images"""
    
    def __init__(self, on_complete=None, on_error=None, on_progress=None):
        """
        Initialize the downloader
        
        Args:
            on_complete: Callback when download completes
            on_error: Callback when an error occurs
            on_progress: Callback for progress updates
        """
        self.on_complete = on_complete
        self.on_error = on_error
        self.on_progress = on_progress
        
    def start_download(self):
        """Start downloading the stations list in a background thread"""
        thread = threading.Thread(target=self._download_thread)
        thread.daemon = True
        thread.start()
    
    def _download_thread(self):
        """Background thread for downloading the stations list"""
        try:
            # Use a temporary file to avoid corrupting the stations file if download fails
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                urllib.request.urlretrieve(config.STATIONS_API_URL, temp_file.name)
                
                # Verify the file is valid JSON
                with open(temp_file.name, 'r') as f:
                    json.load(f)
                
                # Move the temp file to the final destination
                shutil.copy(temp_file.name, config.STATIONS_JSON_PATH)
                
            # Download successful, call the complete callback
            if self.on_complete:
                GLib.idle_add(self.on_complete)
                
        except Exception as e:
            # Download failed, call the error callback
            if self.on_error:
                GLib.idle_add(lambda: self.on_error(str(e)))
    
    def download_station_image(self, station, callback=None):
        """
        Download the favicon/image for a specific station
        
        Args:
            station: Station data dictionary
            callback: Function to call when download completes
        """
        def _download_image_thread():
            try:
                # Get the station UUID as a unique identifier
                station_uuid = station.get('stationuuid', '')
                if not station_uuid:
                    return
                
                # Check if we have a favicon URL
                favicon_url = station.get('favicon')
                if not favicon_url:
                    return
                
                # Create the path for the image file
                image_path = os.path.join(config.STATION_IMAGES_DIR, f"{station_uuid}.png")
                
                # Download the image if it doesn't already exist
                if not os.path.exists(image_path):
                    urllib.request.urlretrieve(favicon_url, image_path)
                
                # Call the callback with the image path
                if callback:
                    GLib.idle_add(lambda: callback(image_path))
                    
            except Exception as e:
                print(f"Failed to download station image: {e}")
                if callback:
                    GLib.idle_add(lambda: callback(None))
        
        # Start the download in a background thread
        thread = threading.Thread(target=_download_image_thread)
        thread.daemon = True
        thread.start()