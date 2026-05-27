"""Generate OMLT Master Presentation PDF via ReportLab.
Mirrors the HTML deck — 25 A4-landscape pages, bilingual."""
import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

import arabic_reshaper
from bidi.algorithm import get_display

# ─── Fonts (use DejaVu — supports Arabic glyphs)
pdfmetrics.registerFont(TTFont("Body",        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold",   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("Display",     "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Display-B",   "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Display-I",   "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono",        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B",      "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"))

# ─── Palette
TERRA = HexColor("#C8442C")
CREAM = HexColor("#F6ECD6")
NAVY  = HexColor("#1B2235")
YOLK  = HexColor("#E6A532")
HERB  = HexColor("#7BA284")
DEEP  = HexColor("#9C3520")
INK   = HexColor("#0F1422")
PAPER = HexColor("#FBF6EA")
GRAY  = HexColor("#6B7775")
HAIR  = HexColor("#E1D9C6")
WHISP = HexColor("#3A4055")

# ─── Page
W, H = landscape(A4)        # 842 x 595
MARG_X, MARG_Y = 58, 50

# ─── Reshape Arabic
def ar(s):
    return get_display(arabic_reshaper.reshape(s))

# ─── helpers
c = None

def page_bg(color=PAPER):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def text_l(s, x, y, font="Body", size=10, color=INK):
    c.setFillColor(color); c.setFont(font, size)
    c.drawString(x, y, s)

def text_r(s, x, y, font="Body", size=10, color=INK):
    c.setFillColor(color); c.setFont(font, size)
    c.drawRightString(x, y, s)

def text_c(s, x, y, font="Body", size=10, color=INK):
    c.setFillColor(color); c.setFont(font, size)
    c.drawCentredString(x, y, s)

def line(x1, y1, x2, y2, color=HAIR, width=0.6):
    c.setStrokeColor(color); c.setLineWidth(width)
    c.line(x1, y1, x2, y2)

def header(num, name_en, name_ar, folio, dark=False):
    col = HexColor("#A09684") if dark else GRAY
    accent = YOLK if dark else TERRA
    y = H - MARG_Y
    text_l(num, MARG_X, y, "Mono-B", 9, accent)
    text_l(name_en + "   ·   " + ar(name_ar), MARG_X + 50, y, "Mono", 9, col)
    text_r(f"{folio:03d} / 026", W - MARG_X, y, "Mono", 9, col)
    line(MARG_X, y - 8, W - MARG_X, y - 8, color=HexColor("#3A4055") if dark else HAIR, width=0.5)

def footer(label, folio, dark=False):
    col = HexColor("#A09684") if dark else GRAY
    y = MARG_Y
    text_l(label, MARG_X, y, "Mono", 8, col)
    text_r(f"{folio:03d}  ·  026", W - MARG_X, y, "Mono", 8, col)

def kicker(s, x, y, color=TERRA, size=9):
    text_l(s.upper(), x, y, "Mono-B", size, color)

def title(s, x, y, size=36, color=NAVY, italic_word=None):
    """Draw a display title; if italic_word given, render that word with Italic serif & accent."""
    c.setFillColor(color); c.setFont("Display-B", size)
    if italic_word and italic_word in s:
        parts = s.split(italic_word, 1)
        c.drawString(x, y, parts[0])
        wbefore = c.stringWidth(parts[0], "Display-B", size)
        c.setFont("Display-I", size); c.setFillColor(TERRA)
        c.drawString(x + wbefore, y, italic_word)
        witalic = c.stringWidth(italic_word, "Display-I", size)
        c.setFont("Display-B", size); c.setFillColor(color)
        c.drawString(x + wbefore + witalic, y, parts[1])
    else:
        c.drawString(x, y, s)

def body_wrap(text, x, y, width, font="Body", size=10, color=INK, leading=14, max_lines=None, align="left"):
    """Word-wrap body text. align: left/right/center."""
    c.setFillColor(color); c.setFont(font, size)
    words = text.split(" ")
    line_words, lines = [], []
    for w in words:
        trial = " ".join(line_words + [w])
        if c.stringWidth(trial, font, size) <= width:
            line_words.append(w)
        else:
            lines.append(" ".join(line_words))
            line_words = [w]
    if line_words: lines.append(" ".join(line_words))
    if max_lines: lines = lines[:max_lines]
    for i, l in enumerate(lines):
        yy = y - i*leading
        if align == "right":
            c.drawRightString(x + width, yy, l)
        elif align == "center":
            c.drawCentredString(x + width/2, yy, l)
        else:
            c.drawString(x, yy, l)
    return y - len(lines)*leading

def ar_wrap(text, x, y, width, font="Body", size=10, color=INK, leading=15, align="right"):
    """Render Arabic line — handle simple wrap."""
    c.setFillColor(color); c.setFont(font, size)
    # naive wrap on spaces in source then reshape
    src_words = text.split(" ")
    line_words, lines = [], []
    for w in src_words:
        trial = " ".join(line_words + [w])
        shaped = ar(trial)
        if c.stringWidth(shaped, font, size) <= width:
            line_words.append(w)
        else:
            lines.append(" ".join(line_words))
            line_words = [w]
    if line_words: lines.append(" ".join(line_words))
    for i, l in enumerate(lines):
        yy = y - i*leading
        shaped = ar(l)
        if align == "right":
            c.drawRightString(x + width, yy, shaped)
        elif align == "center":
            c.drawCentredString(x + width/2, yy, shaped)
        else:
            c.drawString(x, yy, shaped)
    return y - len(lines)*leading

def rule_tiny(x, y, color=TERRA, w=34, h=2):
    c.setFillColor(color); c.rect(x, y, w, h, fill=1, stroke=0)

def card(x, y, w, h, fill=None, stroke=HAIR, line_w=0.6, radius=8):
    if fill:
        c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(line_w)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.setStrokeColor(stroke); c.setLineWidth(line_w)
        c.roundRect(x, y, w, h, radius, fill=0, stroke=1)

def labeled_card(x, y, w, h, num, h_en, h_ar, body_ar_text, dark=False):
    fill = HexColor("#252C44") if dark else HexColor("#FFFFFF")
    stroke = HexColor("#3A4055") if dark else HAIR
    fg = CREAM if dark else NAVY
    sub = HexColor("#A09684") if dark else GRAY
    accent = YOLK if dark else TERRA
    card(x, y, w, h, fill=fill, stroke=stroke)
    pad = 14
    text_l(num, x+pad, y+h-pad-8, "Mono-B", 8, accent)
    text_l(h_en, x+pad, y+h-pad-26, "Display-B", 13, fg)
    text_l(ar(h_ar), x+pad, y+h-pad-42, "Body-Bold", 11, fg)
    ar_wrap(body_ar_text, x+pad, y+h-pad-58, w-2*pad, font="Body", size=9, color=sub, leading=12, align="left")

# ─── Build PDF
OUT = "/sessions/dazzling-busy-tesla/mnt/outputs/OMLT-Master-Presentation.pdf"
c = canvas.Canvas(OUT, pagesize=landscape(A4))
c.setTitle("OMLT — Master Presentation")
c.setAuthor("OMLT")
c.setSubject("Brand & business archive")

logo_path = "/sessions/dazzling-busy-tesla/mnt/outputs/omlt-logo-approved.png"
LOGO = ImageReader(logo_path)

# ═══════════════════════════════════════════════════════
# PAGE 01 — COVER (editorial, type-led — no logo)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
# layered dark gradient
c.setFillColor(HexColor("#0B0F1B")); c.rect(0, 0, W, H, fill=1, stroke=0)
# bottom terra glow
c.saveState(); c.setFillColor(HexColor("#7F2814")); c.setFillAlpha(0.18)
c.circle(W/2, -40, 520, fill=1, stroke=0); c.restoreState()
# upper yolk glow
c.saveState(); c.setFillColor(HexColor("#E6A532")); c.setFillAlpha(0.08)
c.circle(W/2, H-60, 360, fill=1, stroke=0); c.restoreState()

# top meta
text_l("OMLT · MASTER PRESENTATION · V 1.0", MARG_X, H - MARG_Y, "Mono", 9, HexColor("#A09684"))
text_r("ABHA · KSA", W - MARG_X, H - MARG_Y, "Mono", 9, HexColor("#A09684"))

# centered editorial composition
cx = W / 2
# kicker
c.setFillColor(YOLK); c.setFont("Mono-B", 10)
c.drawCentredString(cx, H/2 + 130, "A  BREAKFAST  KITCHEN")
# rule
c.setFillColor(YOLK); c.rect(cx - 22, H/2 + 102, 44, 2, fill=1, stroke=0)

