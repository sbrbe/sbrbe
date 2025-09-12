# Seamless loop GIF: plumber-like runner + UFO that fires short lasers.
# True perfect loop (frame 0 == frame N) with periodic motions.
# Output: ./mario_ufo_loop.gif
from PIL import Image, ImageDraw
import math

W, H = 180, 110
SCALE = 5
FPS = 24
DURATION_S = 3.0
FRAMES = int(FPS * DURATION_S)  # 72

C = {
    "sky": (13,17,23),
    "star1": (90,100,115),
    "star2": (140,155,175),
    "ground": (22,27,34),
    "brick": (35,43,55),
    "grass": (67,160,71),
    "coin": (245,208,66),
    "skin": (233,200,167),
    "cap": (214,65,65),
    "shirt": (214,65,65),
    "overall": (49,130,206),
    "boot": (84,62,49),
    "outline": (0,0,0),
    "ufo_body": (120,200,210),
    "ufo_glass": (180,235,245),
    "ufo_neon": (57,211,83),
    "ufo_shadow": (80,150,160),
    "laser_core": (245,64,99),
    "laser_glow": (255,150,170),
    "impact": (255,220,120),
}

TILE_W = 30
SCROLL_PER_FRAME = 5  # 5*72 = 360; 360 % 30 == 0 -> perfect loop

HERO_X = 42
GROUND_Y = H - 20
LASER_COUNT = 3
LASER_LEN = 12

def new_canvas():
    from PIL import Image
    return Image.new("RGB", (W*SCALE, H*SCALE), C["sky"])

def r(draw, x, y, w, h, col):
    draw.rectangle([x*SCALE, y*SCALE, (x+w)*SCALE-1, (y+h)*SCALE-1], fill=col)

def p(draw, x, y, col):
    r(draw, x, y, 1, 1, col)

def draw_stars(d, t):
    phase = t / FRAMES
    for i in range(0, W, 6):
        x = i
        y = 8 + (i * 17) % 40
        tw = 0.5 + 0.5*math.sin(2*math.pi*(phase*2 + i*0.01))
        col = tuple(int(C["star1"][k]*(0.6 + 0.4*tw)) for k in range(3))
        p(d, x, y, col)
    for i in range(0, W, 8):
        x = (i + 3) % W
        y = 6 + (i * 23) % 46
        tw = 0.5 + 0.5*math.sin(2*math.pi*(phase*2.5 + i*0.008))
        col = tuple(int(C["star2"][k]*(0.6 + 0.4*tw)) for k in range(3))
        p(d, x, y, col)

def draw_ground(d, t):
    r(d, 0, GROUND_Y, W, H-GROUND_Y, C["ground"])
    r(d, 0, GROUND_Y, W, 2, C["grass"])
    offset = (t * SCROLL_PER_FRAME) % TILE_W
    for bx in range(-TILE_W, W+TILE_W, TILE_W):
        x = bx - offset
        r(d, x, GROUND_Y+4, TILE_W-4, 5, C["brick"])
        r(d, x, GROUND_Y+11, TILE_W-4, 5, C["brick"])

def draw_blocks(d, t):
    offset = (t * SCROLL_PER_FRAME) % TILE_W
    for bx in range(-TILE_W, W+TILE_W, TILE_W):
        x = bx - offset + 10
        r(d, x, 44, 12, 12, C["brick"])
        for i in range(12):
            p(d, x+i, 44, C["outline"])
            p(d, x+i, 55, C["outline"])
            p(d, x, 44+i, C["outline"])
            p(d, x+11, 44+i, C["outline"])
        if (bx//TILE_W) % 2 == 0:
            p(d, x+5, 40, C["coin"]); p(d, x+6, 40, C["coin"])
            p(d, x+5, 41, C["coin"]); p(d, x+6, 41, C["coin"])

def draw_hero(d, t, hit=False):
    phase = (t % 12) / 12.0
    x = HERO_X; y = GROUND_Y - 6
    r(d, x+4, y-20, 10, 10, C["skin"])
    r(d, x+3, y-22, 12, 4, C["cap"])
    r(d, x+6, y-26, 10, 6, C["cap"])
    p(d, x+6, y-16, C["outline"])
    r(d, x+4, y-13, 8, 2, C["outline"])
    r(d, x+6, y-12, 10, 10, C["overall"])
    r(d, x+6, y-12, 10, 4, C["shirt"])
    swing = int(math.sin(phase*2*math.pi)*2)
    r(d, x+3, y-10+swing, 3, 6, C["shirt"])
    r(d, x+16, y-10-swing, 3, 6, C["shirt"])
    stride = int(math.cos(phase*2*math.pi)*3)
    r(d, x+6, y-2, 4, 6, C["overall"])
    r(d, x+12, y-2, 4, 6, C["overall"])
    r(d, x+6-stride, y+4, 5, 3, C["boot"])
    r(d, x+12+stride, y+4, 5, 3, C["boot"])
    if hit:
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            p(d, x+9+dx, y-12+dy, C["impact"])

def ufo_pos(t):
    cx = W//2; ax = 24; ay = 3
    px = int(cx + ax * math.sin(2*math.pi * (t/FRAMES)))
    py = 34 + int(ay * math.sin(2*math.pi * (2*t/FRAMES)))
    return px, py

def draw_ufo(d, t):
    cx, cy = ufo_pos(t)
    x = cx - 16; y = cy - 8
    r(d, x+4, y+10, 24, 3, C["ufo_shadow"])
    r(d, x+2, y+6, 28, 6, C["ufo_body"])
    r(d, x+8, y+2, 16, 5, C["ufo_glass"])
    if (t % 12) < 6:
        for i in range(0, 28, 4):
            p(d, x+2+i, y+6, C["ufo_neon"])
    return cx, y+12

def draw_lasers(d, t, origin):
    ox, oy = origin
    for k in range(LASER_COUNT):
        phase = (t/FRAMES + k / LASER_COUNT) % 1.0
        if phase < 0.35:
            prog = phase / 0.35
            head_y = oy + int(prog * (GROUND_Y - oy))
            for dy in range(LASER_LEN):
                yy = head_y + dy
                if oy <= yy < GROUND_Y:
                    p(d, ox, yy, C["laser_core"])
                    if ox-1 >= 0: p(d, ox-1, yy, C["laser_glow"])
                    if ox+1 < W: p(d, ox+1, yy, C["laser_glow"])
            if head_y + LASER_LEN >= GROUND_Y:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    p(d, ox+dx, GROUND_Y-1+dy, C["impact"])

frames = []
for t in range(FRAMES):
    img = new_canvas(); d = ImageDraw.Draw(img)
    draw_stars(d, t); draw_blocks(d, t); draw_ground(d, t)
    origin = draw_ufo(d, t); draw_lasers(d, t, origin)
    ufox, _ = origin
    hit = abs(ufox - (HERO_X+9)) <= 1 and (t % (FRAMES//LASER_COUNT)) in (0,1)
    draw_hero(d, t, hit=hit)
    frames.append(img)

out_path = "mario_ufo_loop.gif"
frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=int(1000/FPS), loop=0, optimize=True, disposal=2)
print(f"Saved: {out_path}")
