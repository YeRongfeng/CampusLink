"""Generate the book listing state-machine diagram for the phase2 design report."""
from PIL import Image, ImageDraw, ImageFont

FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
OUT = r"C:\Users\lenovo\Desktop\web大作业\CampusLink\docs\交付文档\assets\book-states.png"


def font(size):
    return ImageFont.truetype(FONT_REGULAR, size)


LABEL_FONT = font(26)
ARROW_FONT = font(20)
NOTE_FONT = font(18)

BOX_FILL_ACTIVE = (224, 242, 233)
BOX_FILL_TERMINAL = (243, 244, 246)
BOX_OUTLINE_ACTIVE = (24, 160, 88)
BOX_OUTLINE_TERMINAL = (156, 163, 175)
TEXT_COLOR = (31, 41, 55)
ARROW_COLOR = (55, 65, 81)


def rounded_box(draw, xy, radius, fill, outline, width=3):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(draw, box, text, font_obj, fill):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = x0 + ((x1 - x0) - w) / 2
    y = y0 + ((y1 - y0) - h) / 2 - bbox[1]
    draw.text((x, y), text, font=font_obj, fill=fill)


def h_arrow(draw, p0, p1, label, dashed=False):
    x0, y0 = p0
    x1, y1 = p1
    if dashed:
        length = abs(x1 - x0)
        step = 14
        n = int(length // step)
        for i in range(n):
            sx = x0 + (1 if x1 > x0 else -1) * i * step
            draw.line([(sx, y0), (sx + (1 if x1 > x0 else -1) * step * 0.6, y0)], fill=ARROW_COLOR, width=2)
    else:
        draw.line([(x0, y0), (x1, y1)], fill=ARROW_COLOR, width=3)
    ah = 9
    direction = 1 if x1 > x0 else -1
    draw.polygon([(x1, y1), (x1 - ah * direction, y1 - ah // 2), (x1 - ah * direction, y1 + ah // 2)], fill=ARROW_COLOR)
    bbox = draw.textbbox((0, 0), label, font=ARROW_FONT)
    w = bbox[2] - bbox[0]
    draw.text(((x0 + x1) / 2 - w / 2, min(y0, y1) - 30), label, font=ARROW_FONT, fill=TEXT_COLOR)


img = Image.new("RGB", (1800, 520), "white")
d = ImageDraw.Draw(img)

box_w, box_h = 280, 110
y = 90
gap = 160
xs = [60, 60 + box_w + gap, 60 + 2 * (box_w + gap), 60 + 3 * (box_w + gap)]

states = [
    ("在售 listed", True),
    ("已预定 reserved", True),
    ("已售出 sold", False),
    ("已下架 removed", False),
]
for x, (text, active) in zip(xs, states):
    fill = BOX_FILL_ACTIVE if active else BOX_FILL_TERMINAL
    outline = BOX_OUTLINE_ACTIVE if active else BOX_OUTLINE_TERMINAL
    rounded_box(d, (x, y, x + box_w, y + box_h), radius=16, fill=fill, outline=outline)
    centered_text(d, (x, y, x + box_w, y + box_h), text, LABEL_FONT, TEXT_COLOR)

cy = y + box_h / 2
# listed -> reserved
h_arrow(d, (xs[0] + box_w, cy - 14), (xs[1], cy - 14), "标记预定")
# reserved -> listed
h_arrow(d, (xs[1], cy + 22), (xs[0] + box_w, cy + 22), "取消预定")
# reserved -> sold
h_arrow(d, (xs[1] + box_w, cy), (xs[2], cy), "标记售出")
# sold -> removed: not a real transition, skip

# listed -> sold (curved below, approximate with offset line)
below_y = y + box_h + 70
d.line([(xs[0] + box_w / 2, y + box_h), (xs[0] + box_w / 2, below_y)], fill=ARROW_COLOR, width=3)
d.line([(xs[0] + box_w / 2, below_y), (xs[2] + box_w / 2, below_y)], fill=ARROW_COLOR, width=3)
d.line([(xs[2] + box_w / 2, below_y), (xs[2] + box_w / 2, y + box_h)], fill=ARROW_COLOR, width=3)
ah = 9
d.polygon([(xs[2] + box_w / 2, y + box_h), (xs[2] + box_w / 2 - ah // 2, y + box_h + ah), (xs[2] + box_w / 2 + ah // 2, y + box_h + ah)], fill=ARROW_COLOR)
label = "标记售出（在售直接售出）"
bbox = d.textbbox((0, 0), label, font=ARROW_FONT)
w = bbox[2] - bbox[0]
d.text(((xs[0] + box_w / 2 + xs[2] + box_w / 2) / 2 - w / 2, below_y + 8), label, font=ARROW_FONT, fill=TEXT_COLOR)

# listed -> removed, reserved -> removed (further below)
below_y2 = below_y + 70
for src_idx, label in [(0, "下架（在售直接下架）"), (1, "下架（预定后下架）")]:
    sx = xs[src_idx] + box_w / 2
    d.line([(sx, y + box_h if src_idx == 0 else y + box_h), (sx, below_y2)], fill=ARROW_COLOR, width=2)

d.line([(xs[0] + box_w / 2, below_y2), (xs[3] + box_w / 2, below_y2)], fill=ARROW_COLOR, width=3)
d.line([(xs[3] + box_w / 2, below_y2), (xs[3] + box_w / 2, y + box_h)], fill=ARROW_COLOR, width=3)
d.polygon([(xs[3] + box_w / 2, y + box_h), (xs[3] + box_w / 2 - ah // 2, y + box_h + ah), (xs[3] + box_w / 2 + ah // 2, y + box_h + ah)], fill=ARROW_COLOR)
label2 = "下架（在售或已预定均可直接下架）"
bbox2 = d.textbbox((0, 0), label2, font=ARROW_FONT)
w2 = bbox2[2] - bbox2[0]
d.text(((xs[0] + box_w / 2 + xs[3] + box_w / 2) / 2 - w2 / 2, below_y2 + 8), label2, font=ARROW_FONT, fill=TEXT_COLOR)

note = "已售出、已下架为终态，不可再变更状态；仅“在售”状态下允许发布者编辑书籍信息。"
d.text((60, below_y2 + 60), note, font=NOTE_FONT, fill=(107, 114, 128))

img.save(OUT)
print("saved", OUT)
