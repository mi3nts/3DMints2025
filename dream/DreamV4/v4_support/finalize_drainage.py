"""Route the central post's lower wash port sideways out of its new brace."""
import sys,os,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart,Mesh
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support','generated')
report=json.load(open(os.path.join(OUT,'validation.json')))
s=Part.Shape();s.read(os.path.join(OUT,'BaseRevised.brep'))
central=next(h for h in report['hollow_columns'] if h['label']=='M3 -10.0 -0.48')
r=next(r for r in report['nut_pockets'] if r['label']==central['label'])
pt=V(*r['point']);axis=V(*r['axis']);u=V(*r['direction']);t=central['cavity_start']+central['cavity_length']-2
# Old blind cross-bore lies wholly inside the strengthened horizontal beam.
# Fill only that bore, then restore the main axial cavity and the open +Z port.
old=Part.makeCylinder(1.3,9,pt+axis*t,u)
s=s.fuse(old)
s=s.cut(Part.makeCylinder(central['radius'],central['cavity_length'],pt+axis*central['cavity_start'],axis))
s=s.cut(Part.makeCylinder(1.3,9,pt+axis*t,V(0,0,1))).removeSplitter()
assert s.isValid() and len(s.Solids)==1
# The change lies beyond all electronics (Ymax37.3417) and before battery (Ymin44).
assert old.BoundBox.YMin>report['assembly_bbox'][4] and old.BoundBox.YMax<44
checks=[]
for h in report['hollow_columns']:
 r=next(r for r in report['nut_pockets'] if r['label']==h['label'])
 pt=V(*r['point']);axis=V(*r['axis']);u=V(*r['direction']);offset=V(*h['offset'])
 for i,t in enumerate([h['cavity_start']+2,h['cavity_start']+h['cavity_length']-2]):
  direction=V(0,0,1) if h['label']=='M3 -10.0 -0.48' and i==1 else u
  center=pt+axis*t+offset
  path=Part.makeCylinder(1.2,9,center,direction)
  endpoint=Part.makeCylinder(1.2,.5,center+direction*8.9,direction)
  overlap=s.common(path).Volume;end=s.common(endpoint).Volume
  c=dict(label=h['label'],port=i,direction=list(direction),path_overlap=overlap,outlet_overlap=end)
  checks.append(c);assert overlap<.001 and end<.001,c
print('All 18 wash ports open to exterior',flush=True)
s.exportBrep(os.path.join(OUT,'BaseRevised.brep'))
ps=s.copy();ps.rotate(V(0,0,0),V(1,0,0),-90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
if not m.isSolid() or m.hasNonManifolds():
 pts,facets=m.Topology;pts=[tuple(round(v,5) for v in p) for p in pts];m=Mesh.Mesh([tuple(pts[i] for i in f) for f in facets]);m.removeDuplicatedPoints();m.removeDuplicatedFacets();m.fixDegenerations();m.harmonizeNormals()
assert m.isSolid() and not m.hasNonManifolds()
m.write(os.path.join(ROOT,'dreamV4-BaseRevised.stl'))
report['shape_checks']['BaseRevised'].update(volume=s.Volume,mesh_facets=m.CountFacets)
report['drainage_checks']=checks
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
