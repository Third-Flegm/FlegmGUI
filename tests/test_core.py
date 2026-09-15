import platform

import pytest

from flegmgui import Button, Label, Window


@pytest.mark.skipif(platform.system() != "Windows", reason="flegmgui uses the Win32 API")
def test_public_widgets_are_custom_objects():
    assert Window.__module__ == "flegmgui.Classes.window"
    assert Label.__module__ == "flegmgui.Classes.label"
    assert Button.__module__ == "flegmgui.Classes.label"


@pytest.mark.skipif(platform.system() != "Windows", reason="flegmgui uses the Win32 API")
def test_window_exposes_extended_widget_factories():
    assert hasattr(Window, "checkbox")
    assert hasattr(Window, "progress")
    assert hasattr(Window, "separator")
