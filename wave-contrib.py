# UFO pixel-art GIF generator with seamless loop.
# Produces a short, stylish animation: a UFO hovers, background scrolls,
# and short laser bursts fire periodically. All motions are perfectly looping.
#
# Output file: ./ufo_lasers_loop.gif

from PIL import Image, ImageDraw
import math

# ---------------------- Config ----------------------
W, H = 180, 110      # logical canvas (pixels)
SCALE = 5            # upscale factor for crisp pixel look
FPS = 24
DURATION_S = 3.0
FRAMES = int(FPS * DURATION_S)     # ensure integer

# Colors (dark GitHub-y night palette + neon)
C = {
    "sky": (13,17,23),       # #0d1117
    "star1": (80, 90, 105),
    "star2": (130, 145, 165),
    "ground": (22,27,34),    # #161b22
    "building": (30,36,46),
    "window": (246, 220, 92),
    "ufo_body": (120, 200, 210),
    "ufo_glass": (180, 235, 245),
    "ufo_shadow": (80, 150, 160),
    "ufo_neon": (57, 211, 83),   # #39d353
    "laser_core": (245, 64, 99),
    "laser_glow": (255, 150, 170),
    "impact": (255, 220, 120),
}

# Background tile width must divide the scroll period for a perfect loop
TILE_W = 30          # parallax tile width
SCROLL_PX_PER_FRAME = 2  # must divide TILE_W * k over FRAMES for perfect loop
# Ensure seamless: after FRAMES frames, offset == 0 (mod TILE_W)

# Laser timing
LASER_PERIOD = 24      # frames between shots (must divide FRAMES for clean loop)
LASER_SPEED = 6        # pixels per frame (logical)
LASER_LEN = 14         # short beam length

# UFO bob & neon
BOB_PIX = 2            # up/down amplitude
NEON_PERIOD = 12       # frames for neon pulsing

# ---------------------- Helpers ----------------------
def new_canvas():
    return Image.new("RGB", (W*SCALE, H*SCALE), C["sky"])

def r(draw, x, y, w, h, col):
    draw.rectangle([x*SCALE, y*SCALE, (x+w)*SCALE-1, (y+h)*SCALE-1], fill=col)

def p(draw, x, y, col):
    r(draw, x, y, 1, 1, col)

def draw_stars(d, t):
    # Two star layers; parallax via subtle horizontal drift; twinkle via sin
    phase = t / FRAMES
    drift1 = int((phase * W) % W)
    drift2 = int((phase * (W*0.5)) % W)

    for i in range(0, W, 6):
        x = (i - drift1) % W
        y = 10 + (i * 17) % 40
        tw = 0.5 + 0.5*math.sin(2*math.pi*(phase*2 + i*0.01))
        col = tuple(int(C["star1"][k]*(0.6 + 0.4*tw)) for k in range(3))
        p(d, x, y, col)

    for i in range(0, W, 7):
        x = (i - drift2) % W
        y = 6 + (i * 23) % 50
        tw = 0.5 + 0.5*math.sin(2*math.pi*(phase*2.5 + i*0.008))
        col = tuple(int(C["star2"][k]*(0.6 + 0.4*tw)) for k in range(3))
        p(d, x, y, col)

def draw_ground(d):
    r(d, 0, H-18, W, 18, C["ground"])

def draw_buildings(d, t):
    # Repeating skyline that scrolls left and loops perfectly
    offset = (t * SCROLL_PX_PER_FRAME) % TILE_W
    base_y = H-18
    for bx in range(-TILE_W, W+TILE_W, TILE_W):
        x = bx - offset
        h = 8 + ((bx*37) % 28)  # pseudo-random height, repeats on TILE_W
        r(d, x, base_y - h, TILE_W-2, h, C["building"])
        # windows pattern
        for wy in range(base_y - h + 2, base_y-2, 4):
            for wx in range(x+2, x+TILE_W-4, 6):
                if ((wx + wy) // 6) % 3 == 0:
                    p(d, wx, wy, C["window"])

def draw_ufo(d, t):
    # Fixed x; bobbing y; neon pulse — all loop cleanly
    x = W//2 - 18
    bob = int(BOB_PIX * math.sin(2*math.pi*(t/FRAMES)*2))
    y = 34 + bob

    # shadow/underside
    r(d, x+4, y+10, 28, 4, C["ufo_shadow"])
    # body
    r(d, x+2, y+6, 32, 6, C["ufo_body"])
    r(d, x+8, y+2, 20, 6, C["ufo_glass"])

    # neon ring (pulses)
    neon_phase = (t % NEON_PERIOD) / NEON_PERIOD
    neon_on = neon_phase < 0.5
    if neon_on:
        for i in range(0, 32, 4):
            p(d, x+2+i, y+6, C["ufo_neon"])

    return x+18, y+12  # laser origin (center bottom)

def draw_lasers(d, t, origin):
    # Short beams spawned every LASER_PERIOD frames; loop-safe if LASER_PERIOD | FRAMES
    ox, oy = origin
    for n in range(4):  # allow several beams in flight
        t0 = (t // LASER_PERIOD - n) * LASER_PERIOD
        if t0 < 0:
            continue
        age = t - t0
        if 0 <= age < 40:
            y = oy + age * LASER_SPEED
            if y > H-18:
                y = H-18
            # short segment
            for dy in range(14):
                yy = y + dy
                if oy <= yy < H-18:
                    p(d, ox, yy, C["laser_core"])
                    if (yy + dy) % 2 == 0:
                        if ox-1 >= 0: p(d, ox-1, yy, C["laser_glow"])
                        if ox+1 < W: p(d, ox+1, yy, C["laser_glow"])
            # ground impact
            if y >= H-18:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    p(d, ox+dx, H-19+dy, C["impact"])

# ---------------------- Render ----------------------
frames = []
for t in range(FRAMES):
    img = new_canvas()
    d = ImageDraw.Draw(img)

    draw_stars(d, t)
    draw_buildings(d, t)
    draw_ground(d)
    origin = draw_ufo(d, t)
    draw_lasers(d, t, origin)

    frames.append(img)

out_path = "ufo_lasers_loop.gif"
frames[0].save(
    out_path,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000/FPS),
    loop=0,
    optimize=True,
    disposal=2
)

print(f"Saved: {out_path}")
