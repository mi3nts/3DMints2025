"""Run one native Part Fillet in isolation; a failed OCC operation cannot lose earlier work."""
import os,sys,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
p=json.load(open(sys.argv[1]));d=A.openDocument(p['source'])
f=d.addObject('Part::Fillet','StructuralFillet');f.Label=p['label']+' — R'+str(p['radius'])
f.Base=d.getObject(p['base']);f.Edges=[(i,p['radius'],p['radius']) for i in p['edges']]
d.recompute()
s=f.Shape
assert not s.isNull() and s.isValid() and s.isClosed() and len(s.Solids)==1
s.exportBrep(p['brep']);d.saveAs(p['target'])
json.dump(dict(name=f.Name,volume=s.Volume),open(p['result'],'w'))
print('OK',f.Name,flush=True)
