#!/usr/bin/env python3
"""
Framenux Radio - Internet Radio Player
Main entry point
"""

# Use absolute import instead of relative import
from src.ui.app import RadioApp

def main():
    app = RadioApp()
    return app.run()

if __name__ == "__main__":
    main()