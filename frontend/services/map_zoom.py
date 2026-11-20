"""Zoom and pan of the town map (pure functions, no UI).

The view is (zoom, cx, cy): `zoom` goes from MIN_ZOOM (the whole image) to MAX_ZOOM, and (cx, cy) is the point of the
image, as fractions (0-1), shown at the center of the viewport. The image is always kept covering the viewport.
"""

MIN_ZOOM = 1.0
MAX_ZOOM = 3.0
BUTTON_STEP = 1.4    # factor of each "+" / "-" click
WHEEL_STEP = 1.15    # factor of each mouse wheel notch

View = tuple[float, float, float]
DEFAULT_VIEW: View = (MIN_ZOOM, 0.5, 0.5)


def clamp_view(zoom: float, cx: float, cy: float) -> View:
    """Keeps the zoom in range and the viewport inside the image."""
    zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
    half = 0.5 / zoom
    return zoom, max(half, min(1 - half, cx)), max(half, min(1 - half, cy))


def image_rect(view: View, vw: float, vh: float) -> tuple[float, float, float, float]:
    """(left, top, width, height) of the zoomed image inside a viewport of vw x vh."""
    zoom, cx, cy = view
    width, height = vw * zoom, vh * zoom
    return vw / 2 - cx * width, vh / 2 - cy * height, width, height


def to_viewport(view: View, x: float, y: float, vw: float, vh: float) -> tuple[float, float]:
    """Pixel position in the viewport of the image point (x, y), given as fractions of the image."""
    left, top, width, height = image_rect(view, vw, vh)
    return left + x * width, top + y * height


def zoom_at(view: View, factor: float, px: float, py: float, vw: float, vh: float) -> View:
    """Zooms by `factor` keeping the image point under the viewport pixel (px, py) where it is."""
    zoom, _, _ = view
    new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom * factor))
    if new_zoom == zoom:
        return view
    left, top, width, height = image_rect(view, vw, vh)
    u, v = (px - left) / width, (py - top) / height          # the image point under the cursor
    new_width, new_height = vw * new_zoom, vh * new_zoom
    new_left, new_top = px - u * new_width, py - v * new_height
    return clamp_view(new_zoom, (vw / 2 - new_left) / new_width, (vh / 2 - new_top) / new_height)


def pan(view: View, dx: float, dy: float, vw: float, vh: float) -> View:
    """Drags the image by (dx, dy) pixels."""
    zoom, cx, cy = view
    return clamp_view(zoom, cx - dx / (vw * zoom), cy - dy / (vh * zoom))
