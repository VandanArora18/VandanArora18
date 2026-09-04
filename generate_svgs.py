#!/usr/bin/env python3
"""
Generate animated theme-aware SVG hero banners for GitHub profile.
  - High-res dithered portrait with background removal
  - Morphing transitions: Portrait -> </> -> Py -> SQL -> {f} -> V (cycling)
  - macOS terminal window with animated gradients
"""
import os, random
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageOps

# ── Config ───────────────────────────────────────────────────────────
CW, CH = 260, 330
N_PG = 15
N_SG = 8
FI_T0, FI_DT, FI_DUR = 0.15, 0.035, 0.85
SYMBOLS = ["</>", "Py", "SQL", "{f}", "V"]
N_PHASES = 1 + len(SYMBOLS)   # 6 phases
CYC_T = 3.0                   # cycling starts after portrait reveal
CYC_D = 15.0                  # cycle period (seconds)

# ── Helpers ──────────────────────────────────────────────────────────
def _font(size):
    for p in ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _groups(bw_img, n):
    w, h = bw_img.size
    gs = [[] for _ in range(n)]
    for y in range(h):
        for x in range(w):
            if bw_img.getpixel((x, y)) == 0:
                gs[(x*7 + y*13 + random.randint(0, max(1, n-2))) % n].append((x, y))
    return gs

def _path(pixels):
    if not pixels: return ""
    sp = sorted(pixels, key=lambda p: (p[1], p[0]))
    segs, cy, cx, cl = [], None, None, 0
    for px, py in sp:
        if py == cy and px == cx + cl: cl += 1
        else:
            if cy is not None: segs.append((cx, cy, cl))
            cx, cy, cl = px, py, 1
    if cy is not None: segs.append((cx, cy, cl))
    return "".join(
        f"M{x} {y}h{l}v1h-{l}z" if l > 1 else f"M{x} {y}h1v1h-1z"
        for x, y, l in segs)

def _cycle_anim(phase_i):
    p = 1.0 / N_PHASES
    tr = 0.015
    s, e = phase_i * p, (phase_i + 1) * p
    if phase_i == 0:
        v, k = "1;1;0;0;1", f"0;{e-tr:.4f};{e+tr:.4f};{1-tr:.4f};1"
    elif phase_i == N_PHASES - 1:
        v, k = "0;0;1;1;0", f"0;{s-tr:.4f};{s+tr:.4f};{1-tr:.4f};1"
    else:
        v, k = "0;0;1;1;0;0", f"0;{s-tr:.4f};{s+tr:.4f};{e-tr:.4f};{e+tr:.4f};1"
    return f'<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{CYC_D}s" begin="{CYC_T}s" repeatCount="indefinite"/>'

# ── Image Processing ─────────────────────────────────────────────────
def process_photo(path):
    img = Image.open(path).convert('L')
    # Resize first
    img.thumbnail((CW, CH), Image.Resampling.LANCZOS)
    w, h = img.size
    canvas = Image.new('L', (CW, CH), 255)
    canvas.paste(img, ((CW - w) // 2, (CH - h) // 2))

    # Remove dark background: set very dark pixels to white
    px = canvas.load()
    for y in range(CH):
        for x in range(CW):
            if px[x, y] < 30:
                px[x, y] = 255

    # Smooth edges after background removal + enhance
    canvas = canvas.filter(ImageFilter.GaussianBlur(radius=0.4))
    canvas = ImageEnhance.Contrast(canvas).enhance(1.5)
    canvas = ImageEnhance.Sharpness(canvas).enhance(1.5)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=3))

    return _groups(canvas.convert('1', dither=Image.Dither.FLOYDSTEINBERG), N_PG)

