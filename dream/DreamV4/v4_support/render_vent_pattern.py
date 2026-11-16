"""Dimensioned preview of the actual analytic four-corner perforation layout."""
import os,math,json
from PIL import Image,ImageDraw,ImageFont
from fabric_vents import layout
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W,H=1600,1050;S=2
im=Image.new('RGB',(W*S,H*S),'#f2f5f5');d=ImageDraw.Draw(im)
f=lambda n:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',n*S)
def text(x,y,t,n=23,c='#213b45'):d.text((x*S,y*S),t,font=f(n),fill=c)
text(55,35,'DREAM V4  /  FOUR-CORNER VENT PATTERN',34)
text(55,86,'Circular center holes · inward-bowed rows · elongated diagonal corner holes',23)
scale=14;cx=800;cy=460
# Ellipses drawn from the same layout as the native FreeCAD cutting tools.
d.rounded_rectangle((60*S,140*S,1540*S,790*S),radius=28*S,fill='#d8dfe0')
for q in layout():
 a=math.radians(q['angle']);pts=[]
 for k in range(96):
  t=2*math.pi*k/96;x=q['major']/2*math.cos(t);y=q['minor']/2*math.sin(t)
  xx=q['u']+x*math.cos(a)-y*math.sin(a);yy=q['y']+x*math.sin(a)+y*math.cos(a)
  pts.append(((cx+xx*scale)*S,(cy-(yy-12)*scale)*S))
 d.polygon(pts,fill='#315f74' if not q['center_circle'] else '#257d98')
text(55,830,'Center: Ø2.30 mm     Corner: 6.21 × 1.90 mm     Fourfold orientation',27)
r=json.load(open(os.path.join(ROOT,'v4_support/generated/vent-validation.json')))
text(55,881,'Measured minimum ligament: %.2f mm     •     Rear wall omits holes around USB and switch'%r['minimum_ligament'],23)
text(55,939,'A fabric-inspired geometric pattern; not a simulated latex material response.',21,'#556b72')
im.resize((W,H),Image.Resampling.LANCZOS).save(os.path.join(ROOT,'dreamV4-vent-pattern.png'))
