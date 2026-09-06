#!/usr/bin/env python3
"""Generate both profile READMEs and their artwork with Python 3.

Copy is maintained per language; geometry, theme tokens and image descriptions
are shared. Run this file from any directory after editing the copy or layout.
"""
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

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
COPY = {
    'pt-br': {
        'lang': 'pt-BR', 'file': 'README.md',
        'selector': '<strong>Português</strong> · <a href="./README.en.md">English</a>',
        'eyebrow': 'FRONTEND / ENGENHARIA DE SOFTWARE',
        'headline': ('Da interface', 'ao hardware.'),
        'intro': 'Interfaces, serviços e dispositivos conectados.',
        'hero_scope': 'SISTEMAS / EMBARCADOS / IoT',
        'profile_label': 'PERFIL TÉCNICO',
        'profile': ('Minha especialidade é frontend.',),
        'about_heading': 'Sobre mim',
        'about': ('Trabalho com interfaces web, serviços de backend, Linux e sistemas embarcados. '
                  'Gosto de investigar problemas que passam por essas áreas, principalmente quando '
                  'envolvem comunicação com dispositivos ou o tempo de resposta do sistema.'),
        'headings': {
            'hero': 'ButterFlly. Da interface ao hardware.',
            'console': 'Perfil técnico', 'fields': 'Áreas de atuação',
            'toolbox': 'Ferramentas', 'build': 'Como gosto de trabalhar',
            'interests': 'Interesses técnicos', 'activity': 'Atividade no GitHub',
            'footer': 'ButterFlly. Discord: .butterflly',
        },
        'fields': (
            ('01 / INTERFACES', 'Engenharia de frontend',
             ('Interação, estado da aplicação', 'e layouts responsivos.')),
            ('02 / SOFTWARE', 'Serviços e automação',
             ('APIs, tarefas em segundo plano', 'e serviços Linux.')),
            ('03 / HARDWARE', 'Sistemas embarcados',
             ('Firmware, sensores', 'e comunicação serial.')),
            ('04 / CONECTIVIDADE', 'IoT e tempo real',
             ('Integração de dispositivos,', 'telemetria e troca de mensagens.')),
        ),
        'toolbox_labels': ('FRONTEND E INTERFACES', 'SISTEMAS E BACKEND',
                           'EMBARCADOS E IoT', 'INFRA E OBSERVABILIDADE'),
        'build': (
            ('Deixar o estado claro',
             ('Carregamento, dados desatualizados', 'e erros precisam ficar visíveis.')),
            ('Testar quando as coisas falham',
             ('Verificar atrasos, novas tentativas', 'e perda de conexão.')),
            ('Facilitar a recuperação',
             ('Manter logs úteis e um caminho', 'para reverter mudanças.')),
        ),
        'interests': (
            ('Eletrônica', 'Sinais, circuitos e medição.'),
            ('Diagnóstico automotivo', 'Códigos de falha e redes veiculares.'),
        ),
        'activity_alt': 'Animação das contribuições no GitHub',
    },
    'en': {
        'lang': 'en', 'file': 'README.en.md',
        'selector': '<a href="./README.md">Português</a> · <strong>English</strong>',
        'eyebrow': 'FRONTEND / SOFTWARE ENGINEERING',
        'headline': ('From the interface', 'to the hardware.'),
        'intro': 'Interfaces, services and connected devices.',
        'hero_scope': 'SYSTEMS / EMBEDDED / IoT',
        'profile_label': 'ENGINEERING PROFILE',
        'profile': ('I specialize in frontend engineering.',),
        'about_heading': 'About',
        'about': ('I work with web interfaces, backend services, Linux and embedded systems. '
                  'I like investigating problems that cross those boundaries, especially when '
                  'device communication or system response times are involved.'),
        'headings': {
            'hero': 'ButterFlly. From the interface to the hardware.',
            'console': 'Engineering profile', 'fields': 'Fields I work in',
            'toolbox': 'Toolbox', 'build': 'How I like to build',
            'interests': 'Technical interests', 'activity': 'GitHub activity',
            'footer': 'ButterFlly. Discord: .butterflly',
        },
        'fields': (
            ('01 / INTERFACES', 'Frontend engineering',
             ('Interaction, application state', 'and responsive layouts.')),
            ('02 / SOFTWARE', 'Services & automation',
             ('APIs, background work', 'and Linux services.')),
            ('03 / HARDWARE', 'Embedded systems',
             ('Firmware, sensors', 'and serial communication.')),
            ('04 / CONNECTIVITY', 'IoT & realtime software',
             ('Device integration, telemetry', 'and message exchange.')),
        ),
        'toolbox_labels': ('FRONTEND & INTERFACES', 'SYSTEMS & BACKEND',
                           'EMBEDDED & IoT', 'INFRA & OBSERVABILITY'),
        'build': (
            ('Make state visible',
             ('Show loading, stale data', 'and errors clearly.')),
            ('Test when things fail',
             ('Check timing, retries', 'and lost connections.')),
            ('Make recovery practical',
             ('Leave useful logs and a way', 'to roll back changes.')),
        ),
        'interests': (
            ('Electronics', 'Signals, circuits and measurement.'),
            ('Automotive diagnostics', 'Fault codes and vehicle networks.'),
        ),
        'activity_alt': 'Animated GitHub contribution activity',
    },
}
TOOLS = (
    ('TypeScript · React · Vite',),
    ('Go · C# · .NET · Node.js',),
    ('ESP32 · UART · I²C · OTA',),
    ('Linux · Docker · Prometheus', 'GitHub Actions · Tailscale'),
)