# title
c.setFillColor(CREAM); c.setFont("Display-B", 64)
c.drawCentredString(cx, H/2 + 40, "A clear,")
# italic word in yolk
c.setFillColor(YOLK); c.setFont("Display-I", 64)
c.drawCentredString(cx - 80, H/2 - 24, "simple")
c.setFillColor(CREAM); c.setFont("Display-B", 64)
c.drawString(cx + 35, H/2 - 24, "morning.")

# tiny rule
c.setFillColor(YOLK); c.saveState(); c.setFillAlpha(0.6)
c.rect(cx - 12, H/2 - 58, 24, 1.5, fill=1, stroke=0); c.restoreState()

# Arabic subtitle
c.setFillColor(HexColor("#E0D9C2")); c.setFont("Body-Bold", 18)
c.drawCentredString(cx, H/2 - 90, ar("بداية صباح واضحة وبسيطة."))

# subtext
c.setFillColor(HexColor("#9B937A")); c.setFont("Body", 10)
c.drawCentredString(cx, H/2 - 118, ar("عرض مرجعي معتمد لعلامة OMLT — تعريف المشروع، الرؤية، التكاليف، والهوية."))

# bottom strip
line(MARG_X, MARG_Y+22, W - MARG_X, MARG_Y+22, color=WHISP, width=0.4)
text_l("OMLT · BREAKFAST KITCHEN", MARG_X, MARG_Y, "Mono", 8, HexColor("#A09684"))
text_c("VOL.01 · INVESTOR EDITION", W/2, MARG_Y, "Mono", 8, HexColor("#A09684"))
text_r("001 · 026", W - MARG_X, MARG_Y, "Mono", 8, YOLK)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 02 — CONTENTS
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("II", "Contents", "الفهرس", 2)
kicker("The map", MARG_X, H - 110)
title("Twenty-five pages,", MARG_X, H - 160, 30, NAVY)
title("one egg.", MARG_X, H - 195, 30, NAVY, italic_word="egg")
rule_tiny(MARG_X, H - 215)
ar_wrap("من المفهوم إلى الميزانية، إلى الشعار، إلى الصوت — أرشيف مُعتمَد ونهائي لمرحلة التأسيس.",
        MARG_X, H - 245, 300, size=10, color=GRAY, leading=14, align="left")

# TOC right
toc = [
    ("01", "OMLT Concept",            "مفهوم المشروع",      "003"),
    ("02", "Vision & Purpose",        "الرؤية والهدف",       "007"),
    ("03", "Business Setup & Costs",  "التكاليف",            "010"),
    ("04", "Approved Logo",           "الشعار المعتمد",      "015"),
    ("05", "Brand Colors",            "الألوان",             "018"),
    ("06", "Typography",              "الخطوط",              "020"),
    ("07", "Visual Identity",         "الهوية البصرية",      "022"),
    ("08", "Sensory Identity",        "الهوية الحسّية",       "023"),
    ("09", "Audio Identity",          "الهوية الصوتية",       "024"),
]
tx = 440; ty = H - 110
for i, (n, en, arr, p_) in enumerate(toc):
    yy = ty - i*32
    text_l(n, tx, yy, "Mono-B", 10, TERRA)
    text_l(en, tx + 40, yy, "Display-B", 13, NAVY)
    we = c.stringWidth(en, "Display-B", 13)
    c.setFillColor(GRAY); c.setFont("Body", 9)
    c.drawString(tx + 40 + we + 10, yy, ar(arr))
    text_r(p_, W - MARG_X, yy, "Mono", 9, GRAY)
    line(tx, yy - 8, W - MARG_X, yy - 8, color=HAIR, width=0.4)

footer("CONTENTS", 2)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 03 — CONCEPT · DEFINITION
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("01", "Concept · Definition", "تعريف المشروع", 3)

kicker("The concept", MARG_X, H - 115)
title("A specialty", MARG_X, H - 165, 32, NAVY)
title("breakfast kitchen.", MARG_X, H - 200, 32, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 32); c.drawString(MARG_X, H - 235, "Short menu.")
rule_tiny(MARG_X, H - 255)

ar_wrap("OMLT مطبخ فطور متخصّص يعتمد على الأومليت كمنتج رئيسي ضمن قائمة قصيرة ومحدّدة، يُقدّم تجربة صباحية واضحة وسريعة داخل مساحة صغيرة ذات مطبخ مفتوح.",
        MARG_X, H - 285, 440, size=10.5, color=INK, leading=18, align="left")

body_wrap("OMLT is a specialty breakfast kitchen with the omelette as the anchor dish, served from a short and focused menu in a small space with an open kitchen.",
          MARG_X, H - 365, 440, font="Display-I", size=11, color=TERRA, leading=16)

# right — logo on cream stage
card(540, 130, 260, 280, fill=CREAM, stroke=HAIR)
c.drawImage(LOGO, 580, 170, width=180, height=180, mask='auto')

footer("SECTION 01 · CONCEPT", 3)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 04 — CONCEPT · OPERATIONAL CHARACTERISTICS
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("01", "Concept · Operational characteristics", "الخصائص التشغيلية", 4)
kicker("How it operates", MARG_X, H - 115)
title("قائمة قصيرة · إيقاع صباحي ثابت · مطبخ مفتوح.", MARG_X, H - 155, 18, NAVY)
# Replace title rendering for Arabic — use Body-Bold
c.setFillColor(PAPER); c.rect(MARG_X-2, H-180, 700, 30, fill=1, stroke=0)
c.setFillColor(NAVY); c.setFont("Body-Bold", 16)
c.drawString(MARG_X, H - 155, ar("قائمة قصيرة · إيقاع صباحي ثابت · مطبخ مفتوح."))

# 6 cards 3x2
items = [
    ("01 · MENU",    "قائمة مختصرة",        "من ٥ إلى ٧ أصناف أساسية فقط — تركيز على الإتقان لا التوسعة."),
    ("02 · HOURS",   "تشغيل صباحي محدّد",   "يفتح المطبخ ٧:٠٠ ص ويُغلق ٣:٠٠ م — لا برانش، لا عشاء."),
    ("03 · RHYTHM",  "إيقاع ثابت",          "نفس الإيقاع، نفس الجودة، طوال أيام العمل الستة."),
    ("04 · FOCUS",   "تجربة فطور فقط",      "تجربة داخلية مركّزة — لا تتشتّت بين أوقات وأطعمة مختلفة."),
    ("05 · KITCHEN", "مطبخ مفتوح",          "المطبخ ظاهر بالكامل أمام العميل — قلب التجربة."),
    ("06 · SEATS",   "٨ – ١٠ طاولات",        "جلسات محدودة، دوران سريع، مناسب لفترة الصباح."),
]
cw, ch = 240, 130
gx, gy = 22, 22
x0, y0 = MARG_X, 180
for i, (num, h_ar, body) in enumerate(items):
    col = i % 3; row = i // 3
    x = x0 + col*(cw+gx); y = y0 + (1-row)*(ch+gy)
    labeled_card(x, y, cw, ch, num, "", h_ar, body)

footer("SECTION 01 · CONCEPT", 4)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 05 — CONCEPT · WHAT IT IS NOT (dark)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
header("01", "Concept · What it is not", "ما لا يكون", 5, dark=True)
kicker("Discipline by exclusion", MARG_X, H - 115, color=YOLK)
title("What", MARG_X, H - 160, 36, CREAM)
title("OMLT is not.", MARG_X, H - 200, 36, CREAM, italic_word="not")
rule_tiny(MARG_X, H - 220, color=YOLK)
ar_wrap("قوة المشروع تأتي من حدوده الواضحة. هذه القائمة تحمي الفكرة من التمدّد وتُبقي التشغيل بسيطًا.",
        MARG_X, H - 250, 340, size=10, color=HexColor("#C8BFA3"), leading=15, align="left")

# right list
nots = [
    ("Not brunch",         "ليس مطعم برانش"),
    ("Not a café",         "ليس مقهى تقليديًّا"),
    ("Not all-day dining", "ليس مطعمًا طوال اليوم"),
    ("Not luxury",         "ليست تجربة فاخرة مبالغة"),
    ("Not a long menu",    "ليست قائمة كبيرة متعدّدة"),
]
tx = 440; ty = H - 130
for i, (en, arr) in enumerate(nots):
    yy = ty - i*48
    c.setFillColor(YOLK); c.setFont("Display-B", 22); c.drawString(tx, yy, "×")
    c.setFillColor(CREAM); c.setFont("Display-B", 20); c.drawString(tx+30, yy, en)
    c.setFillColor(HexColor("#C8BFA3")); c.setFont("Body", 11); c.drawString(tx+30, yy-18, ar(arr))
    line(tx, yy-26, W - MARG_X, yy-26, color=WHISP, width=0.4)

