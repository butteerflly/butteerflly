#!/usr/bin/env python3
"""Generate paired profile SVGs from shared geometry and theme tokens. No dependencies."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
THEMES = {
 'dark': dict(bg='#0B131C', end='#0C1621', panel='#101B27', text='#F4F8FB', muted='#A7B4C4', border='#2A3C50', accent='#39E2CA', second='#718BFF', grid='#162536'),
 'light': dict(bg='#F7F9FC', end='#FFFFFF', panel='#FFFFFF', text='#151B23', muted='#526171', border='#CCD6E0', accent='#007D6C', second='#536DDA', grid='#E3EAF1'),
}

def render(kind, theme, mobile=False):
 t=THEMES[theme]; w=580 if mobile else 900; p=32; inner=w-2*p
 parts=[]
 def rect(x,y,ww,hh,fill='panel',radius=12,border=True,extra=''):
  parts.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" rx="{radius}" fill="{t.get(fill,fill)}"'+(f' stroke="{t["border"]}"' if border else '')+f' {extra}/>')
 def text(x,y,s,size=20,color='text',weight=400,mono=False,anchor=None):
  attrs=f'font-size="{size}" fill="{t[color]}" font-weight="{weight}"'
  if mono:attrs+=' font-family="Consolas,\'Liberation Mono\',monospace"'
  if anchor:attrs+=f' text-anchor="{anchor}"'
  parts.append(f'<text x="{x}" y="{y}" {attrs}>{escape(s)}</text>')
 def line(x1,y1,x2,y2,accent=False,extra=''):
  parts.append(f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{t["accent" if accent else "border"]}" {extra}/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{t["border"]}" {extra}/>')
 def label(x,y,s):text(x,y,s,16,'accent',400,True)
 if kind=='hero':
  h=536 if mobile else 360
  text(p,53,'FRONTEND / SOFTWARE / SYSTEMS',16,'muted',400,True)
  rect(p,70,88,3,'url(#accent)',2,False)
  text(p,130,'BUTTERFLLY',52,'text',700)
  text(p,175,'From the interface',28,'text',600)
  text(p,210,'to the hardware.',28,'text',600)
  text(p,251,'I like knowing why a system behaves',20,'muted')
  text(p,279,'the way it does.',20,'muted')
  for x,ww,s in [(p,154,'LINUX / OPS'),(p+166,190,'EMBEDDED / IoT')]:
   rect(x,298,ww,30,radius=8);text(x+ww/2,319,s,16,'muted',400,True,'middle')
  x,y,pw,ph=(p,367,inner,137) if mobile else (570,32,298,296)
  rect(x,y,pw,ph,radius=12)
  label(x+24,y+34,'ENGINEERING FOCUS')
  if mobile:
   for xx,s in [(x+24,'Signals'),(x+191,'State'),(x+358,'Feedback')]:
    parts.append(f'<circle class="pulse" cx="{xx+5}" cy="{y+65}" r="4" fill="{t["accent"]}"/>');text(xx,y+104,s,22,'text',600)
   line(x+34,y+65,x+348,y+65,False,'stroke-dasharray="3 7" class="flow"')
  else:
   for i,(a,b) in enumerate([('Signals','Useful evidence.'),('State','Explicit transitions.'),('Feedback','Clear responses.')]):
    yy=y+75+i*74
    parts.append(f'<circle class="pulse" cx="{x+29}" cy="{yy-7}" r="4" fill="{t["accent"]}"/>')
    text(x+46,yy,a,23,'text',600);text(x+46,yy+27,b,19,'muted')
    if i<2:line(x+29,yy+5,x+29,yy+55,False,'stroke-dasharray="3 7" class="flow"')
 elif kind=='console':
  h=260 if mobile else 172
  label(p,48,'ENGINEERING PROFILE')
  if mobile:
   for i,(a,b) in enumerate([('Understand the boundary.','Hardware, services and people.'),('Make behavior explicit.','Timing, state and failure modes.')]):
    yy=94+i*88;text(p,yy,a,24,'text',600);text(p,yy+30,b,20,'muted')
  else:
   for x,a,b in [(p,'Understand the boundary.','Hardware, services and people.'),(466,'Make behavior explicit.','Timing, state and failure modes.')]:
    text(x,94,a,24,'text',600);text(x,128,b,20,'muted')
   line(442,76,442,136)
 elif kind in ('fields','toolbox','build'):
  if kind=='fields':
   entries=[('02 / EMBEDDED SYSTEMS','Software near the hardware',['Sensors, serial buses and device logic.','Where timing meets the physical world.']),('03 / IoT & REALTIME','Connected systems',['Device communication and realtime data.','Making changing state understandable.']),('04 / BACKEND & LINUX','Services and infrastructure',['APIs, workers and automation.','Deployment, monitoring and recovery.']),('01 / FRONTEND','Frontend engineering',['Web applications and control interfaces.','Clear interaction, timing and feedback.'])]
   entries=[entries[3],*entries[:3]]
  elif kind=='toolbox':
   entries=[('SYSTEMS & BACKEND','Go · C# · .NET · Node.js',['Services, APIs and background work.']),('FRONTEND & INTERFACES','TypeScript · React · Vite',['Web interfaces and practical tooling.']),('EMBEDDED & IoT','ESP32 · UART · I²C · OTA',['Firmware and device communication.']),('INFRA & OPS','Linux · Docker · Prometheus',['GitHub Actions · Tailscale'])]
  else:
   entries=[('01 / DEFINE','Start with the boundaries',['Define contracts and ownership.','Make state transitions explicit.']),('02 / OBSERVE','Leave useful evidence',['Log the context that explains a failure.','Measure behavior under real use.']),('03 / VERIFY','Test the awkward cases',['Check timing, retries and lost connections.','Make failures reproducible.']),('04 / RECOVER','Keep a way back',['Plan rollback before deployment.','Exercise recovery before it is needed.'])]
  if kind=='build':
   rh=144 if mobile else 88;h=2*p+4*rh
   for i,(a,b,ls) in enumerate(entries):
    y=p+i*rh
    label(p,y+24,a);text(p,y+58,b,23,'text',600)
    for j,s in enumerate(ls):text(p if mobile else 466,y+(92 if mobile else 27)+j*28,s,19,'muted')
    if i<3:line(p,y+rh-12,w-p,y+rh-12)
  else:
   cw=inner if mobile else (inner-20)/2;ch=162 if kind=='toolbox' else 180;gap=20;cols=1 if mobile else 2;rows=4 if mobile else 2;h=2*p+rows*ch+(rows-1)*gap
   for i,(a,b,ls) in enumerate(entries):
    x=p+(i%cols)*(cw+gap);y=p+(i//cols)*(ch+gap)
    rect(x,y,cw,ch);label(x+24,y+36,a);text(x+24,y+76,b,23,'text',600)
    for j,s in enumerate(ls):text(x+24,y+111+j*28,s,19,'muted')
 elif kind=='interests':
  h=240 if mobile else 156
  entries=[('Electronics','Signals, circuits and measurement.'),('Automotive technology','Diagnostics and vehicle communication.')]
  for i,(a,b) in enumerate(entries):
   x=p if mobile else p+i*434;y=65+i*88 if mobile else 65
   text(x,y,a,23,'text',600);text(x,y+32,b,19,'muted')
  if not mobile:line(442,42,442,114)
 elif kind=='footer':
  h=132 if mobile else 100
  rect(p,32,3,h-64,'url(#accent)',1.5,False)
  text(p+20,62,'BUTTERFLLY',21,'text',600)
  text(p+20 if mobile else w-p,99 if mobile else 62,'discord: .butterflly',18,'muted',400,True,None if mobile else 'end')
 title={'hero':'ButterFlly. From the interface to the hardware.','console':'Engineering profile','fields':'Fields I work in','toolbox':'Toolbox, grouped by function','build':'How I like to build','interests':'Technical interests','footer':'ButterFlly. Discord: .butterflly'}[kind]
 desc=' '.join(__import__('re').findall(r'<text[^>]*>(.*?)</text>',''.join(parts)))
 start=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" fill="none" font-family="Arial, Helvetica, sans-serif" stroke-width="1">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{desc}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{t['bg']}"/><stop offset="1" stop-color="{t['end']}"/></linearGradient>
    <linearGradient id="accent"><stop stop-color="{t['accent']}"/><stop offset="1" stop-color="{t['second']}"/></linearGradient>
  </defs>
  <style>
    @media (prefers-reduced-motion: no-preference) {{
      .pulse {{ animation: pulse 5s ease-in-out infinite; }}
      .flow {{ animation: flow 12s linear infinite; }}
    }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .65; }} 50% {{ opacity: 1; }} }}
    @keyframes flow {{ to {{ stroke-dashoffset: -20; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="16" fill="{'url(#bg)' if kind=='hero' else t['bg']}" stroke="{t['border']}"/>
'''
 if kind=='hero':
  start+=f'<path d="M{w-130} 1V{h-1}M{w-66} 1V{h-1}" stroke="{t["grid"]}" opacity=".45"/>\n'
 return start+'\n'.join('  '+x for x in parts)+'\n</svg>\n'

if __name__=='__main__':
 for kind in ['hero','console','fields','toolbox','build','interests','footer']:
  for theme in THEMES:
   for mobile in [False,True]:
    name=f'{kind}-v5-{theme}.svg' if not mobile else f'{kind}-mobile-{theme}.svg'
    (ROOT/'assets'/name).write_text(render(kind,theme,mobile))
