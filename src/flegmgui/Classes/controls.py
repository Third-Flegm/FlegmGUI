from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..core import (
    DT_LEFT,
    DT_SINGLELINE,
    DT_VCENTER,
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_SURFACE,
    COLOR_TEXT,
    COLOR_TRACK,
    RECT,
    _color,
    ctypes,
    gdi32,
    user32,
    wintypes,
)

if TYPE_CHECKING:
    from .window import Window


class CheckBox:
    """A custom-painted toggle with an optional change callback."""

    height = 32

    def __init__(self, window: Window, text: str, command: Callable[[bool], None] | None = None) -> None:
        self._window = window
        self.text = text
        self.command = command
        self.checked = False
        self._bounds = RECT()

    def set(self, checked: bool) -> None:
        self.checked = checked
        self._window._refresh()

    def _draw(self, hdc: wintypes.HDC) -> None:
        box = RECT(self._bounds.left, self._bounds.top + 4, self._bounds.left + 22, self._bounds.top + 26)
        text_bounds = RECT(self._bounds.left + 34, self._bounds.top, self._bounds.right, self._bounds.bottom)
        brush = _color(COLOR_SURFACE)
        user32.FillRect(hdc, ctypes.byref(box), brush)
        gdi32.DeleteObject(brush)
        border = _color(COLOR_BORDER)
        user32.FrameRect(hdc, ctypes.byref(box), border)
        gdi32.DeleteObject(border)
        if self.checked:
            brush = _color(COLOR_ACCENT)
            user32.FillRect(hdc, ctypes.byref(box), brush)
            gdi32.DeleteObject(brush)
        gdi32.SetTextColor(hdc, COLOR_TEXT)
        user32.DrawTextW(hdc, self.text, -1, ctypes.byref(text_bounds), DT_LEFT | DT_VCENTER | DT_SINGLELINE)

    def _click(self) -> None:
        self.checked = not self.checked
        if self.command is not None:
            self.command(self.checked)
        self._window._refresh()


class ProgressBar:
    """A horizontal progress indicator with a value from 0 to 100."""

    height = 24

    def __init__(self, window: Window, value: int = 0, on_change: Callable[[int], None] | None = None) -> None:
        self._window = window
        self._on_change = on_change
        self.value = 0
        self._bounds = RECT()
        self._animation_timer: int | None = None
        self.set(value)

    def set(self, value: int) -> None:
        new_value = max(0, min(100, value))
        changed = new_value != self.value
        self.value = new_value
        self._window._refresh()
        if changed and self._on_change is not None:
            self._on_change(self.value)

    def increment(self, amount: int = 1) -> None:
        """Move the progress value by amount percentage points."""
        self.set(self.value + amount)

    def set_on_change(self, callback: Callable[[int], None] | None) -> None:
        """Replace the callback invoked after the value changes."""
        self._on_change = callback

    def animate_to(self, value: int, speed: int = 4) -> None:
        """Animate toward value using the window's message-loop timer."""
        target = max(0, min(100, value))
        step = max(1, abs(speed))

        def tick() -> None:
            if self.value == target:
                if self._animation_timer is not None:
                    self._window._stop_timer(self._animation_timer)
                    self._animation_timer = None
                return
            direction = 1 if target > self.value else -1
            self.set(self.value + direction * min(step, abs(target - self.value)))

        if self._animation_timer is not None:
            self._window._stop_timer(self._animation_timer)
        self._animation_timer = self._window._start_timer(tick)

    def _draw(self, hdc: wintypes.HDC) -> None:
        background = _color(COLOR_TRACK)
        user32.FillRect(hdc, ctypes.byref(self._bounds), background)
        gdi32.DeleteObject(background)
        filled = RECT(
            self._bounds.left,
            self._bounds.top,
            self._bounds.left + (self._bounds.right - self._bounds.left) * self.value // 100,
            self._bounds.bottom,
        )
        foreground = _color(COLOR_ACCENT)
        user32.FillRect(hdc, ctypes.byref(filled), foreground)
        gdi32.DeleteObject(foreground)
        border = _color(COLOR_BORDER)
        user32.FrameRect(hdc, ctypes.byref(self._bounds), border)
        gdi32.DeleteObject(border)

    def _click(self) -> None:
        pass


class Separator:
    """A non-interactive horizontal divider."""

    height = 12

    def __init__(self, window: Window) -> None:
        self._window = window
        self._bounds = RECT()

    def _draw(self, hdc: wintypes.HDC) -> None:
        line = RECT(self._bounds.left, self._bounds.top + 5, self._bounds.right, self._bounds.top + 6)
        brush = _color(COLOR_BORDER)
        user32.FillRect(hdc, ctypes.byref(line), brush)
        gdi32.DeleteObject(brush)

    def _click(self) -> None:
        pass