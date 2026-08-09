# ScrollMate

A lightweight Windows accessibility utility that provides
alternative mouse-wheel scrolling through floating controls.

## Why ScrollMate?

ScrollMate was created to provide an alternative way to scroll
when a conventional mouse wheel is unreliable or unavailable.

## Features

- ▲ Scroll up
- ▼ Scroll down
- Adjustable/controlled scrolling
- Resizable Windows interface
- Minimize, maximize and close support
- Draggable interface
- Always-on-top window
- Standalone Windows executable

## Technologies

- Python
- Tkinter
- Windows API
- Git / GitHub
- PyInstaller

## How It Works

ScrollMate detects the window located at the user's last
mouse position and sends a Windows mouse-wheel event to that
application.

This allows the floating controls to act as an alternative
mouse-wheel interface without requiring the physical scroll
wheel.

## Installation

Download the latest Windows executable from the Releases page.

## Development

Clone the repository and run:

python ScrollMate_v1_3_drag_fixed.py

## Future Improvements

- System tray support
- Configurable scroll speed
- Keyboard shortcuts
- Accessibility customization
- Startup with Windows
