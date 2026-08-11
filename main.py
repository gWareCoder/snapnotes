#!/usr/bin/env python3
import sys
import argparse
import os

# Add application directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SnapNotesApp

def parse_args():
    parser = argparse.ArgumentParser(description="SnapNotes — Screen Capture, History & Notes Tool")
    parser.add_argument("-t", "--tray", action="store_true", help="Start minimized in system tray")
    parser.add_argument("-c", "--capture", action="store_true", help="Trigger immediate area screenshot capture")
    parser.add_argument("-f", "--fullscreen", action="store_true", help="Trigger immediate fullscreen screenshot capture")
    return parser.parse_args()

def main():
    args = parse_args()
    app = SnapNotesApp(sys.argv)

    if args.capture:
        app.on_capture_area()
        sys.exit(app.run(start_in_tray=True))
    elif args.fullscreen:
        app.on_capture_fullscreen()
        sys.exit(app.run(start_in_tray=True))
    else:
        start_in_tray = args.tray or app.config.get("start_in_tray", False)
        sys.exit(app.run(start_in_tray=start_in_tray))

if __name__ == "__main__":
    main()
