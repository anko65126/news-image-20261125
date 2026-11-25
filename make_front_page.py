"""Draw the front page for Wednesday 25 November 2026 and save it as entry.png.

One broadsheet page built from the day's reporting as it stands: the second
Houthi hit on Riyadh's tallest tower, Huawei's conviction in the United
States, the corruption probe into Shanghai's party chief, Shenzhou-24
carrying the first foreign astronaut to Tiangong, and the Medal of Freedom
for Rudy Giuliani. Drawn entirely with PIL, so the bytes never change.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
PAPER = (247, 242, 231)
INK = (26, 24, 20)
FADED = (92, 86, 74)
ACCENT = (146, 32, 24)
BAND = (24, 30, 44)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF_BOLD = str(FONT_DIR / "DejaVuSerif-Bold.ttf")
SERIF = str(FONT_DIR / "DejaVuSerif.ttf")
SANS_BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
SANS = str(FONT_DIR / "DejaVuSans.ttf")


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    """Split text into lines that fit width, word by word."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def story(draw, x, y, width, kicker, headline, body, head_size=37):
    """One news block: red kicker, serif headline, then body text."""
    draw.text((x, y), kicker, font=load(SANS_BOLD, 19), fill=ACCENT)
    y += 29
    head_font = load(SERIF_BOLD, head_size)
    for line in wrap(draw, headline, head_font, width):
        draw.text((x, y), line, font=head_font, fill=INK)
        y += head_size + 6
    y += 3
    body_font = load(SERIF, 20)
    for line in wrap(draw, body, body_font, width):
        draw.text((x, y), line, font=body_font, fill=INK)
        y += 27
    return y


def tower_graphic(draw, x, y, w, h):
    """A slim skyscraper glyph with lit windows, for the Riyadh lead."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=5)
    draw.line([x + w // 2, y - 18, x + w // 2, y], fill=INK, width=4)
    win_w, win_h = 16, 20
    step_x, step_y = 30, 36
    rows = (h - 28) // step_y
    cols = (w - 24) // step_x
    for r in range(rows):
        for c in range(cols):
            wx = x + 14 + c * step_x
            wy = y + 16 + r * step_y
            lit = (r * 7 + c * 3) % 4 != 0
            draw.rectangle([wx, wy, wx + win_w, wy + win_h],
                           fill=ACCENT if (r == 1 and c == cols - 1)
                           else (INK if lit else None),
                           outline=INK, width=1)


def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)
    margin = 46
    right = PAGE_W - margin

    # Masthead
    name_font = load(SERIF_BOLD, 64)
    name = "THE WORLD IN ONE PAGE"
    w = draw.textlength(name, font=name_font)
    draw.text(((PAGE_W - w) / 2, 30), name, font=name_font, fill=INK)
    draw.line([margin, 118, right, 118], fill=INK, width=4)
    draw.line([margin, 126, right, 126], fill=INK, width=1)
    date_font = load(SANS, 19)
    date_line = "Wednesday, 25 November 2026  ·  One image, the whole day"
    w = draw.textlength(date_line, font=date_font)
    draw.text(((PAGE_W - w) / 2, 136), date_line, font=date_font, fill=FADED)

    # Lead story, with the tower glyph on its right
    lead_y = 178
    tower_graphic(draw, right - 118, lead_y + 4, 104, 176)
    lead_end = story(
        draw, margin, lead_y, 760,
        "MIDDLE EAST",
        "RIYADH'S TALLEST TOWER HIT AGAIN",
        "Saudi officials called it a terrorist attack: a Houthi strike on "
        "the King Abdullah Financial District injured 11 people, the "
        "second hit on the capital's tallest skyscraper in a week. In the "
        "Strait of Hormuz, Tehran said tankers had been hit by explosions.",
        head_size=44,
    )

    # Two-column rows; each divider sits below the taller column so no
    # story can spill into the next row.
    col_w = 448
    col_r = right - col_w
    rule_y = lead_end + 12
    draw.line([margin, rule_y, right, rule_y], fill=INK, width=2)
    mid_y = rule_y + 18
    mid_left = story(
        draw, margin, mid_y, col_w,
        "BUSINESS / LAW",
        "HUAWEI CONVICTED IN US CRIMINAL TRIAL",
        "A US jury convicted the Chinese tech giant of stealing trade "
        "secrets, in a sprawling criminal trial centred on its business "
        "in Iran.",
        head_size=34,
    )
    mid_right = story(
        draw, col_r, mid_y, col_w,
        "CHINA",
        "XI PROBES SHANGHAI PARTY CHIEF",
        "China is investigating Politburo member and Shanghai party "
        "chief Chen Jining, widening what has become the biggest "
        "leadership shakeup in decades.",
        head_size=34,
    )

    rule_y = max(mid_left, mid_right) + 12
    draw.line([margin, rule_y, right, rule_y], fill=INK, width=2)
    low_y = rule_y + 18
    low_left = story(
        draw, margin, low_y, col_w,
        "SPACE",
        "SHENZHOU-24'S FIRST FOREIGN ASTRONAUT",
        "China's Shenzhou-24 launched with Pakistani Zeeshan Ali "
        "aboard, the first foreign astronaut to visit the Tiangong "
        "space station.",
        head_size=29,
    )
    low_right = story(
        draw, col_r, low_y, col_w,
        "UNITED STATES",
        "GIULIANI RECEIVES MEDAL OF FREEDOM",
        "President Trump awarded the nation's highest civilian honour "
        "to Rudy Giuliani, the former New York mayor and longtime ally.",
        head_size=29,
    )
    assert max(low_left, low_right) <= 950, "stories overflow the page"

    # News-in-brief band along the foot of the page
    band_y = 958
    draw.rectangle([0, band_y, PAGE_W, PAGE_H], fill=BAND)
    band_font = load(SANS_BOLD, 20)
    band_text = "ALSO TODAY · COLOMBIA GUNMEN HOLD 25 HOSTAGE IN SUPERMARKET"
    w = draw.textlength(band_text, font=band_font)
    draw.text(((PAGE_W - w) / 2, band_y + 10), band_text,
              font=band_font, fill=(240, 236, 224))
    small_font = load(SANS, 16)
    small = ("Nvidia comeback rally fades as Huang says he is in therapy · "
             "Solomon Islands signs sweeping pact with Australia")
    w = draw.textlength(small, font=small_font)
    draw.text(((PAGE_W - w) / 2, band_y + 40), small,
              font=small_font, fill=(196, 200, 210))

    out = Path(__file__).with_name("entry.png")
    page.save(out, format="PNG", optimize=True)
    return out


if __name__ == "__main__":
    print(build_page())
