"""Apply unchanged functional tools to the bridge-filleted stock and export the base."""
import sys,os,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart,Mesh
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support/generated')
def load(n):
 s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
# The wider middle node needs a longer lower wash-port exit. This only
# removes material, so earlier conservative collision checks remain valid.
cut_tool=load('BaseFunctionalCuts')
port=Part.makeCylinder(1.3,12,V(-10,39.19,-.48),V(0,0,1))
cut_tool=cut_tool.fuse(port).removeSplitter()
cut_tool.exportBrep(os.path.join(OUT,'BaseFunctionalCuts.brep'))
new=load('BridgeAfterFillets').cut(cut_tool).removeSplitter()
assert new.isValid() and new.isClosed() and len(new.Solids)==1
new.exportBrep(os.path.join(OUT,'BaseRevised.brep'))
ps=new.copy();ps.rotate(V(0,0,0),V(1,0,0),-90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
if not m.isSolid() or m.hasNonManifolds():
 pts,faces=m.Topology;pts=[tuple(round(v,5) for v in p) for p in pts];m=Mesh.Mesh([tuple(pts[i] for i in f) for f in faces]);m.removeDuplicatedPoints();m.removeDuplicatedFacets();m.fixDegenerations();m.harmonizeNormals()
assert m.isSolid() and not m.hasNonManifolds();m.write(os.path.join(ROOT,'dreamV4-BaseRevised.stl'))
r=json.load(open(os.path.join(OUT,'validation.json')));b=new.BoundBox
r['shape_checks']['BaseRevised']=dict(valid=True,closed=True,solids=1,volume=new.Volume,bbox=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],mesh_solid=True,mesh_facets=m.CountFacets)
r['middle_drain_extension']=dict(length=12,diameter=2.6,center=[-10,39.19,-.48],direction=[0,0,1],fit_check_note='Only this additional cylindrical subtraction follows the conservative bridge-patch check; it cannot add interference.')
r['bridge_fillet_validation']=json.load(open(os.path.join(OUT,'bridge-fillet-validation.json')))
r.pop('final_file_reopened',None)
json.dump(r,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print('Base exported:',new.Volume,'mm3;',m.CountFacets,'watertight facets',flush=True)