class Artwork:
    def __init__(self, theme, mobile, locale):
        self.theme = THEMES[theme]
        self.mobile = mobile
        self.copy = COPY[locale]
        self.width = 580 if mobile else 900
        self.parts = []
        self.description = []

    def color(self, token):
        return self.theme.get(token, token)

    def rect(self, x, y, width, height, fill='panel', radius=12, border=True):
        stroke = f' stroke="{self.color("border")}"' if border else ''
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{self.color(fill)}"{stroke}/>')

    def text(self, x, y, value, size=20, color='text', weight=400,
             mono=False, anchor=None, tracking=None):
        attrs = f'font-size="{size}" fill="{self.color(color)}" font-weight="{weight}"'
        if mono:
            attrs += ' font-family="Consolas,\'Liberation Mono\',monospace"'
        if anchor:
            attrs += f' text-anchor="{anchor}"'
        if tracking is not None:
            attrs += f' letter-spacing="{tracking}"'
        self.parts.append(f'<text x="{x}" y="{y}" {attrs}>{escape(value)}</text>')
        self.description.append(value)

    def path(self, data, color='border', extra=''):
        self.parts.append(
            f'<path d="{data}" fill="none" stroke="{self.color(color)}" {extra}/>')

    def label(self, x, y, value, color='accent'):
        self.text(x, y, value, 16, color, mono=True)

    def signature(self, x, y, scale=1):
        """Swept, asymmetric laminae: an abstract wing built as routed signals.

        Coordinates belong to a 320 × 320 optical field. No nodes or labels
        imply a live system. The two planes share a diagonal fold, not an axis
        of symmetry; the silhouette is intentionally incomplete.
        """
        self.parts.append(f'<g transform="translate({x} {y}) scale({scale})" '
                          'aria-hidden="true" stroke-linejoin="round" stroke-linecap="round">')
        # Recessed construction plane and its sparse registration marks.
        self.path('M42 262L276 28M84 302L302 84', 'border', 'opacity=".4"')
        self.path('M26 70H38M32 64V76M290 274H302M296 268V280',
                  'copper', 'opacity=".5"')
        # A quiet surface beneath the engraving gives depth even without motion.
        self.parts.append('<path d="M84 248L100 152Q172 58 292 28'
                          'L266 128Q216 205 84 248Z" fill="url(#wing-upper)"/>')
        self.parts.append('<path d="M98 262Q189 203 284 214L246 280'
                          'Q180 322 124 304Z" fill="url(#wing-lower)"/>')
        # Contours are routed, not a literal butterfly outline.
        self.path('M84 248L100 152Q172 58 292 28L266 128Q216 205 84 248',
                  'accent', 'stroke-width="1.3" opacity=".75"')
        self.path('M98 262Q189 203 284 214L246 280Q180 322 124 304',
                  'copper', 'stroke-width="1.3" opacity=".85"')
        # Parallel traces fan out along the upper plane; uniform spacing at entry.
        for i in range(7):
            start_x, start_y = 48+i*10, 258+i*3
            elbow_x, elbow_y = 80+i*9, 166+i*5
            tip_x, tip_y = 278-i*10, 48+i*15
            bend_x, bend_y = 177+i*7, 88+i*11
            d = (f'M{start_x} {start_y}L{elbow_x} {elbow_y}'
                 f'Q{bend_x} {bend_y} {tip_x} {tip_y}')
            self.path(d, 'accent', f'opacity="{.28+i*.075:.3f}"')
        for i in range(5):
            self.path(f'M{108+i*7} {278+i*5}'
                      f'Q{179+i*6} {223+i*9} {271-i*7} {232+i*10}',
                      'copper', f'opacity="{.28+i*.1:.2f}"')
        # The fold and its open terminals create a signature separate from UI cards.
        self.path('M64 290L124 230L210 148L272 76', 'copper', 'stroke-width="1.5"')
        self.path('M48 258L80 166Q177 88 278 48', 'accent',
                  'class="signal" pathLength="100" stroke-width="2" '
                  'stroke-dasharray="3 97" opacity=".85"')
        self.path('M108 278Q179 223 271 232', 'copper',
                  'class="signal signal-return" pathLength="100" '
                  'stroke-width="2" stroke-dasharray="3 97" opacity=".8"')
        for cx, cy in ((64, 290), (272, 76)):
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" '
                              f'fill="{self.color("bg")}" stroke="{self.color("copper")}"/>')
        self.parts.append('</g>')

    def finish(self, title, height, surface=False, hero=False):
        t = self.theme
        definitions = f'''  <defs>
    <linearGradient id="hero-bg" x1="0" y1="1" x2="1" y2="0">
      <stop stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['end']}"/>
    </linearGradient>
    <radialGradient id="hero-halo">
      <stop stop-color="{t['accent']}" stop-opacity=".10"/>
      <stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="wing-upper" x1="0" y1="1" x2="1" y2="0">
      <stop stop-color="{t['accent']}" stop-opacity=".02"/>
      <stop offset="1" stop-color="{t['accent']}" stop-opacity=".16"/>
    </linearGradient>
    <linearGradient id="wing-lower" x1="0" y1="0" x2="1" y2="1">
      <stop stop-color="{t['copper']}" stop-opacity=".12"/>
      <stop offset="1" stop-color="{t['copper']}" stop-opacity=".02"/>
    </linearGradient>
  </defs>'''
        motion = '''  <style>
    @media (prefers-reduced-motion: no-preference) {
      .signal { animation: signal-travel 18s linear infinite; }
      .signal-return { animation-duration: 24s; animation-direction: reverse; }
    }
    @keyframes signal-travel { to { stroke-dashoffset: -100; } }
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
            f'xml:lang="{self.copy["lang"]}" '
            'role="img" aria-labelledby="title desc" fill="none" '
            'font-family="Arial, Helvetica, sans-serif" stroke-width="1">\n'
            f'  <title id="title">{escape(title)}</title>\n'
            f'  <desc id="desc">{escape(" ".join(self.description))}</desc>\n'
            + (definitions+'\n'+motion+'\n' if hero else '')
            + frame + '\n'.join('  '+part for part in self.parts) + '\n</svg>\n')


def render(kind, theme, mobile=False, locale='pt-br'):
    a = Artwork(theme, mobile, locale)
    c = a.copy
    w, p = a.width, 32
    body_size = 21 if mobile else 19
    title = c['headings'][kind]
    if kind == 'hero':
        # Desktop and mobile have separate editorial arrangements.
        height = 606 if mobile else 378
        if mobile:
            a.parts.append('<ellipse cx="310" cy="430" rx="190" ry="145" '
                           'fill="url(#hero-halo)"/>')
            a.signature(150, 287, .8)
        else:
            a.parts.append('<ellipse cx="704" cy="180" rx="190" ry="174" '
                           'fill="url(#hero-halo)"/>')
            a.signature(548, 0, 1)
        a.text(p, 48, c['eyebrow'], 17 if mobile else 14, 'muted', mono=True, tracking=.4)
        a.text(p-2, 126, 'BUTTERFLLY', 72, weight=700, tracking=-2.4)
        a.rect(p, 146, 52, 2, 'copper', 1, False)
        for i, line in enumerate(c['headline']):
            a.text(p, 205+i*43, line, 39, weight=500, tracking=-.6)
        a.text(p, 291, c['intro'], 23 if mobile else 19, 'muted')
        if mobile:
            a.path('M32 560H548')
            a.text(p, 584, c['hero_scope'], 17, 'muted', mono=True)
        else:
            a.path('M32 332H868')
            a.text(p, 358, c['hero_scope'], 15, 'muted', mono=True)
        return a.finish(title, height, True, True)
    if kind == 'console':
        a.label(p, 24, c['profile_label'], 'muted')
        if mobile:
            for i, line in enumerate(c['profile']):
                a.text(p, 60+i*31, line, 23, weight=600)
            return a.finish(title, 80)
        a.text(p, 60, ' '.join(c['profile']), 23, weight=600)
        return a.finish(title, 80)
    if kind == 'fields':
        # The card inset matches the hero and open sections, without a second frame.
        cw, ch, gap, cols = (w if mobile else 440), 160, 20, (1 if mobile else 2)
        for i, (label, heading, lines) in enumerate(c['fields']):
            x, y = (i % cols)*(cw+gap), 8+(i // cols)*(ch+gap)
            a.rect(x+.5, y+.5, cw-1, ch-1,
                   fill='panel' if theme == 'dark' else 'bg')
            a.label(x+p, y+34, label)
            a.text(x+p, y+74, heading, 25 if mobile else 24, weight=600)
            for j, value in enumerate(lines):
                a.text(x+p, y+107+j*27, value, body_size, 'muted')
        return a.finish(title, 716 if mobile else 356)
    if kind == 'toolbox':
        for i, (label, lines) in enumerate(zip(c['toolbox_labels'], TOOLS)):
            x = p if mobile else p+(i % 2)*460
            y = 28+(i if mobile else i//2)*104
            a.label(x, y, label)
            for j, value in enumerate(lines):
                a.text(x, y+36+j*31, value, 23, weight=500)
            if mobile and i < 3:
                a.path(f'M{p} {y+77}H{w-p}')
        if not mobile:
            a.path('M450 12V216')
        return a.finish(title, 430 if mobile else 224)
    if kind == 'build':
        for i, (heading, lines) in enumerate(c['build']):
            y = 20+i*(118 if mobile else 86)
            a.label(p, y+26, f'0{i+1}', 'copper')
            a.text(p+46, y+26, heading, 23, weight=600)
            if mobile:
                for j, line in enumerate(lines):
                    a.text(p+46, y+58+j*28, line, body_size, 'muted')
            else:
                a.text(p+46, y+58, ' '.join(lines), body_size, 'muted')
            if i < 2:
                a.path(f'M{p+46} {y+(101 if mobile else 72)}H{w-p}')
        return a.finish(title, 366 if mobile else 270)
    if kind == 'interests':
        for i, (heading, detail) in enumerate(c['interests']):
            x = p if mobile else p+i*460
            y = 32+(i*82 if mobile else 0)
            a.text(x, y, heading, 23, weight=600)
            a.text(x, y+32, detail, body_size, 'muted')
        return a.finish(title, 170 if mobile else 84)
    if kind == 'footer':
        a.path(f'M{p} 1H{w-p}')
        a.text(p, 45, 'BUTTERFLLY', 18, 'muted', 600)
        a.text(w-p, 45, 'discord: .butterflly', 18, 'muted', mono=True, anchor='end')
        return a.finish(title, 68)
    raise ValueError(f'Unknown artwork: {kind}')


def asset_path(locale, kind, layout, theme):
    return Path('assets')/locale/f'{kind}-{layout}-{theme}.svg'


def picture(locale, kind):
    """Use the same content for visible artwork and its accessible description."""
    # The root description is generated from the actual visible text.
    root = ET.fromstring(render(kind, 'dark', False, locale))
    alt = root.find('{http://www.w3.org/2000/svg}desc').text
    def src(layout, theme):
        return './'+asset_path(locale, kind, layout, theme).as_posix()
    return f'''<p>
