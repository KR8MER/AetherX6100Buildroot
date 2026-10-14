#!/usr/bin/env python3
"""KR8MER Lightning Edition boot logo for the X6100 (Linux kernel logo).

The kernel's boot logo is limited to 224 colours, so the image is rendered in
full colour, then reduced with Floyd-Steinberg dithering to keep the gradients
smooth. Layout lines up with the in-app splash (src/splash.c in x6100_gui).
"""
import random, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, SS = 800, 480, 2          # supersample for clean edges
FONT_DIR = '/usr/share/fonts/opentype/inter/'

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def hexc(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))

NIGHT, STORM, CLOUD = hexc('#060d1f'), hexc('#14224d'), hexc('#1c2e5e')
BOLT, SPARK, AMBER, PALE = hexc('#ffeb3b'), hexc('#40c4ff'), hexc('#fbc02d'), hexc('#fff9c4')

def S(v): return int(v * SS)

def background():
    w, h = S(W), S(H)
    bg = Image.new('RGB', (w, h))
    px = bg.load()
    cx, cy = S(270), S(180)                     # light source behind the bolt
    for y in range(h):
        base = lerp(STORM, NIGHT, y / h)
        for x in range(w):
            d = math.hypot((x - cx) / w, (y - cy) / h * 0.9)
            glow = max(0.0, 1 - d / 0.55) ** 2
            px[x, y] = lerp(base, hexc('#2a4a9a'), glow * 0.75)
    return bg

def clouds(rng):
    w, h = S(W), S(H)
    layer = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(layer)
    for _ in range(140):
        x, y = rng.uniform(-50, W + 50), rng.gauss(40, 55)
        r = rng.uniform(30, 110)
        d.ellipse([S(x - r), S(y - r * 0.55), S(x + r), S(y + r * 0.55)], fill=rng.randint(30, 90))
    return layer.filter(ImageFilter.GaussianBlur(S(28)))

def branch(d, x, y, angle, length, width, rng, depth=0):
    """Faint forked lightning in the sky."""
    while length > 0 and width > 0.4:
        step = rng.uniform(10, 22)
        angle += rng.gauss(0, 0.45)
        nx, ny = x + math.cos(angle) * step, y + math.sin(angle) * step
        d.line([S(x), S(y), S(nx), S(ny)], fill=255, width=max(1, S(width)))
        if depth < 3 and rng.random() < 0.12:
            branch(d, nx, ny, angle + rng.choice([-0.7, 0.7]), length * 0.4, width * 0.6, rng, depth + 1)
        x, y, length, width = nx, ny, length - step, width * 0.985

def bolt_mask(ox, oy):
    # Same outline as splash.c, in a 96x140 box
    upper = [(60, 4), (84, 4), (58, 60), (42, 80), (8, 80)]
    lower = [(58, 60), (90, 60), (24, 138), (42, 80)]
    m = Image.new('L', (S(W), S(H)), 0)
    d = ImageDraw.Draw(m)
    for poly in (upper, lower):
        d.polygon([(S(ox + x), S(oy + y)) for x, y in poly], fill=255)
    return m

def vgrad(size, top, bottom, mid=None):
    w, h = size
    g = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        if mid:
            c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, bottom, (t - 0.5) * 2)
        else:
            c = lerp(top, bottom, t)
        d.line([(0, y), (w, y)], fill=c)
    return g

def hgrad(size, left, right):
    w, h = size
    g = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(g)
    for x in range(w):
        d.line([(x, 0), (x, h)], fill=lerp(left, right, x / max(1, w - 1)))
    return g

def glow(img, mask, color, radius, strength):
    blurred = mask.filter(ImageFilter.GaussianBlur(radius))
    blurred = blurred.point(lambda v: min(255, int(v * strength)))
    return Image.composite(Image.new('RGB', img.size, color), img, blurred)

