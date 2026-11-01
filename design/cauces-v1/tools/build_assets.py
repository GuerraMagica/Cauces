"""Generate editable, self-contained SVG design proposals; never touches the app.

No audio/model processing, external services, fonts or dependencies. Python 3.9+.
"""
from pathlib import Path
from html import escape
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
TOKENS=json.loads((ROOT/'tokens.json').read_text())
COPY=json.loads((ROOT/'copy.en.json').read_text())
STATES=['empty','ready','processing','review','exported','error']
PALETTE=TOKENS['colors']
NEUTRAL=dict(PALETTE,background='#F3F4F5',titlebar='#E8EBED',surface='#FFFFFF',surfaceRaised='#E9EDF0',border='#B4BEC5',text='#182328',textSecondary='#46565F',textMuted='#53636D',voice1='#344650',voice2='#637580',residual='#637580',original='#344650',action='#273C46',onAction='#FFFFFF',error='#9D3131',success='#24634B')
FONT='-apple-system,BlinkMacSystemFont,Arial,sans-serif'

def text(x,y,value,c,size=14,weight=400,anchor='start',extra=''):
 return f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'
def rect(x,y,w,h,fill,r=12,stroke=None,extra=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+f' {extra}/>'
def group(name,content):return f'<g id="{name}" data-layer="{name}">{content}</g>'
def svg(content,w,h,title):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="svg-title" font-family="{FONT}"><title id="svg-title">{escape(title)}</title><metadata>Editable design proposal for Cauces. Synthetic UI content. No audio processing. Copyright GuerraMagica Audio. Branding is provisional.</metadata>{content}</svg>'''

ICONS={
 'open-audio':'<path d="M3 7.5h6l2-2h4a2 2 0 0 1 2 2v2M3 7.5v11h15l3-9H7l-4 9"/>',
 'play':'<path d="m8 5 11 7-11 7Z"/>',
 'pause':'<path d="M8 5v14M16 5v14"/>',
 'export':'<path d="M12 15V3m-4 4 4-4 4 4M5 12v8h14v-8"/>',
 'folder':'<path d="M3 7h6l2-2h4l3 3v2M3 7v12h15l3-9H7L3 19"/>',
 'check':'<path d="m5 12 4 4L19 6"/>',
 'close':'<path d="m6 6 12 12M18 6 6 18"/>',
 'file-audio':'<path d="M6 3h8l4 4v14H6V3Zm8 0v5h4M9 13v3m3-5v7m3-5v3"/>',
 'arrow-right':'<path d="M4 12h15m-5-5 5 5-5 5"/>'
}
def icon(name,x,y,c,size=20):
 return f'<g transform="translate({x},{y}) scale({size/24})" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'
def button(x,y,w,label,p,primary=False,name='button',with_icon=None):
 c=p['onAction'] if primary else p['text'];bg=p['action'] if primary else p['surfaceRaised']
 content=rect(x,y,w,44,bg,10,None if primary else p['border'])
 if with_icon:content+=icon(with_icon,x+16,y+12,c,20)+text(x+46,y+27,label,c,15,600)
 else:content+=text(x+w/2,y+27,label,c,15,600,'middle')
 return group(name,content)

def flow(p,w=500,h=175,neutral=False):
 s=[]
 # Fine parallel contours suggest channels rather than a literal river illustration.
 for offset in [-18,-9,0,9,18]:
  s.append(f'<path d="M16 {87+offset}C70 {87+offset},92 {68+offset},151 {87+offset}S223 {105+offset},257 {87+offset}" stroke="{p["original"]}" opacity="{.34 if offset else .8}" stroke-width="{1 if offset else 2.5}"/>')
 for direction,color in [(-1,p['voice1']),(1,p['voice2'])]:
  end=87+direction*53
  for offset in [-12,-6,0,6,12]:
   s.append(f'<path d="M237 {87+offset*.35}C303 {87+offset*.35},301 {end+offset},370 {end+offset}H481" stroke="{color}" opacity="{.22 if offset else 1}" stroke-width="{1 if offset else 3}"/>')
 s.append(f'<path d="M252 87C310 87,321 87,368 87H481" stroke="{p["residual"]}" opacity=".47" stroke-width="1.5" stroke-dasharray="3 6"/>')
 for y,color in [(34,p['voice1']),(140,p['voice2'])]:
  s.append(f'<circle cx="481" cy="{y}" r="4.5" fill="{color}"/>')
 return f'<svg x="0" y="0" width="{w}" height="{h}" viewBox="0 0 500 175" fill="none" stroke-linecap="round">'+''.join(s)+'</svg>'

def illustration(x,y,w,h,p,neutral=False):
 if neutral:
  return group('slot-hero-art',rect(x,y,w,h,'none',12,p['border'],'stroke-dasharray="5 6"')+text(x+w/2,y+h/2-4,'CUSTOM ARTWORK',p['textMuted'],12,500,'middle','letter-spacing="1.4"')+text(x+w/2,y+h/2+19,'Replace this vector group',p['textMuted'],12,400,'middle'))
 return group('slot-hero-art',f'<g transform="translate({x},{y})">'+flow(p,w,h)+'</g>')

def screen(state,p=PALETTE,w=1000,h=700,neutral=False):
 inset=48 if w>=960 else 32;cw=w-2*inset;center=w/2;foot=h-26
 s=[rect(.5,.5,w-1,h-1,p['background'],18,p['border'])]
 s+=[group('native-titlebar',rect(1,1,w-2,43,p['titlebar'],18)+rect(1,25,w-2,19,p['titlebar'],0)+''.join(f'<circle cx="{24+i*21}" cy="22" r="5.5" fill="{c}"/>' for i,c in enumerate(['#E57772','#D6AF62','#78AA82'] if not neutral else ['#98A2A9']*3))+text(center,27,'Cauces',p['textSecondary'],12,500,'middle'))]
 # Product content deliberately has no duplicate title, subtitle or beta/CPU pill.
 if state in ['empty','ready','processing','error']:
  y=77;ph=h-148
  s.append(group('import-panel',rect(inset,y,cw,ph,p['surface'],16,p['border'])))
  artw=min(500,cw-100);artx=center-artw/2;arty=152 if h>=680 else 115
  s.append(illustration(artx,arty,artw,175 if h>=680 else 150,p,neutral))
  base=368 if h>=680 else 316
  if state=='empty':
   s.append(group('copy-import',text(center,base,COPY['import.title'],p['text'],30,600,'middle')+text(center,base+31,COPY['import.subtitle'],p['textSecondary'],14,400,'middle')))
   s.append(button(center-84,base+59,168,COPY['import.button'],p,True,'button-open','open-audio'))
   s.append(text(center,base+132,COPY['import.limit'],p['textMuted'],12,400,'middle'))
  elif state=='ready':
   s.append(group('file-summary',text(center,base-2,'dialogue_take_014.wav',p['text'],23,500,'middle')+text(center,base+28,'Mono · 48 kHz · 24-bit · 00:12.000',p['textSecondary'],13,400,'middle')))
   s.append(button(center-92,base+58,184,COPY['action.separate'],p,True,'button-separate'))
   s.append(text(center,base+132,COPY['import.change'],p['textSecondary'],13,500,'middle'))
  elif state=='processing':
   s.append(group('processing-status',text(center,base-2,COPY['status.separate'],p['text'],26,500,'middle')+text(center,base+29,'dialogue_take_014.wav',p['textSecondary'],13,400,'middle')))
   progressw=min(360,cw-150);px=center-progressw/2
   s.append(group('progress',rect(px,base+59,progressw,4,p['border'],2)+rect(px,base+59,progressw*.52,4,p['voice1'],2)+text(px+progressw,base+87,'52%',p['textSecondary'],12,500,'end')))
   s.append(button(center-52,base+106,104,COPY['action.cancel'],p,False,'button-cancel'))
  else:
   s.append(group('error-copy',text(center,base,COPY['error.importTitle'],p['text'],26,500,'middle')+text(center,base+32,COPY['error.importBody'],p['error'],14,400,'middle')))
   s.append(button(center-84,base+64,168,COPY['import.button'],p,True,'button-open','open-audio'))
 else:
  s.append(group('file-summary',rect(inset,80,cw,76,p['surface'],12,p['border'])+icon('file-audio',inset+19,101,p['textSecondary'],26)+text(inset+65,111,'dialogue_take_014.wav',p['text'],17,500)+text(inset+65,135,'Mono · 48 kHz · 24-bit · 00:12.000',p['textSecondary'],12)+text(w-inset-21,122,COPY['import.change'],p['textSecondary'],13,500,'end')))
  s.append(text(inset,208,COPY['review.title'],p['text'],23,500))
  taby=232;gap=12;tabw=(cw-3*gap)/4
  for i,(key,color) in enumerate([('review.original','original'),('review.voice1','voice1'),('review.voice2','voice2'),('review.residual','residual')]):
   x=inset+i*(tabw+gap);selected=i==1
   s.append(group('tab-'+color,rect(x,taby,tabw,53,p['surfaceRaised'] if selected else p['surface'],10,p['voice1'] if selected else p['border'])+f'<circle cx="{x+21}" cy="{taby+26}" r="3.5" fill="{p[color]}"/>'+text(x+36,taby+32,COPY[key],p['text'] if selected else p['textSecondary'],14,500)+(icon('check',x+tabw-29,taby+18,p['text'],17) if selected else '')))
  s.append(group('transport',rect(inset,309,cw,157,p['surface'],16,p['border'])+f'<circle cx="{inset+52}" cy="371" r="25" fill="{p["action"]}"/>'+icon('play',inset+41,359,p['onAction'],24)))
  tx=inset+110;tw=cw-142;position=.35
  s.append(group('timeline',rect(tx,369,tw,3,p['border'],1.5)+rect(tx,369,tw*position,3,p['voice1'],1.5)+f'<circle cx="{tx+tw*position}" cy="370.5" r="6.5" fill="{p["voice1"]}"/>'+text(tx,415,'00:04.200',p['text'],12,500,extra='font-family="Menlo,monospace"')+text(tx+tw,415,'00:12.000',p['textSecondary'],12,400,'end','font-family="Menlo,monospace"')))
  actiony=499
  s.append(button(inset,actiony,164,COPY['action.repeat'],p,False,'button-separate'))
  s.append(button(w-inset-184,actiony,184,COPY['action.export'],p,True,'button-export','export'))
  if state=='exported':
   s.append(group('export-confirmation',icon('check',inset,575,p['success'],20)+text(inset+29,590,COPY['status.exported'],p['success'],14,500)+text(w-inset,590,COPY['action.showExport'],p['textSecondary'],13,500,'end')))
 # One signature; no technical footer or marketing claims.
 s.append(group('copyright',text(center,foot,COPY['footer.copyright'],p['textMuted'],12,400,'middle')))
 return svg(''.join(s),w,h,f'Cauces — {state} screen, '+('neutral designer template' if neutral else 'Flow design proposal'))

def main():
 for name,data in ICONS.items():
  (ROOT/'assets/icons'/f'{name}.svg').write_text(svg(f'<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{data}</g>',24,24,name))
 (ROOT/'assets/brand/flow-hero-dark.svg').write_text(svg(flow(PALETTE),500,175,'Cauces flow artwork, provisional'))
 light=dict(PALETTE,original='#475B65',residual='#6B7B82',voice1='#286F61',voice2='#97672D')
 (ROOT/'assets/brand/flow-hero-light.svg').write_text(svg(flow(light),500,175,'Cauces flow artwork for light backgrounds, provisional'))
 for name,p in [('color',PALETTE),('mono',dict(PALETTE,voice1='#DCE5E3',voice2='#DCE5E3'))]:
  mark=f'<g fill="none" stroke-linecap="round" stroke-width="7"><path d="M35 48C54 48 53 23 78 23H83" stroke="{p["voice1"]}"/><path d="M35 48C54 48 53 73 78 73H83" stroke="{p["voice2"]}"/><path d="M16 48H35" stroke="{p["original"]}"/></g>'
  (ROOT/f'assets/brand/flow-mark-{name}.svg').write_text(svg(mark,96,96,'Provisional Cauces mark — '+name))
 appicon=rect(0,0,1024,1024,PALETTE['background'],222)+f'<g transform="translate(109,109) scale(8.4)">'+f'<g fill="none" stroke-linecap="round" stroke-width="7"><path d="M35 48C54 48 53 23 78 23H83" stroke="{PALETTE["voice1"]}"/><path d="M35 48C54 48 53 73 78 73H83" stroke="{PALETTE["voice2"]}"/><path d="M16 48H35" stroke="{PALETTE["original"]}"/></g></g>'
 (ROOT/'proposal/app-icon-concept.svg').write_text(svg(appicon,1024,1024,'Cauces app icon exploration — not the approved final logo'))
 for state in STATES:
  (ROOT/'proposal'/f'{state}.svg').write_text(screen(state))
  (ROOT/'templates'/f'{state}.svg').write_text(screen(state,NEUTRAL,neutral=True))
 for theme,p in [('proposal',PALETTE),('templates',NEUTRAL)]:
  (ROOT/theme/'empty-compact.svg').write_text(screen('empty',p,860,620,theme=='templates'))
 # An editable overview sheet, with no flattened screenshots or embedded fonts.
 sheet=[rect(0,0,2160,1020,'#0B1114',0),text(64,76,'CAUCES',PALETTE['text'],34,500),text(64,108,'Flow / interface study',PALETTE['textSecondary'],16)]
 for i,state in enumerate(['empty','review']):
  sheet.append(f'<g transform="translate({64+i*1048},163)">'+screen(state).replace('id="','id="'+state+'-').replace('aria-labelledby="svg-title"','aria-labelledby="'+state+'-svg-title"')+'</g>')
  sheet.append(text(64+i*1048,918,'OPEN AUDIO' if state=='empty' else 'LISTEN & EXPORT',PALETTE['textSecondary'],12,500,extra='letter-spacing="1.5"'))
 sheet.append(text(64,980,'Design proposal · Editable vectors · © GuerraMagica Audio',PALETTE['textMuted'],13))
 (ROOT/'proposal/design-board.svg').write_text(svg(''.join(sheet),2160,1020,'Cauces Flow — empty and review screen proposal'))
 for theme,p in [('proposal',PALETTE),('templates',NEUTRAL)]:
  parts=[rect(0,0,1000,490,p['background'],18),text(48,60,'Controls / interaction states',p['text'],23,500),text(48,90,'Reference for native SwiftUI controls',p['textSecondary'],13)]
  for i,label in enumerate(['Default','Hover','Pressed','Disabled','Keyboard focus']):
   x=48+i*186;y=151
   variant=dict(p)
   if label=='Hover':variant['action']='#B9EBDD' if theme=='proposal' else '#37535F'
   if label=='Pressed':variant['action']='#8ECBB9' if theme=='proposal' else '#182C35'
   if label=='Disabled':variant['action']=p['surfaceRaised'];variant['onAction']=p['textMuted']
   parts.append(text(x,y-19,label,p['textSecondary'],12))
   parts.append(button(x,y,164,'Open audio…',variant,True,'control-'+str(i)))
   if label=='Keyboard focus':parts.append(rect(x-4,y-4,172,52,'none',13,p['text'],'stroke-width="2"'))
  parts += [text(48,268,'Selection uses a checkmark and color',p['textSecondary'],14),rect(48,295,216,53,p['surfaceRaised'],10,p['voice1']),text(84,327,'Voice 1',p['text'],14,500),icon('check',235,313,p['text'],17),text(48,399,'Use native focus, keyboard navigation and accessibility semantics.',p['textSecondary'],13),text(48,452,'© GuerraMagica Audio',p['textMuted'],12)]
  (ROOT/theme/'control-states.svg').write_text(svg(''.join(parts),1000,490,'Cauces control state reference'))
 records=[]
 for path in sorted(ROOT.rglob('*.svg')):
  element=ET.parse(path).getroot()
  records.append({'file':str(path.relative_to(ROOT)),'width':int(element.attrib['width']),'height':int(element.attrib['height']),'format':'svg','editable':True,'status':'template' if 'templates' in path.parts else 'proposed','role':'control reference' if path.stem=='control-states' else 'screen' if path.parent.name in ('templates','proposal') and path.stem not in ('app-icon-concept','design-board') else 'artwork'})
 manifest={'version':1,'status':'Design proposal; awaiting approval before app integration','application':'Cauces','owner_signature':'© GuerraMagica Audio','shipping_app_changed':False,'final_logo_approved':False,'font_files_bundled':False,'external_resources':False,'standard_artboard_points':[1000,700],'minimum_artboard_points':[860,620],'states':STATES,'assets':records,'raster_previews':{'directory':'previews','screen_scale':2,'source':'Editable SVG artboards; not production UI images'},'handback_instructions':'START-HERE.md'}
 (ROOT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 print(f'Generated {len(records)} editable SVG assets.')
if __name__=='__main__':main()
