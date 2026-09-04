import os
import random
from PIL import Image, ImageEnhance, ImageOps

def process_photo_to_pixels(image_path, target_width=180, target_height=220):
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return []
    
    img = Image.open(image_path).convert('L') # Grayscale
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)
    
    # Resize aspect fit
    img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
    w, h = img.size
    
    # Floyd-Steinberg dithering or threshold
    dithered = img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    
    pixels_by_group = [[] for _ in range(12)] # 12 animation groups
    
    for y in range(h):
        for x in range(w):
            pixel = dithered.getpixel((x, y))
            if pixel == 0: # Black pixel (portrait feature)
                group_idx = (x * 7 + y * 13 + random.randint(0, 5)) % 12
                pixels_by_group[group_idx].append((x, y))
                
    return pixels_by_group, w, h

def generate_svg_pixel_paths(pixels_by_group, scale_x=1.6, scale_y=1.6, start_x=20, start_y=15):
    group_elements = []
    begin_times = [0.15 + i * 0.04 for i in range(len(pixels_by_group))]
    
    for idx, pixels in enumerate(pixels_by_group):
        if not pixels:
            continue
        path_d_list = []
        # Group contiguous pixels horizontally to reduce path size
        pixels_sorted = sorted(pixels, key=lambda p: (p[1], p[0]))
        
        current_y = None
        current_x_start = None
        current_len = 0
        
        for px, py in pixels_sorted:
            scaled_x = int(start_x + px * scale_x)
            scaled_y = int(start_y + py * scale_y)
            
            if py == current_y and px == current_x_start + current_len:
                current_len += 1
            else:
                if current_y is not None:
                    pw = int(current_len * scale_x)
                    ph = int(scale_y)
                    path_d_list.append(f"M{current_x_start_scaled} {current_y_scaled}h{pw}v{ph}h-{pw}z")
                current_y = py
                current_x_start = px
                current_x_start_scaled = scaled_x
                current_y_scaled = scaled_y
                current_len = 1
                
        if current_y is not None:
            pw = int(current_len * scale_x)
            ph = int(scale_y)
            path_d_list.append(f"M{current_x_start_scaled} {current_y_scaled}h{pw}v{ph}h-{pw}z")
            
        path_d = "".join(path_d_list)
        begin_t = f"{begin_times[idx]:.2f}s"
        
        elem = f'''<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.8s" begin="{begin_t}" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/><path d="{path_d}"/></g>'''
        group_elements.append(elem)
        
    return "\n".join(group_elements)

