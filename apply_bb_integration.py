"""
Atomic restructuring of OMLT-Master-Presentation.html
- Cover redesign (light, editorial, no logo, OMLT wordmark)
- Foundation · Manifesto (new, page 3)
- Remove logo from Concept · Definition
- Rename Logo → The Mark; lighten the Hero
- Insert: The Mark · Variations, Icons & Pattern,
          Applications · Packaging, Signage, Digital, Apparel & Merch
- 8 chapters, 33 pages total. Folios renumbered.
"""
import re

SRC = '/sessions/dazzling-busy-tesla/mnt/outputs/OMLT-Master-Presentation.html'
src = open(SRC).read()

# ───────────────────────────────────────────────────────────────────
# 1) COVER CSS — light, editorial, paper background
# ───────────────────────────────────────────────────────────────────
src = src.replace(
    """/* ───── COVER (editorial, type-led — full-bleed hero band) ───── */
.cover{
  padding:0;
  min-height:100vh;
  background:
    radial-gradient(70% 55% at 50% 38%, rgba(230,165,50,0.13), transparent 65%),
    radial-gradient(85% 60% at 50% 95%, rgba(200,68,44,0.22), transparent 60%),
    linear-gradient(180deg,#0B0F1B 0%,#1B2235 100%);
}
.cover-bg{position:absolute;inset:0;background:transparent;pointer-events:none}
.cover-grain{position:absolute;inset:0;opacity:0.05;background-image:radial-gradient(rgba(255,255,255,0.6) 1px, transparent 1px);background-size:3px 3px;mix-blend-mode:overlay;pointer-events:none}
.cover-inner{
  position:relative;z-index:2;min-height:100vh;
  display:grid;grid-template-rows:auto 1fr auto;
  color:var(--cream);
  padding:72px max(72px, calc((100vw - 1180px) / 2));
}""",
    """/* ───── COVER — editorial, light, type-led (no logo) ───── */
.cover{
  padding:0;
  min-height:100vh;
  background:
    radial-gradient(75% 55% at 50% 30%, rgba(230,165,50,0.10), transparent 70%),
    radial-gradient(70% 50% at 50% 92%, rgba(200,68,44,0.08), transparent 65%),
    linear-gradient(180deg,#FBF6EA 0%,#F2E9CF 100%);
}
.cover-bg{position:absolute;inset:0;background:transparent;pointer-events:none}
.cover-grain{position:absolute;inset:0;opacity:0.04;background-image:radial-gradient(rgba(27,34,53,0.45) 1px, transparent 1px);background-size:3px 3px;mix-blend-mode:multiply;pointer-events:none}
.cover-inner{
  position:relative;z-index:2;min-height:100vh;
  display:grid;grid-template-rows:auto 1fr auto;
  color:var(--navy);
  padding:72px max(72px, calc((100vw - 1180px) / 2));
}"""
)

src = src.replace(
    """.cover-top{
  display:flex;justify-content:space-between;
  font-family:var(--mono);font-size:11px;letter-spacing:0.42em;text-transform:uppercase;
  opacity:0.55;
}""",
    """.cover-top{
  display:flex;justify-content:space-between;
  font-family:var(--mono);font-size:11px;letter-spacing:0.42em;text-transform:uppercase;
  color:rgba(27,34,53,0.6);
}
.cover-spine-line{height:1px;background:rgba(27,34,53,0.18);width:100%;margin:18px 0}"""
)

src = src.replace(
    """.cover-main{
  display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;
  gap:28px;padding:0 40px;
}""",
    """.cover-main{
  display:grid;grid-template-columns:1.1fr 1fr;gap:64px;align-items:center;
  padding:0 24px;
}
.cover-wordmark{
  font-family:var(--serif);font-weight:900;font-size:280px;line-height:0.88;letter-spacing:-0.035em;
  color:var(--navy);text-align:start;
}
.cover-wordmark .dot{color:var(--terra)}
.cover-right{display:flex;flex-direction:column;gap:22px;border-inline-start:1px solid rgba(27,34,53,0.18);padding-inline-start:48px}
"""
)

