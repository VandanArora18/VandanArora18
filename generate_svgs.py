#!/usr/bin/env python3
"""
Generate animated theme-aware SVG hero banners for GitHub profile.
Features:
  - Multi-tone layer quantization (Step 1)
  - Compact SVG horizontal path merging (Step 2)
  - Staggered layer reveal animation (Step 3)
  - Terminal chrome with animated gradient text (Step 4)
  - Scanline/glitch overlay effect (Step 5)
  - Morphing transitions with symbols
"""
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

# ── Config ───────────────────────────────────────────────────────────
CW, CH = 220, 280  # Low-res grid as per step 1
SYMBOLS = ["</>", "Py", "SQL", "{f}", "V"]
N_PHASES = 1 + len(SYMBOLS)
CYC_D = 18.0       # cycle period
CYC_T = 3.5        # start cycle after initial reveal

# ── Helpers ──────────────────────────────────────────────────────────
def _font(size):
    for p in ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

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

# ── Image Processing (Step 1 & 2) ────────────────────────────────────
def process_photo_tones(path):
    img = Image.open(path).convert('L')
    # Resize to low-res grid
    img.thumbnail((CW, CH), Image.Resampling.LANCZOS)
    
    # Background mask (assuming background is very dark)
    mask = img.point(lambda p: 255 if p >= 25 else 0, mode='1')
    
    # Enhance
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    
    w, h = img.size
    px, mx = img.load(), mask.load()
    
    # 3 tones: 1 (Dark), 2 (Mid), 3 (Light)
    tones = {1: [], 2: [], 3: []}
    for y in range(h):
        for x in range(w):
            if mx[x, y] == 0: continue
            v = px[x, y]
            if v < 60: continue
            elif v < 130: tones[1].append((x, y))
            elif v < 190: tones[2].append((x, y))
            else: tones[3].append((x, y))
            
    # Center offsets on canvas
    ox, oy = (CW - w) // 2, (CH - h) // 2
    for k in tones:
        tones[k] = [(x+ox, y+oy) for x, y in tones[k]]
        
    return tones

