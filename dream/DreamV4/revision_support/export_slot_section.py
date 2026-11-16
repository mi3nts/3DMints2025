"""Export exact original/current post cross-sections for the dimensioned figure."""
import sys,json,zipfile,os,tempfile
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUP=os.path.join(ROOT,'revision_support');OUT=os.path.join(SUP,'generated')
plane=Part.makePlane(14,24,A.Vector(30,17,37),A.Vector(0,0,1))
data={}
with tempfile.TemporaryDirectory() as tmp:
 old=os.path.join(tmp,'original.brep')
 with zipfile.ZipFile(os.path.join(SUP,'superseded/2026-11-10-before-orange-pi-slot.zip')) as z:
  open(old,'wb').write(z.read('revision_support/generated/BaseRevised.brep'))
 for name,path in [('Original',old),('Current',os.path.join(OUT,'BaseRevised.brep'))]:
  s=Part.Shape();s.read(path);section=s.common(plane);points,faces=section.tessellate(.015)
  data[name]={'points':[list(v) for v in points],'faces':faces}
json.dump(data,open(os.path.join(OUT,'slot-section.json'),'w'))
print('Exported original and final5mm slit sections')