src = src.replace(
    """.cover-kicker{
  font-family:var(--mono);font-size:11px;letter-spacing:0.55em;text-transform:uppercase;
  color:var(--yolk);font-weight:600;
}
.cover-rule{width:48px;height:2px;background:var(--yolk);opacity:0.85}
.cover-title{
  font-family:var(--serif);font-weight:900;
  font-size:104px;line-height:0.96;letter-spacing:-0.028em;
  color:var(--cream);max-width:14ch;
}
.cover-title em{color:var(--yolk);font-style:italic;font-weight:700}
.cover-ar{
  font-family:var(--ar);font-size:24px;font-weight:500;
  color:rgba(246,236,214,0.88);letter-spacing:0;
}
.cover-sub{
  font-family:var(--ar);font-size:14px;line-height:1.9;
  color:rgba(246,236,214,0.55);max-width:58ch;font-weight:400;
  margin-top:6px;
}
.cover-bottom{
  display:flex;justify-content:space-between;align-items:center;
  font-family:var(--mono);font-size:10px;letter-spacing:0.42em;text-transform:uppercase;
  opacity:0.5;
}""",
    """.cover-kicker{
  font-family:var(--mono);font-size:11px;letter-spacing:0.55em;text-transform:uppercase;
  color:var(--terra);font-weight:600;
}
.cover-rule{width:48px;height:2px;background:var(--terra);opacity:0.85}
.cover-title{
  font-family:var(--serif);font-weight:900;
  font-size:68px;line-height:0.95;letter-spacing:-0.022em;
  color:var(--navy);max-width:14ch;
}
.cover-title em{color:var(--terra);font-style:italic;font-weight:700}
.cover-ar{
  font-family:var(--ar);font-size:24px;font-weight:700;
  color:var(--navy);letter-spacing:0;
}
.cover-sub{
  font-family:var(--ar);font-size:13.5px;line-height:1.9;
  color:rgba(27,34,53,0.65);max-width:48ch;font-weight:400;
  margin-top:4px;
}
.cover-bottom{
  display:flex;justify-content:space-between;align-items:center;
  font-family:var(--mono);font-size:10px;letter-spacing:0.42em;text-transform:uppercase;
  color:rgba(27,34,53,0.55);
}"""
)

# 2) Cover HTML body — replace
COVER_OLD = re.search(r'<section class="page cover">.*?</section>', src, re.S).group(0)
COVER_NEW = '''<section class="page cover">
  <div class="cover-bg"></div>
  <div class="cover-grain"></div>
  <div class="cover-inner">
    <div class="cover-top">
      <span>OMLT · Master Archive · V 2.0</span>
      <span>Abha · KSA</span>
    </div>

    <div class="cover-main">
      <div class="cover-wordmark">OMLT<span class="dot">.</span></div>

      <div class="cover-right">
        <span class="cover-kicker">A book about</span>
        <span class="cover-rule"></span>
        <h1 class="cover-title">A small <em>egg</em>,<br>a loud <em>morning</em>.</h1>
        <p class="cover-ar">بيضة صغيرة، صباح عالٍ.</p>
        <p class="cover-sub">دليل الهوية والمشروع لعلامة OMLT — مطبخ فطور قصير الذاكرة، طويل الأثر. نظام كامل من البيان إلى لافتة المتجر.</p>
      </div>
    </div>

    <div class="cover-bottom">
      <span>OMLT · BREAKFAST KITCHEN</span>
      <span>VOL.02 · EDITORIAL EDITION</span>
      <span>001 / 033</span>
    </div>
  </div>
</section>'''
src = src.replace(COVER_OLD, COVER_NEW)

# ───────────────────────────────────────────────────────────────────
# 3) UPDATE TOC HEADLINE: "Twenty-six pages, one egg." → "Eight chapters, one egg."
#    (Arabic: "ست وعشرون صفحة، بيضة واحدة." → "ثمانية فصول، بيضة واحدة.")
# ───────────────────────────────────────────────────────────────────
src = src.replace('Twenty-five<br>pages,<br>one egg.', 'Eight<br>chapters,<br>one egg.')
src = src.replace('Twenty-five pages, one egg.', 'Eight chapters, one egg.')
src = src.replace('Twenty-six pages, one egg.', 'Eight chapters, one egg.')
src = src.replace('Twenty-six<br>pages,<br>one egg.', 'Eight<br>chapters,<br>one egg.')
# Add Arabic subtitle if not present near the TOC headline
src = src.replace('<p class="lead">من المفهوم إلى الميزانية، إلى الشعار، إلى الصوت — أرشيف مُعتمَد ونهائي لمرحلة التأسيس.</p>',
                  '<p class="ar-subtitle" style="font-family:var(--ar);font-size:18px;color:rgba(15,20,34,0.55);font-weight:500;margin-top:8px">ثمانية فصول، بيضة واحدة.</p>\n      <p class="lead" style="margin-top:16px">من البيان إلى التطبيقات، إلى الصوت — أرشيف مرجعي لعلامة OMLT بإيقاع كتاب علامة.</p>')

