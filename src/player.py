#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class RadioPlayer:
    """
    Radio player implementation using GStreamer
    """
    
    def __init__(self):
        # Initialize GStreamer
        Gst.init(None)
        
        # Create the playbin element for audio playback
        self.player = Gst.ElementFactory.make("playbin", "player")
        
        # Create bus to get events from the pipeline
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
        # Set initial volume
        self.player.set_property("volume", 0.7)
        
        # Track the current state
        self.current_url = None
        self.is_playing = False
        
        # Stream metadata
        self.metadata = {}
        self.metadata_callback = None
        
    def play(self, url):
        """Play a radio station from the given URL"""
        # If already playing something, stop first
        if self.is_playing:
            self.stop()
        
        # Set the URI to play
        self.player.set_property("uri", url)
        self.current_url = url
        
        # Start playback
        self.player.set_state(Gst.State.PLAYING)
        self.is_playing = True
        
    def pause(self):
        """Pause the current playback"""
        if self.is_playing:
            self.player.set_state(Gst.State.PAUSED)
            self.is_playing = False
    
    def resume(self):
        """Resume playback after pausing"""
        if not self.is_playing and self.current_url:
            self.player.set_state(Gst.State.PLAYING)
            self.is_playing = True
    
    def stop(self):
        """Stop the current playback"""
        self.player.set_state(Gst.State.NULL)
        self.is_playing = False
    
    def set_volume(self, volume):
        """Set the playback volume (0.0 to 1.0)"""
        self.player.set_property("volume", volume)
    
    def get_stream_info(self):
        """
        Get information about the current stream such as bitrate, codec, etc.
        Returns a dictionary with the available information
        """
        info = {}
        
        if not self.is_playing:
            return info
        
        try:
            # Get the current audio sink pad
            sink_pad = self.player.get_static_pad("sink")
            if not sink_pad:
                return info
            
            # Get the negotiated caps
            caps = sink_pad.get_current_caps()
            if not caps:
                return info
            
            # Extract information from the caps
            for i in range(caps.get_size()):
                structure = caps.get_structure(i)
                if structure:
                    # Get the codec/format
                    info['format'] = structure.get_name()
                    
                    # Get audio channels
                    channels = structure.get_value("channels")
                    if channels:
                        info['channels'] = channels
                    
                    # Get sample rate
                    rate = structure.get_value("rate")
                    if rate:
                        info['sample_rate'] = f"{rate/1000:.1f} kHz"
        except:
            pass
        
        return info
    
    def set_metadata_callback(self, callback):
        """Set a callback function to receive metadata updates"""
        self.metadata_callback = callback
    
    def on_message(self, bus, message):
        """Handle messages from the GStreamer bus"""
        t = message.type
        
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err.message}")
            self.stop()
        
        elif t == Gst.MessageType.EOS:
            # End of stream, this shouldn't happen for radio stations
            # but just in case, restart the stream
            self.player.set_state(Gst.State.NULL)
            self.player.set_state(Gst.State.PLAYING)
        
        elif t == Gst.MessageType.STATE_CHANGED:
            # Track state changes for debugging
            if message.src == self.player:
                old_state, new_state, pending_state = message.parse_state_changed()
                print(f"Pipeline state changed from {old_state.value_nick} to {new_state.value_nick}")
        
        elif t == Gst.MessageType.TAG:
            # Extract metadata from the stream
            tags = message.parse_tag()
            
            # Process the tags
            tags_dict = {}
            tags.foreach(lambda tag, val: tags_dict.update({tag: val}))
            
            # Update metadata and notify callback
            if tags_dict:
                self.metadata.update(tags_dict)
                if self.metadata_callback:
                    self.metadata_callback(self.metadata)