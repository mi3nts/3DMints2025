import sys,os,json,math
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'revision_support','generated')
D=A.openDocument(os.path.join(ROOT,'dreamV2.FCStd'))
def load(n):s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
def sh(o):
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement);return s
parts={n:load(n) for n in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer']}
report=json.load(open(os.path.join(OUT,'validation.json')))
checks={};collisions=[];electronics=[]
for o in D.DreamV3_1.OutListRecursive:
 if o.TypeId not in ['Part::Feature','PartDesign::Feature']:continue
 if not hasattr(o,'Shape') or o.Shape.isNull() or not o.Shape.Solids:continue
 s=sh(o)
 if s.Volume>.00001:electronics.append((o,s))
print('Checking',len(electronics),'electronic leaf parts',flush=True)
# Test only bounding-box candidates; planar contact is allowed, volumetric intrusion is not.
for n,part in parts.items():
 for o,s in electronics:
  if not part.BoundBox.intersect(s.BoundBox):continue
  try:
   c=part.common(s);v=c.Volume
   if v>.001:collisions.append({'enclosure':n,'component':o.Name,'label':o.Label,'volume':v})
  except Exception as e:collisions.append({'enclosure':n,'component':o.Name,'error':str(e)})
 print(n,'checked',flush=True)
for n in ['TopRevised','USBRetainingCollar','USBClamp']:
 checks[n+'_Base_common_volume']=parts[n].common(parts['BaseRevised']).Volume
# Bound conservative envelopes of actual components, excluding construction axes and origins.
b=A.BoundBox()
for o,s in electronics:b.add(s.BoundBox)
report['assembly_bbox']=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
report['flat_side_clearances']={'left':b.XMin+68.5,'right':68.5-b.XMax,'front':b.ZMin+68.5,'rear':68.5-b.ZMax}
# A component bounding box is conservative. Its four XZ corners must lie within the
# rounded inner profile eroded by 5 mm: half-size=63.5, radius=18, corner center=45.5.
minimum_bound=1e9
worst=None
for o,s in electronics:
 q=s.BoundBox
 for x in [q.XMin,q.XMax]:
  for z in [q.ZMin,q.ZMax]:
   dx=max(abs(x)-45.5,0);dz=max(abs(z)-45.5,0)
   gap=23-math.hypot(dx,dz) if dx and dz else 68.5-max(abs(x),abs(z))
   if gap<minimum_bound:minimum_bound=gap;worst=o.Label
report['minimum_side_clearance_conservative']=minimum_bound;report['limiting_component']=worst
report['pair_checks']=checks;report['collisions']=collisions
report['electronics_checked']=len(electronics)
report['source_invalid_solids']=[o.Name for o,s in electronics if not s.isValid()]
# Sleeve seating is independent of the old extra power board; retained reference objects
# are reported separately as they are not part of DreamV3 1.
report['retained_reference_collisions']=[]
for n in ['Part__Feature3680','Adafruit_PowerBoost_1000C_Rev_B_1']:
 s=sh(D.getObject(n))
 for name,p in parts.items():
  if p.BoundBox.intersect(s.BoundBox):
   v=p.common(s).Volume
   if v>.001:report['retained_reference_collisions'].append({'part':name,'reference':n,'volume':v})
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print(json.dumps({k:report[k] for k in ['flat_side_clearances','minimum_side_clearance_conservative','limiting_component','pair_checks','collisions','retained_reference_collisions','source_invalid_solids']},indent=2),flush=True)
