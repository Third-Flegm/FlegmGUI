# flegmgui

A small, custom Python GUI library built directly on the Windows API.

flegmgui does not wrap Tkinter, Qt, or native button and label controls. It owns
the window class, message loop, layout, painting, and mouse dispatch. The first
backend targets Windows through `ctypes`.

## Quick start

```powershell
python -m pip install -e .
python examples/hello.py
```

```python
from flegmgui import Window

app = Window("My app")
status = app.label("Ready")
app.button("Click me", lambda: status.set("Clicked!"))
app.run()
```

The first version intentionally keeps the API small. New widgets can follow the
same custom painting and event-dispatch pattern as `Label` and `Button` in
`src/flegmgui/core.py`.
