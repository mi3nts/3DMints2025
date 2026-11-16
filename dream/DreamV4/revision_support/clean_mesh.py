"""Weld STL tessellation vertices at 0.00001 mm precision; remove collapsed facets."""
import sys,os,json,collections
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD,Mesh
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name=sys.argv[1] if len(sys.argv)>1 else 'BaseRevised';path=os.path.join(ROOT,'dreamV3-'+name+'.stl')
m=Mesh.Mesh(path);points,faces=m.Topology
points=[tuple(round(c,5) for c in p) for p in points]
q=Mesh.Mesh([tuple(points[i] for i in f) for f in faces])
q.removeDuplicatedPoints();q.removeDuplicatedFacets();q.fixDegenerations();q.harmonizeNormals()
p,f=q.Topology
edges=collections.Counter(tuple(sorted((a,b))) for face in f for a,b in zip(face,face[1:]+face[:1]))
bad=[(k,v) for k,v in edges.items() if v!=2]
r={'part':name,'solid':q.isSolid(),'nonmanifold':q.hasNonManifolds(),'facets':q.CountFacets,'edge_defects':len(bad),'vertex_rounding_mm':.00001}
print(json.dumps(r),flush=True)
if q.isSolid() and not q.hasNonManifolds() and not bad:
 q.write(path)
 json.dump(r,open(os.path.join(ROOT,'revision_support/generated/mesh-cleanup.json'),'w'),indent=2)
else:
 print([(k,v,[list(p[i]) for i in k]) for k,v in bad][:20]);raise RuntimeError('Mesh remains defective')
