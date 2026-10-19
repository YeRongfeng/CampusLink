"""Generate the architecture diagram for the phase2 (book module) design report.
Visual style matches the phase1 report's embedded diagram: rounded light-gray boxes,
black connecting arrows with a short label above each arrow, Microsoft YaHei font.
Run with the system Python (PIL required), output is a standalone PNG consumed by
build_report.py when assembling the docx.
"""
from PIL import Image, ImageDraw, ImageFont

FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
OUT = r"C:\Users\lenovo\Desktop\web大作业\CampusLink\docs\交付文档\assets\book-architecture.png"

SCALE = 2  # render at 2x then the docx picture width controls final on-page size
W, H = 1800 * SCALE // 2, 640 * SCALE // 2


def font(size):
    return ImageFont.truetype(FONT_REGULAR, size)


TITLE_FONT = font(30)
LABEL_FONT = font(24)
ARROW_FONT = font(22)

BOX_FILL = (243, 244, 246)
BOX_OUTLINE = (156, 163, 175)
TEXT_COLOR = (31, 41, 55)
ARROW_COLOR = (55, 65, 81)


def rounded_box(draw, xy, radius, fill, outline, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(draw, box, lines, font_obj, fill):
    x0, y0, x1, y1 = box
    total_h = len(lines) * (font_obj.size + 10) - 10
    y = y0 + ((y1 - y0) - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_obj)
        w = bbox[2] - bbox[0]
        x = x0 + ((x1 - x0) - w) / 2
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + 10


def arrow(draw, p0, p1, label=None, label_font=ARROW_FONT):
    x0, y0 = p0
    x1, y1 = p1
    draw.line([(x0, y0), (x1, y1)], fill=ARROW_COLOR, width=3)
    # arrow head
    ah = 10
    if x1 > x0:
        draw.polygon([(x1, y1), (x1 - ah, y1 - ah // 2), (x1 - ah, y1 + ah // 2)], fill=ARROW_COLOR)
    if label:
        bbox = draw.textbbox((0, 0), label, font=label_font)
        w = bbox[2] - bbox[0]
        mx = (x0 + x1) / 2 - w / 2
        draw.text((mx, min(y0, y1) - 34), label, font=label_font, fill=TEXT_COLOR)


img = Image.new("RGB", (1800, 640), "white")
d = ImageDraw.Draw(img)

box_w, box_h = 420, 150
row1_y = 60
row2_y = 400
gap = 90

xs = [40, 40 + box_w + gap, 40 + 2 * (box_w + gap)]

# Row 1: business data path
boxes1 = [
    ("用户页面", "填写书籍信息和操作"),
    ("项目服务器", "检查身份和业务条件"),
    ("项目数据库", "保存书籍、收藏和联系方式"),
]
for x, (t1, t2) in zip(xs, boxes1):
    rounded_box(d, (x, row1_y, x + box_w, row1_y + box_h), radius=18, fill=BOX_FILL, outline=BOX_OUTLINE)
    centered_text(d, (x, row1_y, x + box_w, row1_y + box_h), [t1, t2], LABEL_FONT, TEXT_COLOR)

arrow(d, (xs[0] + box_w, row1_y + box_h / 2), (xs[1], row1_y + box_h / 2), "提交操作")
arrow(d, (xs[1] + box_w, row1_y + box_h / 2), (xs[2], row1_y + box_h / 2), "读取或保存")

mid_text = "上方处理书籍与收藏数据，下方处理图片上传；结果沿原路返回页面。"
bbox = d.textbbox((0, 0), mid_text, font=ARROW_FONT)
mw = bbox[2] - bbox[0]
d.text(((1800 - mw) / 2, row1_y + box_h + 45), mid_text, font=ARROW_FONT, fill=(107, 114, 128))

# Row 2: image upload path
boxes2 = [
    ("书籍图片选择", "选择并提交图片文件"),
    ("项目服务器", "校验图片并保存到本地目录"),
    ("本地文件目录", "按随机文件名存储，数据库仅存地址"),
]
for x, (t1, t2) in zip(xs, boxes2):
    rounded_box(d, (x, row2_y, x + box_w, row2_y + box_h), radius=18, fill=BOX_FILL, outline=BOX_OUTLINE)
    centered_text(d, (x, row2_y, x + box_w, row2_y + box_h), [t1, t2], LABEL_FONT, TEXT_COLOR)

arrow(d, (xs[0] + box_w, row2_y + box_h / 2), (xs[1], row2_y + box_h / 2), "上传图片")
arrow(d, (xs[1] + box_w, row2_y + box_h / 2), (xs[2], row2_y + box_h / 2), "写入文件")

img.save(OUT)
print("saved", OUT)
