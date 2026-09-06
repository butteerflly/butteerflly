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
        'eyebrow': 'ENGENHARIA DE SOFTWARE / SISTEMAS',
        'headline': ('Da interface', 'ao hardware.'),
        'intro': 'Serviços, interfaces e dispositivos conectados.',
        'hero_scope': 'LINUX / EMBARCADOS / IoT',
        'profile_label': 'CRITÉRIO DE ENGENHARIA',
        'profile': ('Estado, tempo de resposta e recuperação.',),
        'about_heading': 'Sobre mim',
        'about': ('Trabalho com software e sistemas conectados. Isso inclui serviços Linux, automação, '
                  'telemetria, sistemas embarcados e interfaces web. Gosto de entender como as partes '
                  'se comunicam e o que acontece quando algo falha.'),
        'headings': {
            'hero': 'ButterFlly. Da interface ao hardware.',
            'console': 'Perfil técnico', 'fields': 'Áreas de atuação',
            'toolbox': 'Ferramentas', 'build': 'Como gosto de trabalhar',
            'interests': 'Interesses técnicos', 'activity': 'Atividade no GitHub',
            'footer': 'ButterFlly. Discord: .butterflly',
        },
        'fields': (
            ('01 / SOFTWARE', 'Sistemas e automação',
             ('Serviços Linux, APIs', 'e tarefas em segundo plano.')),
            ('02 / DISPOSITIVOS', 'Sistemas embarcados',
             ('Firmware, sensores', 'e comunicação serial.')),
            ('03 / CONECTIVIDADE', 'IoT e tempo real',
             ('Integração de dispositivos,', 'telemetria e troca de mensagens.')),
            ('04 / INTERFACES', 'Interfaces web',
             ('Frontend, estado da aplicação', 'e interação com o sistema.')),
        ),
        'toolbox_labels': ('SISTEMAS E BACKEND', 'EMBARCADOS E IoT',
                           'FRONTEND E INTERFACES', 'INFRA E OBSERVABILIDADE'),
        'build': (
            ('Tornar o estado observável',
             ('Logs, métricas e sinais claros', 'para entender o comportamento.')),
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
        'eyebrow': 'SOFTWARE ENGINEERING / SYSTEMS',
        'headline': ('From the interface', 'to the hardware.'),
        'intro': 'Services, interfaces and connected devices.',
        'hero_scope': 'LINUX / EMBEDDED / IoT',
        'profile_label': 'ENGINEERING CRITERIA',
        'profile': ('State, response time and recovery.',),
        'about_heading': 'About',
        'about': ('I work on software and connected systems, including Linux services, automation, '
                  'telemetry, embedded systems and web interfaces. I like understanding how the parts '
                  'communicate and what happens when something fails.'),
        'headings': {
            'hero': 'ButterFlly. From the interface to the hardware.',
            'console': 'Engineering profile', 'fields': 'Fields I work in',
            'toolbox': 'Toolbox', 'build': 'How I like to build',
            'interests': 'Technical interests', 'activity': 'GitHub activity',
            'footer': 'ButterFlly. Discord: .butterflly',
        },
        'fields': (
            ('01 / SOFTWARE', 'Systems & automation',
             ('Linux services, APIs', 'and background work.')),
            ('02 / DEVICES', 'Embedded systems',
             ('Firmware, sensors', 'and serial communication.')),
            ('03 / CONNECTIVITY', 'IoT & realtime software',
             ('Device integration, telemetry', 'and message exchange.')),
            ('04 / INTERFACES', 'Web interfaces',
             ('Frontend, application state', 'and interaction with the system.')),
        ),
        'toolbox_labels': ('SYSTEMS & BACKEND', 'EMBEDDED & IoT',
                           'FRONTEND & INTERFACES', 'INFRA & OBSERVABILITY'),
        'build': (
            ('Make state observable',
             ('Use logs, metrics and clear signals', 'to understand system behavior.')),
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
    ('Go · C# · .NET · Node.js',),
    ('ESP32 · UART · I²C · OTA',),
    ('TypeScript · React · Vite',),
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
        """Two wing surfaces with nested traces from the same cubic geometry.

        All curves share ordered control points. Trimming their ends leaves
        space at the root and tip instead of piling strokes onto one point.
        The upper traces enter through short, parallel circuit leads.
        """
        def mix(a, b, t):
            return tuple(u+(v-u)*t for u, v in zip(a, b))

        def segment(points, start=.10, end=.90):
            # Exact cubic subcurve: endpoint positions and endpoint tangents.
            def point(t):
                weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
                return tuple(sum(w*p[j] for w, p in zip(weights, points))
                             for j in (0, 1))

            def tangent(t):
                return tuple(3*sum(((1-t)**2, 2*(1-t)*t, t*t)[i]
                                   *(points[i+1][j]-points[i][j])
                                   for i in range(3)) for j in (0, 1))

            first, last = point(start), point(end)
            a, b = tangent(start), tangent(end)
            span = (end-start)/3
            return (first, tuple(first[j]+a[j]*span for j in (0, 1)),
                    tuple(last[j]-b[j]*span for j in (0, 1)), last)

        def curve(points, lead=False):
            first, a, b, last = segment(points)
            xy = lambda p: f'{p[0]:.2f} {p[1]:.2f}'
            entry = (f'M{xy((first[0]-22, first[1]+12))}'
                     f'L{xy((first[0]-10, first[1]+12))}L') if lead else 'M'
            return f'{entry}{xy(first)}C{xy(a)} {xy(b)} {xy(last)}'

        self.parts.append(f'<g transform="translate({x} {y}) scale({scale})" '
                          'aria-hidden="true" stroke-linejoin="round" stroke-linecap="round">')
        self.path('M36 66H48M42 60V72M284 274H296M290 268V280',
                  'copper', 'opacity=".35"')
        # Internal traces follow each surface with ordered control points.
        upper = 'M84 236C74 144 164 50 270 34C269 143 187 231 84 236Z'
        lower = 'M94 248C153 209 236 198 278 216C230 282 153 303 108 280Z'
        for d, gradient, color in ((upper, 'wing-upper', 'accent'),
                                    (lower, 'wing-lower', 'copper')):
            self.parts.append(f'<path d="{d}" fill="url(#{gradient})" '
                              f'stroke="{self.color(color)}" stroke-width="1.3" '
                              'stroke-opacity=".72"/>')
        signals = []
        for i in range(6):
            t = (i+1)/7
            d = curve(((84, 236), mix((74, 144), (187, 231), t),
                       mix((164, 50), (269, 143), t), (270, 34)), lead=True)
            self.path(d, 'accent', f'opacity="{.30+i*.06:.2f}"')
            if i == 2:
                signals.append((d, 'accent', 'signal'))
        for i in range(4):
            t = (i+1)/5
            d = curve(((106, 258), mix((153, 219), (141, 322), t),
                       mix((229, 209), (238, 294), t), (262, 225)))
            self.path(d, 'copper', f'opacity="{.30+i*.08:.2f}"')
            if i == 1:
                signals.append((d, 'copper', 'signal signal-return'))
        # Animation reuses the visible routes, so geometry cannot drift apart.
        for d, color, css_class in signals:
            self.path(d, color, f'class="{css_class}" pathLength="100" '
                      'stroke-width="1.8" stroke-dasharray="2 98" opacity=".75"')
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
            a.signature(150, 295, .8)
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