footer("SECTION 01 · CONCEPT", 5, dark=True)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 06 — OPEN KITCHEN
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("01", "Concept · The open kitchen", "المطبخ المفتوح", 6)
kicker("Heart of the experience", MARG_X, H - 115)
title("The open", MARG_X, H - 160, 30, NAVY)
title("kitchen is", MARG_X, H - 195, 30, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 30); c.drawString(MARG_X, H - 230, "the show.")
rule_tiny(MARG_X, H - 250)
ar_wrap("المطبخ المفتوح ليس عنصر تصميم — بل مركز التجربة اليومية. يظهر مباشرة عند الدخول، فيُشاهد العميل التحضير والطهي والتشغيل، وتصبح حركة العمل جزءًا من الهوية.",
        MARG_X, H - 280, 380, size=10.5, color=INK, leading=17, align="left")

# 4 cards 2x2 right
items = [
    ("SOUND", "صوت البيض وحركة المقلاة", "إيقاع طبيعي من المطبخ يحلّ محل الموسيقى."),
    ("SIGHT", "تحضير الأومليت أمام العميل", "كل أومليت يُصنع في الصالة، لا خلف ستار."),
    ("SMELL", "رائحة الخبز والقهوة", "الروائح تأتي من المطبخ — بدون معطّرات."),
    ("TIME",  "التشغيل ظاهر للعميل", "الإيقاع الصباحي مفتوح طوال الزيارة."),
]
cw, ch = 165, 130
gx, gy = 16, 16
x0, y0 = 480, 150
for i, (num, h_ar, body) in enumerate(items):
    col = i % 2; row = i // 2
    x = x0 + col*(cw+gx); y = y0 + (1-row)*(ch+gy)
    labeled_card(x, y, cw, ch, num, "", h_ar, body)

footer("SECTION 01 · CONCEPT", 6)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 07 — CONCEPT · LOCATION & SPACE  (new)
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("01", "Concept · Location & Space", "الموقع والفراغ", 7)
kicker("Where the morning lives", MARG_X, H - 115)
title("A street, a", MARG_X, H - 160, 30, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 30); c.drawString(MARG_X, H - 195, "sunrise,")
title("a room that breathes.", MARG_X, H - 230, 30, NAVY)
rule_tiny(MARG_X, H - 250)
ar_wrap("الموقع ليس مجرّد عنوان — هو جزء من تجربة OMLT. الاتجاه، الحيّ، وحجم الفراغ كلها قرارات تخدم الإيقاع الصباحي وشعور المكان.",
        MARG_X, H - 280, 440, size=10.5, color=INK, leading=17, align="left")

# 3 cards
items_loc = [
    ("01 · ORIENTATION", "اتجاه شرقي",
     "تفضيل الموقع المُتجه شرقًا قدر الإمكان — ضوء الصباح الطبيعي جزء من تجربة OMLT، يدعم هدوء الجو الصباحي."),
    ("02 · NEIGHBORHOOD", "حيّ نابض بالحياة",
     "شارع حيوي ومأهول في أبها — لا منعزل، لا مخفي. ظاهر للناس وضمن إيقاع يومهم الطبيعي."),
    ("03 · FOOTPRINT", "٨ – ١٠ طاولات",
     "فراغ يستوعب ٨–١٠ طاولات بمسافات مريحة — صغير ليبقى شخصيًّا، كبير ليبقى حيًّا."),
]
cw, ch = 240, 150
gx = 22
y0 = 100
for i, (num, h_ar, body) in enumerate(items_loc):
    x = MARG_X + i*(cw+gx)
    labeled_card(x, y0, cw, ch, num, "", h_ar, body)

# bottom band — the feeling
card(MARG_X, 50, W - 2*MARG_X, 36, fill=CREAM, stroke=HAIR)
text_l("THE FEELING WE TEST FOR", MARG_X+14, 70, "Mono-B", 9, TERRA)
c.setFillColor(NAVY); c.setFont("Display-I", 13); c.drawString(MARG_X+220, 70, "Small enough to feel personal, large enough to feel alive.")
c.setFillColor(GRAY); c.setFont("Body", 10); c.drawRightString(W - MARG_X - 14, 70, ar("صغير ليُحسّ، كبير ليحيا."))

footer("SECTION 01 · CONCEPT", 7)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 08 — VISION · MORNING ROUTINE (terra)
# ═══════════════════════════════════════════════════════
page_bg(TERRA)
header("02", "Vision · Become part of the morning", "جزء من الصباح", 8, dark=True)
kicker("Vision", MARG_X, H - 115, color=YOLK)
title("Become part", MARG_X, H - 170, 36, CREAM)
title("of their", MARG_X, H - 210, 36, CREAM)
c.setFillColor(YOLK); c.setFont("Display-I", 36); c.drawString(MARG_X, H - 250, "morning.")
rule_tiny(MARG_X, H - 270, color=YOLK)
ar_wrap("نهدف إلى صناعة مكان يعود إليه العميل ضمن روتينه الصباحي — لا يأتي مرّة واحدة، بل يجعله جزءًا من أيّامه. النجاح يُقاس بالعودة المتكرّرة، لا بعدد الزيارات الأولى.",
        MARG_X, H - 300, 360, size=10.5, color=CREAM, leading=17, align="left")

# right cards
card(440, 240, 340, 180, fill=HexColor("#A03622"), stroke=HexColor("#E0B79E"))
text_l("CORE PURPOSE", 460, 400, "Mono-B", 9, YOLK)
title("A reliable habit,", 460, 370, 16, CREAM)
title("not a spectacle.", 460, 345, 16, CREAM)
ar_wrap("OMLT يُقدّم وجبة فطور بسيطة ومُتقَنة، في مكان واضح ومألوف، بإيقاع صباحي ثابت. الهدف ليس الإثارة، بل بناء عادة يومية.",
        460, 320, 300, size=9.5, color=CREAM, leading=14, align="left")

card(440, 130, 165, 90, fill=HexColor("#A03622"), stroke=HexColor("#E0B79E"))
text_l("MEASURE", 458, 190, "Mono-B", 8, YOLK)
title("Return rate", 458, 160, 16, CREAM)
card(615, 130, 165, 90, fill=HexColor("#A03622"), stroke=HexColor("#E0B79E"))
text_l("IGNORE", 633, 190, "Mono-B", 8, YOLK)
title("First visits", 633, 160, 16, CREAM)

footer("SECTION 02 · VISION", 8, dark=True)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 09 — PRINCIPLES
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("02", "Vision · Operational principles", "المبادئ التشغيلية", 9)
kicker("Four principles, daily", MARG_X, H - 115)
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(MARG_X, H - 150, "أربعة مبادئ تحكم كل قرار في OMLT.")
c.setFillColor(NAVY); c.setFont("Body-Bold", 20); c.drawString(MARG_X, H - 150, ar("أربعة مبادئ تحكم كل قرار في OMLT."))

princ = [
    ("01", "Plain done well",  "البساطة في التنفيذ — نُتقن قائمة محدودة بدلًا من توسيع المنيو."),
    ("02", "Clear by design",  "الوضوح في التجربة — كل قرار يخدم سهولة الزيارة من الدخول للمغادرة."),
    ("03", "Steady quality",   "ثبات الجودة — نفس الإيقاع والجودة كل صباح، طوال أيام العمل."),
    ("04", "Build the habit",  "بناء العادة — كل قرار يُختبر: هل يدعم عودة العميل؟"),
]
cw, ch = 175, 200
gx = 18
y0 = 170
for i, (num, h, body) in enumerate(princ):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#FFFFFF"), stroke=HAIR)
    # circle number
    c.setFillColor(TERRA); c.circle(x+24, y0+ch-24, 14, fill=1, stroke=0)
    c.setFillColor(CREAM); c.setFont("Mono-B", 10); c.drawCentredString(x+24, y0+ch-28, num)
    # heading
    title(h, x+14, y0+ch-66, 14, NAVY)
    line(x+14, y0+ch-78, x+cw-14, y0+ch-78, color=TERRA, width=1)
    ar_wrap(body, x+14, y0+ch-100, cw-28, size=9.5, color=GRAY, leading=14, align="left")

