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
WM_LBUTTONDOWN = 0x0201
WM_MOUSEMOVE = 0x0200
WM_TIMER = 0x0113
WM_ERASEBKGND = 0x0014
SW_SHOW = 5
DT_LEFT = 0x0000
DT_VCENTER = 0x0004
DT_SINGLELINE = 0x0020
TRANSPARENT = 1
COLOR_BACKGROUND = 0x00F7F9FC
COLOR_SURFACE = 0x00FFFFFF
COLOR_TEXT = 0x002B3440
COLOR_MUTED = 0x006B7785
COLOR_BORDER = 0x00D5DCE5
COLOR_TRACK = 0x00E7ECF2
COLOR_ACCENT = 0x00395DD9
COLOR_ACCENT_DARK = 0x002D49A7


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
        if message == WM_MOUSEMOVE:
            window._move(lparam & 0xFFFF, (lparam >> 16) & 0xFFFF)
            return 0
        if message == WM_LBUTTONDOWN:
            window._press(lparam & 0xFFFF, (lparam >> 16) & 0xFFFF)
            return 0
        if message == WM_LBUTTONUP:
            window._click(lparam & 0xFFFF, (lparam >> 16) & 0xFFFF)
            return 0
        if message == WM_TIMER:
            window._timer(wparam)
            return 0
        if message == WM_ERASEBKGND:
            return 1
        if message == WM_DESTROY:
            _windows.pop(hwnd, None)
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, message, wparam, lparam)

    _window_proc = window_proc
    instance = kernel32.GetModuleHandleW(None)
    window_class = WNDCLASSW(CS_HREDRAW | CS_VREDRAW, ctypes.cast(_window_proc, ctypes.c_void_p), 0, 0, instance, None, user32.LoadCursorW(None, IDC_ARROW), _color(COLOR_BACKGROUND), None, "FlegmGuiWindow")
    if not user32.RegisterClassW(ctypes.byref(window_class)) and ctypes.get_last_error() != 1410:
        raise ctypes.WinError()
    _class_registered = True


from .Classes.controls import CheckBox, ProgressBar, Separator
from .Classes.layout import Row
from .Classes.label import Button, Label
from .Classes.window import Window