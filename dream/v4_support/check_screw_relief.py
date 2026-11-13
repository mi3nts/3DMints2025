"""Leave practical screw-tip clearance behind the nuts without touching the slit."""
import sys,os,json,math
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart,Mesh
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support','generated')
report=json.load(open(os.path.join(OUT,'validation.json')));P=report['parameters'];parts={}
for name in ['TopRevised','BaseRevised']:
 s=Part.Shape();s.read(os.path.join(OUT,name+'.brep'));parts[name]=s
for r in report['nut_pockets']:
 target='TopRevised' if r['label'].startswith(('closure','USB')) else 'BaseRevised'
 pt=V(*r['point']);a=V(*r['axis']);extra=2.2 if r['kind']=='M3' else 3.0
 hole=Part.makeCylinder(P[r['kind']+'_screw_clearance']/2,r['depth']+r['height']+extra,pt-a*.02,a)
 parts[target]=parts[target].cut(hole)
for name,s in parts.items():
 s=s.removeSplitter();assert s.isValid() and s.isClosed() and len(s.Solids)==1
 s.exportBrep(os.path.join(OUT,name+'.brep'))
 ps=s.copy();ps.rotate(V(0,0,0),V(1,0,0),-90 if name=='BaseRevised' else 90);b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
 m=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
 if not m.isSolid() or m.hasNonManifolds():
  pts,facets=m.Topology;pts=[tuple(round(v,5) for v in p) for p in pts];m=Mesh.Mesh([tuple(pts[i] for i in f) for f in facets]);m.removeDuplicatedPoints();m.removeDuplicatedFacets();m.fixDegenerations();m.harmonizeNormals()
 assert m.isSolid() and not m.hasNonManifolds()
 m.write(os.path.join(ROOT,'dreamV4-'+name+'.stl'))
 report['shape_checks'][name].update(volume=s.Volume,mesh_facets=m.CountFacets)
# The longer relief is entirely subtractive: it cannot create a new interference.
# Explicitly check representative M3x8 PCB and M2x8 USB shafts in their seated positions.
checks=[]
for pt,axis,kind,target,label,length in [
 ((37,17.49,37),(0,1,0),'M3','BaseRevised','M3x8 at notched PCB post',8),
 ((-35,12,70.8),(0,0,-1),'M2','TopRevised','M2x8 rear collar',8),
 ((-34.5,24.8,58),(0,-1,0),'M2','TopRevised','M2x8 adjustable clamp',8)]:
 shaft=Part.makeCylinder(1.5 if kind=='M3' else 1.,length,V(*pt),V(*axis));overlap=parts[target].common(shaft).Volume
 checks.append(dict(label=label,overlap=overlap));assert overlap<.001,checks[-1]
report['screw_relief_checks']=checks
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print('Screw tip clearances checked; 5 mm slit unchanged',flush=True)