footer("SECTION 02 · VISION", 9)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 10 — EXPANSION ROADMAP
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("02", "Vision · Realistic expansion", "خطة التوسّع", 10)
kicker("A three-phase path", MARG_X, H - 115)
c.setFillColor(NAVY); c.setFont("Body-Bold", 20); c.drawString(MARG_X, H - 152, ar("نموذج واحد يُثبت أولًا، ثم يُدرَس التوسّع."))

phases = [
    (TERRA, "01", "Phase one",   "إثبات الفكرة",  ["افتتاح الفرع الأول", "بناء قاعدة عملاء أساسية", "تحسين التشغيل اليومي", "إثبات نجاح الفكرة"]),
    (NAVY,  "02", "Phase two",   "توثيق وتطوير",  ["توثيق الوصفات قياسيًا", "تطوير إجراءات موحّدة", "تحسين التجربة", "استقرار مالي للفرع الأول"]),
    (YOLK,  "03", "Phase three", "دراسة التوسّع", ["دراسة فرع ثانٍ", "تقييم الموقع بالبيانات", "نفس النموذج والهوية"]),
]
cw, ch = 240, 250
gx = 22
y0 = 130
for i, (cc, num, ph_en, ph_ar, items) in enumerate(phases):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#FFFFFF"), stroke=HAIR)
    c.setFillColor(cc); c.circle(x+30, y0+ch-30, 16, fill=1, stroke=0)
    c.setFillColor(CREAM if cc != YOLK else NAVY); c.setFont("Mono-B", 11); c.drawCentredString(x+30, y0+ch-34, num)
    text_l(ph_en.upper(), x+56, y0+ch-32, "Mono-B", 9, TERRA)
    title(ph_ar, x+14, y0+ch-70, 14, NAVY)
    c.setFillColor(NAVY); c.setFont("Body-Bold", 14); c.drawString(x+14, y0+ch-72, ar(ph_ar))
    line(x+14, y0+ch-88, x+cw-14, y0+ch-88, color=TERRA, width=0.8)
    for j, b in enumerate(items):
        c.setFillColor(TERRA); c.setFont("Mono-B", 9); c.drawString(x+14, y0+ch-110-j*22, "·")
        c.setFillColor(NAVY); c.setFont("Body", 10); c.drawString(x+24, y0+ch-110-j*22, ar(b))

footer("SECTION 02 · VISION", 10)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 11 — STARTUP COSTS TABLE
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("03", "Business Setup · Startup costs", "التكاليف الأولية", 11)
kicker("Capital required", MARG_X, H - 115)
title("Setup budget,", MARG_X, H - 160, 28, NAVY)
title("itemised.", MARG_X, H - 195, 28, NAVY, italic_word="itemised.")
rule_tiny(MARG_X, H - 215)
ar_wrap("الأرقام تقديرية لنموذج تشغيلي صغير — مساحة محدودة، ٨–١٠ طاولات، فريق مختصر.",
        MARG_X, H - 245, 320, size=10, color=GRAY, leading=15, align="left")

# table
rows = [
    ("Interior · تهيئة وتجهيز",            "Build-out · joinery · lighting",                        "120,000 – 180,000"),
    ("Equipment · معدّات المطبخ",          "Induction · pans · refrigeration · ventilation · POS", "70,000 – 100,000"),
    ("Furniture · أثاث وطاولات",           "Tables · chairs · ceramics",                            "30,000 – 50,000"),
    ("Branding · هوية وطباعة",             "Print · signage · kits",                                "20,000 – 30,000"),
    ("Licensing · تراخيص وتأسيس",          "CR · municipality · health · setup",                    "20,000 – 35,000"),
    ("Working capital · سيولة تشغيل",      "First months runway",                                   "70,000 – 100,000"),
]
tx = 380; ty = H - 110; rh = 38
# header
text_l("ITEM · البند",   tx,        ty, "Mono-B", 9, TERRA)
text_l("DETAIL",         tx + 200,  ty, "Mono-B", 9, TERRA)
text_r("SAR",            W - MARG_X, ty, "Mono-B", 9, TERRA)
line(tx, ty - 12, W - MARG_X, ty - 12, color=HAIR, width=0.6)
for i, (a, b, sar) in enumerate(rows):
    yy = ty - 30 - i*rh
    # left: english on top, arabic below
    en_part = a.split(" · ")[0]
    ar_part = a.split(" · ")[1] if " · " in a else ""
    text_l(en_part, tx, yy+6, "Display-B", 11, NAVY)
    c.setFillColor(GRAY); c.setFont("Body", 9); c.drawString(tx, yy-8, ar(ar_part))
    text_l(b, tx + 200, yy, "Body", 9.5, GRAY)
    text_r(sar, W - MARG_X, yy, "Mono-B", 11, NAVY)
    line(tx, yy - 16, W - MARG_X, yy - 16, color=HAIR, width=0.3)
# total
yy = ty - 30 - len(rows)*rh - 6
c.setStrokeColor(NAVY); c.setLineWidth(1.2); c.line(tx, yy+18, W - MARG_X, yy+18)
text_l("TOTAL · الإجمالي المتوقّع", tx, yy, "Mono-B", 11, TERRA)
text_r("330,000 – 495,000", W - MARG_X, yy, "Mono-B", 13, TERRA)

footer("SECTION 03 · COSTS", 11)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 12 — LAUNCH BUDGET SUMMARY (dark)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
header("03", "Business Setup · Launch budget", "ميزانية الإطلاق", 12, dark=True)
kicker("Expected launch budget", MARG_X, H - 115, color=YOLK)
title("330K", MARG_X, H - 175, 60, CREAM)
c.setFillColor(YOLK); c.setFont("Display-I", 60); c.drawString(MARG_X + 130, H - 175, "—")
title("495K", MARG_X + 200, H - 175, 60, CREAM)
text_l("ريال سعودي · SAR", MARG_X, H - 210, "Mono", 11, HexColor("#C8BFA3"))

# 4 cards
items = [
    ("Interior",  "36%", "تهيئة، تشطيب، إضاءة، تنفيذ المطبخ المفتوح."),
    ("Equipment", "30%", "معدّات الطبخ والتبريد والقهوة وأدوات التشغيل."),
    ("Branding",  "6%",  "الهوية، الطباعة، اللافتات، التغليف الأساسي."),
    ("Reserves",  "14%", "سيولة التشغيل لأوّل أشهر — احتياط أمان."),
]
cw, ch = 175, 140
gx = 18
y0 = 110
for i, (label, pct, body) in enumerate(items):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#252C44"), stroke=WHISP)
    text_l(label.upper(), x+14, y0+ch-22, "Mono-B", 9, YOLK)
    title(pct, x+14, y0+ch-58, 26, CREAM)
    ar_wrap(body, x+14, y0+ch-82, cw-28, size=9, color=HexColor("#C8BFA3"), leading=13, align="left")

# note bar
card(MARG_X, 60, W - 2*MARG_X, 40, fill=HexColor("#252C44"), stroke=WHISP)
c.setFillColor(HexColor("#C8BFA3")); c.setFont("Body", 9.5)
c.drawString(MARG_X+14, 80, "* الأرقام تقديرية لمرحلة التأسيس. الأثاث والتراخيص يدخلان ضمن نسبة مشتركة 14% من إجمالي الميزانية.")

footer("SECTION 03 · COSTS", 12, dark=True)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 13 — STAFFING PLAN
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("03", "Business Setup · Staffing plan", "فريق التشغيل", 13)
kicker("A small, focused team", MARG_X, H - 115)
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(MARG_X, H - 150, "ستّة أدوار،")
c.setFillColor(TERRA); c.setFont("Display-I", 22); c.drawString(MARG_X + 110, H - 150, "فريقٌ")
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(MARG_X + 175, H - 150, "صغير ودقيق.")
ar_wrap("فريق مناسب لمساحة ٨–١٠ طاولات وساعات تشغيل صباحية فقط (٧:٠٠ ص – ٣:٠٠ م).",
        MARG_X, H - 180, 460, size=10, color=GRAY, leading=15, align="left")

