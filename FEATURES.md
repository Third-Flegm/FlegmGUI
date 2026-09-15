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
- Button colors can be supplied as style keyword arguments
- `Button.set_style(...)` updates colors after creation
- Buttons animate hover and pressed visual states
- Button painting is handled by flegmgui using GDI
- Button mouse hit testing is handled by flegmgui
- Button callbacks run when the button is clicked
- `Window.checkbox(text, command)` creates a toggleable `CheckBox`
- `CheckBox.set(checked)` updates its state and repaints
- `Window.progress(value)` creates a `ProgressBar` with a clamped 0-100 value
- `Window.progress(value, on_change)` supports centralized progress updates
- `ProgressBar.set(value)` updates progress and repaints
- `ProgressBar.increment(amount)` advances progress without manual value tracking
- `ProgressBar.animate_to(value, speed)` smoothly moves toward a target value
- `ProgressBar.set_on_change(callback)` attaches progress updates after creation
- `Window.separator()` creates a non-interactive `Separator`
- `Window.row(...)` creates a styled horizontal layout container
- Rows support side-by-side labels, buttons, checkboxes, and progress bars
- Row `gap`, `padding`, `background`, `border`, and child widths are configurable

## Rendering

- Text is painted with Win32 `DrawTextW`
- Labels and buttons use flegmgui-managed rectangles
- Buttons use custom colors, sizing, and layout
- Controls share a light background, accent color, border, and spacing palette
- Rendering uses double buffering to reduce flashing during updates and animation
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
- Current widgets are `Window`, `Label`, `Button`, `CheckBox`, `ProgressBar`, and `Separator`
- Layout is a simple vertical flow
- No keyboard navigation, menus, text inputs, images, themes, or accessibility layer yet

## Ideas

- Add a `TextInput` widget with keyboard input, selection, and clipboard support
- Add `Slider` and `SpinBox` controls for numeric values
- Add `ComboBox` and `ListBox` controls for choosing from options
- Add horizontal and grid layout containers
- Add window close events and a reusable application object
- Add keyboard focus, tab navigation, and accelerator keys
- Add menu bars, context menus, and keyboard shortcuts
- Add themes for colors, fonts, spacing, and widget states
- Add image loading and an image widget
- Add accessibility metadata and high-contrast rendering
- Add timers for animations and periodic callbacks
- Add automated Windows integration tests with screenshot checks
