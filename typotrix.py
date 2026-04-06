import pygame
import requests
import os
import random
import json
import urllib.request

os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':0'

API_KEY = "AIzaSyCltIMLz8FERwlYfYPOPlj0tzM4GneDbhg"
BASE_LETTERS = ["T", "Y", "P", "E"]
SCREEN_SIZE = (720, 720)
FONT_CACHE = os.path.expanduser("~/fonts")
os.makedirs(FONT_CACHE, exist_ok=True)

WEIGHT_PRIORITY = ["900italic","900","800italic","800","700italic","700",
                   "600italic","600","500italic","500","italic","regular",
                   "400italic","400","300italic","300","200italic","200",
                   "100italic","100"]

EXCLUDE_FONTS = {
    "material symbols outlined", "material symbols rounded",
    "material symbols sharp", "material icons", "material icons outlined",
    "material icons round", "material icons sharp", "material icons two tone",
    "noto emoji", "noto color emoji"
}

WORDS = [
    "TYPE", "KERN", "GRID", "FLUX", "BOLD", "GLYPH", "INK", "LEAD",
    "FONT", "FORM", "MARK", "AXIS", "BEAM", "CROP", "DASH", "EDGE",
    "FACE", "GRIT", "HEFT", "JOIN", "KNOT", "LIFT", "MESH", "NODE",
    "OPEN", "PATH", "QUAD", "RULE", "SLAB", "THIN", "UNIT", "VOID",
    "WAVE", "XRAY", "YARD", "ZERO", "APEX", "BARE", "COAT", "DIRE",
    "EMIT", "FINE", "GRIP", "HARD", "IRON", "JUST", "KEEN", "LOOP",
    "MAST", "NEON", "OVAL", "PINE", "QUAT", "RIFT", "SCAN", "TILT",
    "URGE", "VANE", "WARP", "XACT", "YOKE", "ZONE", "ARCH", "BLOC",
    "CORD", "DUCT", "EXPO", "FOLD", "GLOW", "HALO", "IDEA", "JOLT",
    "KNOB", "LACE", "MINT", "NULL", "ORBS", "PEAK", "QUIT", "RING",
    "SLOT", "TRIM", "UPON", "VENT", "WIRE", "ZOOM", "ALTO", "BASS",
    "CLEF", "DEEP", "ECHO", "FLAT", "GLUE", "HOOK", "OPUS", "PULSE",
]

def get_colormind_color():
    try:
        req = urllib.request.Request(
            "http://colormind.io/api/",
            data=json.dumps({"model": "default"}).encode(),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
            return tuple(random.choice(data["result"]))
    except:
        return (random.randint(30,255), random.randint(30,255), random.randint(30,255))

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def get_fonts():
    url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={API_KEY}&sort=popularity"
    r = requests.get(url)
    data = r.json()
    result = []
    for f in data["items"]:
        if f["family"].lower() in EXCLUDE_FONTS:
            continue
        for w in WEIGHT_PRIORITY:
            if w in f["files"]:
                f["_use"] = w
                result.append(f)
                break
    return result

def download_font(font_item):
    weight = font_item.get("_use", "regular")
    name = font_item["family"].replace(" ", "_") + f"_{weight}"
    path = os.path.join(FONT_CACHE, f"{name}.ttf")
    if not os.path.exists(path):
        try:
            url = font_item["files"][weight]
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"Download failed: {e}")
            if os.path.exists(path):
                os.remove(path)
            return None
    try:
        pygame.font.Font(path, 100)
        return path
    except:
        print(f"Font unreadable, skipping: {path}")
        os.remove(path)
        return None

def find_font_size(font_path, ch, max_w, max_h, scale=1.4):
    lo, hi = 10, 900
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        try:
            f = pygame.font.Font(font_path, mid)
        except:
            f = pygame.font.SysFont("monospace", mid)
        w, h = f.size(ch)
        if w <= max_w and h <= max_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    sized = int(best * scale)
    try:
        return pygame.font.Font(font_path, sized)
    except:
        return pygame.font.SysFont("monospace", sized)