roles = [
    ("01", "Head Chef",          "شيف رئيسي",          "مسؤول عن الجودة والإشراف والتشغيل اليومي للمطبخ."),
    ("02", "Kitchen Assistant",  "مساعد مطبخ",         "التجهيز والتحضير ودعم التشغيل في وقت الذروة."),
    ("03", "Beverage Specialist","مسؤول مشروبات",      "تحضير القهوة والشاي والمشروبات الصباحية."),
    ("04", "Service Staff",      "موظّف خدمة",         "الاستقبال، تقديم الطلبات، متابعة الطاولات."),
    ("05", "Cashier",            "كاشير",              "نقاط البيع، التقفيل، الجرد، طلبات التوريد."),
    ("06", "Cleaning & Support", "نظافة ومساندة",      "نظافة الصالة والمطبخ ودعم تشغيلي عام."),
]
cw, ch = 240, 100
gx, gy = 22, 18
x0, y0 = MARG_X, 80
for i, (num, en, arr, body) in enumerate(roles):
    col = i % 3; row = i // 3
    x = x0 + col*(cw+gx); y = y0 + (1-row)*(ch+gy)
    card(x, y, cw, ch, fill=HexColor("#FFFFFF"), stroke=HAIR)
    text_l(num, x+14, y+ch-22, "Mono-B", 9, TERRA)
    text_l(en, x+40, y+ch-22, "Display-B", 12, NAVY)
    c.setFillColor(NAVY); c.setFont("Body-Bold", 11); c.drawString(x+14, y+ch-42, ar(arr))
    ar_wrap(body, x+14, y+ch-58, cw-28, size=9, color=GRAY, leading=13, align="left")

footer("SECTION 03 · COSTS", 13)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 14 — ESTIMATED SALARIES
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("03", "Business Setup · Estimated salaries", "الرواتب الشهرية", 14)
kicker("Monthly payroll", MARG_X, H - 115)
title("A lean", MARG_X, H - 160, 28, NAVY)
title("monthly", MARG_X, H - 195, 28, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 28); c.drawString(MARG_X, H - 230, "payroll.")
rule_tiny(MARG_X, H - 250)
ar_wrap("الأرقام شاملة لكل بنود التوظيف، مبنية على ساعات تشغيل صباحية فقط (٧:٠٠ – ٣:٠٠).",
        MARG_X, H - 280, 320, size=10, color=GRAY, leading=15, align="left")

# table right
salaries = [
    ("شيف رئيسي",       "Head Chef",          "5,500 – 6,500"),
    ("مساعد مطبخ",      "Kitchen Assistant",  "2,500 – 3,500"),
    ("مسؤول مشروبات",  "Beverage Specialist","2,500 – 3,000"),
    ("موظّف خدمة",      "Service Staff",      "2,500 – 3,000"),
    ("كاشير",           "Cashier",            "3,000 – 3,500"),
    ("نظافة ومساندة",   "Cleaning & Support", "1,800 – 2,200"),
]
tx = 380; ty = H - 110; rh = 36
text_l("الوظيفة · ROLE",   tx,        ty, "Mono-B", 9, TERRA)
text_l("ENGLISH",          tx + 160,  ty, "Mono-B", 9, TERRA)
text_r("SAR / month",      W - MARG_X, ty, "Mono-B", 9, TERRA)
line(tx, ty - 12, W - MARG_X, ty - 12, color=HAIR, width=0.6)
for i, (a, b, s) in enumerate(salaries):
    yy = ty - 30 - i*rh
    c.setFillColor(NAVY); c.setFont("Body-Bold", 12); c.drawString(tx, yy, ar(a))
    c.setFillColor(GRAY); c.setFont("Display-I", 11); c.drawString(tx + 160, yy, b)
    text_r(s, W - MARG_X, yy, "Mono-B", 11, NAVY)
    line(tx, yy - 12, W - MARG_X, yy - 12, color=HAIR, width=0.3)
yy = ty - 30 - len(salaries)*rh
c.setStrokeColor(NAVY); c.setLineWidth(1.2); c.line(tx, yy+18, W - MARG_X, yy+18)
text_l("Total monthly payroll · إجمالي", tx, yy, "Mono-B", 11, TERRA)
text_r("17,800 – 21,700", W - MARG_X, yy, "Mono-B", 13, TERRA)

footer("SECTION 03 · COSTS", 14)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 15 — REVENUE MODEL
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("03", "Business Setup · Revenue model", "نموذج الإيرادات", 15)
kicker("Realistic financial targets", MARG_X, H - 115)
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(MARG_X, H - 155, "Revenue grounded in")
c.setFillColor(TERRA); c.setFont("Display-I", 22); c.drawString(MARG_X+250, H - 155, "stability.")

metrics = [
    ("Avg ticket",    "35–55",        "SAR / guest"),
    ("Daily guests",  "50–80",        "covers / day"),
    ("Operating",     "6 / wk",       "days per week"),
    ("Hours",         "07–15",        "morning shift"),
]
cw, ch = 175, 130
gx = 18
y0 = 220
for i, (label, val, sub) in enumerate(metrics):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#FFFFFF"), stroke=HAIR)
    text_l(label.upper(), x+14, y0+ch-22, "Mono-B", 9, TERRA)
    title(val, x+14, y0+ch-72, 32, NAVY)
    text_l(sub, x+14, y0+ch-100, "Mono", 9, GRAY)

# principles
items = [
    ("P1", "الهدف عملاء متكرّرون", "قاعدة عملاء مخلصين قبل ملاحقة الإيرادات."),
    ("P2", "قائمة مختصرة",          "تحكّم بتكاليف المواد والإنتاج."),
    ("P3", "فريق مختصر",            "رواتب أقل، تشغيل أبسط."),
]
y1 = 90
for i, (num, h, body) in enumerate(items):
    x = MARG_X + i*(240+22)
    card(x, y1, 240, 100, fill=HexColor("#FFFFFF"), stroke=HAIR)
    text_l(num, x+14, y1+80, "Mono-B", 9, TERRA)
    c.setFillColor(NAVY); c.setFont("Body-Bold", 12); c.drawString(x+40, y1+80, ar(h))
    ar_wrap(body, x+14, y1+60, 240-28, size=9.5, color=GRAY, leading=13, align="left")

footer("SECTION 03 · COSTS", 15)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 16 — LOGO HERO (dark)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
header("04", "Approved Logo · The mark", "الشعار المعتمد", 16, dark=True)

# stage card — larger, more presence
stage_x, stage_y, stage_w, stage_h = 70, 80, 380, 400
card(stage_x, stage_y, stage_w, stage_h, fill=HexColor("#0F1422"), stroke=WHISP)
# inner borders for editorial framing
c.setStrokeColor(HexColor("#3A4055")); c.setLineWidth(0.6)
c.roundRect(stage_x+20, stage_y+20, stage_w-40, stage_h-40, 6, fill=0, stroke=1)
c.saveState(); c.setStrokeColor(HexColor("#3A4055")); c.setLineWidth(0.3); c.setDash(2, 3)
c.roundRect(stage_x+40, stage_y+40, stage_w-80, stage_h-80, 4, fill=0, stroke=1)
c.restoreState()
# logo centered in stage
logo_size = 270
c.drawImage(LOGO, stage_x + (stage_w-logo_size)/2, stage_y + (stage_h-logo_size)/2,
            width=logo_size, height=logo_size, mask='auto')

# text right — more breathing room
tx = 490
kicker("Direction C · Final · Approved", tx, H - 155, color=YOLK)
title("The badge.", tx, H - 205, 38, CREAM)
c.setFillColor(YOLK); c.setFont("Display-I", 38); c.drawString(tx, H - 250, "One mark,")
title("every surface.", tx, H - 295, 38, CREAM)
rule_tiny(tx, H - 320, color=YOLK)
ar_wrap("شارة دائرية تحوي رمز البيضة في المنتصف، نصًّا مُقوَّسًا حول الأعلى، واسم العلامة OMLT في الأسفل. اعتُمدت رسميًّا كهوية وحيدة للمشروع.",
        tx, H - 350, 290, size=10.5, color=HexColor("#C8BFA3"), leading=17, align="left")

text_l("FILE", tx, 130, "Mono-B", 9, YOLK)
text_l("OMLT-Logo-Layered-HiRes", tx, 112, "Mono", 10, CREAM)
text_l("STATUS", tx+170, 130, "Mono-B", 9, YOLK)
text_l("APPROVED · FINAL", tx+170, 112, "Mono", 10, CREAM)

footer("SECTION 04 · LOGO", 16, dark=True)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 17 — LOGO ANATOMY
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("04", "Approved Logo · Anatomy", "تشريح الشعار", 17)

# left stage (cream)
card(60, 90, 360, 380, fill=CREAM, stroke=HAIR)
c.drawImage(LOGO, 100, 130, width=280, height=280, mask='auto')

