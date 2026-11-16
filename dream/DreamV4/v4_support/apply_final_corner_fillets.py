"""Apply the final small joint blends and check their added material against all references."""
import os,sys,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart,Mesh
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support/generated')
def load(n):
 s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
old=load('BaseRevised');new=load('BaseAfterFillets').cut(load('BaseFunctionalCuts')).removeSplitter()
assert new.isValid() and new.isClosed() and len(new.Solids)==1
# Only four short edges changed; bound their blend neighborhoods explicitly.
# Local differences avoid an expensive all-face comparison of coincident solids.
zones=[Part.makeBox(4,3,7,V(-48,35,-4)),Part.makeBox(4,4,5,V(64.5,36.5,3.5))]
adds=[];removed=[]
for zone in zones:
 n=new.common(zone);o=old.common(zone);adds.append(n.cut(o));removed.append(o.cut(n))
added=Part.makeCompound(adds)
# Mass properties of the large trimmed B-spline solid have finite integration
# accuracy; compare at one part per million of the enclosing solid volume.
volume_residual=abs((new.Volume-old.Volume)-(sum(x.Volume for x in adds)-sum(x.Volume for x in removed)))
volume_tolerance=max(.001,old.Volume*1e-6)
assert volume_residual<volume_tolerance,(volume_residual,volume_tolerance)
print('Localized corner changes isolated',flush=True)
D=A.openDocument(os.path.join(ROOT,'dreamV3-enclosure.FCStd'))
checked=0;collisions=[]
for o in D.DreamV3.OutListRecursive:
 if not hasattr(o,'Shape') or not o.Shape.Solids:continue
 checked+=1
 if added.BoundBox.intersect(o.Shape.BoundBox):
  v=added.common(o.Shape).Volume
  if v>.001:collisions.append([o.Name,v])
assert checked>=717 and not collisions,(checked,collisions)
exception=new.common(D.Part__Feature4149.Shape).Volume
assert 0<exception<14.063,exception
pairs={}
for name in ['TopRevised','USBRetainingCollar','USBClamp']:
 pairs[name]=new.common(load(name)).Volume
assert all(v<.001 for v in pairs.values()),pairs
new.exportBrep(os.path.join(OUT,'BaseRevised.brep'))
ps=new.copy();ps.rotate(V(0,0,0),V(1,0,0),-90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
if not m.isSolid() or m.hasNonManifolds():
 pts,faces=m.Topology;pts=[tuple(round(v,5) for v in p) for p in pts];m=Mesh.Mesh([tuple(pts[i] for i in f) for f in faces]);m.removeDuplicatedPoints();m.removeDuplicatedFacets();m.fixDegenerations();m.harmonizeNormals()
assert m.isSolid() and not m.hasNonManifolds();m.write(os.path.join(ROOT,'dreamV4-BaseRevised.stl'))
r=dict(volume_crosscheck_residual=volume_residual,volume_crosscheck_tolerance=volume_tolerance,added_volume=added.Volume,reference_parts_checked=checked,new_collisions=collisions,retained_orange_pi_overlap=exception,mating_checks=pairs,base_volume=new.Volume,mesh_facets=m.CountFacets,mesh_solid=m.isSolid())
json.dump(r,open(os.path.join(OUT,'small-corner-validation.json'),'w'),indent=2)
print(json.dumps(r,indent=2),flush=True)