def draw_loading(screen, font, font_name, inverted):
    bg = (255, 255, 255) if inverted else (0, 0, 0)
    fg = (80, 80, 80) if inverted else (160, 160, 160)
    screen.fill(bg)
    msg = font.render(f"loading  {font_name}...", True, fg)
    screen.blit(msg, (SCREEN_SIZE[0]//2 - msg.get_width()//2,
                      SCREEN_SIZE[1]//2 - msg.get_height()//2))
    pygame.display.flip()

class Scene:
    def __init__(self, letters, label, circle):
        self.letters = letters
        self.label = label
        self.circle = circle
        self.order = list(range(len(letters)))
        random.shuffle(self.order)
        self.shown = 0
        self.show_timer = 0
        self.show_interval = 0.08

    def update(self, dt):
        self.show_timer += dt
        while self.show_timer >= self.show_interval and self.shown < len(self.order):
            self.show_timer -= self.show_interval
            self.shown += 1

    def draw(self, screen, inverted, growing_circle=None):
        bg = (255, 255, 255) if inverted else (0, 0, 0)
        screen.fill(bg)

        if self.circle:
            cx, cy, cr, colour = self.circle
            pygame.draw.circle(screen, colour, (cx, cy), max(1, cr))

        if growing_circle:
            cx, cy, cr, colour = growing_circle
            if cr > 1:
                pygame.draw.circle(screen, colour, (cx, cy), int(cr))

        for i in self.order[:self.shown]:
            surf, x, y = self.letters[i]
            screen.blit(surf, (x, y))

        if self.label:
            lsurf, lx, ly, lalpha = self.label
            lsurf.set_alpha(lalpha)
            screen.blit(lsurf, (lx, ly))

def build_scene(fonts, fi, ui_font, inverted, screen, case_cache, circle=None):
    fg = (0, 0, 0) if inverted else (255, 255, 255)
    label_fg = (80, 80, 80) if inverted else (160, 160, 160)

    attempts = 0
    path = None
    font_item = None
    while path is None and attempts < 10:
        font_item = fonts[fi % len(fonts)]
        draw_loading(screen, ui_font, font_item['family'], inverted)
        path = download_font(font_item)
        if path is None:
            fi += 1
        attempts += 1

    if path is None:
        return None, fi

    print(f"Font: {font_item['family']} ({font_item.get('_use','regular')}) index={fi}")

    cols = 2
    rows = 2
    label_h = 27
    cell_w = SCREEN_SIZE[0] // cols
    cell_h = (SCREEN_SIZE[1] - label_h) // rows

    if fi not in case_cache:
        word = random.choice(WORDS)
        upper = random.random() < 0.5
        case_cache[fi] = [ch.upper() if upper else ch.lower() for ch in word[:4]]
    chars = list(case_cache[fi])

    digit_key = f"digit_{fi}"
    if digit_key not in case_cache:
        case_cache[digit_key] = (random.randint(0, 3), str(random.randint(0, 9)))
    digit_index, digit_char = case_cache[digit_key]
    chars[digit_index] = digit_char

    ROWS = [chars[:2], chars[2:]]

    letters = []
    for ri, row in enumerate(ROWS):
        for ci, ch in enumerate(row):
            font = find_font_size(path, ch, cell_w, cell_h, scale=1.4)
            surf = font.render(ch, True, fg)
            w, h = surf.get_size()
            cell_x = ci * cell_w
            cell_y = ri * cell_h
            x = cell_x + (cell_w - w) // 2
            y = cell_y + (cell_h - h) // 2
            letters.append((surf, x, y))

    weight_label = font_item.get('_use', 'regular')
    label_text = f"{font_item['family']} / {weight_label}"
    lsurf = ui_font.render(label_text, True, label_fg)
    lx = SCREEN_SIZE[0]//2 - lsurf.get_width()//2
    ly = SCREEN_SIZE[1] - label_h + 4
    label = (lsurf, lx, ly, 180)

    return Scene(letters, label, circle), fi

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("typotrix")
    clock = pygame.time.Clock()

    print("Fetching fonts...")
    fonts = get_fonts()
    print(f"{len(fonts)} fonts loaded")

    ui_font = pygame.font.SysFont("monospace", 14)
    font_index = 0
    inverted = False
    case_cache = {}
    circle = None

    scene, font_index = build_scene(fonts, font_index, ui_font, inverted, screen, case_cache, circle)

    touches = {}
    long_press_fired = set()
    LONG_PRESS_MS = 700
    CENTER_ZONE = 0.1
    CIRCLE_MAX_R = 600
    CIRCLE_GROW_DURATION = 4.0

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        dt = min(dt, 0.05)
        now = pygame.time.get_ticks()

        growing_circle = None

        for fid, t in list(touches.items()):
            held_ms = now - t['start_time']
            cur_x = 1.0 - t.get('cur_x', t['start_x'])
            cur_y = t.get('cur_y', t['start_y'])
            is_center = abs(cur_x - 0.5) < CENTER_ZONE and abs(cur_y - 0.5) < CENTER_ZONE

            if held_ms >= LONG_PRESS_MS:
                if fid not in long_press_fired:
                    long_press_fired.add(fid)
                    if is_center:
                        inverted = not inverted
                        scene, font_index = build_scene(fonts, font_index, ui_font, inverted, screen, case_cache, circle)
                    else:
                        t['circle_colour'] = get_colormind_color()
                        t['circle_start_ms'] = now

                if not is_center and 'circle_colour' in t:
                    grow_secs = (now - t['circle_start_ms']) / 1000.0
                    progress = min(grow_secs / CIRCLE_GROW_DURATION, 1.0)
                    eased = ease_in_out(progress)
                    r = eased * CIRCLE_MAX_R
                    px = int(cur_x * SCREEN_SIZE[0])
                    py = int((1.0 - cur_y) * SCREEN_SIZE[1])
                    # auto reset when fully grown
                    if progress >= 1.0:
                        t['circle_colour'] = get_colormind_color()
                        t['circle_start_ms'] = now
                        if scene:
                            scene.circle = None
                    growing_circle = (px, py, r, t['circle_colour'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    font_index += 1
                    circle = None
                    scene, font_index = build_scene(fonts, font_index, ui_font, inverted, screen, case_cache, circle)
                elif event.key == pygame.K_LEFT:
                    font_index = max(0, font_index - 1)
                    circle = None
                    scene, font_index = build_scene(fonts, font_index, ui_font, inverted, screen, case_cache, circle)

            elif event.type == pygame.FINGERDOWN:
                touches[event.finger_id] = {
                    'start_x': event.x,
                    'start_y': event.y,
                    'cur_x': event.x,
                    'cur_y': event.y,
                    'start_time': now
                }

            elif event.type == pygame.FINGERMOTION:
                if event.finger_id in touches:
                    touches[event.finger_id]['cur_x'] = event.x
                    touches[event.finger_id]['cur_y'] = event.y

            elif event.type == pygame.FINGERUP:
                if event.finger_id not in touches:
                    continue
                t = touches.pop(event.finger_id)
                was_long = event.finger_id in long_press_fired
                long_press_fired.discard(event.finger_id)

                if was_long:
                    if growing_circle:
                        cx, cy, cr, colour = growing_circle
                        circle = (cx, cy, max(1, int(cr)), colour)
                        if scene:
                            scene.circle = circle
                        print(f"CIRCLE COMMITTED r={int(cr)}")
                else:
                    sx = t['start_x']
                    circle = None
                    if sx < 0.5:
                        font_index += 1
                    else:
                        font_index = max(0, font_index - 1)
                    scene, font_index = build_scene(fonts, font_index, ui_font, inverted, screen, case_cache, circle)

        if scene:
            scene.update(dt)
            scene.draw(screen, inverted, growing_circle)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
