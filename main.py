import badger2040
import badger_os
import time
import jpegdec
import pngdec
import os
import re

WIDTH = badger2040.WIDTH
HEIGHT = badger2040.HEIGHT
LEFT_PADDING = 7
LINE_HEIGHT = 32
LINE_SPACING = 4
TEXT_WIDTH = WIDTH - LEFT_PADDING

FONTS = ["bitmap8", "serif", "sans", "gothic", "cursive", "bitmap14_outline"]
THICKNESSES = [1, 3, 3, 2, 3, 1]
SIZE_ADJ = [1, 0.3, 0.3, 0.3, 0.3, 0.8]

DEFAULT_TEXT = "Firstname\tLastname\tCompany\tTitle"

state = {
    "font_idx": 0,
    "picture_idx": 0,
    "badge_idx": 0,
}
images = []

def extract_image_width_from_filename(filename):
    match = re.search(r'_(\d+)\.', filename)
    if match:
        return int(match.group(1))
    return 0

def find_images(path):
    try:
        return [
            f for f in os.listdir(path)
            if f.endswith(".jpg") or f.endswith(".png")
        ]
    except OSError:
        pass

def read_data(path):
    data = []
    
    try:
        badge = open(path, "r")
    except OSError:
        with open(path, "w") as f:
            f.write(DEFAULT_TEXT)
            f.flush()
        badge = open(path, "r")
    
    try:
        row = badge.readline().split('\t')
        while len(row) >= 4:
            data.append({
                "first_name": row[0],
                "last_name": row[1],
                "company": row[2],
                "title": row[3],
            })
            row = badge.readline().split('\t')
    finally:
        badge.close()

    return data

def draw_background():
    try:
        target_image = images[state["picture_idx"]]
        image_size = extract_image_width_from_filename(target_image)

        # If no image was pulled from the name, it must be the background.
        if(image_size == 0):
            image_size = WIDTH
        
        image_path = f"/badges/{target_image}"
        if image_path.endswith(".png"):
            png.open_file(image_path)
            png.decode(WIDTH - image_size, 0)
        else:
            jpeg.open_file(image_path)
            jpeg.decode(WIDTH - image_size, 0)
    except OSError:
        print("Badge background error")

def draw_text(text, line, size, scale):
    display.set_pen(0)
    vertical_adjustment = int(1 / scale) * 3
    scale = 4 * scale
    while True:
        name_length = display.measure_text(text, scale)
        if name_length >= TEXT_WIDTH and scale >= 0.1:
            scale -= 0.01
        else:
            display.text(text, LEFT_PADDING, (LINE_HEIGHT * line) + LINE_SPACING + vertical_adjustment, TEXT_WIDTH, scale)
            break

def draw_badge():
    size_adjustment = SIZE_ADJ[state["font_idx"]]
    
    display.set_pen(15)
    display.clear()

    draw_background()

    display.set_pen(0)
    display.set_font(FONTS[state["font_idx"]])
    display.set_thickness(THICKNESSES[state["font_idx"]])

    draw_text(badges[state["badge_idx"]]["first_name"], 0, 32, size_adjustment)
    draw_text(badges[state["badge_idx"]]["last_name"], 1, 32, size_adjustment)

    display.set_pen(0)
    display.set_thickness(int(THICKNESSES[state["font_idx"]] * 0.75))
    draw_text(badges[state["badge_idx"]]["title"], 2, 16, size_adjustment * 0.85)
    draw_text(badges[state["badge_idx"]]["company"], 3, 16, size_adjustment * 0.65)
    
    display.update()

def handle_event():
    if display.pressed(badger2040.BUTTON_DOWN):
        state["badge_idx"] = (state["badge_idx"] - 1) % len(badges)
        return True

    if display.pressed(badger2040.BUTTON_UP):
        state["badge_idx"] = (state["badge_idx"] + 1) % len(badges)
        return True

    if display.pressed(badger2040.BUTTON_A):
        state["font_idx"] = (state["font_idx"] + 1) % len(FONTS)
        return True

    if display.pressed(badger2040.BUTTON_B):
        state["picture_idx"] = (state["picture_idx"] + 1) % len(images)
        return True
        
    if display.pressed(badger2040.BUTTON_C):
        print("GPIO Goes Here")
        return False

# ------------------------------
#        Init State
# ------------------------------
badger_os.state_load("badge", state)
badges = read_data("/badges/badge.txt")
images = find_images("/badges")

# Avoid trying to be an invalid state if images are removed.
state["picture_idx"] = state["picture_idx"] % len(images)

display = badger2040.Badger2040()
display.led(128)
display.set_update_speed(badger2040.UPDATE_FAST)

jpeg = jpegdec.JPEG(display.display)
png = pngdec.PNG(display.display)

# ------------------------------
#       Main Event Loop
# ------------------------------
draw_badge()
while True:
    display.keepalive()

    if handle_event():
        badger_os.state_save("badge", state)
        draw_badge()

    time.sleep(0.1)
    display.halt()
