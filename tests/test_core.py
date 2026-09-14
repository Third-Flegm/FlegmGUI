import platform

import pytest

from flegmgui import Button, Label, Window


@pytest.mark.skipif(platform.system() != "Windows", reason="flegmgui uses the Win32 API")
def test_public_widgets_are_custom_objects():
    assert Window.__module__ == "flegmgui.core"
    assert Label.__module__ == "flegmgui.core"
    assert Button.__module__ == "flegmgui.core"
