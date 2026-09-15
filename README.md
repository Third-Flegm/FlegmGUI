# flegmgui

A small, custom Python GUI library built directly on the Windows API.

flegmgui does not wrap Tkinter, Qt, or native button and label controls. It owns
the window class, message loop, layout, painting, and mouse dispatch. The first
backend targets Windows through `ctypes`.

## Quick start

```powershell
python -m pip install git+https://github.com/ThatFlegm/flegmgui.git
python examples/hello.py
```

For local development, install the checkout in editable mode instead:

```powershell
python -m pip install -e .
```

```python
from flegmgui import Window

app = Window("My app", width=560, height=360)
status = app.label("Ready")
progress = app.progress(0, lambda value: status.set(f"Progress: {value}%"))
actions = app.row(gap=12, padding=10)
actions.button("Advance", lambda: progress.animate_to(progress.value + 10))
actions.button("Reset", lambda: progress.set(0))
app.run()
```

The library supports Windows 10 and later through the built-in `ctypes` module;
it has no third-party runtime dependencies. The included
[`examples/hello.py`](examples/hello.py) demonstrates a larger build-console
application with multiple progress stages, checkboxes, styled buttons, and
horizontal layout rows.

## Development

```powershell
python -m pip install -e .
python -m pip install pytest
pytest
```

The GUI itself must be run on Windows. Import and packaging tests can still be
run on other platforms where the test suite skips Windows-only behavior.