def text_width(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    return sum(d.textlength(ch, font=font) / SS + spacing for ch in text) - spacing

def text_mask(text, font, xy, spacing=0):
    m = Image.new('L', (S(W), S(H)), 0)
    d = ImageDraw.Draw(m)
    x, y = xy
    for ch in text:
        d.text((S(x), S(y)), ch, font=font, fill=255)
        x += d.textlength(ch, font=font) / SS + spacing
    return m

def build(out):
    rng = random.Random(8)

    # Layout: bolt + wordmark centred as one row, rule and tagline under it
    heavy = ImageFont.truetype(FONT_DIR + 'Inter-Black.otf', S(70))
    semi = ImageFont.truetype(FONT_DIR + 'Inter-Bold.otf', S(24))
    word_w = text_width('KR8MER', heavy, 3)
    row_w = 92 + 26 + word_w
    row_x = (W - row_w) / 2
    bolt_x, bolt_y = row_x, 104
    word_x = row_x + 92 + 26
    tag = 'X6100   LIGHTNING EDITION'
    tag_w = text_width(tag, semi, 4)
    rule_w = max(row_w, tag_w) + 40

    global LAYOUT
    LAYOUT = dict(bolt=(bolt_x, bolt_y))
    img = background()

    # storm clouds along the top
    img = Image.composite(Image.new('RGB', img.size, hexc('#24366b')), img, clouds(rng))

    # distant forked lightning
    sky = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(sky)
    branch(d, 650, -10, math.radians(105), 260, 2.2, rng)
    branch(d, 120, -10, math.radians(80), 180, 1.6, rng)
    img = glow(img, sky, SPARK, S(6), 0.9)
    img = Image.composite(Image.new('RGB', img.size, hexc('#b3e5fc')), img, sky.point(lambda v: v * 0.55))

    # the bolt: wide cyan aura, yellow halo, gradient body
    bm = bolt_mask(bolt_x, bolt_y)
    img = glow(img, bm, SPARK, S(26), 1.1)
    img = glow(img, bm, BOLT, S(9), 1.4)
    body = vgrad(img.size, PALE, AMBER, BOLT)
    img = Image.composite(body, img, bm)

    # wordmark
    tm = text_mask('KR8MER', heavy, (word_x, 134), spacing=3)
    img = glow(img, tm, SPARK, S(10), 0.7)
    img = Image.composite(vgrad(img.size, (255, 255, 255), hexc('#c9d6f0')), img, tm)

    # EAS Station accent rule
    rule = Image.new('L', img.size, 0)
    rx = (W - rule_w) / 2
    ImageDraw.Draw(rule).rounded_rectangle([S(rx), S(268), S(rx + rule_w), S(274)], radius=S(3), fill=255)
    img = glow(img, rule, BOLT, S(6), 0.6)
    img = Image.composite(hgrad(img.size, BOLT, SPARK), img, rule)

    # tagline
    tm2 = text_mask(tag, semi, ((W - tag_w) / 2, 292), spacing=4)
    img = Image.composite(Image.new('RGB', img.size, SPARK), img, tm2)

    img = img.resize((W, H), Image.LANCZOS)

    # Kernel logo: at most 224 colours. Reserve ramps for the accent rule and
    # the bolt so their gradients do not band, quantize the rest, then dither.
    ramp = [lerp(BOLT, SPARK, i / 31) for i in range(32)] + \
           [lerp(PALE, AMBER, i / 15) for i in range(16)]
    rest = img.quantize(colors=224 - len(ramp), method=Image.Quantize.MEDIANCUT)
    pal = ramp + [tuple(rest.getpalette()[i * 3:i * 3 + 3]) for i in range(224 - len(ramp))]
    pal_img = Image.new('P', (1, 1))
    pal_img.putpalette([c for rgb in pal for c in rgb] + [0, 0, 0] * (256 - len(pal)))
    q = img.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG)

    q.convert('RGB').save(out, optimize=True)
    img.save(out.replace('.png', '_full.png'))

    # Same picture for the app's splash: LVGL 8-bit indexed image body
    # (256 x ARGB8888 palette, then one index byte per pixel)
    raw = bytearray()
    flat = q.getpalette()[:768] + [0] * max(0, 768 - len(q.getpalette()))
    for i in range(256):
        r, g, b = flat[i * 3:i * 3 + 3]
        raw += bytes((b, g, r, 255))
    raw += q.tobytes()
    open(out.replace('.png', '.bin'), 'wb').write(raw)

    print(out, len(q.convert('RGB').getcolors(1 << 24)), 'colours, bolt at', LAYOUT['bolt'])

if __name__ == '__main__':
    build(sys.argv[1])