def make_symbol(text):
    img = Image.new('L', (CW, CH), 255)
    draw = ImageDraw.Draw(img)
    for sz in range(240, 40, -8):
        f = _font(sz)
        bb = draw.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw < CW * 0.88 and th < CH * 0.68: break
    draw.text(((CW - tw) // 2 - bb[0], (CH - th) // 2 - bb[1]), text, font=f, fill=0)
    return _groups(img.convert('1', dither=Image.Dither.FLOYDSTEINBERG), N_SG)

# ── SVG Builders ─────────────────────────────────────────────────────
def portrait_svg(groups):
    parts = []
    for i, g in enumerate(groups):
        d = _path(g)
        if not d: continue
        t = FI_T0 + i * FI_DT
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" '
            f'dur="{FI_DUR}s" begin="{t:.3f}s" fill="freeze" calcMode="spline" '
            f'keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{d}"/></g>')
    return "\n      ".join(parts)

def symbol_svg(groups):
    all_px = [p for g in groups for p in g]
    return f'<path d="{_path(all_px)}"/>'

# ── SVG Template ─────────────────────────────────────────────────────
def build_svg(mode, p_svg, sym_svgs):
    dk = mode == "dark"
    C = {
        'bg':  "#030712"  if dk else "#E2E8F0",
        'p0':  "#090D16"  if dk else "#FFFFFF",
        'p1':  "#0F172A"  if dk else "#F1F5F9",
        'hdr': "#0B132B"  if dk else "#E2E8F0",
        'hln': "rgba(255,255,255,0.08)" if dk else "rgba(0,0,0,0.08)",
        'ttl': "#94A3B8"  if dk else "#475569",
        'brd': "#38BDF8"  if dk else "#0284C7",
        'bxf': "#070C18"  if dk else "#F8FAFC",
        'bxa': "rgba(56,189,248,0.3)" if dk else "rgba(2,132,199,0.3)",
        'lbl': "#64748B",
        'stc': "#38BDF8"  if dk else "#0284C7",
        'stb': "rgba(15,23,42,0.85)" if dk else "#FFFFFF",
        'sta': "rgba(56,189,248,0.3)" if dk else "rgba(2,132,199,0.3)",
        'dot': "#10B981"  if dk else "#059669",
        'g0':  "#60A5FA"  if dk else "#2563EB",
        'g1':  "#A78BFA"  if dk else "#6D28D9",
        'g2':  "#38BDF8"  if dk else "#0284C7",
        'a0':  "#3B82F6"  if dk else "#2563EB",
        'a1':  "#8B5CF6"  if dk else "#7C3AED",
        'a2':  "#06B6D4"  if dk else "#0284C7",
        'bbg': "rgba(59,130,246,0.15)" if dk else "rgba(37,99,235,0.1)",
        'bbr': "rgba(59,130,246,0.4)"  if dk else "rgba(37,99,235,0.3)",
        'btx': "#60A5FA"  if dk else "#2563EB",
        'nm':  "#F8FAFC"  if dk else "#0F172A",
        'sub': "#94A3B8"  if dk else "#475569",
        'bl':  "#38BDF8"  if dk else "#0284C7",
        'bt':  "#E2E8F0"  if dk else "#1E293B",
        'div': "rgba(255,255,255,0.08)" if dk else "rgba(0,0,0,0.08)",
        'tb':  "#1E293B"  if dk else "#F1F5F9",
        'pbg': "#070C18"  if dk else "#FFFFFF",
        'ptl': "#94A3B8"  if dk else "#64748B",
        'pc1': "#38BDF8"  if dk else "#0284C7",
        'pc2': "#A78BFA"  if dk else "#6D28D9",
        'pds': "#94A3B8"  if dk else "#475569",
    }
    T = {
        'py': (("#38BDF8","rgba(56,189,248,0.2)")  if dk else ("#0284C7","rgba(2,132,199,0.3)")),
        'cp': (("#A78BFA","rgba(139,92,246,0.2)")  if dk else ("#6D28D9","rgba(109,40,217,0.3)")),
        'cv': (("#34D399","rgba(16,185,129,0.2)")  if dk else ("#059669","rgba(5,150,105,0.3)")),
        'tf': (("#FBBF24","rgba(245,158,11,0.2)")  if dk else ("#D97706","rgba(217,119,6,0.3)")),
        'pt': (("#F87171","rgba(239,68,68,0.2)")   if dk else ("#DC2626","rgba(220,38,38,0.3)")),
        'fa': (("#34D399","rgba(16,185,129,0.2)")  if dk else ("#059669","rgba(5,150,105,0.3)")),
        'fl': (("#38BDF8","rgba(56,189,248,0.2)")  if dk else ("#0284C7","rgba(2,132,199,0.3)")),
        'ro': (("#C084FC","rgba(168,85,247,0.2)")  if dk else ("#9333EA","rgba(147,51,234,0.3)")),
        'gi': (("#CBD5E1","rgba(148,163,184,0.2)") if dk else ("#475569","rgba(71,85,105,0.3)")),
        'li': (("#60A5FA","rgba(59,130,246,0.2)")  if dk else ("#2563EB","rgba(37,99,235,0.3)")),
    }
    sx, sy = round(360 / CW, 4), round(420 / CH, 4)
    sfx = "" if dk else "L"

    # Build pixel art groups dynamically
    art_parts = [f'''    <g>
      {_cycle_anim(0)}
      {p_svg}
    </g>''']
    for i, s_svg in enumerate(sym_svgs, 1):
        art_parts.append(f'''    <g opacity="0">
      {_cycle_anim(i)}
      {s_svg}
    </g>''')
    art_block = "\n".join(art_parts)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610"
  font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
  role="img" aria-label="Vandan Arora - profile.sh --live">
<defs>
  <linearGradient id="ac{sfx}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['a0']}"><animate attributeName="stop-color" values="{C['a0']};{C['a1']};{C['a2']};{C['a0']}" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset=".5" stop-color="{C['a1']}"><animate attributeName="stop-color" values="{C['a1']};{C['a2']};{C['a0']};{C['a1']}" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset="1" stop-color="{C['a2']}"><animate attributeName="stop-color" values="{C['a2']};{C['a0']};{C['a1']};{C['a2']}" dur="8s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <linearGradient id="ag{sfx}" x1="0" y1="0" x2="0" y2="{CH}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{C['g0']}"/><stop offset=".5" stop-color="{C['g1']}"/><stop offset="1" stop-color="{C['g2']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 -120;0 120;0 -120" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="pg{sfx}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['p0']}"/><stop offset="1" stop-color="{C['p1']}"/></linearGradient>
  <filter id="gl3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <clipPath id="wc{sfx}"><rect x="2" y="2" width="1176" height="606" rx="16"/></clipPath>
</defs>

<rect x="2" y="2" width="1176" height="606" rx="16" fill="{C['bg']}"/>
<g clip-path="url(#wc{sfx})">
  <rect x="2" y="2" width="1176" height="606" fill="url(#pg{sfx})"/>
  <rect x="2" y="2" width="1176" height="44" fill="{C['hdr']}"/>
  <line x1="2" y1="46" x2="1178" y2="46" stroke="{C['hln']}"/>
  <circle cx="28" cy="23" r="5.5" fill="#FF5F56"/>
  <circle cx="48" cy="23" r="5.5" fill="#FFBD2E"/>
  <circle cx="68" cy="23" r="5.5" fill="#27C93F"/>
  <text x="590" y="27" text-anchor="middle" font-size="12" fill="{C['ttl']}" font-weight="500">vandanarora18@gmail.com - zsh profile.sh --live</text>

  <text x="38" y="74" font-size="10" letter-spacing="3" fill="{C['lbl']}" font-weight="bold">AI.SYSTEM.VISUALIZER</text>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="none" stroke="{C['brd']}" stroke-width="2" opacity="0.4" filter="url(#gl3)"/>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="{C['bxf']}" stroke="{C['bxa']}"/>

  <g transform="translate(48,96) scale({sx},{sy})" fill="url(#ag{sfx})" shape-rendering="crispEdges">
{art_block}
  </g>

  <rect x="52" y="525" width="358" height="36" rx="8" fill="{C['stb']}" stroke="{C['sta']}"/>
  <circle cx="70" cy="543" r="4" fill="{C['dot']}"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
  <text x="82" y="547" font-size="11" fill="{C['stc']}" font-weight="600">SYSTEM STATUS: ACTIVE &amp; BUILDING</text>

  <g transform="translate(460,75)">
    <rect x="0" y="0" width="170" height="24" rx="12" fill="{C['bbg']}" stroke="{C['bbr']}"/>
    <text x="85" y="16" text-anchor="middle" font-size="11" fill="{C['btx']}" font-weight="600">ROBOTICS &amp; AI ENGINEER</text>
    <text x="0" y="58" font-size="28" font-weight="800" fill="{C['nm']}" letter-spacing="-0.5">Vandan Arora</text>
    <text x="0" y="80" font-size="14" fill="{C['sub']}">Thapar Institute of Engineering and Technology</text>

    <g font-size="13" fill="{C['bt']}">
      <text x="0" y="118"><tspan fill="{C['bl']}" font-weight="bold">&gt; role:</tspan> AI/ML &amp; Computer Vision Developer</text>
      <text x="0" y="144"><tspan fill="{C['bl']}" font-weight="bold">&gt; focus:</tspan> Intelligent Autonomous Systems, Edge AI &amp; Robotics</text>
      <text x="0" y="170"><tspan fill="{C['bl']}" font-weight="bold">&gt; stack:</tspan> Python, C++, FastAPI, OpenCV, TensorFlow, PyTorch</text>
      <text x="0" y="196"><tspan fill="{C['bl']}" font-weight="bold">&gt; status:</tspan> Open to AI/ML &amp; Robotics Internships / Projects</text>
    </g>

    <line x1="0" y1="220" x2="680" y2="220" stroke="{C['div']}"/>
    <text x="0" y="248" font-size="11" letter-spacing="2" fill="{C['lbl']}" font-weight="bold">TECH_STACK // CAPABILITIES</text>

    <g transform="translate(0,262)">
      <rect x="0" y="0" width="105" height="32" rx="6" fill="{C['tb']}" stroke="{T['py'][1]}"/><text x="12" y="20" font-size="12" fill="{T['py'][0]}" font-weight="600">Python</text>
      <rect x="115" y="0" width="95" height="32" rx="6" fill="{C['tb']}" stroke="{T['cp'][1]}"/><text x="127" y="20" font-size="12" fill="{T['cp'][0]}" font-weight="600">C++</text>
      <rect x="220" y="0" width="105" height="32" rx="6" fill="{C['tb']}" stroke="{T['cv'][1]}"/><text x="232" y="20" font-size="12" fill="{T['cv'][0]}" font-weight="600">OpenCV</text>
      <rect x="335" y="0" width="125" height="32" rx="6" fill="{C['tb']}" stroke="{T['tf'][1]}"/><text x="347" y="20" font-size="12" fill="{T['tf'][0]}" font-weight="600">TensorFlow</text>
      <rect x="470" y="0" width="105" height="32" rx="6" fill="{C['tb']}" stroke="{T['pt'][1]}"/><text x="482" y="20" font-size="12" fill="{T['pt'][0]}" font-weight="600">PyTorch</text>
    </g>
    <g transform="translate(0,304)">
      <rect x="0" y="0" width="105" height="32" rx="6" fill="{C['tb']}" stroke="{T['fa'][1]}"/><text x="12" y="20" font-size="12" fill="{T['fa'][0]}" font-weight="600">FastAPI</text>
      <rect x="115" y="0" width="100" height="32" rx="6" fill="{C['tb']}" stroke="{T['fl'][1]}"/><text x="127" y="20" font-size="12" fill="{T['fl'][0]}" font-weight="600">Flutter</text>
      <rect x="225" y="0" width="115" height="32" rx="6" fill="{C['tb']}" stroke="{T['ro'][1]}"/><text x="237" y="20" font-size="12" fill="{T['ro'][0]}" font-weight="600">ROS / AI</text>
      <rect x="350" y="0" width="95" height="32" rx="6" fill="{C['tb']}" stroke="{T['gi'][1]}"/><text x="362" y="20" font-size="12" fill="{T['gi'][0]}" font-weight="600">Git</text>
      <rect x="455" y="0" width="120" height="32" rx="6" fill="{C['tb']}" stroke="{T['li'][1]}"/><text x="467" y="20" font-size="12" fill="{T['li'][0]}" font-weight="600">Linux/Docker</text>
    </g>

    <g transform="translate(0,356)">
      <rect x="0" y="0" width="675" height="120" rx="10" fill="{C['pbg']}" stroke="url(#ac{sfx})" stroke-width="1.5"/>
      <text x="20" y="30" font-size="12" fill="{C['ptl']}" font-weight="600">HIGHLIGHTED PROJECTS &amp; INNOVATIONS</text>
      <g transform="translate(20,44)" font-size="12">
        <text x="0" y="15" fill="{C['pc1']}" font-weight="bold">Carrier Lock System</text><text x="170" y="15" fill="{C['pds']}">Automated carrier locking security system for mobile devices</text>
        <text x="0" y="42" fill="{C['pc2']}" font-weight="bold">AdmitOne App</text><text x="170" y="42" fill="{C['pds']}">Smart authentication &amp; ticketing platform with Flutter &amp; Firebase</text>
      </g>
    </g>
  </g>
</g>
</svg>'''


def main():
    repo = r"d:\readme\VandanArora18"
    photo = os.path.join(repo, "photo.jpg")

    print("1/3  Processing photo (background removal + high-res dithering)...")
    pg = process_photo(photo)

    print("2/3  Generating language symbols...")
    sym_groups = [make_symbol(s) for s in SYMBOLS]
    sym_svgs_list = [symbol_svg(sg) for sg in sym_groups]
    print(f"     Symbols: {', '.join(SYMBOLS)}")

    print("3/3  Building SVGs...")
    p = portrait_svg(pg)

    for m in ("dark", "light"):
        out = os.path.join(repo, f"{m}.svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(build_svg(m, p, sym_svgs_list))
        print(f"     {m}.svg -> {os.path.getsize(out):,} bytes")

    print("Done!")


if __name__ == "__main__":
    main()
