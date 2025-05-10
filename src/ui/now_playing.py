#!/usr/bin/env python3
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Pango

# Update relative imports to absolute imports
from src.utils import config 
from src.utils.downloader import StationDownloader

class NowPlayingView(Gtk.Box):
    """
    Widget that displays the currently playing station with image and detailed information
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(15)
        self.set_margin_bottom(15)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Force a consistent width for the whole component
        self.set_size_request(210, -1)
        
        # Create a default station image
        self.image = Gtk.Image()
        self.set_default_image()
        
        # Center the image horizontally without a frame
        image_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        image_box.pack_start(Gtk.Label(), True, True, 0)  # Spacer
        image_box.pack_start(self.image, False, False, 0)
        image_box.pack_start(Gtk.Label(), True, True, 0)  # Spacer
        
        self.pack_start(image_box, False, False, 0)
        
        # Station name (big and bold)
        self.name_label = Gtk.Label()
        self.name_label.set_markup("<b>No station selected</b>")
        self.name_label.set_line_wrap(True)
        self.name_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.name_label.set_max_width_chars(25)
        self.name_label.set_width_chars(25)  # Fixed width to prevent resizing
        self.name_label.set_justify(Gtk.Justification.CENTER)
        self.name_label.set_margin_top(10)
        self.pack_start(self.name_label, False, False, 0)
        
        # Station country and language
        self.location_label = Gtk.Label()
        self.location_label.set_markup("<i>Country: Unknown</i>")
        self.location_label.set_line_wrap(True)
        self.location_label.set_max_width_chars(25)
        self.location_label.set_width_chars(25)  # Fixed width
        self.location_label.set_justify(Gtk.Justification.CENTER)
        self.location_label.set_margin_top(5)
        self.pack_start(self.location_label, False, False, 0)
        
        # Codec and bitrate
        self.codec_label = Gtk.Label()
        self.codec_label.set_markup("<i>Format: Unknown</i>")
        self.codec_label.set_line_wrap(True)
        self.codec_label.set_max_width_chars(25)
        self.codec_label.set_width_chars(25)  # Fixed width
        self.codec_label.set_justify(Gtk.Justification.CENTER)
        self.codec_label.set_margin_top(5)
        self.pack_start(self.codec_label, False, False, 0)
        
        # Currently playing song/title (from stream metadata)
        self.now_playing_label = Gtk.Label()
        self.now_playing_label.set_markup("<i>Not playing</i>")
        self.now_playing_label.set_line_wrap(True)
        self.now_playing_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.now_playing_label.set_max_width_chars(25)
        self.now_playing_label.set_width_chars(25)  # Fixed width
        self.now_playing_label.set_justify(Gtk.Justification.CENTER)
        self.now_playing_label.set_margin_top(10)
        self.pack_start(self.now_playing_label, False, False, 0)
        
        # Create a downloader for station images
        self.downloader = StationDownloader()
        
        # Current station data
        self.current_station = None
        
    def set_default_image(self):
        """Set the default radio image when no station is selected"""
        try:
            # Check if default image exists, otherwise use a generic icon
            if os.path.exists(config.DEFAULT_STATION_IMAGE):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    config.DEFAULT_STATION_IMAGE,
                    config.STATION_IMAGE_SIZE,
                    config.STATION_IMAGE_SIZE,
                    True
                )
            else:
                # Use a generic music icon if the default image is missing
                icon_theme = Gtk.IconTheme.get_default()
                pixbuf = icon_theme.load_icon("audio-x-generic", config.STATION_IMAGE_SIZE, 0)
            
            self.image.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error setting default image: {e}")
    
    def update_station(self, station, is_playing=False):
        """
        Update the display with a new station
        
        Args:
            station: Station data dictionary
            is_playing: Whether the station is currently playing
        """
        self.current_station = station
        
        if not station:
            self.set_default_image()
            self.name_label.set_markup("<b>No station selected</b>")
            self.location_label.set_markup("<i>Country: Unknown</i>")
            self.codec_label.set_markup("<i>Format: Unknown</i>")
            self.now_playing_label.set_markup("<i>Not playing</i>")
            return
        
        # Update station name
        name = station.get('name', 'Unknown Station')
        self.name_label.set_markup(f"<b>{name}</b>")
        
        # Update location info
        country = station.get('country', 'Unknown')
        language = station.get('language', 'Unknown')
        self.location_label.set_markup(f"<i>Country: {country} • Language: {language}</i>")
        
        # Update codec info
        codec = station.get('codec', 'Unknown')
        bitrate = station.get('bitrate', 'Unknown')
        self.codec_label.set_markup(f"<i>Format: {codec} • Bitrate: {bitrate} kbps</i>")
        
        # Update now playing status
        if is_playing:
            self.now_playing_label.set_markup("<i>Playing...</i>")
        else:
            self.now_playing_label.set_markup("<i>Not playing</i>")
        
        # Try to load the station image
        self.load_station_image(station)
    
    def load_station_image(self, station):
        """Load and display the station image"""
        # Check if station has a favicon
        if not station or not station.get('favicon'):
            self.set_default_image()
            return
        
        # Get the station UUID
        station_uuid = station.get('stationuuid', '')
        if not station_uuid:
            self.set_default_image()
            return
        
        # Check if we've already downloaded this image
        image_path = os.path.join(config.STATION_IMAGES_DIR, f"{station_uuid}.png")
        if os.path.exists(image_path):
            self.set_station_image(image_path)
        else:
            # Download the image
            self.downloader.download_station_image(station, self.set_station_image)
    
    def set_station_image(self, image_path):
        """
        Set the station image from a file path
        
        Args:
            image_path: Path to the image file, or None if download failed
        """
        if not image_path or not os.path.exists(image_path):
            self.set_default_image()
            return
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                image_path,
                config.STATION_IMAGE_SIZE,
                config.STATION_IMAGE_SIZE,
                True
            )
            self.image.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"Error loading station image: {e}")
            self.set_default_image()
    
    def update_now_playing(self, metadata):
        """
        Update the currently playing track information from stream metadata
        
        Args:
            metadata: Dictionary containing stream metadata
        """
        if not metadata:
            return
        
        # Try to extract title and artist information
        title = metadata.get('title', '')
        artist = metadata.get('artist', '')
        
        if title and artist:
            self.now_playing_label.set_markup(f"<i>Now Playing: {artist} - {title}</i>")
        elif title:
            self.now_playing_label.set_markup(f"<i>Now Playing: {title}</i>")
        
    def update_stream_info(self, stream_info):
        """
        Update the codec and format information from stream info
        
        Args:
            stream_info: Dictionary of stream information
        """
        if not stream_info or not self.current_station:
            return
        
        # Update codec info with live stream information if available
        codec = self.current_station.get('codec', 'Unknown')
        bitrate = self.current_station.get('bitrate', 'Unknown')
        
        # Add any additional stream info
        format_info = stream_info.get('format', '')
        sample_rate = stream_info.get('sample_rate', '')
        
        info_text = f"<i>Format: {codec}"
        if bitrate and bitrate != 'Unknown':
            info_text += f" • Bitrate: {bitrate} kbps"
        if sample_rate:
            info_text += f" • {sample_rate}"
        info_text += "</i>"
        
        self.codec_label.set_markup(info_text)