# flegmgui Features

This file is the current feature inventory for flegmgui.

## Platform

- Windows desktop support through `ctypes`
- Direct Win32 window creation
- Direct GDI drawing
- No Tkinter, Qt, or other GUI framework dependency
- No third-party runtime dependency

## Window

- `Window(title, width, height)` creates a native top-level window
- Configurable title and initial size
- Minimum client size of 280 by 180 pixels
- Custom message loop through `Window.run()`
- Automatic relayout when the window is resized
- Custom background color

## Widgets

- `Window.label(text)` creates a library-owned `Label`
- `Label.set(text)` updates text and repaints the label
- `Window.button(text, command)` creates a library-owned `Button`
- Button painting is handled by flegmgui using GDI
- Button mouse hit testing is handled by flegmgui
- Button callbacks run when the button is clicked

## Rendering

- Text is painted with Win32 `DrawTextW`
- Labels and buttons use flegmgui-managed rectangles
- Buttons use custom colors, sizing, and layout
- Painting occurs in the native `WM_PAINT` handler

## Public API

```python
from flegmgui import Button, Label, Window

app = Window("My app", width=520, height=320)
status = app.label("Ready")
app.button("Click me", lambda: status.set("Clicked"))
app.run()
```

## Current limitations

- Windows only
- Current widgets are `Window`, `Label`, and `Button`
- Layout is a simple vertical flow
- No keyboard navigation, menus, text inputs, images, themes, or accessibility layer yet