# ───────────────────────────────────────────────────────────────────
# 4) REPLACE TOC ENTRIES — new 8-chapter map
# ───────────────────────────────────────────────────────────────────
toc_block_old_re = re.compile(r'<ol class="toc">.*?</ol>', re.S)
toc_block_new = '''<ol class="toc">
      <li><span class="n">01</span><span class="t">Foundation <span class="ar">البيان</span></span><span class="p">003</span></li>
      <li><span class="n">02</span><span class="t">Concept <span class="ar">المفهوم</span></span><span class="p">004</span></li>
      <li><span class="n">03</span><span class="t">Vision &amp; Purpose <span class="ar">الرؤية والهدف</span></span><span class="p">009</span></li>
      <li><span class="n">04</span><span class="t">Business Setup &amp; Costs <span class="ar">التكاليف</span></span><span class="p">012</span></li>
      <li><span class="n">05</span><span class="t">The Mark <span class="ar">الشارة</span></span><span class="p">017</span></li>
      <li><span class="n">06</span><span class="t">Color &amp; Type <span class="ar">الألوان والخطوط</span></span><span class="p">021</span></li>
      <li><span class="n">07</span><span class="t">Applications <span class="ar">التطبيقات</span></span><span class="p">025</span></li>
      <li><span class="n">08</span><span class="t">Brand Voice <span class="ar">الصوت والحسّ</span></span><span class="p">030</span></li>
    </ol>'''
src = toc_block_old_re.sub(toc_block_new, src)

# Also update the kicker on the contents page
src = src.replace('<span class="kicker">The map</span>', '<span class="kicker">The map · Eight chapters</span>')

# ───────────────────────────────────────────────────────────────────
# 5) REMOVE LOGO FROM CONCEPT · DEFINITION (PAGE 3 → 4)
# ───────────────────────────────────────────────────────────────────
# Find Concept · Definition page, remove the right-hand stage div with logo
def_logo_block = '''<div class="center" style="position:relative">
      <div style="aspect-ratio:1/1;width:90%;background:var(--cream);border-radius:14px;display:flex;align-items:center;justify-content:center;padding:32px;border:1px solid var(--hair)">
        <img src="omlt-logo-approved.png" alt="OMLT logo" style="width:80%;height:auto;filter:drop-shadow(0 20px 40px rgba(0,0,0,0.18))"/>
      </div>
    </div>'''
def_logo_replacement = '''<div class="center" style="position:relative">
      <div style="aspect-ratio:1/1;width:90%;background:linear-gradient(135deg,var(--cream),var(--paper));border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px;border:1px solid var(--hair);text-align:center;gap:18px">
        <span style="font-family:var(--mono);font-size:10px;letter-spacing:0.42em;text-transform:uppercase;color:var(--terra);font-weight:600">The dish</span>
        <div style="font-family:var(--serif);font-style:italic;font-weight:700;font-size:42px;line-height:1.15;color:var(--navy);max-width:14ch">The omelette,<br>plain done well.</div>
        <div style="height:1px;width:32px;background:var(--terra);opacity:0.6"></div>
        <div style="font-family:var(--ar);font-size:15px;color:rgba(15,20,34,0.6);max-width:30ch;line-height:1.85">صنفٌ واحد، إيقاع واحد، اتقان واحد كل صباح.</div>
      </div>
    </div>'''
src = src.replace(def_logo_block, def_logo_replacement)

# ───────────────────────────────────────────────────────────────────
# 6) LOGO HERO → THE MARK · HERO  (lighter, editorial — remove `dark` class)
# ───────────────────────────────────────────────────────────────────
# Update the section: remove dark class, change name to "The Mark · The badge"
old_hero_section = re.search(
    r'<!-- ═[^>]*?PAGE 16 · LOGO — HERO[^>]*?-->\s*<section class="page dark">.*?</section>',
    src, re.S
)
if old_hero_section:
    new_hero = '''<!-- ═══════════════════════════════════════════════════════════════
     PAGE 17 · THE MARK · HERO (editorial, light)
     ═══════════════════════════════════════════════════════════════ -->
<section class="page">
  <header class="head">
    <span class="num">05</span>
    <span class="name">The Mark · The badge <span class="ar">الشارة</span></span>
    <span>017 / 033</span>
  </header>

  <div class="logo-hero" style="grid-template-columns:1.05fr 1fr;gap:72px">
    <div class="stage stage-light">
      <img src="omlt-logo-approved.png" alt="OMLT approved logo" />
    </div>
    <div class="col stack-lg">
      <span class="kicker">Direction C · Final · Approved</span>
      <h2 class="h-1">The badge.<br><em>One mark,</em><br>every surface.</h2>
      <span class="rule-tiny"></span>
      <p class="lead">شارة دائرية تحوي رمز البيضة في المنتصف، نصًّا مُقوَّسًا حول الأعلى، واسم العلامة OMLT في الأسفل. اعتُمدت رسميًّا كهوية وحيدة للمشروع.</p>
      <div style="display:flex;gap:32px;margin-top:8px">
        <div><span class="kicker">File</span><div style="font-family:var(--mono);color:var(--navy);font-size:13px;letter-spacing:0.18em;margin-top:6px">OMLT-Logo-Layered-HiRes</div></div>
        <div><span class="kicker">Status</span><div style="font-family:var(--mono);color:var(--navy);font-size:13px;letter-spacing:0.18em;margin-top:6px">APPROVED · FINAL</div></div>
      </div>
    </div>
  </div>

  <div class="foot">
    <span>CHAPTER 05 · THE MARK</span>
    <span>017 <span class="dot"></span> 033</span>
  </div>
</section>'''
    src = src.replace(old_hero_section.group(0), new_hero)
    print('✓ Logo hero converted to light editorial')

