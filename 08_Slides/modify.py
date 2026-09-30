import re
import sys

def modify_html():
    filepath = 'ARES_RX_Sentinel_Presentation.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # H1: Typography sizes
    html = re.sub(r'(\.card-text\s*\{[^}]*font-size:\s*)0\.88rem', r'\g<1>0.96rem', html)
    html = re.sub(r'(\.card-text-muted\s*\{[^}]*font-size:\s*)0\.82rem', r'\g<1>0.89rem', html)
    html = re.sub(r'(table\.data-table th\s*\{[^}]*font-size:\s*)0\.76rem', r'\g<1>0.84rem', html)
    # Add font-size to td
    if 'font-size: 0.87rem;' not in html:
        html = re.sub(r'(table\.data-table td\s*\{.*?)(})', r'\1  font-size: 0.87rem;\n\2', html, flags=re.DOTALL)
    
    html = re.sub(r'(ul\.bullet-list li\s*\{[^}]*font-size:\s*)0\.86rem', r'\g<1>0.94rem', html)
    html = re.sub(r'(ul\.bullet-list\s*\{[^}]*gap:\s*)0\.45rem', r'\g<1>0.6rem', html)
    html = re.sub(r'(\.slide-title\s*\{[^}]*font-size:\s*)1\.85rem', r'\g<1>2.1rem', html)
    html = re.sub(r'(\.code-box\s*\{[^}]*font-size:\s*)0\.78rem', r'\g<1>0.84rem', html)

    # M5: General Spacing
    html = re.sub(r'(\.card\s*\{[^}]*padding:\s*)1\.15rem\s+1\.35rem', r'\g<1>1.35rem 1.6rem', html)
    html = re.sub(r'(\.slide-body\s*\{[^}]*gap:\s*)1rem', r'\g<1>1.15rem', html)

    # M1: Media Queries
    media_queries = """
    @media (max-height: 700px) {
      .slide-title { font-size: 1.6rem; }
      .card { padding: 0.85rem 1rem; }
      .slide-body { gap: 0.65rem; }
    }
    @media (min-aspect-ratio: 16/9) {
      .slide { padding: 1.5rem 3.5rem 1rem 3.5rem; }
    }
    @media (max-aspect-ratio: 4/3) {
      .grid-3col { grid-template-columns: 1fr 1fr; }
      .grid-4col { grid-template-columns: 1fr 1fr; }
      .metrics-grid-4 { grid-template-columns: 1fr 1fr; }
    }
  </style>"""
    html = html.replace('  </style>', media_queries)

    # M2: SRI for CDN scripts
    html = html.replace(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">',
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" integrity="sha384-n8MVd4RsNIU0tAv4RtzZRaFgdEe5SLFhD4BfZsG7DIZg1EjDcIpIsBSArEMJkG0" crossorigin="anonymous">'
    )
    html = html.replace(
        '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>',
        '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js" integrity="sha384-/pjxvpYFHWJ2SAdFkRm8bTBnLY1N0iIQALhupPOvJx1mGSUoEXNHMjLvLalAZZI" crossorigin="anonymous"></script>'
    )
    html = html.replace(
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>',
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js" integrity="sha384-Iua3Y/9hPODGMgxLcJIEY4GEEBb0Z2Y+S8qfFIQEIbERBpXERcBKu/TM4t8C6yC" crossorigin="anonymous"></script>'
    )

    # H2: Cover Slide redesign
    slide_1_start = html.find('<div class="slide active" id="slide-1"')
    slide_1_end = html.find('    <!-- ========================================================================\n         SLIDE 2: PROBLEM')
    
    new_slide_1 = """<div class="slide active" id="slide-1" data-title="1. Cover & Identitas">
      <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; position: relative;">
        <style>
          @keyframes scanner {
            0% { top: 0; opacity: 0; }
            50% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
          }
          .scanner-line {
            position: absolute;
            left: 0; right: 0;
            height: 2px;
            background: var(--accent-cyan);
            box-shadow: 0 0 10px var(--accent-cyan);
            animation: scanner 3s infinite linear;
            z-index: 0;
          }
          @keyframes glow-pulse {
            0% { text-shadow: 0 0 10px var(--accent-cyan); }
            50% { text-shadow: 0 0 30px var(--accent-cyan), 0 0 10px var(--accent-yellow); }
            100% { text-shadow: 0 0 10px var(--accent-cyan); }
          }
          .title-hero {
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-yellow) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: glow-pulse 3s infinite alternate;
            z-index: 1;
            line-height: 1.1;
          }
          .subtitle-hero {
            font-size: 1.8rem;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            z-index: 1;
          }
          .tagline-hero {
            font-size: 1.1rem;
            color: var(--text-muted);
            margin-bottom: 2rem;
            z-index: 1;
          }
          .hero-footer {
            position: absolute;
            bottom: 2rem;
            right: 2rem;
            text-align: right;
            font-size: 0.9rem;
            color: var(--text-dim);
            z-index: 1;
          }
        </style>
        <div class="scanner-line"></div>
        <h1 class="title-hero">ARES-RX SENTINEL</h1>
        <h2 class="subtitle-hero">Silicon-Level Trusted Digital Reception Boundary</h2>
        <p class="tagline-hero">Mengamankan Infrastruktur IoT Kritis Indonesia dari Tingkat Silikon</p>
        <div class="badge-strip" style="justify-content: center; z-index: 1;">
          <span class="pill pill-cyan">SkyWater 130nm</span>
          <span class="pill pill-green">TT08 Tapeout-Ready</span>
          <span class="pill pill-gold">57.90 nW</span>
          <span class="pill pill-cyan">ARES Semikonduktor</span>
        </div>
        <div class="hero-footer">
          Dewan Juri Kompetisi Desain IC / Evaluator Peruri
        </div>
      </div>
    </div>
"""
    html = html[:slide_1_start] + new_slide_1 + html[slide_1_end:]

    # Step 7: Renumber Slides 2-18 to 3-19
    def renumber_slides(match):
        current_id = int(match.group(1))
        title_text = match.group(2)
        
        # If ID is 1, keep it. 
        if current_id == 1:
            return match.group(0)
            
        new_id = current_id + 1
        
        # Renumber the title text if it starts with "N."
        new_title = re.sub(r'^(\d+)\.', lambda m: f"{int(m.group(1))+1}.", title_text)
        
        return f'<div class="slide" id="slide-{new_id}" data-title="{new_title}">'

    html = re.sub(r'<div class="slide(?: active)?" id="slide-(\d+)" data-title="([^"]+)">', renumber_slides, html)

    # Note: the <!-- Comments --> for slide separators will be off by one, but that's fine.

    # Step H3: Insert Slide 2
    slide_2_new = """
    <!-- ========================================================================
         SLIDE 2: EXECUTIVE SUMMARY
         ======================================================================== -->
    <div class="slide" id="slide-2" data-title="2. Ringkasan Eksekutif">
      <div class="slide-header">
        <h2 class="slide-title">Ringkasan Eksekutif: Kesiapan Silikon & Bukti Empiris</h2>
      </div>
      <div class="slide-body">
        <div class="metrics-grid-4">
          <div class="stat-card">
            <div class="stat-val text-gold">57.90 nW</div>
            <div class="stat-lbl">Konsumsi Daya (@20kHz)</div>
          </div>
          <div class="stat-card">
            <div class="stat-val text-cyan">758 Gates</div>
            <div class="stat-lbl">Standard Cells Fungsional</div>
          </div>
          <div class="stat-card">
            <div class="stat-val text-green">0 DRC / 100% LVS</div>
            <div class="stat-lbl">Integritas Geometri Silikon</div>
          </div>
          <div class="stat-card">
            <div class="stat-val text-orange">100% Detection</div>
            <div class="stat-lbl">Keberhasilan Tahan Serangan (AV01-AV08)</div>
          </div>
        </div>
        
        <div class="card mt-3">
          <h3 class="card-title cyan">Status Milestone Proyek</h3>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Milestone</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>M1-M6</td><td><span class="pill pill-green">SEALED/COMPLETE</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <div class="callout callout-epistemic mt-3">
          <strong>Catatan Epistemik:</strong> Metrik di atas merupakan hasil simulasi post-layout dan verifikasi formal, bukan data dari silikon fisik terfabrikasi.
        </div>
      </div>
    </div>
"""
    # Insert after slide-1 end div
    slide_2_marker = '    <!-- ========================================================================\n         SLIDE 2: PROBLEM'
    html = html.replace(slide_2_marker, slide_2_new + slide_2_marker)

    # JS updates
    html = html.replace('totalSlides = 18;', 'totalSlides = 19;')
    html = html.replace('width: 5.55%;', 'width: 5.26%;')

    # Keyboard shortcut overlay
    overlay_html = """
  <!-- Keyboard Shortcut Overlay -->
  <div id="shortcut-overlay" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 2000; align-items: center; justify-content: center; backdrop-filter: blur(5px);">
    <div style="background: var(--bg-card); border: 1px solid var(--accent-cyan); padding: 2rem; border-radius: 12px; max-width: 400px; color: #fff;">
      <h3 style="color: var(--accent-cyan); margin-bottom: 1rem; text-align: center;">Keyboard Shortcuts</h3>
      <ul style="list-style: none; padding: 0; line-height: 1.8;">
        <li><kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">Right</kbd> / <kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">Space</kbd> : Next Slide</li>
        <li><kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">Left</kbd> : Previous Slide</li>
        <li><kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">N</kbd> : Toggle Presenter Notes</li>
        <li><kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">G</kbd> / <kbd style="background: #333; padding: 2px 6px; border-radius: 4px;">?</kbd> : Toggle this Help Overlay</li>
      </ul>
      <button onclick="document.getElementById('shortcut-overlay').style.display='none'" style="margin-top: 1.5rem; width: 100%; padding: 0.5rem; background: var(--accent-cyan); color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer;">Tutup</button>
    </div>
  </div>
"""
    html = html.replace('</body>', overlay_html + '\n</body>')

    # Add event listeners for G and ?
    js_kb = """
      if (e.key === 'n' || e.key === 'N') {
        toggleNotes();
      }
      if (e.key === 'g' || e.key === 'G' || e.key === '?') {
        const overlay = document.getElementById('shortcut-overlay');
        if (overlay) overlay.style.display = overlay.style.display === 'flex' ? 'none' : 'flex';
      }
"""
    html = html.replace("if (e.key === 'n' || e.key === 'N') {\n        toggleNotes();\n      }", js_kb)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    modify_html()
