"""A small custom Win32 GUI toolkit for flegmgui.

The widgets here are drawn directly into one native window. There are no Tk,
Qt, or native button/label controls involved; flegmgui owns painting, layout,
and mouse dispatch.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from collections.abc import Callable

if not hasattr(ctypes, "windll"):
    raise RuntimeError("flegmgui currently supports Windows only")

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
user32.DefWindowProcW.restype = ctypes.c_ssize_t

CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
CW_USEDEFAULT = 0x80000000
IDC_ARROW = 32512
COLOR_WINDOW = 5
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_SIZE = 0x0005
WM_LBUTTONUP = 0x0202
SW_SHOW = 5
DT_LEFT = 0x0000
DT_VCENTER = 0x0004
DT_SINGLELINE = 0x0020
TRANSPARENT = 1


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", RECT), ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", wintypes.BYTE * 32)]


class WNDCLASSW(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", ctypes.c_void_p), ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON), ("hCursor", wintypes.HCURSOR), ("hbrBackground", wintypes.HBRUSH), ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t)
_windows: dict[int, Window] = {}
_window_proc: object = None
_class_registered = False


def _color(value: int) -> wintypes.HBRUSH:
    return gdi32.CreateSolidBrush(value)


def _register_class() -> None:
    global _class_registered, _window_proc
    if _class_registered:
        return

    @WNDPROC
    def window_proc(hwnd: int, message: int, wparam: int, lparam: int) -> int:
        window = _windows.get(hwnd)
        if window is None:
            return user32.DefWindowProcW(hwnd, message, wparam, lparam)
        if message == WM_PAINT:
            window._paint()
            return 0
        if message == WM_SIZE:
            window._layout()
            return 0
        if message == WM_LBUTTONUP:
            window._click(lparam & 0xFFFF, (lparam >> 16) & 0xFFFF)
            return 0
        if message == WM_DESTROY:
            _windows.pop(hwnd, None)
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, message, wparam, lparam)

    _window_proc = window_proc
    instance = kernel32.GetModuleHandleW(None)
    window_class = WNDCLASSW(CS_HREDRAW | CS_VREDRAW, ctypes.cast(_window_proc, ctypes.c_void_p), 0, 0, instance, None, user32.LoadCursorW(None, IDC_ARROW), _color(0x00F1F4F4), None, "FlegmGuiWindow")
    if not user32.RegisterClassW(ctypes.byref(window_class)) and ctypes.get_last_error() != 1410:
        raise ctypes.WinError()
    _class_registered = True


class Window:
    """A top-level native window rendered by flegmgui itself."""

    def __init__(self, title: str = "flegmgui", width: int = 420, height: int = 280) -> None:
        _register_class()
        self._widgets: list[Label | Button] = []
        self._hwnd = user32.CreateWindowExW(0, "FlegmGuiWindow", title, 0x10CF0000, CW_USEDEFAULT, CW_USEDEFAULT, width, height, None, None, kernel32.GetModuleHandleW(None), None)
        if not self._hwnd:
            raise ctypes.WinError()
        _windows[self._hwnd] = self
        user32.ShowWindow(self._hwnd, SW_SHOW)
        user32.UpdateWindow(self._hwnd)

    def label(self, text: str) -> Label:
        label = Label(self, text)
        self._widgets.append(label)
        self._layout()
        return label

    def button(self, text: str, command: Callable[[], None]) -> Button:
        button = Button(self, text, command)
        self._widgets.append(button)
        self._layout()
        return button

    def run(self) -> None:
        """Run flegmgui's native Windows message loop."""
        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))

    def _layout(self) -> None:
        client = RECT()
        user32.GetClientRect(self._hwnd, ctypes.byref(client))
        y = 24
        for widget in self._widgets:
            widget._bounds = RECT(24, y, client.right - 24, y + widget.height)
            y += widget.height + 10
        user32.InvalidateRect(self._hwnd, None, False)

    def _paint(self) -> None:
        paint = PAINTSTRUCT()
        hdc = user32.BeginPaint(self._hwnd, ctypes.byref(paint))
        gdi32.SetBkMode(hdc, TRANSPARENT)
        for widget in self._widgets:
            widget._draw(hdc)
        user32.EndPaint(self._hwnd, ctypes.byref(paint))

    def _click(self, x: int, y: int) -> None:
        for widget in reversed(self._widgets):
            if widget._bounds.left <= x <= widget._bounds.right and widget._bounds.top <= y <= widget._bounds.bottom:
                widget._click()
                break


class Label:
    """Text painted directly into the window."""

    height = 32

    def __init__(self, window: Window, text: str) -> None:
        self._window = window
        self.text = text
        self._bounds = RECT()

    def set(self, text: str) -> None:
        self.text = text
        user32.InvalidateRect(self._window._hwnd, ctypes.byref(self._bounds), False)

    def _draw(self, hdc: wintypes.HDC) -> None:
        gdi32.SetTextColor(hdc, 0x00232124)
        user32.DrawTextW(hdc, self.text, -1, ctypes.byref(self._bounds), DT_LEFT | DT_VCENTER | DT_SINGLELINE)

    def _click(self) -> None:
        pass


class Button:
    """A custom painted button with library-owned hit testing."""

    height = 44

    def __init__(self, window: Window, text: str, command: Callable[[], None]) -> None:
        self._window = window
        self.text = text
        self.command = command
        self._bounds = RECT()

    def _draw(self, hdc: wintypes.HDC) -> None:
        brush = _color(0x00395DD9)
        gdi32.FillRect(hdc, ctypes.byref(self._bounds), brush)
        gdi32.DeleteObject(brush)
        gdi32.SetTextColor(hdc, 0x00FFFFFF)
        user32.DrawTextW(hdc, self.text, -1, ctypes.byref(self._bounds), DT_LEFT | DT_VCENTER | DT_SINGLELINE)

    def _click(self) -> None:
        self.command()