# annotations
def anno(x, y, label, num):
    card(x, y, 116, 22, fill=HexColor("#FFFFFF"), stroke=HAIR, radius=11)
    text_l(num, x+10, y+7, "Mono-B", 8, TERRA)
    text_l(label, x+30, y+7, "Mono", 8, NAVY)

anno(70, 430, "Frame", "01")
anno(330, 430, "Arc text", "02")
anno(60, 260, "Yolk #E6A532", "04")
anno(340, 260, "Egg shape", "03")
anno(80, 130, "Anchor", "06")
anno(290, 130, "Wordmark", "05")

# right text
tx = 460
kicker("Composition", tx, H - 165)
title("Six layers,", tx, H - 210, 30, NAVY)
title("one signal.", tx, H - 245, 30, NAVY, italic_word="signal.")
rule_tiny(tx, H - 265)

anatomy = [
    ("01 · FRAME",    "دائرة معبّأة قرميدية بحدّ كحلي."),
    ("02 · ARC",      "نص مُقوَّس Space Grotesk حول الأعلى."),
    ("03 · EGG",      "بيضة عضوية كريمية بحدّ كحلي."),
    ("04 · YOLK",     "صفار #E6A532 — نقطة التركيز."),
    ("05 · WORDMARK", "OMLT — Frank Ruhl Libre 900، كريمي."),
    ("06 · ANCHOR",   "زخرفة رفيعة مع نقطة صفراء صغيرة."),
]
for i, (label, body) in enumerate(anatomy):
    yy = H - 295 - i*30
    text_l(label, tx, yy, "Mono-B", 9, TERRA)
    c.setFillColor(NAVY); c.setFont("Body", 10); c.drawString(tx, yy-14, ar(body))
    line(tx, yy-22, W - MARG_X, yy-22, color=HAIR, width=0.3)

footer("SECTION 04 · LOGO", 17)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 18 — LOGO USAGE — VISUAL DO / DON'T
# ═══════════════════════════════════════════════════════
page_bg(CREAM)
header("04", "Approved Logo · Usage rules", "قواعد الاستخدام", 18)
kicker("Do · Don't", MARG_X, H - 115)
c.setFillColor(NAVY); c.setFont("Display-B", 26); c.drawString(MARG_X, H - 155, "A logo doesn't")
c.setFillColor(TERRA); c.setFont("Display-I", 26); c.drawString(MARG_X + 200, H - 155, "negotiate.")

# row layout
cw, ch = 175, 145
gx = 16
rx0 = MARG_X

# DO row
text_l("✓  CORRECT USAGE", MARG_X, H - 190, "Mono-B", 10, HERB)
y_do = H - 360
labels_do = [
    ("CLEAR SPACE",      "مساحة آمنة محفوظة"),
    ("APPROVED BG",      "خلفية معتمدة"),
    ("MIN SIZE 32mm",    "الحجم الأدنى"),
    ("COMPLETE",         "كاملًا في مكانه"),
]
for i in range(4):
    x = rx0 + i*(cw+gx)
    # outer card
    c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(HAIR); c.setLineWidth(0.5)
    c.roundRect(x, y_do, cw, ch, 8, fill=1, stroke=1)
    # demo box
    demo_h = 92
    if i == 0:
        # clear space — dashed terra outline + logo
        c.setFillColor(CREAM); c.rect(x+8, y_do+ch-demo_h-2, cw-16, demo_h, fill=1, stroke=0)
        c.saveState()
        c.setStrokeColor(HexColor("#C8442C")); c.setLineWidth(0.8); c.setDash(3, 3)
        c.rect(x+20, y_do+ch-demo_h+10, cw-44, demo_h-22, fill=0, stroke=1)
        c.restoreState()
        c.drawImage(LOGO, x+44, y_do+ch-demo_h+20, width=cw-88, height=demo_h-40, mask='auto', preserveAspectRatio=True)
    elif i == 1:
        # approved navy bg
        c.setFillColor(NAVY); c.rect(x+8, y_do+ch-demo_h-2, cw-16, demo_h, fill=1, stroke=0)
        c.drawImage(LOGO, x+38, y_do+ch-demo_h+8, width=cw-76, height=demo_h-16, mask='auto', preserveAspectRatio=True)
    elif i == 2:
        # min size — three logos in scale
        c.setFillColor(CREAM); c.rect(x+8, y_do+ch-demo_h-2, cw-16, demo_h, fill=1, stroke=0)
        c.drawImage(LOGO, x+18, y_do+ch-demo_h+18, width=56, height=56, mask='auto')
        c.drawImage(LOGO, x+82, y_do+ch-demo_h+22, width=42, height=42, mask='auto')
        c.drawImage(LOGO, x+132, y_do+ch-demo_h+28, width=30, height=30, mask='auto')
    else:
        # complete & centered
        c.setFillColor(CREAM); c.rect(x+8, y_do+ch-demo_h-2, cw-16, demo_h, fill=1, stroke=0)
        c.drawImage(LOGO, x+38, y_do+ch-demo_h+8, width=cw-76, height=demo_h-16, mask='auto', preserveAspectRatio=True)
    # caption
    line(x+10, y_do+30, x+cw-10, y_do+30, color=HAIR, width=0.4)
    c.setFillColor(HERB); c.setFont("Mono-B", 11); c.drawString(x+12, y_do+14, "✓")
    text_l(labels_do[i][0], x+28, y_do+18, "Mono-B", 8, NAVY)
    c.setFillColor(GRAY); c.setFont("Body", 8.5); c.drawString(x+28, y_do+6, ar(labels_do[i][1]))

# DON'T row
text_l("✕  NEVER DO", MARG_X, H - 385, "Mono-B", 10, DEEP)
y_no = 70
labels_no = [
    ("STRETCH / SQUASH",  "تمديد أو ضغط"),
    ("ROTATION",          "إمالة أو دوران"),
    ("COLOR MODIFICATION","تعديل الألوان"),
    ("OFF-PALETTE BG",    "خلفية خارج اللوحة"),
]
for i in range(4):
    x = rx0 + i*(cw+gx)
    c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(HAIR); c.setLineWidth(0.5)
    c.roundRect(x, y_no, cw, ch, 8, fill=1, stroke=1)
    demo_h = 92
    bx, by, bw, bh = x+8, y_no+ch-demo_h-2, cw-16, demo_h
    if i == 0:
        # stretched
        c.setFillColor(CREAM); c.rect(bx, by, bw, bh, fill=1, stroke=0)
        c.drawImage(LOGO, bx+10, by+24, width=bw-20, height=bh-50, mask='auto', preserveAspectRatio=False)
    elif i == 1:
        # rotated
        c.setFillColor(CREAM); c.rect(bx, by, bw, bh, fill=1, stroke=0)
        c.saveState()
        c.translate(bx+bw/2, by+bh/2); c.rotate(-18)
        c.drawImage(LOGO, -34, -34, width=68, height=68, mask='auto')
        c.restoreState()
    elif i == 2:
        # color modification — overlay a wrong color box
        c.setFillColor(CREAM); c.rect(bx, by, bw, bh, fill=1, stroke=0)
        c.drawImage(LOGO, bx+38, by+8, width=bw-76, height=bh-16, mask='auto', preserveAspectRatio=True)
        c.setFillColor(HexColor("#7BA284")); c.setStrokeColor(HexColor("#7BA284"))
        # green tint overlay illustrating "wrong color" demo
        c.saveState()
        c.setFillAlpha(0.45)
        c.circle(bx+bw/2, by+bh/2, min(bw, bh)/2.4, fill=1, stroke=0)
        c.restoreState()
    else:
        # off-palette gradient bg
        # approximate gradient with three bands
        c.setFillColor(HexColor("#7BA284")); c.rect(bx, by, bw/3, bh, fill=1, stroke=0)
        c.setFillColor(HexColor("#E6A532")); c.rect(bx+bw/3, by, bw/3, bh, fill=1, stroke=0)
        c.setFillColor(HexColor("#9C3520")); c.rect(bx+2*bw/3, by, bw/3+1, bh, fill=1, stroke=0)
        c.drawImage(LOGO, bx+38, by+8, width=bw-76, height=bh-16, mask='auto', preserveAspectRatio=True)
    # caption
    line(x+10, y_no+30, x+cw-10, y_no+30, color=HAIR, width=0.4)
    c.setFillColor(DEEP); c.setFont("Mono-B", 11); c.drawString(x+12, y_no+14, "✕")
    text_l(labels_no[i][0], x+28, y_no+18, "Mono-B", 8, NAVY)
    c.setFillColor(GRAY); c.setFont("Body", 8.5); c.drawString(x+28, y_no+6, ar(labels_no[i][1]))

