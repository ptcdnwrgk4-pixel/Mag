#!/usr/bin/env python3
"""Erzeugt die App-Icons fuer die Checklisten-PWA (Padella Vino)."""
from PIL import Image, ImageDraw

ACCENT = (138, 128, 96)   # --accent
BG = (247, 244, 239)      # --bg
WHITE = (255, 255, 255)
OUT = "/home/user/Mag/docs"


def rounded(size, radius_ratio=0.22, bg=ACCENT, full_bleed=False):
    """Icon mit optional abgerundeten Ecken + weissem Haken."""
    scale = 4
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if full_bleed:
        d.rectangle([0, 0, S, S], fill=bg)
    else:
        r = int(S * radius_ratio)
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=r, fill=bg)

    # Weisser Haken, zentriert
    w = int(S * 0.11)  # Strichbreite
    pts = [
        (S * 0.30, S * 0.52),
        (S * 0.44, S * 0.66),
        (S * 0.72, S * 0.34),
    ]
    d.line(pts, fill=WHITE, width=w, joint="curve")
    # abgerundete Enden
    for (x, y) in [pts[0], pts[2]]:
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=WHITE)

    return img.resize((size, size), Image.LANCZOS)


# Standard PWA-Icons (transparente Ecken)
rounded(192).save(f"{OUT}/icon-192.png")
rounded(512).save(f"{OUT}/icon-512.png")

# Maskable: voll ausgefuellter Hintergrund, Haken im Safe-Zone-Bereich
mask = Image.new("RGBA", (512, 512), ACCENT + (255,))
d = ImageDraw.Draw(mask)
w = int(512 * 0.10)
pts = [(512 * 0.33, 512 * 0.53), (512 * 0.45, 512 * 0.64), (512 * 0.68, 512 * 0.38)]
d.line(pts, fill=WHITE, width=w, joint="curve")
for (x, y) in [pts[0], pts[2]]:
    d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=WHITE)
mask.save(f"{OUT}/icon-maskable-512.png")

# Apple-Touch: kein Transparenz-/Rundungsbedarf (iOS maskiert selbst)
rounded(180, full_bleed=True).convert("RGB").save(f"{OUT}/apple-touch-icon.png")

# Favicon
rounded(64).save(f"{OUT}/favicon-64.png")
print("Icons erstellt in", OUT)
