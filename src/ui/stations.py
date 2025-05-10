#!/usr/bin/env python3
import json
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

# Update relative import to absolute import
from src.utils import config

class StationsList:
    """
    Manages the stations list and favorites
    """
    
    def __init__(self, on_station_activated=None):
        # Callback when a station is activated
        self.on_station_activated = on_station_activated
        
        # Stations data
        self.stations = []
        self.filtered_stations = []
        self.favorites = []
        
        # Lazy loading parameters
        self.current_page = 0
        self.is_loading_more = False
        
        # Create the UI elements
        self.create_stations_view()
        self.create_favorites_view()
        
        # Load favorites if available
        self.load_favorites()
    
    def create_stations_view(self):
        """Create the stations list view"""
        # Create a scrolled window for the stations list
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Create the list box to hold the stations
        self.stations_list = Gtk.ListBox()
        self.stations_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.stations_list.connect("row-activated", self._on_station_activated)
        self.scrolled_window.add(self.stations_list)
        
        # Add lazy loading functionality
        self.scrolled_window.connect("edge-reached", self._on_edge_reached)
        
        # Create a status label
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_margin_start(10)
        self.status_label.set_margin_bottom(5)
    
    def create_favorites_view(self):
        """Create the favorites list view"""
        # Create a scrolled window for the favorites list
        self.favorites_scrolled = Gtk.ScrolledWindow()
        self.favorites_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Create the list box to hold the favorites
        self.favorites_list = Gtk.ListBox()
        self.favorites_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.favorites_list.connect("row-activated", self._on_favorite_activated)
        self.favorites_scrolled.add(self.favorites_list)
    
    def load_stations(self, stations_file=None):
        """
        Load stations from a JSON file
        
        Args:
            stations_file: Optional path to the stations file
        """
        if stations_file is None:
            stations_file = config.STATIONS_JSON_PATH
            
        try:
            with open(stations_file, 'r') as f:
                self.stations = json.load(f)
            
            # Reset filtered stations and pagination
            self.filtered_stations = self.stations
            self.current_page = 0
            
            # Populate the initial page
            self.populate_stations_list(self.filtered_stations[:config.PAGE_SIZE])
            self.update_status_label()
            
            # Mark favorites in the stations list
            self.update_favorites_in_list()
            
            return True
        except Exception as e:
            print(f"Failed to load stations: {str(e)}")
            return False
    
    def load_favorites(self):
        """Load favorites from the saved JSON file"""
        try:
            if os.path.exists(config.FAVORITES_PATH):
                with open(config.FAVORITES_PATH, 'r') as f:
                    self.favorites = json.load(f)
                self.populate_favorites_list()
        except Exception as e:
            print(f"Failed to load favorites: {str(e)}")
            self.favorites = []
    
    def save_favorites(self):
        """Save favorites to a JSON file"""
        try:
            with open(config.FAVORITES_PATH, 'w') as f:
                json.dump(self.favorites, f)
            return True
        except Exception as e:
            print(f"Failed to save favorites: {str(e)}")
            return False
    
    def populate_stations_list(self, stations_to_show):
        """
        Populate the stations list with the given stations
        
        Args:
            stations_to_show: List of station dictionaries to display
        """
        # Clear the list first
        for child in self.stations_list.get_children():
            self.stations_list.remove(child)
        
        # Reset pagination
        self.current_page = 0
        
        # Add stations to the list
        if stations_to_show:
            for station in stations_to_show:
                self.add_station_row(station)
        
        self.stations_list.show_all()
    
    def append_stations_to_list(self, stations_to_append):
        """
        Append more stations to the existing list
        
        Args:
            stations_to_append: List of station dictionaries to append
        """
        for station in stations_to_append:
            self.add_station_row(station)
        self.stations_list.show_all()
    
    def add_station_row(self, station):
        """
        Create and add a new row for a station
        
        Args:
            station: Station dictionary data
        """
        row = Gtk.ListBoxRow()
        row.get_style_context().add_class("station-row")
        row.station_data = station  # Store station data in the row
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_start(10)
        hbox.set_margin_end(10)
        hbox.set_margin_top(5)
        hbox.set_margin_bottom(5)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        # Station name with width constraint to prevent window expansion
        name_label = Gtk.Label(label=station.get('name', 'Unknown Station'))
        name_label.set_halign(Gtk.Align.START)
        name_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        name_label.set_max_width_chars(40)  # Limit width
        name_label.get_style_context().add_class("station-name")
        vbox.pack_start(name_label, False, False, 0)
        
        # Station info with width constraint
        info_text = f"{station.get('country', 'Unknown')} • {station.get('language', 'Unknown')} • {station.get('codec', 'Unknown')}"
        info_label = Gtk.Label(label=info_text)
        info_label.set_halign(Gtk.Align.START)
        info_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        info_label.set_max_width_chars(50)  # Limit width
        info_label.get_style_context().add_class("station-info")
        vbox.pack_start(info_label, False, False, 0)
        
        hbox.pack_start(vbox, True, True, 0)
        
        # Add a star icon if the station is in favorites
        if any(fav.get('stationuuid') == station.get('stationuuid') for fav in self.favorites):
            star = Gtk.Image.new_from_icon_name("starred-symbolic", Gtk.IconSize.BUTTON)
            hbox.pack_end(star, False, False, 0)
        
        row.add(hbox)
        self.stations_list.add(row)
    
    def populate_favorites_list(self):
        """Populate the favorites list with saved favorites"""
        # Clear the list first
        for child in self.favorites_list.get_children():
            self.favorites_list.remove(child)
        
        # Add each favorite to the list
        for station in self.favorites:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("station-row")
            row.station_data = station  # Store station data in the row
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_start(10)
            hbox.set_margin_end(10)
            hbox.set_margin_top(5)
            hbox.set_margin_bottom(5)
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            
            # Station name
            name_label = Gtk.Label(label=station.get('name', 'Unknown Station'))
            name_label.set_halign(Gtk.Align.START)
            name_label.get_style_context().add_class("station-name")
            vbox.pack_start(name_label, False, False, 0)
            
            # Station info
            info_text = f"{station.get('country', 'Unknown')} • {station.get('language', 'Unknown')} • {station.get('codec', 'Unknown')}"
            info_label = Gtk.Label(label=info_text)
            info_label.set_halign(Gtk.Align.START)
            info_label.get_style_context().add_class("station-info")
            vbox.pack_start(info_label, False, False, 0)
            
            hbox.pack_start(vbox, True, True, 0)
            
            # Add a remove button
            remove_btn = Gtk.Button()
            remove_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
            remove_btn.add(remove_icon)
            remove_btn.set_tooltip_text("Remove from favorites")
            remove_btn.connect("clicked", lambda btn, s=station: self.remove_favorite(s))
            hbox.pack_end(remove_btn, False, False, 0)
            
            row.add(hbox)
            self.favorites_list.add(row)
        
        self.favorites_list.show_all()
    
    def search_stations(self, search_text):
        """
        Search for stations matching the given text
        
        Args:
            search_text: Text to search for
        """
        if not search_text:
            # If search field is empty, show all stations
            self.filtered_stations = self.stations
        else:
            # Convert to lowercase for case-insensitive search
            search_text = search_text.lower()
            
            # Filter stations based on search text
            self.filtered_stations = [
                station for station in self.stations 
                if search_text in station.get('name', '').lower() or 
                   search_text in station.get('country', '').lower() or
                   search_text in station.get('language', '').lower() or
                   search_text in station.get('tags', '').lower()
            ]
        
        # Show the first page of filtered stations
        self.populate_stations_list(self.filtered_stations[:config.PAGE_SIZE])
        self.update_status_label()
    
    def filter_stations(self, filter_type):
        """
        Filter stations by the specified type
        
        Args:
            filter_type: Type of filter to apply (e.g., 'All', 'Favorites', etc.)
        """
        if filter_type == "All Stations":
            self.filtered_stations = self.stations
        elif filter_type == "Favorites":
            # Show all stations that are in favorites
            self.filtered_stations = [s for s in self.stations if any(
                f.get('stationuuid') == s.get('stationuuid') for f in self.favorites)]
        # Additional filters can be implemented here
        
        # Show the first page of filtered stations
        self.populate_stations_list(self.filtered_stations[:config.PAGE_SIZE])
        self.update_status_label()
    
    def is_favorite(self, station):
        """
        Check if a station is in favorites
        
        Args:
            station: Station dictionary to check
        
        Returns:
            bool: True if the station is a favorite, False otherwise
        """
        if not station:
            return False
            
        return any(
            fav.get('stationuuid') == station.get('stationuuid') 
            for fav in self.favorites
        )
    
    def add_favorite(self, station):
        """
        Add a station to favorites
        
        Args:
            station: Station dictionary to add
        """
        # Check if already in favorites
        if self.is_favorite(station):
            return
        
        # Add to favorites
        self.favorites.append(station)
        self.save_favorites()
        self.populate_favorites_list()
        
        # Update any star icons in the main list
        self.update_favorites_in_list()
    
    def remove_favorite(self, station):
        """
        Remove a station from favorites
        
        Args:
            station: Station dictionary to remove
        """
        if not station:
            return
            
        # Filter out the station to remove
        self.favorites = [fav for fav in self.favorites 
                         if fav.get('stationuuid') != station.get('stationuuid')]
        self.save_favorites()
        self.populate_favorites_list()
        
        # Update any star icons in the main list
        self.update_favorites_in_list()
        
    def toggle_favorite(self, station):
        """
        Toggle favorite status for a station
        
        Args:
            station: Station dictionary
        
        Returns:
            bool: True if station is now a favorite, False if it was removed
        """
        if not station:
            return False
            
        # Check if this station is already a favorite
        if self.is_favorite(station):
            self.remove_favorite(station)
            return False
        else:
            self.add_favorite(station)
            return True
    
    def update_favorites_in_list(self):
        """Update star icons in the main stations list"""
        for row in self.stations_list.get_children():
            if hasattr(row, 'station_data'):
                station = row.station_data
                
                # Check if this station is in favorites
                is_favorite = any(
                    fav.get('stationuuid') == station.get('stationuuid') 
                    for fav in self.favorites
                )
                
                # Get the hbox containing station info
                hbox = row.get_child()
                
                # Check if there's already a star icon
                star = None
                for child in hbox.get_children():
                    if isinstance(child, Gtk.Image):
                        star = child
                        break
                
                if is_favorite and not star:
                    # Add a star icon
                    star = Gtk.Image.new_from_icon_name("starred-symbolic", Gtk.IconSize.BUTTON)
                    hbox.pack_end(star, False, False, 0)
                elif not is_favorite and star:
                    # Remove the star icon
                    hbox.remove(star)
        
        self.stations_list.show_all()
    
    def update_status_label(self):
        """Update the status label to show how many results are being displayed"""
        total = len(self.filtered_stations)
        displayed = min((self.current_page + 1) * config.PAGE_SIZE, total)
        
        if total == len(self.stations):
            # No filtering applied
            self.status_label.set_text(f"Showing {displayed} of {total} stations. Scroll down to load more.")
        else:
            # Filtering applied
            self.status_label.set_text(f"Found {total} stations. Showing {displayed}. Scroll down to load more.")
    
    def _on_edge_reached(self, scrolled_window, pos):
        """Handle scrolling to the bottom to load more stations"""
        if pos == Gtk.PositionType.BOTTOM and not self.is_loading_more:
            self._load_more_stations()
    
    def _load_more_stations(self):
        """Load the next page of stations"""
        if self.is_loading_more:
            return
        
        self.is_loading_more = True
        
        # Calculate the next page of stations to load
        start_index = (self.current_page + 1) * config.PAGE_SIZE
        end_index = start_index + config.PAGE_SIZE
        
        # Check if there are more stations to load
        if start_index >= len(self.filtered_stations):
            self.is_loading_more = False
            return
        
        # Get the next batch of stations
        next_batch = self.filtered_stations[start_index:end_index]
        
        # If there are no more stations, stop
        if not next_batch:
            self.is_loading_more = False
            return
        
        # Add the next batch to the list
        self.append_stations_to_list(next_batch)
        
        # Increment the current page
        self.current_page += 1
        self.update_status_label()
        
        self.is_loading_more = False
    
    def _on_station_activated(self, listbox, row):
        """Handle station selection in the main list"""
        if hasattr(row, 'station_data') and self.on_station_activated:
            self.on_station_activated(row.station_data)
    
    def _on_favorite_activated(self, listbox, row):
        """Handle station selection in the favorites list"""
        if hasattr(row, 'station_data') and self.on_station_activated:
            # Only activate the station, don't alter favorite status
            self.on_station_activated(row.station_data)