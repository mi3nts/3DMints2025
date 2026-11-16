"""Geometric nut fit, insertion, antirotation and hollow/flush verification."""
import os,sys,json,math
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part,MeshPart,Mesh
V=App.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'v4_support','generated')
P=json.load(open(os.path.join(ROOT,'v4_support','parameters.json')))
report=json.load(open(os.path.join(OUT,'validation.json')))
# Reuse deterministic geometry helpers without running a build or opening the source.
s=open(os.path.join(ROOT,'v4_support','build_enclosure.py')).read()
exec(s[s.index('def rounded('):s.index("say('Building enlarged")])
def load(n):
 s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
parts={n:load(n) for n in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp']}
def nut(r,af=None,height=None):
 a=V(*r['axis']);u=V(*r['direction']);v=a.cross(u);pt=V(*r['point'])+a*(r['depth']+.15)
 af=af or P[r['kind']+'_nut_AF'];height=height or P[r['kind']+'_nut_height'];rad=af/math.sqrt(3)
 pts=[pt+u*(rad*math.cos(i*math.pi/3))+v*(rad*math.sin(i*math.pi/3)) for i in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(a*height)
checks=[];hardware=[]
for r in report['nut_pockets']:
 target='TopRevised' if r['label'].startswith(('closure','USB')) else 'BaseRevised'
 p=parts[target];n=nut(r);seated=p.common(n).Volume
 # Exact convex sweep of the hexagonal nut through its straight insertion path.
 a=V(*r['axis']);u=V(*r['direction']);v=a.cross(u)
 center=V(*r['point'])+a*(r['depth']+.15)
 af=P[r['kind']+'_nut_AF'];rad=af/math.sqrt(3);length=r['entry']
 coords=[(-rad,0),(-rad/2,-af/2),(length+rad/2,-af/2),(length+rad,0),(length+rad/2,af/2),(-rad/2,af/2)]
 pathpts=[center+u*x+v*y for x,y in coords]
 sweep=Part.Face(Part.makePolygon(pathpts+[pathpts[0]])).extrude(a*P[r['kind']+'_nut_height'])
 path_max=p.common(sweep).Volume
 rotated=n.copy();rotated.rotate(V(*r['point']),V(*r['axis']),30)
 blocked=p.common(rotated).Volume
 c=dict(label=r['label'],target=target,seated_overlap=seated,insertion_overlap=path_max,rotation30_blocked_volume=blocked)
 checks.append(c);hardware.append((r,n))
 print(c,flush=True)
 assert seated<.001 and path_max<.001 and blocked>.01,c
pair=[]
for i,(r,n) in enumerate(hardware):
 for q,m in hardware[i+1:]:
  if n.BoundBox.intersect(m.BoundBox):
   overlap=n.common(m).Volume
   assert overlap<.001,(r['label'],q['label'],overlap)
   pair.append([r['label'],q['label'],overlap])
# Exact screw-head volumes in the seated positions, below outer faces by 0.2 mm.
headchecks=[]
for x in [-35.,-9.]:
 head=cyl(1.9,2.,(x,12,70.8),V(0,0,1))
 headchecks.append(dict(part='USBRetainingCollar',x=x,head_overlap=parts['USBRetainingCollar'].common(head).Volume,recess=.2))
for x in [-34.5,-9.5]:
 for z in [55,58,61]:
  head=cyl(1.9,2.,(x,24.8,z))
  headchecks.append(dict(part='USBClamp',x=x,z=z,head_overlap=parts['USBClamp'].common(head).Volume,recess=.2))
assert all(c['head_overlap']<.001 for c in headchecks),headchecks
mating={}
for a,b in [('TopRevised','USBRetainingCollar'),('TopRevised','USBClamp'),('USBClamp','USBRetainingCollar')]:
 mating[a+' / '+b]=parts[a].common(parts[b]).Volume
assert all(v<.001 for v in mating.values()),mating
# Slot equivalence: same cut envelope, and same rear-right boss local geometry
# except the newly requested nut/hollow details above/beside the original cut.
slot=box(20,26.6,29,15.2,5,16);slot=slot.makeFillet(.7,slot.Edges)
slot_overlap=parts['BaseRevised'].common(slot).Volume
assert slot_overlap<.001
# Nut coupon includes three allowance variants, two nut sizes, real side entries.
coupon=box(0,0,0,72,4,36)
layout=[]
for row,kind in enumerate(['M3','M2']):
 for col,allow in enumerate([.2,.3,.4]):
  x=12+col*24;z=9+row*18
  block=box(x-6,0,z-6,12,13,12)
  # Face at Y=13, axis into block; slot loads toward +Z.
  P['nut_AF_allowance']=allow
  block=block.cut(nut_tool(V(x,13,z),V(0,-1,0),kind,V(0,0,1),depth=2.4,entry=7,label='coupon'))
  for dot in range(col+1):block=block.cut(cyl(.55,.5,(x-2+dot*2,13,z-4.5),V(0,-1,0)))
  coupon=coupon.fuse(block)
  layout.append(dict(kind=kind,x=x,z=z,AF_allowance=allow))
coupon=coupon.removeSplitter();assert coupon.isValid() and len(coupon.Solids)==1
coupon.exportBrep(os.path.join(OUT,'NutFitCoupon.brep'))
cp=coupon.copy();cp.rotate(V(0,0,0),V(1,0,0),90);b=cp.BoundBox;cp.translate(V(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=cp,LinearDeflection=.03,AngularDeflection=.12,Relative=False);assert m.isSolid();m.write(os.path.join(ROOT,'dreamV4-NutFitCoupon.stl'))
result=dict(nut_checks=checks,nut_pair_checks=pair,head_checks=headchecks,mating_checks=mating,orange_pi_slot_overlap=slot_overlap,hollow_columns=report['hollow_columns'],coupon_layout=layout)
json.dump(result,open(os.path.join(OUT,'fastener-validation.json'),'w'),indent=2)
print('Fastener validation passed',flush=True)
