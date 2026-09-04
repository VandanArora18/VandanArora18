import base64

def get_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

grab_scale_b64 = get_base64("grabscale_logo.png")
carrier_lock_b64 = get_base64("carrierlock_logo.png")

svg = f"""<svg width="1000" height="220" viewBox="0 0 1000 220" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <style>
      .bg {{ fill: transparent; }}
      .card-bg {{ fill: #070C18; stroke: #1E293B; stroke-width: 1.5; rx: 12; }}
      .title {{ fill: #F8FAFC; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: bold; font-size: 16px; }}
      .desc {{ fill: #94A3B8; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
      .tag-bg {{ fill: rgba(167, 139, 250, 0.15); stroke: rgba(167, 139, 250, 0.3); stroke-width: 1; rx: 10; }}
      .tag-text {{ fill: #A78BFA; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 10px; font-weight: bold; }}
      .stat-text {{ fill: #64748B; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; }}
      .ring-bg {{ fill: none; stroke: #1E293B; stroke-width: 6; }}
      .repo-title {{ fill: #64748B; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; }}
      .proj-list-title {{ fill: #38BDF8; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; font-weight: bold; letter-spacing: 1px; }}
    </style>
    
    <clipPath id="imgClip"><rect width="48" height="48" rx="8"/></clipPath>
  </defs>

  <rect width="1000" height="220" class="bg" />
  
  <text x="20" y="30" class="proj-list-title">PROJECTS.LIST  ./projects.sh --all</text>

  <!-- CARD 1: GrabScale -->
  <g transform="translate(20, 50)">
    <rect width="470" height="150" class="card-bg"/>
    <circle cx="15" cy="15" r="3" fill="#38BDF8"/>
    <text x="25" y="19" class="repo-title">VandanArora18/GrabScale</text>
    <circle cx="455" cy="15" r="3" fill="#1E293B"/>
    
    <g transform="translate(15, 45)">
      <g clip-path="url(#imgClip)">
        <image href="data:image/png;base64,{grab_scale_b64}" width="48" height="48" />
      </g>
      <text x="65" y="16" class="title">GrabScale_</text>
      <text x="65" y="38" class="desc">Smart dimensioning platform</text>
      
      <!-- Tags -->
      <rect x="65" y="55" width="60" height="20" class="tag-bg"/>
      <text x="95" y="69" class="tag-text" text-anchor="middle">Flutter</text>
      <rect x="130" y="55" width="60" height="20" class="tag-bg"/>
      <text x="160" y="69" class="tag-text" text-anchor="middle">FastAPI</text>
      <rect x="195" y="55" width="65" height="20" class="tag-bg"/>
      <text x="227.5" y="69" class="tag-text" text-anchor="middle">Firebase</text>
      
      <text x="65" y="92" class="stat-text">★ 12   updated 2d ago</text>
    </g>
    
    <!-- Circular Chart for Card 1 (Right side) -->
    <g transform="translate(430, 85)">
      <circle r="26" class="ring-bg"/>
      <!-- Dart 60%, Python 40% -->
      <circle r="26" fill="none" stroke="#38BDF8" stroke-width="6" stroke-dasharray="98 163.3" transform="rotate(-90)"/>
      <circle r="26" fill="none" stroke="#34D399" stroke-width="6" stroke-dasharray="65.3 163.3" transform="rotate(126)"/>
      <text y="4" text-anchor="middle" fill="#F8FAFC" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="12" font-weight="bold">60%</text>
    </g>
    <g transform="translate(390, 65)">
      <text x="0" y="0" class="stat-text" fill="#94A3B8" text-anchor="end">Dart 60%</text>
      <circle cx="-55" cy="-3" r="3" fill="#38BDF8"/>
      <text x="0" y="15" class="stat-text" fill="#94A3B8" text-anchor="end">Python 40%</text>
      <circle cx="-65" cy="12" r="3" fill="#34D399"/>
    </g>
  </g>

  <!-- CARD 2: Carrier Lock -->
  <g transform="translate(510, 50)">
    <rect width="470" height="150" class="card-bg"/>
    <circle cx="15" cy="15" r="3" fill="#A78BFA"/>
    <text x="25" y="19" class="repo-title">VandanArora18/CarrierLock</text>
    <circle cx="455" cy="15" r="3" fill="#1E293B"/>
    
    <g transform="translate(15, 45)">
      <g clip-path="url(#imgClip)">
        <image href="data:image/png;base64,{carrier_lock_b64}" width="48" height="48" />
      </g>
      <text x="65" y="16" class="title">CarrierLock_</text>
      <text x="65" y="38" class="desc">Automated carrier locking security</text>
      
      <!-- Tags -->
      <rect x="65" y="55" width="60" height="20" class="tag-bg"/>
      <text x="95" y="69" class="tag-text" text-anchor="middle">Flutter</text>
      <rect x="130" y="55" width="65" height="20" class="tag-bg"/>
      <text x="162.5" y="69" class="tag-text" text-anchor="middle">Firebase</text>
      
      <text x="65" y="92" class="stat-text">★ 8    updated 5d ago</text>
    </g>
    
    <!-- Circular Chart for Card 2 (Right side) -->
    <g transform="translate(430, 85)">
      <circle r="26" class="ring-bg"/>
      <!-- Dart 85%, Java 15% -->
      <circle r="26" fill="none" stroke="#A78BFA" stroke-width="6" stroke-dasharray="138.8 163.3" transform="rotate(-90)"/>
      <circle r="26" fill="none" stroke="#F59E0B" stroke-width="6" stroke-dasharray="24.5 163.3" transform="rotate(216)"/>
      <text y="4" text-anchor="middle" fill="#F8FAFC" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" font-size="12" font-weight="bold">85%</text>
    </g>
    <g transform="translate(390, 65)">
      <text x="0" y="0" class="stat-text" fill="#94A3B8" text-anchor="end">Dart 85%</text>
      <circle cx="-55" cy="-3" r="3" fill="#A78BFA"/>
      <text x="0" y="15" class="stat-text" fill="#94A3B8" text-anchor="end">Java 15%</text>
      <circle cx="-55" cy="12" r="3" fill="#F59E0B"/>
    </g>
  </g>

</svg>
"""

with open("projects.svg", "w", encoding="utf-8") as f:
    f.write(svg)
