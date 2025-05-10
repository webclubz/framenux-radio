#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Convert relative imports to absolute imports
from src.player import RadioPlayer
from src.utils import config
from src.utils.downloader import StationDownloader
from src.ui.now_playing import NowPlayingView
from src.ui.stations import StationsList

# Add main function for entry point
def main():
    app = RadioApp()
    return app.run()

class RadioApp(Gtk.Application):
    """
    Main Framenux Radio application
    """
    
    def __init__(self):
        super().__init__(application_id="com.framenux.radio")
        self.connect("activate", self.on_activate)
        
        # Initialize the radio player
        self.player = RadioPlayer()
        self.player.set_metadata_callback(self.on_metadata_update)
        
        # Current state
        self.current_station = None
        self.is_playing = False
        
        # Store signal handler IDs for later use
        self.favorite_handler_id = None
    
    def on_activate(self, app):
        # Create the main window
        self.window = Gtk.ApplicationWindow(application=app, title="Framenux Radio")
        self.window.set_default_size(800, 600)  # Wider window to accommodate station image
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Add constraints to prevent window from expanding too much
        screen = Gdk.Screen.get_default()
        monitor_geometry = screen.get_monitor_geometry(0)  # Primary monitor
        max_width = min(1200, monitor_geometry.width - 50)  # Max width with some margin
        self.window.set_size_request(700, 500)  # Minimum size
        self.window.set_default_size(min(700, max_width), 600)
        
        # Apply CSS styling
        self.setup_css()

        # Create main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.window.add(main_box)

        # Create header with title and buttons
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Framenux Radio"
        self.window.set_titlebar(header)

        # Update button - moved to the left side
        update_button = Gtk.Button()
        update_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        update_button.add(update_icon)
        update_button.set_tooltip_text("Update Station List")
        update_button.connect("clicked", self.on_update_clicked)
        header.pack_start(update_button)
        
        # Clear images cache button - added to the left side
        clear_cache_button = Gtk.Button()
        clear_icon = Gtk.Image.new_from_icon_name("edit-clear-all-symbolic", Gtk.IconSize.BUTTON)
        clear_cache_button.add(clear_icon)
        clear_cache_button.set_tooltip_text("Clear Station Images Cache")
        clear_cache_button.connect("clicked", self.clear_station_images)
        header.pack_start(clear_cache_button)
        
        # Left side: Station list and search
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Create search entry
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        search_box.set_margin_top(10)
        search_box.set_margin_bottom(10)
        search_box.set_margin_start(10)
        search_box.set_margin_end(10)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search stations...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, True, True, 0)
        
        # Filter dropdown
        filter_combo = Gtk.ComboBoxText()
        filter_combo.append_text("All Stations")
        filter_combo.append_text("By Country")
        filter_combo.append_text("By Language")
        filter_combo.append_text("Favorites")
        filter_combo.set_active(0)
        filter_combo.connect("changed", self.on_filter_changed)
        search_box.pack_start(filter_combo, False, False, 0)
        
        left_box.pack_start(search_box, False, False, 0)
        
        # Initialize the stations list manager
        self.stations_manager = StationsList(on_station_activated=self.on_station_activated)
        
        # Add status label to left box
        left_box.pack_start(self.stations_manager.status_label, False, False, 0)
        
        # Create a tab view for All Stations and Favorites
        notebook = Gtk.Notebook()
        left_box.pack_start(notebook, True, True, 0)
        
        # All Stations tab
        all_stations_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebook.append_page(all_stations_page, Gtk.Label(label="All Stations"))
        all_stations_page.pack_start(self.stations_manager.scrolled_window, True, True, 0)
        
        # Favorites tab
        favorites_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebook.append_page(favorites_page, Gtk.Label(label="Favorites"))
        favorites_page.pack_start(self.stations_manager.favorites_scrolled, True, True, 0)
        
        # Add the left box to the main layout
        main_box.pack_start(left_box, True, True, 0)
        
        # Right side: Now Playing view with station image and details
        # Create a separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(separator, False, False, 0)
        
        # Create a fixed-width container for the now playing view
        # Using a GtkBox inside a GtkAlignment to enforce consistent width
        right_align = Gtk.Alignment()
        right_align.set_size_request(230, -1)  # Strict fixed width
        
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        right_box.set_homogeneous(False)
        # Apply CSS for strict width control
        right_box.get_style_context().add_class("sidebar")
        
        # Add the now playing view to the right box
        self.now_playing_view = NowPlayingView()
        right_box.pack_start(self.now_playing_view, False, False, 0)
        
        # Add spacer to push controls to the bottom
        right_box.pack_start(Gtk.Box(), True, True, 0)
        
        # Create player controls at the bottom of the right panel
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        controls_box.get_style_context().add_class("player-controls")
        controls_box.set_margin_top(10)
        controls_box.set_margin_bottom(10)
        controls_box.set_margin_start(10)
        controls_box.set_margin_end(10)
        
        # Play/Pause and Stop buttons in one row
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        buttons_box.set_halign(Gtk.Align.CENTER)
        
        # Play/Pause button
        self.play_button = Gtk.Button()
        play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON)
        self.play_button.add(play_icon)
        self.play_button.connect("clicked", self.on_play_clicked)
        buttons_box.pack_start(self.play_button, False, False, 0)
        
        # Stop button
        stop_button = Gtk.Button()
        stop_icon = Gtk.Image.new_from_icon_name("media-playback-stop-symbolic", Gtk.IconSize.BUTTON)
        stop_button.add(stop_icon)
        stop_button.connect("clicked", self.on_stop_clicked)
        buttons_box.pack_start(stop_button, False, False, 0)
        
        # Favorite button
        self.favorite_button = Gtk.ToggleButton()
        favorite_icon = Gtk.Image.new_from_icon_name("non-starred-symbolic", Gtk.IconSize.BUTTON)
        self.favorite_button.add(favorite_icon)
        self.favorite_handler_id = self.favorite_button.connect("toggled", self.on_favorite_toggled)
        buttons_box.pack_start(self.favorite_button, False, False, 0)
        
        controls_box.pack_start(buttons_box, False, False, 0)
        
        # Volume control
        volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        volume_box.set_margin_top(5)
        volume_box.set_halign(Gtk.Align.CENTER)
        
        volume_icon = Gtk.Image.new_from_icon_name("audio-volume-medium-symbolic", Gtk.IconSize.BUTTON)
        volume_box.pack_start(volume_icon, False, False, 0)
        
        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.volume_scale.set_value(70)  # Default volume
        self.volume_scale.set_size_request(180, -1)
        self.volume_scale.connect("value-changed", self.on_volume_changed)
        volume_box.pack_start(self.volume_scale, False, False, 0)
        
        controls_box.pack_start(volume_box, False, False, 0)
        
        # Add controls to the right box
        right_box.pack_start(controls_box, False, False, 0)
        
        # Add right_box to the alignment container
        right_align.add(right_box)
        
        # Add the right alignment to the main layout
        main_box.pack_start(right_align, False, False, 0)
        
        # Load stations if available, otherwise prompt to download
        if not self.check_stations_file():
            self.show_download_dialog()
        
        self.window.show_all()
    
    def setup_css(self):
        """Set up CSS styling for the application"""
        css_provider = Gtk.CssProvider()
        css = """
        .station-row {
            padding: 10px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
        .station-name {
            font-weight: bold;
            font-size: 14px;
        }
        .station-info {
            font-size: 12px;
            
        }
        .player-controls {
            background-color: rgba(0, 0, 0, 0.05);
            border-radius: 5px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            padding-top: 10px;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def check_stations_file(self):
        """Check if the stations file exists and load it"""
        import os
        if os.path.exists(config.STATIONS_JSON_PATH):
            return self.stations_manager.load_stations()
        return False
    
    def show_download_dialog(self):
        """Show dialog to confirm downloading the station list"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Download Radio Station List"
        )
        dialog.format_secondary_text(
            "The radio station list needs to be downloaded (approx. 54,000 stations). Do you want to download it now?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.download_stations()
        else:
            # Exit if user cancels the download
            self.quit()
    
    def download_stations(self):
        """Download the stations list"""
        # Show progress dialog
        self.show_progress_dialog()
        
        # Create downloader with callbacks
        downloader = StationDownloader(
            on_complete=self.on_download_complete,
            on_error=self.on_download_error
        )
        
        # Start the download
        downloader.start_download()
    
    def show_progress_dialog(self):
        """Show a progress dialog during download"""
        self.progress_dialog = Gtk.Dialog(
            title="Downloading",
            transient_for=self.window,
            flags=0
        )
        self.progress_dialog.set_default_size(300, 100)
        
        box = self.progress_dialog.get_content_area()
        label = Gtk.Label(label="Downloading radio station list...")
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        box.pack_start(label, True, True, 0)
        
        spinner = Gtk.Spinner()
        spinner.start()
        box.pack_start(spinner, True, True, 0)
        
        self.progress_dialog.show_all()
    
    def close_progress_dialog(self):
        """Close the progress dialog"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()
            delattr(self, 'progress_dialog')
    
    def on_download_complete(self):
        """Handle successful download"""
        self.close_progress_dialog()
        self.stations_manager.load_stations()
    
    def on_download_error(self, error_message):
        """Handle download error"""
        self.close_progress_dialog()
        self.show_error_dialog(error_message)
    
    def show_error_dialog(self, message):
        """Show an error dialog with the given message"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def on_update_clicked(self, button):
        """Handle the update button click"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Update Station List"
        )
        dialog.format_secondary_text(
            "Do you want to download the latest radio station list from the server?"
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.download_stations()
    
    def on_search_changed(self, search_entry):
        """Handle search as the user types"""
        search_text = search_entry.get_text()
        self.stations_manager.search_stations(search_text)
    
    def on_filter_changed(self, combo):
        """Handle filter dropdown changes"""
        filter_text = combo.get_active_text()
        self.stations_manager.filter_stations(filter_text)
    
    def on_station_activated(self, station):
        """Handle station selection"""
        self.current_station = station
        
        # Update favorite button state
        is_favorite = self.stations_manager.is_favorite(station)
        
        # Block signal temporarily to prevent triggering the toggle handler
        if self.favorite_handler_id is not None:
            self.favorite_button.handler_block(self.favorite_handler_id)
        
        self.favorite_button.set_active(is_favorite)
        
        # Unblock signal
        if self.favorite_handler_id is not None:
            self.favorite_button.handler_unblock(self.favorite_handler_id)
        
        # Update now playing view
        self.now_playing_view.update_station(station)
        
        # Start playing
        self.play_station()
    
    def on_play_clicked(self, button):
        """Handle play/pause button click"""
        if not self.current_station:
            return
            
        if self.is_playing:
            self.pause_station()
        else:
            self.play_station()
    
    def on_stop_clicked(self, button):
        """Handle stop button click"""
        self.stop_station()
    
    def on_favorite_toggled(self, button):
        """Handle favorite button toggle"""
        if not self.current_station:
            return
        
        # Get the current state of the toggle button
        is_favorite = button.get_active()
        
        # Add or remove from favorites based on the button state
        if is_favorite:
            self.stations_manager.add_favorite(self.current_station)
        else:
            self.stations_manager.remove_favorite(self.current_station)
    
    def on_volume_changed(self, scale):
        """Handle volume change"""
        volume = scale.get_value() / 100.0
        try:
            self.player.set_volume(volume)
        except Exception as e:
            self.show_error_dialog(f"Failed to change volume: {str(e)}")
    
    def on_metadata_update(self, metadata):
        """Handle metadata updates from the stream"""
        # Update the now playing information
        self.now_playing_view.update_now_playing(metadata)
        
        # Also check for stream format information
        stream_info = self.player.get_stream_info()
        if stream_info:
            self.now_playing_view.update_stream_info(stream_info)
    
    def play_station(self):
        """Play the current station"""
        if not self.current_station:
            return
        
        url = self.current_station.get('url')
        if not url:
            self.show_error_dialog("This station does not have a valid URL")
            return
        
        try:
            self.player.play(url)
            self.is_playing = True
            
            # Update UI
            self.now_playing_view.update_station(self.current_station, is_playing=True)
            play_icon = Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON)
            self.play_button.get_children()[0].destroy()
            self.play_button.add(play_icon)
            self.play_button.show_all()
        except Exception as e:
            self.show_error_dialog(f"Failed to play station: {str(e)}")
    
    def pause_station(self):
        """Pause the current station"""
        try:
            self.player.pause()
            self.is_playing = False
            
            # Update UI
            play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON)
            self.play_button.get_children()[0].destroy()
            self.play_button.add(play_icon)
            self.play_button.show_all()
        except Exception as e:
            self.show_error_dialog(f"Failed to pause playback: {str(e)}")
    
    def stop_station(self):
        """Stop playing the current station"""
        try:
            self.player.stop()
            self.is_playing = False
            
            # Update UI
            if self.current_station:
                self.now_playing_view.update_station(self.current_station, is_playing=False)
                
            play_icon = Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON)
            self.play_button.get_children()[0].destroy()
            self.play_button.add(play_icon)
            self.play_button.show_all()
        except Exception as e:
            self.show_error_dialog(f"Failed to stop playback: {str(e)}")
    
    def clear_station_images(self, button):
        """Clear all downloaded station images from the cache folder"""
        import os
        import shutil
        
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Clear Station Images Cache"
        )
        dialog.format_secondary_text(
            "Do you want to delete all downloaded station images? This will free up disk space."
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            try:
                # Count files before deletion
                file_count = len([f for f in os.listdir(config.STATION_IMAGES_DIR) 
                                if os.path.isfile(os.path.join(config.STATION_IMAGES_DIR, f))])
                
                # Empty the directory by recreating it
                shutil.rmtree(config.STATION_IMAGES_DIR)
                os.makedirs(config.STATION_IMAGES_DIR, exist_ok=True)
                
                # Show success message
                success_dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Cache Cleared"
                )
                success_dialog.format_secondary_text(
                    f"Successfully deleted {file_count} station images from the cache."
                )
                success_dialog.run()
                success_dialog.destroy()
                
                # Reset the current display image to default if there's a current station
                if self.current_station:
                    self.now_playing_view.set_default_image()
                    
            except Exception as e:
                self.show_error_dialog(f"Failed to clear image cache: {str(e)}")