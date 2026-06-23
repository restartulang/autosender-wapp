import sys
import os

def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # We are running in normal python environment
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
    return os.path.join(base_path, relative_path)

def set_window_icon(window):
    """Sets the logo icon for the given window."""
    try:
        icon_path = get_resource_path("assets/logo_final.ico")
        window.iconbitmap(icon_path)
        # CustomTkinter overwrites Toplevel icons after 200ms, so we overwrite it again after 250ms
        window.after(250, lambda: window.iconbitmap(icon_path))
    except Exception as e:
        pass
