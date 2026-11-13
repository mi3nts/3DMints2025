"""Re-export the strengthened clamp; rerun local fit checks after increasing its end margins."""
import sys,os,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part,MeshPart,Mesh
V=App.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support','generated')
s=open(os.path.join(ROOT,'v4_support','build_enclosure.py')).read();P=json.load(open(os.path.join(ROOT,'v4_support','parameters.json')))
exec(s[s.index('def rounded('):s.index("say('Building enlarged")])
exec(s[s.index('clamp=box('):s.index('# Flowing staggered')])
assert clamp.isValid() and len(clamp.Solids)==1
clamp.exportBrep(os.path.join(OUT,'USBClamp.brep'))
ps=clamp.copy();ps.rotate(V(0,0,0),V(1,0,0),90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
assert m.isSolid();m.write(os.path.join(ROOT,'dreamV4-USBClamp.stl'))
D=App.openDocument(os.path.join(ROOT,'dreamV3-enclosure.FCStd'))
collisions=[]
for o in D.DreamV3.OutListRecursive:
 if not hasattr(o,'Shape') or not o.Shape.Solids:continue
 if clamp.BoundBox.intersect(o.Shape.BoundBox):
  v=clamp.common(o.Shape).Volume
  if v>.001:collisions.append([o.Name,v])
assert not collisions,collisions
json.dump(dict(valid=True,solids=1,volume=clamp.Volume,bbox=[clamp.BoundBox.XMin,clamp.BoundBox.YMin,clamp.BoundBox.ZMin,clamp.BoundBox.XMax,clamp.BoundBox.YMax,clamp.BoundBox.ZMax],electronics_collisions=collisions,mesh_facets=m.CountFacets,mesh_solid=m.isSolid()),open(os.path.join(OUT,'clamp-update-validation.json'),'w'),indent=2)
print('Strengthened clamp checked',flush=True)
