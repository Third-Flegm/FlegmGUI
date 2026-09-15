from __future__ import annotations

from collections.abc import Callable

from ..core import (
    CW_USEDEFAULT,
    PAINTSTRUCT,
    RECT,
    SW_SHOW,
    TRANSPARENT,
    COLOR_BACKGROUND,
    _register_class,
    _windows,
    _color,
    ctypes,
    gdi32,
    kernel32,
    user32,
    wintypes,
)
from .controls import CheckBox, ProgressBar, Separator
from .layout import Row
from .label import Button, Label


class Window:
    """A top-level native window rendered by flegmgui itself."""

    def __init__(self, title: str = "flegmgui", width: int = 420, height: int = 280) -> None:
        _register_class()
        self._widgets: list[Label | Button | CheckBox | ProgressBar | Separator | Row] = []
        self._timers: dict[int, Callable[[], None]] = {}
        self._next_timer_id = 1
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

    def button(self, text: str, command: Callable[[], None], **style: int) -> Button:
        button = Button(self, text, command, **style)
        self._widgets.append(button)
        self._layout()
        return button

    def checkbox(self, text: str, command: Callable[[bool], None] | None = None) -> CheckBox:
        checkbox = CheckBox(self, text, command)
        self._widgets.append(checkbox)
        self._layout()
        return checkbox

    def progress(self, value: int = 0, on_change: Callable[[int], None] | None = None) -> ProgressBar:
        progress = ProgressBar(self, value, on_change)
        self._widgets.append(progress)
        self._layout()
        return progress

    def separator(self) -> Separator:
        separator = Separator(self)
        self._widgets.append(separator)
        self._layout()
        return separator

    def row(self, **style: int) -> Row:
        row = Row(self, **style)
        self._widgets.append(row)
        self._layout()
        return row

    def run(self) -> None:
        """Run flegmgui's native Windows message loop."""
        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))

    def _layout(self) -> None:
        client = RECT()
        user32.GetClientRect(self._hwnd, ctypes.byref(client))
        left = 24
        right = max(left, client.right - 24)
        y = 24
        for widget in self._widgets:
            widget._bounds = RECT(left, y, right, y + widget.height)
            arrange = getattr(widget, "_layout_children", None)
            if arrange is not None:
                arrange()
            y += widget.height + 12
        self._refresh()

    def _refresh(self) -> None:
        """Repaint the complete window so removed text cannot remain visible."""
        user32.InvalidateRect(self._hwnd, None, False)

    def _start_timer(self, callback: Callable[[], None], interval_ms: int = 16) -> int:
        timer_id = self._next_timer_id
        self._next_timer_id += 1
        self._timers[timer_id] = callback
        user32.SetTimer(self._hwnd, timer_id, interval_ms, None)
        return timer_id

    def _stop_timer(self, timer_id: int) -> None:
        self._timers.pop(timer_id, None)
        user32.KillTimer(self._hwnd, timer_id)

    def _paint(self) -> None:
        paint = PAINTSTRUCT()
        hdc = user32.BeginPaint(self._hwnd, ctypes.byref(paint))
        client = RECT()
        user32.GetClientRect(self._hwnd, ctypes.byref(client))
        width = client.right - client.left
        height = client.bottom - client.top
        buffer_hdc = gdi32.CreateCompatibleDC(hdc)
        buffer_bitmap = gdi32.CreateCompatibleBitmap(hdc, width, height)
        previous_bitmap = gdi32.SelectObject(buffer_hdc, buffer_bitmap)
        background = _color(COLOR_BACKGROUND)
        user32.FillRect(buffer_hdc, ctypes.byref(client), background)
        gdi32.DeleteObject(background)
        gdi32.SetBkMode(buffer_hdc, TRANSPARENT)
        for widget in self._widgets:
            widget._draw(buffer_hdc)
        gdi32.BitBlt(hdc, 0, 0, width, height, buffer_hdc, 0, 0, 0x00CC0020)
        gdi32.SelectObject(buffer_hdc, previous_bitmap)
        gdi32.DeleteObject(buffer_bitmap)
        gdi32.DeleteDC(buffer_hdc)
        user32.EndPaint(self._hwnd, ctypes.byref(paint))

    def _click(self, x: int, y: int) -> None:
        for widget in self._widgets:
            release = getattr(widget, "_release", None)
            if release is not None:
                release()
        for widget in reversed(self._widgets):
            if widget._bounds.left <= x <= widget._bounds.right and widget._bounds.top <= y <= widget._bounds.bottom:
                click = getattr(widget, "_click_at", None)
                if click is not None:
                    click(x, y)
                else:
                    widget._click()
                break

    def _press(self, x: int, y: int) -> None:
        for widget in self._widgets:
            press = getattr(widget, "_press_at", None)
            if press is not None:
                press(x, y)
                continue
            press = getattr(widget, "_press", None)
            if press is not None:
                press(widget._bounds.left <= x <= widget._bounds.right and widget._bounds.top <= y <= widget._bounds.bottom)

    def _move(self, x: int, y: int) -> None:
        for widget in self._widgets:
            move = getattr(widget, "_move_at", None)
            if move is not None:
                move(x, y)
                continue
            move = getattr(widget, "_move", None)
            if move is not None:
                move(widget._bounds.left <= x <= widget._bounds.right and widget._bounds.top <= y <= widget._bounds.bottom)

    def _timer(self, timer_id: int) -> None:
        callback = self._timers.get(timer_id)
        if callback is not None:
            callback()