def create_dark_svg(pixel_groups_svg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Vandan Arora — profile.sh --live">
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3B82F6"><animate attributeName="stop-color" values="#3B82F6;#8B5CF6;#06B6D4;#3B82F6" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset="0.5" stop-color="#8B5CF6"><animate attributeName="stop-color" values="#8B5CF6;#06B6D4;#3B82F6;#8B5CF6" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset="1" stop-color="#06B6D4"><animate attributeName="stop-color" values="#06B6D4;#3B82F6;#8B5CF6;#06B6D4" dur="8s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#60A5FA"/>
    <stop offset="0.5" stop-color="#A78BFA"/>
    <stop offset="1" stop-color="#38BDF8"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 -100; 0 100; 0 -100" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#090D16"/>
    <stop offset="1" stop-color="#0F172A"/>
  </linearGradient>
  <filter id="glow8" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8"/></filter>
  <filter id="glow3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="16"/></clipPath>
</defs>

<rect x="2" y="2" width="1176" height="606" rx="16" fill="#030712"/>
<g clip-path="url(#winClip)">
  <rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
  <!-- Top macOS Window Header -->
  <rect x="2" y="2" width="1176" height="44" fill="#0B132B"/>
  <line x1="2" y1="46" x2="1178" y2="46" stroke="rgba(255,255,255,0.08)"/>
  <circle cx="28" cy="23" r="5.5" fill="#FF5F56"/>
  <circle cx="48" cy="23" r="5.5" fill="#FFBD2E"/>
  <circle cx="68" cy="23" r="5.5" fill="#27C93F"/>
  <text x="590" y="27" text-anchor="middle" font-size="12" fill="#94A3B8" font-weight="500">vandanarora18@gmail.com — zsh profile.sh --live</text>

  <!-- Left Visual Map Box -->
  <text x="38" y="74" font-size="10" letter-spacing="3" fill="#64748B" font-weight="bold">AI.SYSTEM.VISUALIZER</text>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="none" stroke="#38BDF8" stroke-width="2" opacity="0.4" filter="url(#glow3)"/>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="#070C18" stroke="rgba(56,189,248,0.3)"/>

  <!-- Pixel Art Portrait Container -->
  <g transform="translate(48, 96)" fill="url(#asciiGrad)" shape-rendering="crispEdges">
    {pixel_groups_svg}
  </g>

  <!-- Left Box Overlay Labels & Live Status -->
  <rect x="52" y="525" width="358" height="36" rx="8" fill="rgba(15,23,42,0.85)" stroke="rgba(56,189,248,0.3)"/>
  <circle cx="70" cy="543" r="4" fill="#10B981">
    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
  </circle>
  <text x="82" y="547" font-size="11" fill="#38BDF8" font-weight="600">SYSTEM STATUS: ACTIVE &amp; BUILDING</text>

  <!-- Right Terminal Info Panel -->
  <g transform="translate(460, 75)">
    <!-- Header Badge -->
    <rect x="0" y="0" width="170" height="24" rx="12" fill="rgba(59,130,246,0.15)" stroke="rgba(59,130,246,0.4)"/>
    <text x="85" y="16" text-anchor="middle" font-size="11" fill="#60A5FA" font-weight="600">⚡ ROBOTICS &amp; AI ENGINEER</text>

    <!-- Name Header -->
    <text x="0" y="58" font-size="28" font-weight="800" fill="#F8FAFC" letter-spacing="-0.5">Vandan Arora</text>
    <text x="0" y="80" font-size="14" fill="#94A3B8">Thapar Institute of Engineering and Technology</text>

    <!-- Bio / Typewriter text lines -->
    <g font-size="13" fill="#E2E8F0">
      <text x="0" y="118">
        <tspan fill="#38BDF8" font-weight="bold">&gt; role:</tspan> AI/ML &amp; Computer Vision Developer
      </text>
      <text x="0" y="144">
        <tspan fill="#38BDF8" font-weight="bold">&gt; focus:</tspan> Intelligent Autonomous Systems, Edge AI &amp; Robotics
      </text>
      <text x="0" y="170">
        <tspan fill="#38BDF8" font-weight="bold">&gt; stack:</tspan> Python, C++, FastAPI, OpenCV, TensorFlow, PyTorch
      </text>
      <text x="0" y="196">
        <tspan fill="#38BDF8" font-weight="bold">&gt; status:</tspan> Open to AI/ML &amp; Robotics Internships / Projects
      </text>
    </g>

    <!-- Divider Line -->
    <line x1="0" y1="220" x2="680" y2="220" stroke="rgba(255,255,255,0.08)"/>

    <!-- Tech Stack Grid Section -->
    <text x="0" y="248" font-size="11" letter-spacing="2" fill="#64748B" font-weight="bold">TECH_STACK // CAPABILITIES</text>

    <!-- Badges Row 1 -->
    <g transform="translate(0, 262)">
      <!-- Python -->
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(56,189,248,0.2)"/>
      <text x="12" y="20" font-size="12" fill="#38BDF8" font-weight="600">🐍 Python</text>

      <!-- C++ -->
      <rect x="115" y="0" width="95" height="32" rx="6" fill="#1E293B" stroke="rgba(139,92,246,0.2)"/>
      <text x="127" y="20" font-size="12" fill="#A78BFA" font-weight="600">⚡ C++</text>

      <!-- OpenCV -->
      <rect x="220" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(16,185,129,0.2)"/>
      <text x="232" y="20" font-size="12" fill="#34D399" font-weight="600">👁️ OpenCV</text>

      <!-- TensorFlow -->
      <rect x="335" y="0" width="125" height="32" rx="6" fill="#1E293B" stroke="rgba(245,158,11,0.2)"/>
      <text x="347" y="20" font-size="12" fill="#FBBF24" font-weight="600">🧠 TensorFlow</text>

      <!-- PyTorch -->
      <rect x="470" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(239,68,68,0.2)"/>
      <text x="482" y="20" font-size="12" fill="#F87171" font-weight="600">🔥 PyTorch</text>
    </g>

    <!-- Badges Row 2 -->
    <g transform="translate(0, 304)">
      <!-- FastAPI -->
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#1E293B" stroke="rgba(16,185,129,0.2)"/>
      <text x="12" y="20" font-size="12" fill="#34D399" font-weight="600">🚀 FastAPI</text>

      <!-- Flutter -->
      <rect x="115" y="0" width="100" height="32" rx="6" fill="#1E293B" stroke="rgba(56,189,248,0.2)"/>
      <text x="127" y="20" font-size="12" fill="#38BDF8" font-weight="600">📱 Flutter</text>

      <!-- ROS / Robotics -->
      <rect x="225" y="0" width="115" height="32" rx="6" fill="#1E293B" stroke="rgba(168,85,247,0.2)"/>
      <text x="237" y="20" font-size="12" fill="#C084FC" font-weight="600">🤖 ROS / AI</text>

      <!-- Git / GitHub -->
      <rect x="350" y="0" width="95" height="32" rx="6" fill="#1E293B" stroke="rgba(148,163,184,0.2)"/>
      <text x="362" y="20" font-size="12" fill="#CBD5E1" font-weight="600">🐙 Git</text>

      <!-- Linux / Docker -->
      <rect x="455" y="0" width="120" height="32" rx="6" fill="#1E293B" stroke="rgba(59,130,246,0.2)"/>
      <text x="467" y="20" font-size="12" fill="#60A5FA" font-weight="600">🐧 Linux/Docker</text>
    </g>

    <!-- Quick Stats Cards Summary Bar inside Terminal -->
    <g transform="translate(0, 356)">
      <rect x="0" y="0" width="675" height="120" rx="10" fill="#070C18" stroke="url(#accent)" stroke-width="1.5"/>
      <text x="20" y="30" font-size="12" fill="#94A3B8" font-weight="600">HIGHLIGHTED PROJECTS &amp; INNOVATIONS</text>

      <g transform="translate(20, 44)" font-size="12">
        <text x="0" y="15" fill="#38BDF8" font-weight="bold">🔹 Carrier Lock System</text>
        <text x="180" y="15" fill="#94A3B8">Automated carrier locking security system for mobile devices</text>

        <text x="0" y="42" fill="#A78BFA" font-weight="bold">🔹 AdmitOne App</text>
        <text x="180" y="42" fill="#94A3B8">Smart authentication &amp; ticketing platform with Flutter &amp; Firebase</text>
      </g>
    </g>

  </g>
</g>
</svg>'''

def create_light_svg(pixel_groups_svg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Vandan Arora — profile.sh --live">
<defs>
  <linearGradient id="accentLight" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#2563EB"><animate attributeName="stop-color" values="#2563EB;#7C3AED;#0284C7;#2563EB" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset="0.5" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#0284C7;#2563EB;#7C3AED" dur="8s" repeatCount="indefinite"/></stop>
    <stop offset="1" stop-color="#0284C7"><animate attributeName="stop-color" values="#0284C7;#2563EB;#7C3AED;#0284C7" dur="8s" repeatCount="indefinite"/></stop>
  </linearGradient>
  <linearGradient id="asciiGradLight" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#2563EB"/>
    <stop offset="0.5" stop-color="#6D28D9"/>
    <stop offset="1" stop-color="#0284C7"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 -100; 0 100; 0 -100" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="panelGradLight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFFFFF"/>
    <stop offset="1" stop-color="#F1F5F9"/>
  </linearGradient>
  <clipPath id="winClipLight"><rect x="2" y="2" width="1176" height="606" rx="16"/></clipPath>
</defs>

<rect x="2" y="2" width="1176" height="606" rx="16" fill="#E2E8F0"/>
<g clip-path="url(#winClipLight)">
  <rect x="2" y="2" width="1176" height="606" fill="url(#panelGradLight)"/>
  <!-- Top macOS Window Header -->
  <rect x="2" y="2" width="1176" height="44" fill="#E2E8F0"/>
  <line x1="2" y1="46" x2="1178" y2="46" stroke="rgba(0,0,0,0.08)"/>
  <circle cx="28" cy="23" r="5.5" fill="#FF5F56"/>
  <circle cx="48" cy="23" r="5.5" fill="#FFBD2E"/>
  <circle cx="68" cy="23" r="5.5" fill="#27C93F"/>
  <text x="590" y="27" text-anchor="middle" font-size="12" fill="#475569" font-weight="500">vandanarora18@gmail.com — zsh profile.sh --live</text>

  <!-- Left Visual Map Box -->
  <text x="38" y="74" font-size="10" letter-spacing="3" fill="#64748B" font-weight="bold">AI.SYSTEM.VISUALIZER</text>
  <rect x="36" y="84" width="390" height="492" rx="12" fill="#F8FAFC" stroke="#0284C7" stroke-width="1.5" opacity="0.8"/>

  <!-- Pixel Art Portrait Container -->
  <g transform="translate(48, 96)" fill="url(#asciiGradLight)" shape-rendering="crispEdges">
    {pixel_groups_svg}
  </g>

  <!-- Left Box Overlay Labels & Live Status -->
  <rect x="52" y="525" width="358" height="36" rx="8" fill="#FFFFFF" stroke="rgba(2,132,199,0.3)"/>
  <circle cx="70" cy="543" r="4" fill="#059669">
    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
  </circle>
  <text x="82" y="547" font-size="11" fill="#0284C7" font-weight="600">SYSTEM STATUS: ACTIVE &amp; BUILDING</text>

  <!-- Right Terminal Info Panel -->
  <g transform="translate(460, 75)">
    <!-- Header Badge -->
    <rect x="0" y="0" width="170" height="24" rx="12" fill="rgba(37,99,235,0.1)" stroke="rgba(37,99,235,0.3)"/>
    <text x="85" y="16" text-anchor="middle" font-size="11" fill="#2563EB" font-weight="600">⚡ ROBOTICS &amp; AI ENGINEER</text>

    <!-- Name Header -->
    <text x="0" y="58" font-size="28" font-weight="800" fill="#0F172A" letter-spacing="-0.5">Vandan Arora</text>
    <text x="0" y="80" font-size="14" fill="#475569">Thapar Institute of Engineering and Technology</text>

    <!-- Bio / Typewriter text lines -->
    <g font-size="13" fill="#1E293B">
      <text x="0" y="118">
        <tspan fill="#0284C7" font-weight="bold">&gt; role:</tspan> AI/ML &amp; Computer Vision Developer
      </text>
      <text x="0" y="144">
        <tspan fill="#0284C7" font-weight="bold">&gt; focus:</tspan> Intelligent Autonomous Systems, Edge AI &amp; Robotics
      </text>
      <text x="0" y="170">
        <tspan fill="#0284C7" font-weight="bold">&gt; stack:</tspan> Python, C++, FastAPI, OpenCV, TensorFlow, PyTorch
      </text>
      <text x="0" y="196">
        <tspan fill="#0284C7" font-weight="bold">&gt; status:</tspan> Open to AI/ML &amp; Robotics Internships / Projects
      </text>
    </g>

    <!-- Divider Line -->
    <line x1="0" y1="220" x2="680" y2="220" stroke="rgba(0,0,0,0.08)"/>

    <!-- Tech Stack Grid Section -->
    <text x="0" y="248" font-size="11" letter-spacing="2" fill="#64748B" font-weight="bold">TECH_STACK // CAPABILITIES</text>

    <!-- Badges Row 1 -->
    <g transform="translate(0, 262)">
      <!-- Python -->
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#F1F5F9" stroke="rgba(2,132,199,0.3)"/>
      <text x="12" y="20" font-size="12" fill="#0284C7" font-weight="600">🐍 Python</text>

      <!-- C++ -->
      <rect x="115" y="0" width="95" height="32" rx="6" fill="#F1F5F9" stroke="rgba(109,40,217,0.3)"/>
      <text x="127" y="20" font-size="12" fill="#6D28D9" font-weight="600">⚡ C++</text>

      <!-- OpenCV -->
      <rect x="220" y="0" width="105" height="32" rx="6" fill="#F1F5F9" stroke="rgba(5,150,105,0.3)"/>
      <text x="232" y="20" font-size="12" fill="#059669" font-weight="600">👁️ OpenCV</text>

      <!-- TensorFlow -->
      <rect x="335" y="0" width="125" height="32" rx="6" fill="#F1F5F9" stroke="rgba(217,119,6,0.3)"/>
      <text x="347" y="20" font-size="12" fill="#D97706" font-weight="600">🧠 TensorFlow</text>

      <!-- PyTorch -->
      <rect x="470" y="0" width="105" height="32" rx="6" fill="#F1F5F9" stroke="rgba(220,38,38,0.3)"/>
      <text x="482" y="20" font-size="12" fill="#DC2626" font-weight="600">🔥 PyTorch</text>
    </g>

    <!-- Badges Row 2 -->
    <g transform="translate(0, 304)">
      <!-- FastAPI -->
      <rect x="0" y="0" width="105" height="32" rx="6" fill="#F1F5F9" stroke="rgba(5,150,105,0.3)"/>
      <text x="12" y="20" font-size="12" fill="#059669" font-weight="600">🚀 FastAPI</text>

      <!-- Flutter -->
      <rect x="115" y="0" width="100" height="32" rx="6" fill="#F1F5F9" stroke="rgba(2,132,199,0.3)"/>
      <text x="127" y="20" font-size="12" fill="#0284C7" font-weight="600">📱 Flutter</text>

      <!-- ROS / Robotics -->
      <rect x="225" y="0" width="115" height="32" rx="6" fill="#F1F5F9" stroke="rgba(147,51,234,0.3)"/>
      <text x="237" y="20" font-size="12" fill="#9333EA" font-weight="600">🤖 ROS / AI</text>

      <!-- Git / GitHub -->
      <rect x="350" y="0" width="95" height="32" rx="6" fill="#F1F5F9" stroke="rgba(71,85,105,0.3)"/>
      <text x="362" y="20" font-size="12" fill="#475569" font-weight="600">🐙 Git</text>

      <!-- Linux / Docker -->
      <rect x="455" y="0" width="120" height="32" rx="6" fill="#F1F5F9" stroke="rgba(37,99,235,0.3)"/>
      <text x="467" y="20" font-size="12" fill="#2563EB" font-weight="600">🐧 Linux/Docker</text>
    </g>

    <!-- Quick Stats Cards Summary Bar inside Terminal -->
    <g transform="translate(0, 356)">
      <rect x="0" y="0" width="675" height="120" rx="10" fill="#FFFFFF" stroke="url(#accentLight)" stroke-width="1.5"/>
      <text x="20" y="30" font-size="12" fill="#64748B" font-weight="600">HIGHLIGHTED PROJECTS &amp; INNOVATIONS</text>

      <g transform="translate(20, 44)" font-size="12">
        <text x="0" y="15" fill="#0284C7" font-weight="bold">🔹 Carrier Lock System</text>
        <text x="180" y="15" fill="#475569">Automated carrier locking security system for mobile devices</text>

        <text x="0" y="42" fill="#6D28D9" font-weight="bold">🔹 AdmitOne App</text>
        <text x="180" y="42" fill="#475569">Smart authentication &amp; ticketing platform with Flutter &amp; Firebase</text>
      </g>
    </g>

  </g>
</g>
</svg>'''

def main():
    repo_dir = "d:\\readme\\VandanArora18"
    photo_path = os.path.join(repo_dir, "photo.jpg")
    
    print(f"Processing photo: {photo_path}")
    pixels_by_group, w, h = process_photo_to_pixels(photo_path)
    
    # Calculate scale to fit inside 360x410 pixels
    scale_x = round(360 / w, 2)
    scale_y = round(410 / h, 2)
    
    pixel_groups_svg = generate_svg_pixel_paths(pixels_by_group, scale_x=scale_x, scale_y=scale_y)
    
    dark_svg_content = create_dark_svg(pixel_groups_svg)
    light_svg_content = create_light_svg(pixel_groups_svg)
    
    dark_path = os.path.join(repo_dir, "dark.svg")
    light_path = os.path.join(repo_dir, "light.svg")
    
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg_content)
    print(f"Generated: {dark_path} ({os.path.getsize(dark_path)} bytes)")
    
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg_content)
    print(f"Generated: {light_path} ({os.path.getsize(light_path)} bytes)")

if __name__ == "__main__":
    main()
