from PIL import Image, ImageDraw, ImageFilter
import random
import os

def _clamp(v): return max(0, min(255, int(v)))

def _generate_pbr_carbon_fiber(size, rng):
    w, h = size
    img = Image.new('RGBA', size, (18, 18, 18, 255))
    draw = ImageDraw.Draw(img)
    step = 6
    for y in range(0, h, step):
        for x in range(0, w, step):
            if (x//step + y//step) % 2 == 0:
                draw.line([(x, y), (x+step, y+step)], fill=(38, 38, 38, 255), width=2)
                draw.line([(x, y+2), (x+step, y+step+2)], fill=(10, 10, 10, 255), width=1)
            else:
                draw.line([(x+step, y), (x, y+step)], fill=(45, 45, 45, 255), width=2)
                draw.line([(x+step, y+2), (x, y+step+2)], fill=(15, 15, 15, 255), width=1)
    return img

def _generate_pbr_brushed_metal(size, base_color, rng):
    w, h = size
    bc = (int(base_color[0]*0.4), int(base_color[1]*0.4), int(base_color[2]*0.4), 255)
    img = Image.new('RGBA', size, bc)
    draw = ImageDraw.Draw(img)
    for _ in range(h * 3):
        y = rng.randint(0, h)
        x1 = rng.randint(0, w//2)
        x2 = rng.randint(w//2, w)
        lum = rng.randint(-30, 40)
        a = rng.randint(20, 80)
        c = (_clamp(bc[0]+lum), _clamp(bc[1]+lum), _clamp(bc[2]+lum), a)
        draw.line([(x1, y), (x2, y)], fill=c, width=1)
    grad = Image.new('RGBA', size, (0,0,0,0))
    gd = ImageDraw.Draw(grad)
    for x in range(w):
        t = x / w
        val = int(255 * (1.0 - abs(t - 0.5)*2))
        gd.line([(x, 0), (x, h)], fill=(255,255,255, int(val*0.25)))
    img.alpha_composite(grad)
    return img

def _apply_gaussian_glow(base_img, color, draw_mask_func):
    w, h = base_img.size
    light_src = Image.new('RGBA', (w, h), (0,0,0,0))
    draw_mask_func(ImageDraw.Draw(light_src), color)
    glow = Image.new('RGBA', (w, h), (0,0,0,0))
    for r in [4, 12, 24, 48, 80]:
        blurred = light_src.filter(ImageFilter.GaussianBlur(r))
        rc, gc, bc, ac = blurred.split()
        alpha_mult = max(0.1, 1.0 - (r / 100))
        ac = ac.point(lambda p, am=alpha_mult: int(p * 0.4 * am))
        layer = Image.merge('RGBA', (rc, gc, bc, ac))
        glow.alpha_composite(layer)
    glow.alpha_composite(light_src)
    glow.alpha_composite(base_img)
    return glow

rng = random.Random(42)
metal = _generate_pbr_brushed_metal((200, 200), (200, 50, 50), rng)
carbon = _generate_pbr_carbon_fiber((200, 200), rng)

w, h = 640, 480
base = Image.new('RGBA', (w, h), (0,0,0,0))
def draw_mask(draw, c):
    draw.line([(0,0),(200,0)], fill=(c[0],c[1],c[2],255), width=10)
    draw.line([(0,0),(0,200)], fill=(c[0],c[1],c[2],255), width=10)

final = _apply_gaussian_glow(base, (255, 0, 0), draw_mask)
print("TEST SUCCESS")
