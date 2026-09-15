from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..core import (
    COLOR_BACKGROUND,
    COLOR_BORDER,
    RECT,
    _color,
    ctypes,
    gdi32,
    user32,
    wintypes,
)
from .controls import CheckBox, ProgressBar, Separator
from .label import Button, Label

if TYPE_CHECKING:
    from .window import Window


Widget = Label | Button | CheckBox | ProgressBar | Separator


class Row:
    """A styled horizontal container for multiple widgets."""

    height = 64

    def __init__(
        self,
        window: Window,
        *,
        gap: int = 12,
        padding: int = 12,
        background: int = COLOR_BACKGROUND,
        border: int = COLOR_BORDER,
    ) -> None:
        self._window = window
        self.gap = gap
        self.padding = padding
        self.background = background
        self.border = border
        self._children: list[tuple[Widget, int | None]] = []
        self._bounds = RECT()

    def _add(self, widget: Widget, width: int | None = None) -> Widget:
        self._children.append((widget, width))
        self._layout_children()
        self._window._layout()
        return widget

    def label(self, text: str, width: int | None = None) -> Label:
        return self._add(Label(self._window, text), width)  # type: ignore[return-value]

    def button(self, text: str, command: Callable[[], None], width: int | None = None, **style: int) -> Button:
        return self._add(Button(self._window, text, command, **style), width)  # type: ignore[return-value]

    def checkbox(self, text: str, command: Callable[[bool], None] | None = None, width: int | None = None) -> CheckBox:
        return self._add(CheckBox(self._window, text, command), width)  # type: ignore[return-value]

    def progress(self, value: int = 0, on_change: Callable[[int], None] | None = None, width: int | None = None) -> ProgressBar:
        return self._add(ProgressBar(self._window, value, on_change), width)  # type: ignore[return-value]

    def _layout_children(self) -> None:
        if not self._children:
            return
        available = max(0, self._bounds.right - self._bounds.left - self.padding * 2)
        gaps = self.gap * (len(self._children) - 1)
        fixed = sum(width for _, width in self._children if width is not None)
        flexible = sum(width is None for _, width in self._children)
        flexible_width = max(0, (available - gaps - fixed) // flexible) if flexible else 0
        x = self._bounds.left + self.padding
        center = (self._bounds.top + self._bounds.bottom) // 2
        for child, width in self._children:
            child_width = width if width is not None else flexible_width
            child_height = min(child.height, self._bounds.bottom - self._bounds.top - self.padding * 2)
            child_top = center - child_height // 2
            child._bounds = RECT(x, child_top, x + child_width, child_top + child_height)
            x += child_width + self.gap

    def _draw(self, hdc: wintypes.HDC) -> None:
        background = _color(self.background)
        user32.FillRect(hdc, ctypes.byref(self._bounds), background)
        gdi32.DeleteObject(background)
        border = _color(self.border)
        user32.FrameRect(hdc, ctypes.byref(self._bounds), border)
        gdi32.DeleteObject(border)
        self._layout_children()
        for child, _ in self._children:
            child._draw(hdc)

    def _click(self, x: int, y: int) -> None:
        self._click_at(x, y)

    def _click_at(self, x: int, y: int) -> None:
        for child, _ in reversed(self._children):
            if child._bounds.left <= x <= child._bounds.right and child._bounds.top <= y <= child._bounds.bottom:
                child._click()
                break

    def _press(self, pressed: bool) -> None:
        for child, _ in self._children:
            press = getattr(child, "_press", None)
            if press is not None:
                press(pressed)

    def _press_at(self, x: int, y: int) -> None:
        for child, _ in self._children:
            press = getattr(child, "_press", None)
            if press is not None:
                press(child._bounds.left <= x <= child._bounds.right and child._bounds.top <= y <= child._bounds.bottom)

    def _move(self, hovered: bool) -> None:
        for child, _ in self._children:
            move = getattr(child, "_move", None)
            if move is not None:
                move(hovered)

    def _move_at(self, x: int, y: int) -> None:
        for child, _ in self._children:
            move = getattr(child, "_move", None)
            if move is not None:
                move(child._bounds.left <= x <= child._bounds.right and child._bounds.top <= y <= child._bounds.bottom)

    def _release(self) -> None:
        for child, _ in self._children:
            release = getattr(child, "_release", None)
            if release is not None:
                release()
