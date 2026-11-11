import json,os
from PIL import Image,ImageDraw,ImageFont
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
data=json.load(open(root+'revision_support/generated/slot-section.json'))
params=json.load(open(root+'revision_support/parameters.json'))
slot_height=params['orange_pi_relief_height'];slot_center=params['orange_pi_relief_center_y'];S=2
im=Image.new('RGB',(1500*S,940*S),'#f5f7f8');d=ImageDraw.Draw(im)
f=lambda n:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',n*S)
def text(x,y,t,n=20,c='#22343e'):d.text((x*S,y*S),t,font=f(n),fill=c)
def line(a,b,c='#5c7280',w=1):d.line((tuple(v*S for v in a),tuple(v*S for v in b)),fill=c,width=w*S)
text(35,22,'Orange Pi corner post — exact CAD section at Z = 37 mm',29)
text(35,67,'Higher on the page = toward the column tip. Dimensions in millimetres.',20)
for i,(name,a) in enumerate(data.items()):
 ox=100+i*730;oy=145;sc=25
 def p(x,y):return ((ox+(x-30)*sc)*S,(oy+(y-17)*sc)*S)
 text(ox,110,'Original' if i==0 else f'Current revision — {slot_height:g} mm',25)
 for face in a['faces']:d.polygon([p(*a['points'][j][:2]) for j in face],fill='#91acb8')
 # Actual insert maximum envelope, shown as a gold outline.
 d.rectangle([p(34.64,19),p(39.36,22.43)],outline='#aa7e1d',width=2*S)
 # Stored Orange Pi PCB position (the section crosses the PCB at this Z).
 d.rectangle([p(30,33.8039),p(34.5,35.0939)],fill='#d87466')
 lo,hi=(32.6,36.3) if i==0 else (slot_center-slot_height/2,slot_center+slot_height/2)
 ax=ox-38
 for yy in [lo,hi]:
  py=oy+(yy-17)*sc;line((ax-5,py),(ox+25,py));line((ax-5,py),(ax+5,py))
 line((ax,oy+(lo-17)*sc),(ax,oy+(hi-17)*sc))
 text(ax-40,oy+((lo+hi)/2-17)*sc-10,'3.7' if i==0 else f'{slot_height:.1f}',20)
 px,py=ox+370,oy+80
 text(px,py,'M3 pocket',19);text(px,py+25,'3.6 deep' if i==0 else '4.6 deep',19)
 text(ox,760,'PCB clears original slit.' if i==0 else 'Stored PCB now overlaps the post.',20,'#7c332a' if i else '#22343e')
 if i:
  # Dashed datum for the old top and solid line for the new bottom.
  yold=oy+(32.6-17)*sc;ynew=oy+(31.6-17)*sc
  for x in range(ox-15,ox+320,14):line((x,yold),(x+7,yold),'#7b8791')
  line((ox+335,ynew),(ox+335,yold))
  text(ox+345,ynew-4,'1.0',18)
text(35,823,'Blue: resin section     Gold outline: specified 3.43 mm M3 insert     Red: Orange Pi PCB reference',20)
text(35,862,'The 5 mm slit leaves the complete insert depth stop intact. Physical Orange Pi sits higher than its CAD reference.',20)
im.resize((1500,940),Image.Resampling.LANCZOS).save(root+'dreamV3-slot-comparison.png')
