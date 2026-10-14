"""Post effects on finished PIL images (screen space) + small motion helpers."""
import functools
import math

import numpy as np
from PIL import Image, ImageEnhance

from .core import H, W, clamp


def desaturate(img, amount=1.0):
    """amount 0 = unchanged, 1 = fully grey (Scene 7 mood)."""
    if amount <= 0:
        return img
    grey = img.convert("L").convert("RGB")
    return Image.blend(img, grey, clamp(amount))


def tint(img, color, amount):
    if amount <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, color), clamp(amount))


def fade(img, amount, color=(0, 0, 0)):
    """Fade to colour: amount 0 = image, 1 = solid colour."""
    return tint(img, color, amount)


def flash(img, amount):
    return tint(img, (255, 255, 255), amount)


def brightness(img, factor):
    return ImageEnhance.Brightness(img).enhance(factor)


@functools.lru_cache(maxsize=4)
def _vignette_mask(w, h, strength):
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    m = np.clip((d - 0.55) / 0.85, 0, 1) ** 1.6 * strength
    return Image.fromarray((m * 255).astype(np.uint8), "L")


def vignette(img, strength=0.6, color=(0, 0, 0)):
    mask = _vignette_mask(img.width, img.height, round(strength, 2))
    return Image.composite(Image.new("RGB", img.size, color), img, mask)


def freeze_frame(img, amount=1.0):
    """OverSimplified-style freeze: slightly desaturated, warm-tinted, high-contrast."""
    if amount <= 0:
        return img
    out = desaturate(img, 0.35 * amount)
    out = tint(out, (255, 230, 180), 0.12 * amount)
    return ImageEnhance.Contrast(out).enhance(1 + 0.15 * amount)


def iris(img, amount, center=(W / 2, H / 2), color=(0, 0, 0)):
    """Iris wipe: amount 0 = fully open, 1 = closed to black around center."""
    if amount <= 0:
        return img
    from PIL import ImageDraw
    mask = Image.new("L", img.size, 255)
    r = (1 - clamp(amount)) * math.hypot(img.width, img.height) * 0.6
    sx, sy = img.width / W, img.height / H
    cx, cy = center[0] * sx, center[1] * sy
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    return Image.composite(Image.new("RGB", img.size, color), img, mask)


def shake(t, amp=8.0, freq=18.0, seed=0):
    """(dx, dy) camera shake offset - use inside cv.camera(...)."""
    return (amp * math.sin(t * freq + seed) * math.cos(t * freq * 0.7 + seed * 2),
            amp * math.sin(t * freq * 1.3 + seed * 3))


def letterbox(img, amount=1.0, bar=60):
    from PIL import ImageDraw
    if amount <= 0:
        return img
    img = img.copy()
    d = ImageDraw.Draw(img)
    b = int(bar * amount * img.height / H)
    d.rectangle([0, 0, img.width, b], fill=(0, 0, 0))
    d.rectangle([0, img.height - b, img.width, img.height], fill=(0, 0, 0))
    return img
