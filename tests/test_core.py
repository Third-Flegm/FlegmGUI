import platform

import pytest

from flegmgui import Button, Label, ProgressBar, Row, Window


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
    assert hasattr(Window, "row")


def test_public_package_exports_current_version_and_layout_api():
    import flegmgui

    assert flegmgui.__version__ == "0.1.1"
    assert Row.__module__ == "flegmgui.Classes.layout"
    assert ProgressBar.__module__ == "flegmgui.Classes.controls"