footer("SECTION 04 · LOGO", 18)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 19 — COLORS PALETTE
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("05", "Brand Colors · Palette", "لوحة الألوان", 19)
kicker("Six colors, fixed ratios", MARG_X, H - 115)
title("Six colors.", MARG_X, H - 160, 30, NAVY)
title("Locked ratios.", MARG_X, H - 195, 30, NAVY, italic_word="ratios.")

palette = [
    ("Terracotta", "قرميدي", "#C8442C", "50%", TERRA, CREAM),
    ("Cream",      "كريمي",  "#F6ECD6", "25%", CREAM, NAVY),
    ("Navy",       "كحلي",   "#1B2235", "12%", NAVY, CREAM),
    ("Yolk",       "صفار",   "#E6A532", "8%",  YOLK, NAVY),
    ("Herb",       "عشبي",   "#7BA284", "3%",  HERB, CREAM),
    ("Deep",       "عميق",   "#9C3520", "2%",  DEEP, CREAM),
]
sw_w, sw_h = 117, 200
sw_gx = 14
sx0 = MARG_X; sy0 = 90
for i, (nm, arr, hx, pct, bg, fg) in enumerate(palette):
    x = sx0 + i*(sw_w + sw_gx); y = sy0
    c.setFillColor(bg); c.setStrokeColor(HAIR); c.setLineWidth(0.4)
    c.roundRect(x, y, sw_w, sw_h, 8, fill=1, stroke=1)
    text_l(hx, x+12, y+sw_h-22, "Mono", 8, fg)
    text_l(nm, x+12, y+sw_h-42, "Display-B", 14, fg)
    c.setFillColor(fg); c.setFont("Body-Bold", 10); c.drawString(x+12, y+sw_h-58, ar(arr))
    text_l(pct, x+12, y+14, "Mono-B", 22, fg)

# proportion bar
bar_y = sy0 + sw_h + 20
total = sum([50, 25, 12, 8, 3, 2])
xb = MARG_X
for pct, col in zip([50, 25, 12, 8, 3, 2], [TERRA, CREAM, NAVY, YOLK, HERB, DEEP]):
    seg_w = (W - 2*MARG_X) * pct / total
    c.setFillColor(col); c.setStrokeColor(HAIR); c.setLineWidth(0.4)
    c.rect(xb, bar_y, seg_w, 14, fill=1, stroke=1)
    xb += seg_w

footer("SECTION 05 · COLORS", 19)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 20 — YOLK RULE
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("05", "Brand Colors · The yolk rule", "قاعدة الصفار", 20)
kicker("One yolk per design", MARG_X, H - 115)
title("One drop of", MARG_X, H - 165, 30, NAVY)
c.setFillColor(YOLK); c.setFont("Display-I", 36); c.drawString(MARG_X, H - 210, "yolk.")
title("Never a sea.", MARG_X, H - 250, 30, NAVY)
rule_tiny(MARG_X, H - 270)
ar_wrap("اللون الصفار يظهر لمسة واحدة فقط في كل تصميم — لا اثنتين، ولا يُستخدم كخلفية أبدًا. هذا ما يجعله توقيعًا، لا حشوًا.",
        MARG_X, H - 300, 360, size=11, color=INK, leading=17, align="left")
ar_wrap("النسب ثابتة في كل التطبيقات. زيادة لون عن نسبته المحدّدة تُخلّ بشخصية العلامة.",
        MARG_X, H - 370, 360, size=10, color=GRAY, leading=15, align="left")

# right two cards
card(440, 280, 340, 130, fill=CREAM, stroke=HAIR)
text_l("RIGHT  ✓  CORRECT", 460, 388, "Mono-B", 9, HERB)
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(460, 355, "A small")
c.setFillColor(YOLK); c.setFont("Display-B", 22); c.drawString(540, 355, "·")
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(555, 355, "bright")
c.setFillColor(NAVY); c.setFont("Display-B", 22); c.drawString(460, 330, "start to the day.")
c.setFillColor(GRAY); c.setFont("Body", 9.5); c.drawString(460, 305, ar("نقطة صفار واحدة فقط — توقيع."))

card(440, 130, 340, 130, fill=CREAM, stroke=HAIR)
text_l("WRONG  ✕  INCORRECT", 460, 238, "Mono-B", 9, DEEP)
c.setFillColor(YOLK); c.rect(460, 178, 280, 38, fill=1, stroke=0)
c.setFillColor(NAVY); c.setFont("Display-B", 18); c.drawString(470, 188, "Yolk used as a background.")
c.setFillColor(GRAY); c.setFont("Body", 9.5); c.drawString(460, 155, ar("الصفار خلفيةً يُفقده دوره كتوقيع."))

footer("SECTION 05 · COLORS", 20)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 21 — TYPE · FRANK RUHL LIBRE
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("06", "Typography · Frank Ruhl Libre", "الخط الأول", 21)
kicker("Display · Headlines", MARG_X, H - 115)
title("The serif that", MARG_X, H - 170, 28, NAVY)
title("speaks slow.", MARG_X, H - 205, 28, NAVY, italic_word="slow.")
rule_tiny(MARG_X, H - 225)
ar_wrap("يُستخدم Frank Ruhl Libre للعناوين الرئيسية، اسم العلامة، الجمل التحريرية، والاقتباسات. أوزانه المعتمدة: ٤٠٠، ٥٠٠، ٧٠٠، ٩٠٠.",
        MARG_X, H - 255, 360, size=11, color=INK, leading=17, align="left")

# specimen
tx = 460
c.setFillColor(NAVY); c.setFont("Display-B", 60); c.drawString(tx, H - 230, "Frank Ruhl")
c.setFillColor(TERRA); c.setFont("Display-I", 60); c.drawString(tx, H - 280, "Libre.")
c.setFillColor(GRAY); c.setFont("Body", 11); c.drawString(tx, H - 320, "A breakfast kitchen.")

# weight chips
weights = ["400 Regular", "500 Medium", "700 Bold", "900 Black"]
cy = 100; cx = MARG_X
for w_ in weights:
    width = c.stringWidth(w_, "Display-B", 10) + 16
    card(cx, cy, width, 24, fill=HexColor("#FFFFFF"), stroke=HAIR, radius=12)
    text_l(w_, cx+8, cy+8, "Display-B", 10, NAVY)
    cx += width + 8

footer("SECTION 06 · TYPE", 21)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 22 — TYPE · SPACE GROTESK & TAJAWAL
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("06", "Typography · Space Grotesk & Tajawal", "الخطان الثاني والثالث", 22)
kicker("UI · Body · Arabic", MARG_X, H - 115)
title("Two more workhorses.", MARG_X, H - 155, 22, NAVY)

# Specimen — Space Grotesk
text_l("SPACE GROTESK · LATIN · UI", MARG_X, H - 200, "Mono-B", 9, TERRA)
c.setFillColor(NAVY); c.setFont("Mono-B", 38); c.drawString(MARG_X, H - 250, "Mushroom omelette ·")
c.setFillColor(TERRA); c.setFont("Mono-B", 38); c.drawString(MARG_X, H - 295, "38 SAR")
ar_wrap("للنصوص الإنجليزية والقائمة والأرقام وواجهات الموقع. الأوزان: ٤٠٠، ٥٠٠، ٦٠٠، ٧٠٠.",
        MARG_X, H - 330, 360, size=10, color=GRAY, leading=14, align="left")

# Specimen — Tajawal
tx = 440
text_l("TAJAWAL · ARABIC · BODY", tx, H - 200, "Mono-B", 9, TERRA)
c.setFillColor(NAVY); c.setFont("Body-Bold", 32); c.drawString(tx, H - 250, ar("تجوال"))
c.setFillColor(NAVY); c.setFont("Body-Bold", 28); c.drawString(tx, H - 290, ar("مطبخ"))
c.setFillColor(TERRA); c.setFont("Body-Bold", 28); c.drawString(tx+90, H - 290, ar("فطور"))
c.setFillColor(NAVY); c.setFont("Body-Bold", 28); c.drawString(tx+180, H - 290, ar("صغير"))
ar_wrap("كل النصوص العربية بدون استثناء. أوزان: ٥٠٠ متن، ٧٠٠ تأكيد، ٩٠٠ عناوين. ارتفاع السطر ١.٨٥.",
        tx, H - 330, 320, size=10, color=GRAY, leading=14, align="left")