def make_symbol_tones(text):
    img = Image.new('L', (CW, CH), 0)
    draw = ImageDraw.Draw(img)
    for sz in range(200, 40, -8):
        f = _font(sz)
        bb = draw.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw < CW * 0.85 and th < CH * 0.65: break
    
    draw.text(((CW - tw) // 2 - bb[0], (CH - th) // 2 - bb[1]), text, font=f, fill=255)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
    
    px = img.load()
    tones = {1: [], 2: [], 3: []}
    for y in range(CH):
        for x in range(CW):
            v = px[x, y]
            if v < 40: continue
            elif v < 100: tones[1].append((x, y))
            elif v < 180: tones[2].append((x, y))
            else: tones[3].append((x, y))
    return tones

# ── Animation (Step 3) ───────────────────────────────────────────────
def _cycle_anim(phase_i, tone_i):
    p = 1.0 / N_PHASES
    tr = 0.02
    s, e = phase_i * p, (phase_i + 1) * p
    off = (tone_i - 1) * 0.025  # Stagger layers: darkest first
    
    def clamp(val): return max(0.0, min(1.0, val))
    t1, t2 = clamp(s - tr + off), clamp(s + tr + off)
    t3, t4 = clamp(e - tr + off), clamp(e + tr + off)
    
    if phase_i == 0:
        v = "1;1;0;0;1"
        k = f"0;{t3:.4f};{t4:.4f};{clamp(1-tr+off):.4f};1"
        t_rev = 0.2 + (tone_i - 1) * 0.4
        anim = f'<animate attributeName="opacity" values="0;1" dur="1.2s" begin="{t_rev:.3f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
        anim += f'<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{CYC_D}s" begin="{CYC_T}s" repeatCount="indefinite"/>'
    else:
        if phase_i == N_PHASES - 1:
            v = "0;0;1;1;0"
            k = f"0;{t1:.4f};{t2:.4f};{clamp(1-tr+off):.4f};1"
        else:
            v = "0;0;1;1;0;0"
            k = f"0;{t1:.4f};{t2:.4f};{t3:.4f};{t4:.4f};1"
        anim = f'<animate attributeName="opacity" values="{v}" keyTimes="{k}" dur="{CYC_D}s" begin="{CYC_T}s" repeatCount="indefinite"/>'
    return anim

# ── SVG Builders (Step 4 & 5) ────────────────────────────────────────
def build_svg(mode, p_tones, sym_tones_list):
    dk = mode == "dark"
    sfx = "" if dk else "L"
    sx, sy = round(360 / CW, 4), round(420 / CH, 4)
    
    # 3-Tone Palette
    if dk:
        tc = {1: "#1E293B", 2: "#38BDF8", 3: "#F8FAFC"} # Slate, Sky, White
        C = {'bg': "#030712", 'hdr': "#0B132B", 'hln': "rgba(255,255,255,0.08)", 'bxf': "#070C18", 'bxa': "rgba(56,189,248,0.3)"}
    else:
        tc = {1: "#94A3B8", 2: "#0284C7", 3: "#0F172A"} # Slate, Sky, Dark
        C = {'bg': "#E2E8F0", 'hdr': "#F8FAFC", 'hln': "rgba(0,0,0,0.08)", 'bxf': "#FFFFFF", 'bxa': "rgba(2,132,199,0.3)"}

    # Art layers
    art_parts = []
    # Portrait
    art_parts.append('    <g>')
    for ti in (1, 2, 3):
        d = _path(p_tones[ti])
        if not d: continue
        art_parts.append(f'      <g opacity="0" fill="{tc[ti]}">{_cycle_anim(0, ti)}<path d="{d}"/></g>')
    art_parts.append('    </g>')
    # Symbols
    for phase_i, s_tones in enumerate(sym_tones_list, 1):
        art_parts.append('    <g>')
        for ti in (1, 2, 3):
            d = _path(s_tones[ti])
            if not d: continue
            art_parts.append(f'      <g opacity="0" fill="{tc[ti]}">{_cycle_anim(phase_i, ti)}<path d="{d}"/></g>')
        art_parts.append('    </g>')
    art_block = "\n".join(art_parts)

    # Step 5: Scanline effect
    glitch_anim = (
        f'<use href="#tvlight" y="0"><animate attributeName="y" values="-100;500;-100" dur="8s" repeatCount="indefinite"/></use>'
        f'<use href="#tvlight" y="200" opacity="0.5"><animate attributeName="y" values="500;-100;500" dur="6s" repeatCount="indefinite"/></use>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610"
  font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
  role="img" aria-label="Vandan Arora - profile.sh --live">
<defs>
  <!-- Animated gradient for title -->
  <linearGradient id="textGrad{sfx}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#38BDF8">
      <animate attributeName="stop-color" values="#38BDF8;#A78BFA;#34D399;#38BDF8" dur="8s" repeatCount="indefinite"/>
    </stop>
    <stop offset="50%" stop-color="#A78BFA">
      <animate attributeName="stop-color" values="#A78BFA;#34D399;#38BDF8;#A78BFA" dur="8s" repeatCount="indefinite"/>
    </stop>
    <stop offset="100%" stop-color="#34D399">
      <animate attributeName="stop-color" values="#34D399;#38BDF8;#A78BFA;#34D399" dur="8s" repeatCount="indefinite"/>
    </stop>
  </linearGradient>
  
  <filter id="glow"><feGaussianBlur stdDeviation="4" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="wc{sfx}"><rect x="2" y="2" width="1176" height="606" rx="16"/></clipPath>
  
  <!-- Scanline / TV light symbol -->
  <symbol id="tvlight"><rect width="390" height="20" fill="url(#scanGrad{sfx})" opacity="0.15"/></symbol>
  <linearGradient id="scanGrad{sfx}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{tc[2]}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{tc[2]}" stop-opacity="1"/>
    <stop offset="100%" stop-color="{tc[2]}" stop-opacity="0"/>
  </linearGradient>
</defs>

<rect x="2" y="2" width="1176" height="606" rx="16" fill="{C['bg']}"/>
<g clip-path="url(#wc{sfx})">
  <!-- Window Chrome -->
  <rect x="2" y="2" width="1176" height="606" fill="{C['bg']}"/>
  <rect x="2" y="2" width="1176" height="44" fill="{C['hdr']}"/>
  <line x1="2" y1="46" x2="1178" y2="46" stroke="{C['hln']}"/>
  <circle cx="28" cy="23" r="5.5" fill="#FF5F56"/>
  <circle cx="48" cy="23" r="5.5" fill="#FFBD2E"/>
  <circle cx="68" cy="23" r="5.5" fill="#27C93F"/>
  <text x="590" y="27" text-anchor="middle" font-size="13" fill="#64748B" font-weight="600">user@vandan - % ./profile.sh --live</text>

  <!-- Left Side: Art Panel -->
  <text x="38" y="74" font-size="10" letter-spacing="3" fill="#64748B" font-weight="bold">AI.SYSTEM.VISUALIZER</text>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="{C['bxf']}" stroke="{C['bxa']}"/>

  <!-- Pixel Art container -->
  <g transform="translate(48,96) scale({sx},{sy})" shape-rendering="crispEdges">
{art_block}
  </g>
  
  <!-- Scanline overlay clipped to art box -->
  <g transform="translate(36,84)">
    <svg width="390" height="492">
      {glitch_anim}
    </svg>
  </g>

  <!-- Status Bar -->
  <rect x="52" y="525" width="358" height="36" rx="8" fill="rgba(15,23,42,0.85)" stroke="{C['bxa']}"/>
  <circle cx="70" cy="543" r="4" fill="#10B981"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
  <text x="82" y="547" font-size="11" fill="#38BDF8" font-weight="600">SYSTEM STATUS: ACTIVE &amp; BUILDING</text>

  <!-- Right Side: Info Panel -->
  <g transform="translate(460,75)">
    <rect x="0" y="0" width="170" height="24" rx="12" fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.4)"/>
    <text x="85" y="16" text-anchor="middle" font-size="11" fill="#60A5FA" font-weight="600">ROBOTICS &amp; AI ENGINEER</text>
    
    <!-- Title with animated gradient -->
    <text x="0" y="58" font-size="32" font-weight="800" fill="url(#textGrad{sfx})" filter="url(#glow)" letter-spacing="-0.5">Vandan Arora</text>
    <text x="0" y="80" font-size="14" fill="#94A3B8">Thapar Institute of Engineering and Technology</text>

    <!-- Rest of the details (hardcoded colors for simplicity in dark/light mode for this demo) -->
    <g font-size="13" fill="#E2E8F0">
      <text x="0" y="118"><tspan fill="#38BDF8" font-weight="bold">&gt; role:</tspan> AI/ML &amp; Computer Vision Developer</text>
      <text x="0" y="144"><tspan fill="#38BDF8" font-weight="bold">&gt; focus:</tspan> Intelligent Autonomous Systems, Edge AI &amp; Robotics</text>
      <text x="0" y="170"><tspan fill="#38BDF8" font-weight="bold">&gt; stack:</tspan> Python, C++, FastAPI, OpenCV, TensorFlow, PyTorch</text>
      <text x="0" y="196"><tspan fill="#38BDF8" font-weight="bold">&gt; status:</tspan> Open to AI/ML &amp; Robotics Internships / Projects</text>
    </g>

    <line x1="0" y1="220" x2="680" y2="220" stroke="rgba(255,255,255,0.08)"/>
    <text x="0" y="248" font-size="11" letter-spacing="2" fill="#64748B" font-weight="bold">TECH_STACK // CAPABILITIES</text>

    <!-- Tech Badges -->
    <g transform="translate(0,262)">
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(56,189,248,0.2)"/><text x="12" y="20" font-size="12" fill="#38BDF8" font-weight="600">Python</text>
      <rect x="115" y="0" width="95" height="32" rx="6" fill="#1E293B" stroke="rgba(139,92,246,0.2)"/><text x="127" y="20" font-size="12" fill="#A78BFA" font-weight="600">C++</text>
      <rect x="220" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(16,185,129,0.2)"/><text x="232" y="20" font-size="12" fill="#34D399" font-weight="600">OpenCV</text>
      <rect x="335" y="0" width="125" height="32" rx="6" fill="#1E293B" stroke="rgba(245,158,11,0.2)"/><text x="347" y="20" font-size="12" fill="#FBBF24" font-weight="600">TensorFlow</text>
      <rect x="470" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(239,68,68,0.2)"/><text x="482" y="20" font-size="12" fill="#F87171" font-weight="600">PyTorch</text>
    </g>
    <g transform="translate(0,304)">
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(16,185,129,0.2)"/><text x="12" y="20" font-size="12" fill="#34D399" font-weight="600">FastAPI</text>
      <rect x="115" y="0" width="100" height="32" rx="6" fill="#1E293B" stroke="rgba(56,189,248,0.2)"/><text x="127" y="20" font-size="12" fill="#38BDF8" font-weight="600">Flutter</text>
      <rect x="225" y="0" width="115" height="32" rx="6" fill="#1E293B" stroke="rgba(168,85,247,0.2)"/><text x="237" y="20" font-size="12" fill="#C084FC" font-weight="600">ROS / AI</text>
      <rect x="350" y="0" width="95" height="32" rx="6" fill="#1E293B" stroke="rgba(148,163,184,0.2)"/><text x="362" y="20" font-size="12" fill="#CBD5E1" font-weight="600">Git</text>
      <rect x="455" y="0" width="120" height="32" rx="6" fill="#1E293B" stroke="rgba(59,130,246,0.2)"/><text x="467" y="20" font-size="12" fill="#60A5FA" font-weight="600">Linux/Docker</text>
    </g>

    <g transform="translate(0,356)">
      <rect x="0" y="0" width="675" height="120" rx="10" fill="#070C18" stroke="url(#textGrad{sfx})" stroke-width="1.5"/>
      <text x="20" y="30" font-size="12" fill="#94A3B8" font-weight="600">HIGHLIGHTED PROJECTS &amp; INNOVATIONS</text>
      <g transform="translate(20,44)" font-size="12">
        <text x="0" y="15" fill="#38BDF8" font-weight="bold">Carrier Lock System</text><text x="170" y="15" fill="#94A3B8">Automated carrier locking security system for mobile devices</text>
        <text x="0" y="42" fill="#A78BFA" font-weight="bold">AdmitOne App</text><text x="170" y="42" fill="#94A3B8">Smart authentication &amp; ticketing platform with Flutter &amp; Firebase</text>
      </g>
    </g>
  </g>
</g>
</svg>'''

def main():
    repo = r"d:\readme\VandanArora18"
    photo = os.path.join(repo, "photo.jpg")

    print("1/3  Processing photo (multi-tone logic)...")
    p_tones = process_photo_tones(photo)

    print("2/3  Generating symbol tones...")
    sym_tones = [make_symbol_tones(s) for s in SYMBOLS]
    print(f"     Symbols: {', '.join(SYMBOLS)}")

    print("3/3  Building SVGs...")
    for m in ("dark", "light"):
        out = os.path.join(repo, f"{m}.svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(build_svg(m, p_tones, sym_tones))
        print(f"     {m}.svg -> {os.path.getsize(out):,} bytes")

    print("Done!")

if __name__ == "__main__":
    main()