# Light stage CSS for the new hero
src = src.replace(
    """.logo-hero{display:grid;grid-template-columns:1.15fr 1fr;gap:64px;align-items:center;height:100%}
.logo-hero .stage{aspect-ratio:1/1;background:radial-gradient(circle at 50% 38%, rgba(230,165,50,0.22), transparent 65%), var(--navy);border-radius:14px;display:flex;align-items:center;justify-content:center;padding:56px;position:relative;box-shadow:inset 0 0 60px rgba(0,0,0,0.35)}
.logo-hero .stage::before{content:"";position:absolute;inset:22px;border:1px solid rgba(246,236,214,0.14);border-radius:10px}
.logo-hero .stage::after{content:"";position:absolute;inset:40px;border:1px dashed rgba(246,236,214,0.06);border-radius:6px}
.logo-hero .stage img{width:80%;height:auto;filter:drop-shadow(0 40px 80px rgba(0,0,0,0.55))}""",
    """.logo-hero{display:grid;grid-template-columns:1.05fr 1fr;gap:72px;align-items:center}
.logo-hero .stage{aspect-ratio:1/1;background:radial-gradient(circle at 50% 38%, rgba(230,165,50,0.10), transparent 65%), var(--paper);border-radius:14px;display:flex;align-items:center;justify-content:center;padding:64px;position:relative;border:1px solid var(--hair)}
.logo-hero .stage::before{content:"";position:absolute;inset:24px;border:1px solid rgba(27,34,53,0.10);border-radius:10px}
.logo-hero .stage::after{content:"";position:absolute;inset:44px;border:1px dashed rgba(27,34,53,0.06);border-radius:6px}
.logo-hero .stage img{width:78%;height:auto;filter:drop-shadow(0 28px 50px rgba(27,34,53,0.18))}
.logo-hero .stage.stage-light{background:radial-gradient(circle at 50% 38%, rgba(230,165,50,0.12), transparent 65%), var(--paper)}"""
)

# ───────────────────────────────────────────────────────────────────
# 7) RENAME "Approved Logo · Anatomy" → "The Mark · Anatomy"
# ───────────────────────────────────────────────────────────────────
src = src.replace('Approved Logo · Anatomy <span class="ar">تشريح الشعار</span>',
                  'The Mark · Anatomy <span class="ar">تشريح الشارة</span>')
src = src.replace('Approved Logo · Usage rules <span class="ar">قواعد الاستخدام</span>',
                  'The Mark · Usage <span class="ar">قواعد الاستخدام</span>')
src = src.replace('Approved Logo · The mark <span class="ar">الشعار المعتمد</span>',
                  'The Mark · The badge <span class="ar">الشارة</span>')
# also update SECTION refs
src = src.replace('SECTION 04 · LOGO', 'CHAPTER 05 · THE MARK')

# Other chapter labels rewritten
src = src.replace('SECTION 01 · CONCEPT', 'CHAPTER 02 · CONCEPT')
src = src.replace('SECTION 02 · VISION',  'CHAPTER 03 · VISION')
src = src.replace('SECTION 03 · COSTS',   'CHAPTER 04 · BUSINESS')
src = src.replace('SECTION 05 · COLORS',  'CHAPTER 06 · COLOR & TYPE')
src = src.replace('SECTION 06 · TYPE',    'CHAPTER 06 · COLOR & TYPE')
src = src.replace('SECTION 07 · VISUAL',  'CHAPTER 08 · BRAND VOICE')
src = src.replace('SECTION 08 · SENSORY', 'CHAPTER 08 · BRAND VOICE')
src = src.replace('SECTION 09 · AUDIO',   'CHAPTER 08 · BRAND VOICE')

# Also update head chapter numbers from "04" to "05" for Mark pages etc.
# (handled per-page when new sections inserted)

open(SRC, 'w').write(src)
print('Phase A complete — sections so far:', src.count('<section class="page'))
print('Folio /033 currently:', src.count('/ 033'))
