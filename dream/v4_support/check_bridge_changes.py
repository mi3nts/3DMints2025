"""Check conservative bridge patch envelopes against every retained reference.

The unchanged base stock is verified byte-for-byte against the previous release.
The saved bridge feature is exactly its union with these two patches, followed
by the common functional subtraction. Checking the entire patches therefore
covers all newly added material, including more than just the difference solid.
"""
import os,sys,json,zipfile,hashlib
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support/generated')
def load(n):
 s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
with zipfile.ZipFile(os.path.join(ROOT,'v4_support/superseded/V4-before-bridge-joint-fillets.zip')) as z:
 original=z.read('v4_support/generated/BaseAfterFillets.brep')
current=open(os.path.join(OUT,'BaseAfterFillets.brep'),'rb').read()
assert hashlib.sha256(original).digest()==hashlib.sha256(current).digest()
r=json.load(open(os.path.join(OUT,'bridge-fillet-validation.json')))
H=A.openDocument(r['history']);final=H.getObject(r['final_feature']);roots=final.Shapes
assert len(roots)==3 and roots[0].Name=='StructuralFillet015'
assert [o.Name for o in roots[1:]]==[r['steps'][0]['name'],r['steps'][-1]['name']]
tool=load('BaseFunctionalCuts')
patches=[o.Shape.cut(tool).removeSplitter() for o in roots[1:]]
for p in patches:assert p.isValid() and not p.isNull()
print('Unchanged source stock verified; two conservative bridge patches prepared',flush=True)
D=A.openDocument(os.path.join(ROOT,'dreamV3-enclosure.FCStd'))
checked=0;collisions=[]
for o in D.DreamV3.OutListRecursive:
 if not hasattr(o,'Shape') or not o.Shape.Solids:continue
 checked+=1
 for i,p in enumerate(patches):
  if p.BoundBox.intersect(o.Shape.BoundBox):
   v=p.common(o.Shape).Volume
   if v>.001:collisions.append([i,o.Name,v])
assert checked>=717 and not collisions,(checked,collisions)
pairs={}
for name in ['TopRevised','USBRetainingCollar','USBClamp']:
 s=load(name);pairs[name]=sum(p.common(s).Volume for p in patches if p.BoundBox.intersect(s.BoundBox))
assert all(v<.001 for v in pairs.values()),pairs
report=json.load(open(os.path.join(OUT,'validation.json')))
stat=dict(method='Conservative complete patch envelopes; unchanged source stock SHA256 and union feature graph verified',source_stock_sha256=hashlib.sha256(current).hexdigest(),reference_parts_checked=checked,new_collisions=collisions,patch_volumes=[p.Volume for p in patches],mating_patch_checks=pairs,middle_nut_slot='Checked separately by full nut insertion sweep')
report['bridge_fit_validation']=stat
json.dump(stat,open(os.path.join(OUT,'bridge-fit-validation.json'),'w'),indent=2)
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print(json.dumps(stat,indent=2),flush=True)
