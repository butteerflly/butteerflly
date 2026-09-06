#!/usr/bin/env python3
"""Generate profile artwork from shared copy, geometry and accessible theme tokens.

Run from any directory with Python 3. No external dependencies are required.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('hero', 'console', 'fields', 'toolbox', 'build', 'interests', 'footer')
THEMES = {
    'dark': {
        'bg': '#111719', 'end': '#151B1D', 'panel': '#172023',
        'text': '#F2F1ED', 'muted': '#ACB7B8', 'border': '#304044',
        'accent': '#80C9B8', 'copper': '#CCA17F',
    },
    'light': {
        'bg': '#F7F8F6', 'end': '#FFFFFF', 'panel': '#FFFFFF',
        'text': '#242D30', 'muted': '#536367', 'border': '#CDD8D6',
        'accent': '#236E5C', 'copper': '#89603F',
    },
}
FIELDS = (
    ('01 / INTERFACES', 'Frontend engineering',
     ('Interaction, application state', 'and responsive layouts.')),
    ('02 / SOFTWARE', 'Services & automation',
     ('APIs, background work', 'and Linux services.')),
    ('03 / HARDWARE', 'Embedded systems',
     ('Firmware, sensors', 'and serial communication.')),
    ('04 / CONNECTIVITY', 'IoT & realtime software',
     ('Device integration, telemetry', 'and changing state.')),
)
TOOLBOX = (
    ('FRONTEND & INTERFACES', ('TypeScript · React · Vite',)),
    ('SYSTEMS & BACKEND', ('Go · C# · .NET · Node.js',)),
    ('EMBEDDED & IoT', ('ESP32 · UART · I²C · OTA',)),
    ('INFRA & OPS', ('Linux · Docker · Prometheus', 'GitHub Actions · Tailscale')),
)
BUILD = (
    ('Make state visible', 'Show loading, stale data and errors clearly.'),
    ('Test beyond the happy path', 'Check timing, retries and lost connections.'),
    ('Keep changes recoverable', 'Leave useful logs and a practical rollback path.'),
)


class Artwork:
    def __init__(self, theme, mobile):
        self.theme = THEMES[theme]
        self.mobile = mobile
        self.width = 580 if mobile else 900
        self.parts = []
        self.copy = []

    def color(self, token):
        return self.theme.get(token, token)

    def rect(self, x, y, width, height, fill='panel', radius=12, border=True):
        stroke = f' stroke="{self.color("border")}"' if border else ''
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{self.color(fill)}"{stroke}/>')

    def text(self, x, y, value, size=20, color='text', weight=400,
             mono=False, anchor=None):
        attrs = f'font-size="{size}" fill="{self.color(color)}" font-weight="{weight}"'
        if mono:
            attrs += ' font-family="Consolas,\'Liberation Mono\',monospace"'
        if anchor:
            attrs += f' text-anchor="{anchor}"'
        self.parts.append(f'<text x="{x}" y="{y}" {attrs}>{escape(value)}</text>')
        self.copy.append(value)

    def path(self, data, color='border', extra=''):
        self.parts.append(
            f'<path d="{data}" fill="none" stroke="{self.color(color)}" {extra}/>')

    def label(self, x, y, value, color='accent'):
        self.text(x, y, value, 16, color, mono=True)

    def diagram(self, x, y, mobile=False):
        # Conceptual relationship only; this is not a project architecture.
        if mobile:
            nodes = ((0, 'INTERFACE'), (194, 'LOGIC'), (388, 'DEVICE'))
            self.path(f'M{x+128} {y+27}H{x+194}M{x+322} {y+27}H{x+388}')
            self.path(f'M{x+128} {y+27}H{x+194}M{x+322} {y+27}H{x+388}',
                      'accent', 'class="signal" stroke-dasharray="3 13"')
            for offset, label in nodes:
                self.rect(x+offset, y, 128, 54, radius=10)
                self.text(x+offset+64, y+33, label, 18, anchor='middle', mono=True)
        else:
            self.path(f'M{x+54} {y+54}V{y+109}H{x+100}'
                      f'M{x+156} {y+109}H{x+206}V{y+166}')
            self.path(f'M{x+54} {y+54}V{y+109}H{x+100}'
                      f'M{x+156} {y+109}H{x+206}V{y+166}',
                      'accent', 'class="signal" stroke-dasharray="3 13"')
            self.path(f'M{x+206} {y+166}V{y+27}H{x+108}',
                      'border', 'stroke-dasharray="2 7" opacity=".65"')
            self.rect(x, y, 108, 54, radius=10)
            self.text(x+54, y+33, 'INTERFACE', 16, anchor='middle', mono=True)
            self.parts.append(
                f'<circle cx="{x+128}" cy="{y+109}" r="28" '
                f'fill="{self.color("panel")}" stroke="{self.color("copper")}" '
                f'class="node-pulse"/>')
            self.text(x+128, y+114, 'LOGIC', 16, 'copper', mono=True, anchor='middle')
            self.rect(x+152, y+166, 108, 54, radius=10)
            self.text(x+206, y+199, 'DEVICE', 16, anchor='middle', mono=True)

    def finish(self, title, height, surface=False, hero=False):
        t = self.theme
        definitions = f'''  <defs>
    <linearGradient id="hero-bg" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['end']}"/>
    </linearGradient>
  </defs>'''
        motion = '''  <style>
    @media (prefers-reduced-motion: no-preference) {
      .signal { animation: signal-travel 12s linear infinite; }
      .node-pulse { animation: node-breathe 6s ease-in-out infinite; }
    }
    @keyframes signal-travel { to { stroke-dashoffset: -64; } }
    @keyframes node-breathe {
      0%, 100% { stroke-opacity: .65; }
      50% { stroke-opacity: 1; }
    }
  </style>'''
        frame = ''
        if surface:
            frame = (f'  <rect x="0.5" y="0.5" width="{self.width-1}" '
                     f'height="{height-1}" rx="16" '
                     f'fill="{"url(#hero-bg)" if hero else t["bg"]}" '
                     f'stroke="{t["border"]}"/>\n')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{height}" viewBox="0 0 {self.width} {height}" '
            'role="img" aria-labelledby="title desc" fill="none" '
            'font-family="Arial, Helvetica, sans-serif" stroke-width="1">\n'
            f'  <title id="title">{escape(title)}</title>\n'
            f'  <desc id="desc">{escape(" ".join(self.copy))}</desc>\n'
            + (definitions+'\n'+motion+'\n' if hero else '')
            + frame + '\n'.join('  '+part for part in self.parts) + '\n</svg>\n')


def render(kind, theme, mobile=False):
    a = Artwork(theme, mobile)
    w, p = a.width, 32
    body_size = 21 if mobile else 19
    if kind == 'hero':
        a.label(p, 54, 'FRONTEND / SOFTWARE ENGINEERING', 'muted')
        a.rect(p, 74, 86, 3, 'copper', 1.5, False)
        a.text(p, 132, 'BUTTERFLLY', 52, weight=700)
        a.text(p, 179, 'From the interface', 29, weight=600)
        a.text(p, 215, 'to the hardware.', 29, weight=600)
        a.text(p, 263, 'Interfaces, services and connected devices.', 22 if mobile else 20, 'muted')
        if mobile:
            a.diagram(p, 304, True)
            return a.finish('ButterFlly. From the interface to the hardware.', 390, True, True)
        a.path('M576 42V286')
        a.diagram(608, 54)
        return a.finish('ButterFlly. From the interface to the hardware.', 320, True, True)
    if kind == 'console':
        a.label(p, 28, 'ENGINEERING PROFILE', 'muted')
        if mobile:
            a.text(p, 64, 'Frontend engineering,', 23, weight=600)
            a.text(p, 95, 'with a view of the whole system.', 23, weight=600)
            return a.finish('Engineering profile', 118)
        a.text(p, 64, 'Frontend engineering, with a view of the whole system.', 23, weight=600)
        return a.finish('Engineering profile', 88)
    if kind == 'fields':
        cw = w-64 if mobile else 408
        ch, gap, cols = 160, 20, 1 if mobile else 2
        for i, (label, title, lines) in enumerate(FIELDS):
            x, y = p+(i % cols)*(cw+gap), p+(i // cols)*(ch+gap)
            a.rect(x, y, cw, ch)
            a.label(x+24, y+34, label)
            a.text(x+24, y+74, title, 25 if mobile else 24, weight=600)
            for j, value in enumerate(lines):
                a.text(x+24, y+107+j*27, value, body_size, 'muted')
        return a.finish('Fields I work in', 764 if mobile else 404, True)
    if kind == 'toolbox':
        for i, (label, lines) in enumerate(TOOLBOX):
            x = p if mobile else p+(i % 2)*434
            y = 32+(i if mobile else i//2)*118
            a.label(x, y, label)
            for j, value in enumerate(lines):
                a.text(x, y+38+j*31, value, 23, weight=500)
            if mobile and i < 3:
                a.path(f'M{p} {y+84}H{w-p}')
        if not mobile:
            a.path('M442 16V240')
        return a.finish('Toolbox, grouped by function', 490 if mobile else 252)
    if kind == 'build':
        # Copy is intentionally concrete: UI states, communication failures, rollback.
        for i, (title, detail) in enumerate(BUILD):
            y = p+i*(100 if mobile else 86)
            a.label(p, y+26, f'0{i+1}', 'copper')
            a.text(p+46, y+26, title, 23, weight=600)
            a.text(p+46, y+58, detail, body_size, 'muted')
            if i < 2:
                a.path(f'M{p+46} {y+(82 if mobile else 72)}H{w-p}')
        return a.finish('How I like to build', 340 if mobile else 298)
    if kind == 'interests':
        entries = (
            ('Electronics', 'Signals, circuits and measurement.'),
            ('Automotive diagnostics', 'Fault finding and vehicle communication.'),
        )
        for i, (title, detail) in enumerate(entries):
            x = p if mobile else p+i*434
            y = 40+(i*90 if mobile else 0)
            a.text(x, y, title, 23, weight=600)
            a.text(x, y+32, detail, body_size, 'muted')
        return a.finish('Technical interests', 186 if mobile else 96)
    if kind == 'footer':
        a.path(f'M{p} 1H{w-p}')
        a.text(p, 45, 'BUTTERFLLY', 18, 'muted', 600)
        a.text(w-p, 45, 'discord: .butterflly', 18, 'muted', mono=True, anchor='end')
        return a.finish('ButterFlly. Discord: .butterflly', 68)
    raise ValueError(f'Unknown artwork: {kind}')


if __name__ == '__main__':
    for kind in KINDS:
        for theme in THEMES:
            for mobile in (False, True):
                suffix = 'mobile' if mobile else 'v5'
                (ROOT/'assets'/f'{kind}-{suffix}-{theme}.svg').write_text(
                    render(kind, theme, mobile), encoding='utf-8')
