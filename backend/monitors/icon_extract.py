"""
Extract application icon from Windows .exe for process list.
Uses icoextract + Pillow if available; otherwise returns default PNG.
"""
import base64
import io
import os
import urllib.parse
from typing import Optional

# Optional: icoextract (pip install icoextract) and Pillow (pip install Pillow)
_IconExtractor = None
_IconExtractorError = Exception
_PIL_Image = None
try:
    from icoextract import IconExtractor, IconExtractorError
    _IconExtractor = IconExtractor
    _IconExtractorError = IconExtractorError
except ImportError:
    pass
try:
    from PIL import Image
    _PIL_Image = Image
except ImportError:
    pass

# Tiny 16x16 default "application" icon as PNG (grey box)
_DEFAULT_ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAHklEQVQ4T2NkYGD4z0ABYBw1gGE0DBgZ"
    "GRn5Gf4z/McEAcAAA0gLMA0AAAAASUVORK5CYII="
)
_DEFAULT_ICON_BYTES = base64.b64decode(_DEFAULT_ICON_B64)


def exe_icon_to_png_bytes(exe_path: str, size: int = 32) -> Optional[bytes]:
    """
    Extract the first icon from a Windows .exe and return as PNG bytes.
    Returns None if extraction fails or libs missing.
    """
    if not exe_path or not os.path.isfile(exe_path):
        return None
    if not exe_path.lower().endswith((".exe", ".dll")):
        return None
    if _IconExtractor is None or _PIL_Image is None:
        return None
    try:
        extractor = _IconExtractor(exe_path)
        ico_data = extractor.get_icon(num=0)
    except _IconExtractorError:
        return None
    except Exception:
        return None
    if not ico_data:
        return None
    try:
        img = _PIL_Image.open(io.BytesIO(ico_data))
        # ICO can have multiple frames (sizes); use the first
        if getattr(img, "n_frames", 1) > 1:
            img.seek(0)
        # Ensure RGBA for consistent PNG (ICO may be P or I mode)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        w, h = img.size
        if w != size or h != size:
            resample = getattr(_PIL_Image, "Resampling", _PIL_Image)
            lanczos = getattr(resample, "LANCZOS", _PIL_Image.LANCZOS)
            img = img.resize((size, size), lanczos)
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        return None


def get_process_icon_png(path_query: str, size: int = 32) -> bytes:
    """
    Decode URL-encoded path, extract icon, return PNG bytes.
    Falls back to default icon on any error.
    """
    try:
        path = urllib.parse.unquote(path_query)
        if not path or ".." in path:
            return _DEFAULT_ICON_BYTES
        path = os.path.normpath(path)
        png = exe_icon_to_png_bytes(path, size=size)
        return png if png else _DEFAULT_ICON_BYTES
    except Exception:
        return _DEFAULT_ICON_BYTES