<picture>
  <source media="(max-width: 767px) and (prefers-color-scheme: dark)" srcset="{src('mobile', 'dark')}">
  <source media="(max-width: 767px)" srcset="{src('mobile', 'light')}">
  <source media="(prefers-color-scheme: dark)" srcset="{src('desktop', 'dark')}">
  <source media="(prefers-color-scheme: light)" srcset="{src('desktop', 'light')}">
  <img alt="{escape(alt, quote=True)}" src="{src('desktop', 'dark')}" width="100%">
</picture>
</p>'''


def readme(locale):
    c = COPY[locale]
    sections = [
        '<!-- Generated by scripts/render-assets.py. Edit copy and layout there. -->',
        f'<p align="right">{c["selector"]}</p>',
        picture(locale, 'hero'), picture(locale, 'console'),
        f'## {c["about_heading"]}\n\n{c["about"]}',
    ]
    for kind in ('fields', 'toolbox', 'build', 'interests'):
        sections.extend((f'## {c["headings"][kind]}', picture(locale, kind)))
    sections.append(f'## {c["headings"]["activity"]}')
    activity = 'https://raw.githubusercontent.com/butteerflly/butteerflly/output/github-contribution-grid-snake'
    sections.append(f'''<p>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{activity}-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="{activity}.svg">
  <img alt="{c['activity_alt']}" src="{activity}.svg" width="100%">
</picture>
</p>''')
    sections.append(picture(locale, 'footer'))
    return '\n\n'.join(sections)+'\n'


if __name__ == '__main__':
    for locale in COPY:
        for kind in KINDS:
            for theme in THEMES:
                for mobile in (False, True):
                    path = ROOT/asset_path(locale, kind, 'mobile' if mobile else 'desktop', theme)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(render(kind, theme, mobile, locale), encoding='utf-8')
        (ROOT/COPY[locale]['file']).write_text(readme(locale), encoding='utf-8')
