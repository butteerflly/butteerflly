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
        'nodes': ('INTERFACE', 'LÓGICA', 'DISPOSITIVO'),
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
        'nodes': ('INTERFACE', 'LOGIC', 'DEVICE'),
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
             mono=False, anchor=None):
        attrs = f'font-size="{size}" fill="{self.color(color)}" font-weight="{weight}"'
        if mono:
            attrs += ' font-family="Consolas,\'Liberation Mono\',monospace"'
        if anchor:
            attrs += f' text-anchor="{anchor}"'
        self.parts.append(f'<text x="{x}" y="{y}" {attrs}>{escape(value)}</text>')
        self.description.append(value)

    def path(self, data, color='border', extra=''):
        self.parts.append(
            f'<path d="{data}" fill="none" stroke="{self.color(color)}" {extra}/>')

    def label(self, x, y, value, color='accent'):
        self.text(x, y, value, 16, color, mono=True)

    def diagram(self, x, y):
        # A conceptual relationship, not a project architecture.
        interface, logic, device = self.copy['nodes']
        if self.mobile:
            self.path(f'M{x+148} {y+27}H{x+184}M{x+332} {y+27}H{x+368}')
            self.path(f'M{x+148} {y+27}H{x+184}M{x+332} {y+27}H{x+368}',
                      'accent', 'class="signal" stroke-dasharray="3 13"')
            for offset, label in zip((0, 184, 368), (interface, logic, device)):
                self.rect(x+offset, y, 148, 54, radius=10)
                self.text(x+offset+74, y+33, label, 18, anchor='middle', mono=True)
        else:
            route = (f'M{x+64} {y+54}V{y+109}H{x+96}'
                     f'M{x+160} {y+109}H{x+196}V{y+166}')
            self.path(route)
            self.path(route, 'accent', 'class="signal" stroke-dasharray="3 13"')
            self.path(f'M{x+196} {y+166}V{y+27}H{x+128}',
                      'border', 'stroke-dasharray="2 7" opacity=".65"')
            self.rect(x, y, 128, 54, radius=10)
            self.text(x+64, y+33, interface, 15, anchor='middle', mono=True)
            self.parts.append(
                f'<circle cx="{x+128}" cy="{y+109}" r="32" '
                f'fill="{self.color("panel")}" stroke="{self.color("copper")}" '
                f'class="node-pulse"/>')
            self.text(x+128, y+114, logic, 15, 'copper', mono=True, anchor='middle')
            self.rect(x+132, y+166, 128, 54, radius=10)
            self.text(x+196, y+199, device, 15, anchor='middle', mono=True)

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
        a.label(p, 54, c['eyebrow'], 'muted')
        a.rect(p, 74, 86, 3, 'copper', 1.5, False)
        a.text(p, 132, 'BUTTERFLLY', 52, weight=700)
        for i, line in enumerate(c['headline']):
            a.text(p, 179+i*36, line, 29, weight=600)
        a.text(p, 263, c['intro'], 22 if mobile else 20, 'muted')
        if mobile:
            a.diagram(p, 304)
            return a.finish(title, 390, True, True)
        a.path('M576 42V286')
        a.diagram(608, 54)
        return a.finish(title, 320, True, True)
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
