"""Independently probe the saved CAD's insert pockets and export preview triangles."""
import sys, os, json, gzip
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A, Part, MeshPart
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'revision_support', 'generated')
D = A.openDocument(os.path.join(ROOT, 'dreamV3-enclosure.FCStd'))
r = json.load(open(os.path.join(OUT, 'validation.json')))
p = r['parameters']
tests = []
for mount in r['mounts']:
    tests.append(('BaseRevised', 'M2' if 'M2' in mount['kind'] else 'M3',
                  A.Vector(*mount['point']), A.Vector(*mount['axis'])))
for x in [-56., 56.]:
    for z in [-56., 56.]:
        tests.append(('TopRevised', 'M3', A.Vector(x,43,z), A.Vector(0,-1,0)))
for x in [-34.5, -9.5]:
    tests.append(('TopRevised', 'M2', A.Vector(x,20,58), A.Vector(0,-1,0)))
for x in [-35., -9.]:
    tests.append(('TopRevised', 'M2', A.Vector(x,12,73), A.Vector(0,0,-1)))
results = []
for obj, kind, pt, axis in tests:
    s = D.getObject(obj).Shape
    rad, depth = p[kind+'_pocket_diameter']/2, p[kind+'_pocket_depth']
    probe = Part.makeCylinder(rad-.005, depth-.04, pt+axis*.02, axis)
    intrusion = s.common(probe).Volume
    # A narrow ring immediately below the insert pocket must remain a depth stop.
    pos = pt+axis*(depth+.05)
    seat = Part.makeCylinder(rad-.05, .1, pos, axis).cut(
        Part.makeCylinder(1.7 if kind == 'M3' else 1.2, .1, pos, axis))
    seat_fraction = s.common(seat).Volume / seat.Volume
    result = dict(object=obj, insert=kind, point=list(pt), diameter=rad*2,
                  nominal_depth=depth, pocket_intrusion_mm3=intrusion,
                  depth_stop_fraction=seat_fraction)
    assert intrusion < .001, result
    assert seat_fraction > .99, result
    results.append(result)
    print(obj, kind, list(pt), 'clear / depth stop present', flush=True)
r['insert_pocket_checks'] = results
json.dump(r, open(os.path.join(OUT, 'validation.json'), 'w'), indent=2)

data = {}
for name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp',
             'CozirSpacer1','CozirSpacer2','IPSSpacer','MintsIcon']:
    o = D.getObject(name)
    m = o.Mesh if name == 'MintsIcon' else MeshPart.meshFromShape(
        Shape=o.Shape, LinearDeflection=.12, AngularDeflection=.2, Relative=False)
    pts, faces = m.Topology
    data[name] = {'points':[list(v) for v in pts], 'faces':faces}
with gzip.open(os.path.join(OUT, 'preview-meshes.json.gz'), 'wt') as f:
    json.dump(data, f)
print('Verified', len(results), 'pockets and exported preview geometry', flush=True)