# rules bar
card(MARG_X, 90, W - 2*MARG_X, 50, fill=CREAM, stroke=HAIR)
text_l("GENERAL RULES", MARG_X+18, 122, "Mono-B", 9, TERRA)
c.setFillColor(NAVY); c.setFont("Body", 11)
c.drawRightString(W - MARG_X - 18, 118, ar("العربية أساس · الإنجليزية مساندة · لا italic للعربية · لا خط رابع"))

footer("SECTION 06 · TYPE", 22)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 23 — VISUAL IDENTITY · PERSONALITY
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("07", "Visual Identity · Personality", "شخصية العلامة", 23)
kicker("Brand personality", MARG_X, H - 115)
title("Warm · Clear · Brief ·", MARG_X, H - 155, 22, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 22); c.drawString(MARG_X+260, H - 155, "Signed.")

pers = [
    (TERRA, "W", "دافئة · Warm",   "ألوان طبيعية، إضاءة هادئة، إحساس بمكان مألوف — ليس رسميًّا."),
    (NAVY,  "C", "واضحة · Clear", "بدون مبالغات بصرية. كل عنصر له وظيفة وسبب وجود."),
    (YOLK,  "B", "مختصرة · Brief","لغة قصيرة، ثقة في فهم العميل دون شرح طويل."),
    (DEEP,  "S", "موقّعة · Signed","ظهور واحد للشارة في كل سطح — لا تكرار."),
]
cw, ch = 175, 200
gx = 18
y0 = 130
for i, (cc, lb, h_ar, body) in enumerate(pers):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#FFFFFF"), stroke=HAIR)
    c.setFillColor(cc); c.circle(x+24, y0+ch-24, 14, fill=1, stroke=0)
    c.setFillColor(CREAM if cc != YOLK else NAVY); c.setFont("Display-B", 12); c.drawCentredString(x+24, y0+ch-28, lb)
    c.setFillColor(NAVY); c.setFont("Body-Bold", 13); c.drawString(x+14, y0+ch-66, ar(h_ar))
    ar_wrap(body, x+14, y0+ch-90, cw-28, size=9.5, color=GRAY, leading=14, align="left")

card(MARG_X, 70, W - 2*MARG_X, 50, fill=CREAM, stroke=HAIR)
ar_wrap("الشعار ليس عنصرًا زخرفيًّا، بل جزء من تجربة المكان. يظهر في الواجهة، الكوب، القائمة، الإيصال. لا يُكرَّر بدون داعٍ، ولا يُستخدم كخلفية.",
        MARG_X+18, 102, W - 2*MARG_X - 36, size=10.5, color=NAVY, leading=15, align="left")

footer("SECTION 07 · VISUAL", 23)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 24 — SENSORY (dark)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
header("08", "Sensory Identity · Four senses", "الهوية الحسّية", 24, dark=True)
kicker("Four sensory gates", MARG_X, H - 115, color=YOLK)
title("Sight · Smell ·", MARG_X, H - 165, 30, CREAM)
title("Touch ·", MARG_X, H - 200, 30, CREAM)
c.setFillColor(YOLK); c.setFont("Display-I", 30); c.drawString(MARG_X+110, H - 200, "Warmth.")

senses = [
    ("◐", "البصر · Sight",   "إضاءة دافئة، مطبخ مفتوح ومرئي، مساحة منظَّمة. لا شاشات."),
    ("∿", "الشمّ · Smell",   "روائح الخبز والبيض والقهوة — من المطبخ مباشرة."),
    ("○", "اللمس · Touch",  "أكواب وأطباق متينة بجودة جيّدة، مريحة في الاستخدام."),
    ("☼", "الحرارة · Warmth","إضاءة دافئة ٢٧٠٠K. لا ضوء بارد. مكان مريح طوال الصباح."),
]
cw, ch = 175, 175
gx = 18
y0 = 110
for i, (ico, h_ar, body) in enumerate(senses):
    x = MARG_X + i*(cw+gx)
    card(x, y0, cw, ch, fill=HexColor("#252C44"), stroke=WHISP)
    c.setFillColor(YOLK); c.circle(x+24, y0+ch-24, 14, fill=1, stroke=0)
    c.setFillColor(NAVY); c.setFont("Display-B", 13); c.drawCentredString(x+24, y0+ch-28, ico)
    c.setFillColor(CREAM); c.setFont("Body-Bold", 13); c.drawString(x+14, y0+ch-66, ar(h_ar))
    ar_wrap(body, x+14, y0+ch-86, cw-28, size=9.5, color=HexColor("#C8BFA3"), leading=14, align="left")

card(MARG_X, 65, W - 2*MARG_X, 50, fill=HexColor("#252C44"), stroke=WHISP)
ar_wrap("تجربة العميل المعتاد — نهدف لمعرفة العملاء بشكل طبيعي، بدون مبالغات. الموظف يتذكّر الوجوه والطلبات بشكل عمليّ يُسرّع الخدمة.",
        MARG_X+18, 97, W - 2*MARG_X - 36, size=10.5, color=CREAM, leading=15, align="left")

footer("SECTION 08 · SENSORY", 24, dark=True)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 25 — AUDIO IDENTITY
# ═══════════════════════════════════════════════════════
page_bg(PAPER)
header("09", "Audio Identity · Voice of the room", "الهوية الصوتية", 25)
kicker("Sound of the morning", MARG_X, H - 115)
title("Let the", MARG_X, H - 165, 30, NAVY)
c.setFillColor(TERRA); c.setFont("Display-I", 36); c.drawString(MARG_X, H - 210, "kitchen")
title("speak.", MARG_X, H - 250, 30, NAVY)
rule_tiny(MARG_X, H - 270)
ar_wrap("خلال ساعات الصباح، تكون أصوات المطبخ — تحضير البيض، حركة المقلاة، تجهيز القهوة — جزءًا واضحًا من تجربة المكان. الموسيقى هادئة منخفضة عند الحاجة، دون أن تطغى.",
        MARG_X, H - 300, 360, size=11, color=INK, leading=17, align="left")

audio = [
    ("PRIMARY", TERRA, "أصوات المطبخ هي العنصر الأساسي"),
    ("SOFT",    HERB,  "موسيقى هادئة منخفضة عند الحاجة"),
    ("NEVER",   DEEP,  "لا موسيقى صاخبة أو لا تناسب الصباح"),
    ("SPACE",   NAVY,  "معالجة صوتية لتقليل الصدى والضوضاء"),
    ("HUMAN",   TERRA, "التحيات طبيعية ومباشرة — بلا نصوص محفوظة"),
]
tx = 440
for i, (tag, col, ar_text) in enumerate(audio):
    yy = H - 130 - i*46
    card(tx, yy, 340, 36, fill=HexColor("#FFFFFF"), stroke=HAIR)
    c.setFillColor(col); c.setFont("Mono-B", 8); c.drawString(tx+12, yy+13, tag)
    c.setFillColor(NAVY); c.setFont("Body-Bold", 11); c.drawRightString(tx+340-12, yy+13, ar(ar_text))

footer("SECTION 09 · AUDIO", 25)
c.showPage()

# ═══════════════════════════════════════════════════════
# PAGE 26 — CLOSING (dark)
# ═══════════════════════════════════════════════════════
page_bg(NAVY)
header("·", "End of archive", "ختام الأرشيف", 26, dark=True)

c.drawImage(LOGO, W/2 - 60, H/2 + 0, width=120, height=120, mask='auto')

c.setFillColor(YOLK); c.setFont("Mono-B", 9); c.drawCentredString(W/2, H/2 - 20, "THE OMLT PROMISE")

c.setFillColor(CREAM); c.setFont("Display-B", 48)
c.drawCentredString(W/2, H/2 - 80, "A clear and")
c.setFillColor(YOLK); c.setFont("Display-I", 48); c.drawCentredString(W/2, H/2 - 130, "simple morning.")

c.setFillColor(CREAM); c.setFont("Body-Bold", 20)
c.drawCentredString(W/2, H/2 - 170, ar("بداية صباح واضحة وبسيطة."))

c.setStrokeColor(HexColor("#3A4055")); c.setLineWidth(0.5)
c.line(W/2 - 40, H/2 - 195, W/2 + 40, H/2 - 195)

c.setFillColor(HexColor("#A09684")); c.setFont("Mono", 9)
c.drawCentredString(W/2, H/2 - 215, "OMLT · MASTER ARCHIVE · ABHA · KSA")

footer("OMLT · BREAKFAST KITCHEN", 26, dark=True)
c.showPage()

c.save()
print("PDF written:", OUT, os.path.getsize(OUT), "bytes")
