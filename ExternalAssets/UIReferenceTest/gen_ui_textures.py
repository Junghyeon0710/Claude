"""Procedurally generate the UI textures for /Game/UIReferenceTest.

Nothing here is traced from the reference screenshot: the background is a
stylised silhouette painting built from noise + polygons, and every icon is
drawn with primitives so it can be regenerated / tweaked.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(OUT, exist_ok=True)

rng = np.random.default_rng(20260814)


# ----------------------------------------------------------------------------
# noise helpers
# ----------------------------------------------------------------------------
def value_noise(w, h, res, seed):
    """Bilinearly interpolated value noise at `res` cells across the width."""
    r = np.random.default_rng(seed)
    ch = max(2, int(res * h / w) + 1)
    grid = r.random((ch + 1, res + 1))
    ys = np.linspace(0, ch, h, endpoint=False)
    xs = np.linspace(0, res, w, endpoint=False)
    y0 = ys.astype(int)
    x0 = xs.astype(int)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    # smoothstep
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    g00 = grid[np.ix_(y0, x0)]
    g01 = grid[np.ix_(y0, x0 + 1)]
    g10 = grid[np.ix_(y0 + 1, x0)]
    g11 = grid[np.ix_(y0 + 1, x0 + 1)]
    top = g00 * (1 - fx) + g01 * fx
    bot = g10 * (1 - fx) + g11 * fx
    return top * (1 - fy) + bot * fy


def fbm(w, h, res, octaves, seed, gain=0.5, lac=2.0):
    total = np.zeros((h, w))
    amp = 1.0
    norm = 0.0
    r = res
    for o in range(octaves):
        total += amp * value_noise(w, h, int(r), seed + o * 977)
        norm += amp
        amp *= gain
        r *= lac
    return total / norm


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ----------------------------------------------------------------------------
# T_UI_Background : stylised dark-fantasy key art
# ----------------------------------------------------------------------------
W, H = 1920, 1080


def build_background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)

    # --- sky gradient: dark slate at the top, pale light band near the horizon
    t = yy / H
    top = np.array([26, 28, 33], float)
    mid = np.array([70, 74, 80], float)
    low = np.array([138, 140, 136], float)
    a = np.clip(t / 0.40, 0, 1)[..., None]
    b = np.clip((t - 0.40) / 0.22, 0, 1)[..., None]
    sky = top * (1 - a) + mid * a
    sky = sky * (1 - b) + low * b

    # --- god-light: a broad glow breaking through the clouds behind the castle
    for (cx, cy, rad, power, col) in [
        (1120, 430, 760, 1.0, np.array([222, 221, 212], float)),
        (860, 500, 500, 0.60, np.array([200, 201, 193], float)),
        (1460, 360, 420, 0.34, np.array([178, 184, 188], float)),
    ]:
        dd = np.sqrt(((xx - cx) / rad) ** 2 + ((yy - cy) / (rad * 0.60)) ** 2)
        g = np.clip(1.0 - dd, 0, 1) ** 2.0 * power
        sky = sky * (1 - g[..., None]) + col * g[..., None]

    # --- clouds: layered fbm, lit from the glow centre. Two passes so the
    #     upper sky gets heavy dark banks and the middle gets bright billows.
    dl = np.sqrt(((xx - 1120) / 950.0) ** 2 + ((yy - 400) / 540.0) ** 2)
    lit = np.clip(1.30 - dl, 0, 1)

    def cloud_layer(seed, res, thresh, contrast, ymask, bright, dark, warp=0.0):
        n = fbm(W, H, res, 6, seed)
        if warp:
            n2 = fbm(W, H, res * 2, 4, seed + 313)
            n = np.clip(n * (1 - warp) + n2 * warp, 0, 1)
            # squash vertically so banks stretch horizontally like real cloud
        m = np.clip((n - thresh) * contrast, 0, 1) * ymask
        col = (dark * (1 - lit[..., None]) + bright * lit[..., None])
        return m, col

    # high dark bank across the top
    m1, c1 = cloud_layer(
        11, 4, 0.40, 3.0,
        np.clip((0.52 - t) / 0.52, 0, 1) ** 0.7,
        np.array([120, 122, 126], float), np.array([20, 21, 26], float), warp=0.35)
    sky = sky * (1 - m1[..., None]) + c1 * m1[..., None]
    # bright billowing mid layer
    m2, c2 = cloud_layer(
        733, 8, 0.46, 3.4,
        np.clip(1.15 - np.abs(t - 0.33) / 0.34, 0, 1),
        np.array([216, 216, 210], float), np.array([56, 58, 64], float), warp=0.45)
    sky = sky * (1 - m2[..., None]) + c2 * m2[..., None]
    # wispy streaks near the horizon
    m3, c3 = cloud_layer(
        4457, 16, 0.52, 2.6,
        np.clip(1.1 - np.abs(t - 0.50) / 0.16, 0, 1) * 0.55,
        np.array([206, 206, 200], float), np.array([96, 98, 102], float))
    sky = sky * (1 - m3[..., None]) + c3 * m3[..., None]

    img = to_img(sky).convert("RGBA")

    # ------------------------------------------------------------------
    # far mountains (right side), hazy blue-grey - noisy ridgelines
    # ------------------------------------------------------------------
    def ridge(points, col, blur=0):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).polygon(points, fill=col)
        if blur:
            layer = layer.filter(ImageFilter.GaussianBlur(blur))
        img.alpha_composite(layer)

    def noisy_ridge(x0, x1, peaks, base_y, col, seed, blur=2.0, jag=0.30):
        """Ridge line built from peak anchors plus per-sample jitter."""
        r = random.Random(seed)
        px = [p[0] for p in peaks]
        py = [p[1] for p in peaks]
        pts = []
        n = 150
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = np.interp(x, px, py)
            # jagged detail: sum of a couple of sines plus noise
            y += (math.sin(x * 0.031 + seed) * 9 + math.sin(x * 0.077 + seed * 2) * 5
                  + (r.random() - 0.5) * 10) * jag
            pts.append((x, float(y)))
        ridge(pts + [(x1, base_y), (x0, base_y)], col, blur=blur)

    noisy_ridge(1130, 1920,
                [(1130, 585), (1250, 470), (1330, 505), (1440, 352),
                 (1520, 440), (1610, 392), (1700, 470), (1810, 400),
                 (1920, 462)], 660, (92, 100, 110, 195), 3, blur=3.5)
    noisy_ridge(1240, 1920,
                [(1240, 630), (1400, 470), (1490, 520), (1600, 452),
                 (1730, 522), (1840, 472), (1920, 515)], 690,
                (64, 71, 80, 220), 17, blur=2.5)
    # left-hand hill mass
    noisy_ridge(-20, 760,
                [(-20, 706), (120, 630), (300, 656), (430, 606), (560, 664),
                 (660, 634), (760, 672)], 1090, (36, 37, 36, 238), 29, blur=2.0)

    # ------------------------------------------------------------------
    # castle silhouette (centre-left) : towers + spires
    # ------------------------------------------------------------------
    castle = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(castle, "RGBA")
    CC = (31, 33, 38, 255)
    base_y = 620

    def tower(cx, top_y, half_w, spire_ratio=4.2, col=CC, ring=True):
        """Slender gothic tower: tapering shaft, needle spire, crenellation."""
        cd.polygon([(cx - half_w, base_y), (cx - half_w * 0.80, top_y),
                    (cx + half_w * 0.80, top_y), (cx + half_w, base_y)], fill=col)
        cd.polygon([(cx - half_w * 0.86, top_y),
                    (cx, top_y - half_w * spire_ratio),
                    (cx + half_w * 0.86, top_y)], fill=col)
        if ring:
            cd.rectangle([cx - half_w * 1.25, top_y - 4,
                          cx + half_w * 1.25, top_y + 7], fill=col)

    # rock outcrop the castle stands on
    cd.polygon([(636, 1080), (658, 712), (694, 650), (748, 618),
                (866, 616), (934, 652), (962, 726), (984, 1080)],
               fill=(23, 24, 28, 255))
    # curtain wall + keep body
    cd.polygon([(676, 486), (700, 452), (886, 452), (908, 486),
                (912, 644), (672, 644)], fill=CC)
    # battlements along the keep roof
    for i in range(11):
        bx = 686 + i * 20
        cd.rectangle([bx, 440, bx + 11, 458], fill=CC)
    # towers, tallest near the middle - deliberately uneven
    tower(700, 424, 15, 4.6)
    tower(742, 356, 19, 4.4)
    tower(786, 286, 15, 5.2)
    tower(806, 214, 11, 5.8)          # the tall central needle
    tower(836, 330, 17, 4.8)
    tower(874, 400, 14, 4.6)
    tower(662, 500, 12, 4.0)
    tower(918, 512, 12, 4.0)
    tower(946, 556, 10, 3.6)
    # low outbuildings further down the ridge
    for (ox, oy, ow) in [(950, 596, 34), (642, 588, 30), (612, 618, 22)]:
        cd.rectangle([ox, oy, ox + ow, oy + 58], fill=CC)
        cd.polygon([(ox - 5, oy), (ox + ow / 2, oy - 26), (ox + ow + 5, oy)], fill=CC)
    castle = castle.filter(ImageFilter.GaussianBlur(0.7))
    img.alpha_composite(castle)

    # atmospheric haze over the castle so it reads as distant
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze, "RGBA")
    for i in range(26):
        yv = 470 + i * 7
        hd.rectangle([560, yv, 1060, yv + 8], fill=(178, 180, 176, int(4 + i * 2.1)))
    img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(22)))

    # ------------------------------------------------------------------
    # mid-ground terrain: valley floor with a pale river
    # ------------------------------------------------------------------
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground, "RGBA")
    gpts = []
    rg = random.Random(77)
    for i in range(80):
        x = i / 79.0 * W
        y = (668 + math.sin(x * 0.0042) * 16 + math.sin(x * 0.011) * 7
             + (rg.random() - 0.5) * 5)
        gpts.append((x, y))
    gd.polygon(gpts + [(W, 1090), (0, 1090)], fill=(50, 47, 36, 255))
    img.alpha_composite(ground.filter(ImageFilter.GaussianBlur(1.6)))

    # river: a pale winding ribbon catching the sky, widening downstream
    river = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(river, "RGBA")
    pts_l, pts_r = [], []
    for i in range(70):
        s = i / 69.0
        y = 664 + s * 420
        cx = 852 - s * 120 + math.sin(s * 5.0) * 66 + math.sin(s * 12.0) * 12
        wdt = 5 + s ** 1.7 * 86
        pts_l.append((cx - wdt, y))
        pts_r.append((cx + wdt * 0.9, y))
    rd.polygon(pts_l + pts_r[::-1], fill=(126, 130, 124, 205))
    img.alpha_composite(river.filter(ImageFilter.GaussianBlur(6)))

    # terrain texture: fbm shading, plus aerial perspective that lifts the
    # far side of the valley towards the sky colour
    terr = fbm(W, H, 14, 6, 4241)
    terr2 = fbm(W, H, 40, 4, 8123)
    tmask = np.clip((yy - 668) / 60.0, 0, 1)
    depth = np.clip((yy - 668) / 380.0, 0, 1)
    base = np.asarray(img.convert("RGB"), float)
    shade = ((terr - 0.5) * 46 + (terr2 - 0.5) * 24)[..., None] * tmask[..., None]
    base = np.clip(base + shade, 0, 255)
    # haze near the horizon line
    hazy = np.clip(1.0 - depth / 0.22, 0, 1)[..., None] * tmask[..., None] * 0.45
    base = base * (1 - hazy) + np.array([120, 122, 116], float) * hazy
    # darken towards the camera
    base *= (1.0 - depth[..., None] * 0.42)
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

    # conifers on the right ridge
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fg, "RGBA")
    for (x, y, hgt) in [(1362, 706, 92), (1398, 722, 70), (1436, 698, 104),
                        (1470, 726, 62), (1330, 730, 58), (1500, 706, 78),
                        (1246, 718, 66), (1560, 732, 54), (1604, 716, 68),
                        (1298, 700, 48), (1686, 726, 58)]:
        wdt = hgt * 0.30
        fd.polygon([(x, y - hgt), (x - wdt, y), (x + wdt, y)], fill=(27, 29, 27, 235))
        fd.polygon([(x, y - hgt * 0.6), (x - wdt * 1.25, y), (x + wdt * 1.25, y)],
                   fill=(27, 29, 27, 235))
    img.alpha_composite(fg.filter(ImageFilter.GaussianBlur(1.3)))

    # foreground boulders: irregular blobs, only a few, very dark
    rocks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kd = ImageDraw.Draw(rocks, "RGBA")
    r = random.Random(9)
    for i in range(120):
        s = r.random() ** 0.6
        y = 780 + s * 320
        x = r.random() * W
        rad = 10 + s * 52
        dark = int(14 + (1 - s) * 12)
        n = 9
        poly = []
        for k in range(n):
            a = k * math.pi * 2 / n
            rr = rad * (0.55 + r.random() * 0.55)
            poly.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.40))
        kd.polygon(poly, fill=(dark, dark, dark - 3, 205))
    # grass tufts catching the last light
    for i in range(400):
        s = r.random()
        y = 700 + s * 300
        x = r.random() * W
        h2 = 3 + s * 12
        v = int(52 + (1 - s) * 34)
        kd.line([(x, y), (x + (r.random() - 0.5) * 6, y - h2)],
                fill=(v, v - 2, v - 12, 120), width=1)
    img.alpha_composite(rocks.filter(ImageFilter.GaussianBlur(1.9)))

    # ------------------------------------------------------------------
    # hero silhouette: cloaked figure seen from behind, centre-right
    # ------------------------------------------------------------------
    hero = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hero, "RGBA")
    HC = (21, 22, 26, 255)
    cx, head_y, feet_y = 1148, 138, 1004

    # legs and boots first, so the coat overlaps them
    hd.polygon([(cx - 44, 820), (cx - 8, 820), (cx - 4, 986), (cx - 52, 986)], fill=HC)
    hd.polygon([(cx + 10, 820), (cx + 46, 820), (cx + 56, 986), (cx + 8, 986)], fill=HC)
    hd.polygon([(cx - 60, 962), (cx - 2, 962), (cx + 2, 1004), (cx - 66, 1004)], fill=HC)
    hd.polygon([(cx + 6, 962), (cx + 58, 962), (cx + 68, 1004), (cx + 2, 1004)], fill=HC)

    # body + cloak as one continuous silhouette driven by a width profile:
    # collar -> shoulders -> waist -> flared hem
    prof_s = [0.00, 0.04, 0.09, 0.17, 0.30, 0.40, 0.52, 0.66, 0.80, 0.92, 1.00]
    prof_w = [46.0, 82.0, 104.0, 98.0, 80.0, 82.0, 96.0, 116.0, 134.0, 148.0, 154.0]
    shoulder_y = 236.0
    left, right = [], []
    n = 90
    for i in range(n):
        s = i / (n - 1.0)
        y = shoulder_y + s * (feet_y - shoulder_y)
        wdt = float(np.interp(s, prof_s, prof_w))
        # cloth wobble grows towards the loose hem
        wob = (math.sin(s * 6.4) * 5.0 + math.sin(s * 15.0) * 2.0) * s
        lean = s * s * 7.0          # slight lean with the wind
        left.append((cx - wdt * 1.05 - wob * 0.7 - lean, y))
        right.append((cx + wdt * 0.93 + wob - lean * 0.4, y))
    # ragged, wind-torn hem
    hem = []
    rh = random.Random(4)
    for i in range(21):
        s = i / 20.0
        hx = left[-1][0] + s * (right[-1][0] - left[-1][0])
        hy = feet_y - 44 + (i % 2) * 44 + math.sin(s * 6.0) * 20 + rh.random() * 16
        hem.append((hx, hy))
    hd.polygon(left + hem + right[::-1], fill=HC)
    # rounded pauldrons softening the shoulder line
    hd.ellipse([cx - 106, 244, cx - 38, 300], fill=HC)
    hd.ellipse([cx + 38, 244, cx + 104, 300], fill=HC)
    # a torn flap of cloak lifting away from the left hip
    hd.polygon([(cx - 92, 560), (cx - 132, 640), (cx - 138, 730),
                (cx - 112, 742), (cx - 96, 660)], fill=HC)

    # neck + head
    hd.polygon([(cx - 19, 196), (cx + 19, 196), (cx + 23, 248), (cx - 23, 248)], fill=HC)
    hd.ellipse([cx - 31, head_y, cx + 31, head_y + 72], fill=HC)
    # windswept hair: a few overlapping locks rather than one solid cap
    for lock in [
        [(cx - 33, head_y + 32), (cx - 31, head_y + 8), (cx - 14, head_y - 4),
         (cx + 10, head_y - 6), (cx + 29, head_y + 4), (cx + 34, head_y + 24),
         (cx + 26, head_y + 42), (cx - 20, head_y + 44)],
        [(cx - 37, head_y + 22), (cx - 27, head_y + 2), (cx - 8, head_y + 10),
         (cx - 23, head_y + 44)],
        [(cx + 22, head_y + 8), (cx + 39, head_y + 14), (cx + 40, head_y + 36),
         (cx + 24, head_y + 34)],
    ]:
        hd.polygon(lock, fill=HC)
    hero = hero.filter(ImageFilter.GaussianBlur(1.6))
    img.alpha_composite(hero)

    # rim light along the figure's right edge (sun is to the right)
    rim = hero.filter(ImageFilter.GaussianBlur(3))
    ra = np.asarray(rim)[..., 3].astype(float) / 255.0
    edge = np.zeros_like(ra)
    for shift, weight in ((4, 1.0), (8, 0.5)):
        sh = np.zeros_like(ra)
        sh[:, :-shift] = ra[:, shift:]
        edge = np.maximum(edge, np.clip(ra - sh, 0, 1) * weight)
    # only the upper body catches the rim, and gently
    edge *= 0.34 * np.clip(1.25 - (yy - 200) / 700.0, 0, 1)
    base = np.asarray(img.convert("RGB"), float)
    base = np.clip(base + edge[..., None] * np.array([188, 190, 182], float), 0, 255)
    img = Image.fromarray(base.astype(np.uint8)).convert("RGBA")

    # ------------------------------------------------------------------
    # grading: vignette + a heavy left-side falloff so the menu stays legible
    # ------------------------------------------------------------------
    base = np.asarray(img.convert("RGB"), float)
    nx = (xx / W - 0.5) * 2.0
    ny = (yy / H - 0.5) * 2.0
    vign = np.clip(1.0 - 0.52 * (nx * nx * 0.85 + ny * ny), 0.30, 1.0)
    base *= vign[..., None]
    leftfade = np.clip(1.0 - (xx / 760.0), 0, 1) ** 1.5 * 0.62
    base *= (1.0 - leftfade)[..., None]
    bottom = np.clip((yy - 830) / 250.0, 0, 1) ** 1.4 * 0.45
    base *= (1.0 - bottom)[..., None]
    # slight cool shadow / warm light split-tone
    lum = base.mean(axis=2, keepdims=True) / 255.0
    base = base + (1 - lum) * np.array([-6, -2, 10], float) + lum * np.array([10, 6, -8], float)
    # film grain
    base += (rng.random((H, W, 1)) - 0.5) * 7.0
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")

    img.save(os.path.join(OUT, "T_UI_Background.png"))
    return img


# ----------------------------------------------------------------------------
# icons - drawn 4x then downsampled for clean antialiasing
# ----------------------------------------------------------------------------
SS = 4


def new_icon(size):
    im = Image.new("RGBA", (size * SS, size * SS), (255, 255, 255, 0))
    return im, ImageDraw.Draw(im, "RGBA")


def save_icon(im, size, name):
    im = im.resize((size, size), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))


def chevron(name, size=64, flip=False, thickness=0.09, span=0.30):
    """A stroked '>' (or '<'), drawn as a rounded polyline."""
    im, d = new_icon(size)
    s = size * SS
    th = s * thickness
    cx, cy = s * 0.5, s * 0.5
    dx = s * span * 0.62
    dy = s * span
    if flip:
        pts = [(cx + dx * 0.5, cy - dy), (cx - dx * 0.5, cy), (cx + dx * 0.5, cy + dy)]
    else:
        pts = [(cx - dx * 0.5, cy - dy), (cx + dx * 0.5, cy), (cx - dx * 0.5, cy + dy)]
    d.line(pts, fill=(255, 255, 255, 255), width=int(th), joint="curve")
    for p in pts:
        d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2],
                  fill=(255, 255, 255, 255))
    save_icon(im, size, name)


def close_icon(name="T_UI_Close", size=64):
    im, d = new_icon(size)
    s = size * SS
    th = int(s * 0.075)
    m = s * 0.27
    for pts in ([(m, m), (s - m, s - m)], [(s - m, m), (m, s - m)]):
        d.line(pts, fill=(255, 255, 255, 255), width=th)
        for p in pts:
            d.ellipse([p[0] - th / 2, p[1] - th / 2, p[0] + th / 2, p[1] + th / 2],
                      fill=(255, 255, 255, 255))
    save_icon(im, size, name)


def gear_icon(name="T_UI_Settings", size=64):
    im, d = new_icon(size)
    s = size * SS
    cx = cy = s / 2
    teeth, r_out, r_in = 8, s * 0.42, s * 0.30
    pts = []
    for i in range(teeth * 4):
        a = i * math.pi * 2 / (teeth * 4)
        r = r_out if (i % 4) in (0, 1) else r_in
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=(255, 255, 255, 255))
    hole = s * 0.15
    d.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=(255, 255, 255, 0))
    save_icon(im, size, name)


def play_icon(name="T_UI_Play", size=64):
    im, d = new_icon(size)
    s = size * SS
    d.polygon([(s * 0.32, s * 0.22), (s * 0.78, s * 0.5), (s * 0.32, s * 0.78)],
              fill=(255, 255, 255, 255))
    save_icon(im, size, name)


def exit_icon(name="T_UI_Exit", size=64):
    """Door + outgoing arrow."""
    im, d = new_icon(size)
    s = size * SS
    th = int(s * 0.07)
    d.rectangle([s * 0.20, s * 0.16, s * 0.56, s * 0.84], outline=(255, 255, 255, 255),
                width=th)
    d.rectangle([s * 0.40, s * 0.16, s * 0.60, s * 0.42], fill=(255, 255, 255, 0))
    d.line([(s * 0.50, s * 0.50), (s * 0.86, s * 0.50)], fill=(255, 255, 255, 255),
           width=th)
    d.polygon([(s * 0.74, s * 0.36), (s * 0.92, s * 0.50), (s * 0.74, s * 0.64)],
              fill=(255, 255, 255, 255))
    save_icon(im, size, name)


def slider_handle(name="T_UI_SliderHandle", size=64):
    im, d = new_icon(size)
    s = size * SS
    r = s * 0.34
    c = s / 2
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 255, 255, 255))
    # a faint outer halo so the handle reads against a light track
    halo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([c - r * 1.34, c - r * 1.34, c + r * 1.34, c + r * 1.34],
                                 fill=(255, 255, 255, 46))
    halo = halo.filter(ImageFilter.GaussianBlur(s * 0.03))
    halo.alpha_composite(im)
    save_icon(halo, size, name)


def border_9slice(name="T_UI_Border", size=48, inset=0, thickness=2):
    """1px-ish white outline, transparent centre. Use Draw As Box, margin=t/size."""
    im = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([inset, inset, size - 1 - inset, size - 1 - inset],
                outline=(255, 255, 255, 255), width=thickness)
    im.save(os.path.join(OUT, name + ".png"))


def rounded_border(name="T_UI_KeyBadge", size=48, radius=8, thickness=2):
    im = Image.new("RGBA", (size * SS, size * SS), (255, 255, 255, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([thickness * SS // 2, thickness * SS // 2,
                         size * SS - 1 - thickness * SS // 2,
                         size * SS - 1 - thickness * SS // 2],
                        radius=radius * SS, outline=(255, 255, 255, 255),
                        width=thickness * SS)
    im.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name + ".png"))


def grad_h(name, w, h, stops, fade_edges=False):
    """Horizontal white gradient described by (position, alpha) stops."""
    arr = np.zeros((h, w, 4), float)
    arr[..., :3] = 255
    xs = np.linspace(0, 1, w)
    pos = np.array([s[0] for s in stops])
    val = np.array([s[1] for s in stops])
    alpha = np.interp(xs, pos, val)
    arr[..., 3] = alpha[None, :] * 255
    to_img(arr).convert("RGBA").save(os.path.join(OUT, name + ".png"))


def grad_v(name, w, h, stops):
    arr = np.zeros((h, w, 4), float)
    arr[..., :3] = 255
    ys = np.linspace(0, 1, h)
    alpha = np.interp(ys, [s[0] for s in stops], [s[1] for s in stops])
    arr[..., 3] = alpha[:, None] * 255
    to_img(arr).convert("RGBA").save(os.path.join(OUT, name + ".png"))


def panel_noise(name="T_UI_PanelNoise", size=256):
    n = fbm(size, size, 24, 4, 55)
    n2 = value_noise(size, size, 128, 991)
    v = np.clip((n * 0.55 + n2 * 0.45 - 0.5) * 2.2, -1, 1)
    arr = np.zeros((size, size, 4), float)
    arr[..., :3] = 255
    arr[..., 3] = np.abs(v) * 90
    to_img(arr).convert("RGBA").save(os.path.join(OUT, name + ".png"))


def scanline(name="T_UI_PanelScan", w=8, h=8):
    arr = np.zeros((h, w, 4), float)
    arr[..., :3] = 255
    for y in range(h):
        arr[y, :, 3] = 34 if y % 4 == 0 else 0
    to_img(arr).convert("RGBA").save(os.path.join(OUT, name + ".png"))


def main():
    build_background()

    chevron("T_UI_ChevronRight", 64, flip=False, thickness=0.085, span=0.26)
    chevron("T_UI_ArrowRight", 64, flip=False, thickness=0.10, span=0.24)
    chevron("T_UI_ArrowLeft", 64, flip=True, thickness=0.10, span=0.24)
    close_icon()
    gear_icon()
    play_icon()
    exit_icon()
    slider_handle()

    border_9slice("T_UI_Border", 48, inset=0, thickness=2)
    rounded_border("T_UI_KeyBadge", 48, radius=10, thickness=3)

    # selection highlight: bright on the left, fading out to the right
    grad_h("T_UI_ButtonHighlight", 256, 8,
           [(0.0, 0.55), (0.18, 0.30), (0.62, 0.10), (1.0, 0.0)])
    # divider: fades in and out at both ends
    grad_h("T_UI_Divider", 256, 4,
           [(0.0, 0.0), (0.06, 0.85), (0.5, 1.0), (0.94, 0.85), (1.0, 0.0)])
    # accent bar on the selected menu entry (soft top/bottom falloff)
    grad_v("T_UI_AccentBar", 8, 128,
           [(0.0, 0.10), (0.14, 1.0), (0.86, 1.0), (1.0, 0.10)])
    # slider track
    grad_h("T_UI_SliderTrack", 128, 4, [(0.0, 1.0), (1.0, 1.0)])
    # left-edge screen scrim behind the menu column
    grad_h("T_UI_LeftScrim", 256, 8,
           [(0.0, 0.86), (0.35, 0.55), (0.72, 0.16), (1.0, 0.0)])

    panel_noise()
    scanline()

    print("\n".join(sorted(os.listdir(OUT))))


main()
