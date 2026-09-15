from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..core import (
    DT_LEFT,
    DT_SINGLELINE,
    DT_VCENTER,
    COLOR_ACCENT,
    COLOR_ACCENT_DARK,
    COLOR_BORDER,
    COLOR_SURFACE,
    COLOR_TEXT,
    RECT,
    _color,
    ctypes,
    gdi32,
    user32,
    wintypes,
)

if TYPE_CHECKING:
    from .window import Window


class Label:
    """Text painted directly into the window."""

    height = 32

    def __init__(self, window: Window, text: str) -> None:
        self._window = window
        self.text = text
        self._bounds = RECT()

    def set(self, text: str) -> None:
        self.text = text
        self._window._refresh()

    def _draw(self, hdc: wintypes.HDC) -> None:
        gdi32.SetTextColor(hdc, COLOR_TEXT)
        user32.DrawTextW(hdc, self.text, -1, ctypes.byref(self._bounds), DT_LEFT | DT_VCENTER | DT_SINGLELINE)

    def _click(self) -> None:
        pass


class Button:
    """A custom painted button with library-owned hit testing."""

    height = 44

    def __init__(
        self,
        window: Window,
        text: str,
        command: Callable[[], None],
        *,
        background: int = COLOR_ACCENT,
        hover_background: int = 0x004B70E8,
        pressed_background: int = COLOR_ACCENT_DARK,
        foreground: int = COLOR_SURFACE,
        border: int = COLOR_ACCENT_DARK,
    ) -> None:
        self._window = window
        self.text = text
        self.command = command
        self.background = background
        self.hover_background = hover_background
        self.pressed_background = pressed_background
        self.foreground = foreground
        self.border = border
        self._hovered = False
        self._pressed = False
        self._bounds = RECT()

    def set_style(self, **colors: int) -> None:
        """Update button color properties and repaint it."""
        for name in ("background", "hover_background", "pressed_background", "foreground", "border"):
            if name in colors:
                setattr(self, name, colors[name])
        self._window._refresh()

    def _draw(self, hdc: wintypes.HDC) -> None:
        fill_color = self.pressed_background if self._pressed else self.hover_background if self._hovered else self.background
        brush = _color(fill_color)
        user32.FillRect(hdc, ctypes.byref(self._bounds), brush)
        gdi32.DeleteObject(brush)
        border = _color(self.border)
        user32.FrameRect(hdc, ctypes.byref(self._bounds), border)
        gdi32.DeleteObject(border)
        gdi32.SetTextColor(hdc, self.foreground)
        text_bounds = RECT(self._bounds.left + 12, self._bounds.top, self._bounds.right - 12, self._bounds.bottom)
        user32.DrawTextW(hdc, self.text, -1, ctypes.byref(text_bounds), DT_LEFT | DT_VCENTER | DT_SINGLELINE)

    def _click(self) -> None:
        self.command()

    def _move(self, hovered: bool) -> None:
        if self._hovered != hovered:
            self._hovered = hovered
            self._window._refresh()

    def _press(self, pressed: bool) -> None:
        if self._pressed != pressed:
            self._pressed = pressed
            self._window._refresh()

    def _release(self) -> None:
        self._press(False)