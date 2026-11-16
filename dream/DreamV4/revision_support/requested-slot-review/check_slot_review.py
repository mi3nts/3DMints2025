import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE);STAGE=os.path.join(HERE,'requested-slot-review')
# Run the normal cavity/preview checks against the staged document. Record the
# deliberately exposed bottom of the revised corner pocket rather than hiding it.
s=open(os.path.join(HERE,'verify_pockets.py')).read()
s=s.replace("os.path.join(ROOT, 'dreamV3-enclosure.FCStd')", "os.path.join(STAGE, 'dreamV3-enclosure-slot-review.FCStd')")
s=s.replace("    assert seat_fraction > .99, result", "    result['complete_depth_stop'] = seat_fraction > .99\n    if not result['complete_depth_stop']:\n        assert obj == 'BaseRevised' and (pt-A.Vector(37,19,37)).Length < .001 and seat_fraction > .8, result\n        result['limitation'] = 'Lower pocket extension opens into the user-requested raised slit; partial depth stop.'")
s=s.replace("json.dump(r, open(os.path.join(OUT, 'validation.json'), 'w'), indent=2)","json.dump(r, open(os.path.join(STAGE, 'pocket-validation.json'), 'w'), indent=2)")
exec(compile(s,os.path.join(HERE,'verify_pockets.py'),'exec'))
import Mesh,collections
checks={}
for name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer','MintsIcon','InsertFitCoupon']:
 m=Mesh.Mesh(os.path.join(STAGE,'dreamV3-'+name+'.stl'));pts,f=m.Topology
 e=collections.Counter(tuple(sorted((a,b))) for tri in f for a,b in zip(tri,tri[1:]+tri[:1]))
 stats={'solid':m.isSolid(),'nonmanifold':m.hasNonManifolds(),'facets':m.CountFacets,'edge_defects':sum(n!=2 for n in e.values())}
 assert stats['solid'] and not stats['nonmanifold'] and not stats['edge_defects'],(name,stats)
 checks[name]=stats
json.dump(checks,open(os.path.join(STAGE,'mesh-validation.json'),'w'),indent=2)
print('Nine review STL meshes are closed and manifold',flush=True)
