import sys,os,json,zipfile,xml.etree.ElementTree as ET
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,Mesh,MeshPart
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'revision_support/generated')
STAGE=os.path.join(ROOT,'revision_support/requested-slot-review')
P=json.load(open(os.path.join(ROOT,'revision_support/parameters.json')))
source=os.path.join(ROOT,'dreamV3-enclosure.FCStd');target=os.path.join(STAGE,'dreamV3-enclosure-slot-review.FCStd')
with zipfile.ZipFile(source) as z:
 gui=z.read('GuiDocument.xml');tree=ET.fromstring(gui)
 assets={el.attrib['file']:z.read(el.attrib['file']) for el in tree.iter() if 'file' in el.attrib}
D=A.openDocument(source)
for name in ['TopRevised','BaseRevised']:
 s=Part.Shape();s.read(os.path.join(OUT,name+'.brep'));assert s.isValid() and s.isClosed() and len(s.Solids)==1
 D.getObject(name).Shape=s
for g in [D.Top,D.Bottom]:
 g.M3PocketDepth=P['M3_pocket_depth'];g.M2PocketDepth=P['M2_pocket_depth']
def note(o,n,v):
 if n not in o.PropertiesList:o.addProperty('App::PropertyString',n,'Revision')
 setattr(o,n,v)
note(D.Bottom,'OrangePiSlot','Rear-right M3 PCB post X37 Z37: slit Y22.9..31.6, height8.7. New bottom1mm above old topY32.6.')
note(D.Bottom,'ReviewStatus','REFERENCE FIT CONFLICT: new slit no longer clears the Orange Pi PCB at its stored Y33.8039..35.0939 position. Awaiting physical mounting confirmation.')
note(D.Bottom,'NotchedInsertPocket','M3 pocket4.6deep: lower extension opens into the slit; approximately85.4% of depth stop remains. Original3.43mm insert fully surrounded at flush installation.')
D.DreamV3.FitCheck='Prior side-wall clearance6.5069mm remains. Revised base overlaps the stored Orange Pi PCB by14.062mm^3; do not interpret this as fit-validated.'
D.Label='DREAM V3 slit revision — reference fit review'
D.recompute();D.saveAs(target);A.closeDocument(D.Name)
with zipfile.ZipFile(target) as z:entries={n:z.read(n) for n in z.namelist()}
entries['GuiDocument.xml']=gui;entries.update(assets)
with zipfile.ZipFile(target+'.tmp','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in entries.items():z.writestr(n,b)
os.replace(target+'.tmp',target)
Q=A.openDocument(target);assert Q.BaseRevised.Shape.isValid();assert Q.TopRevised.Shape.isValid()
# Reuse the established coupon generator with the new pocket depths.
code=open(os.path.join(ROOT,'revision_support/save_final.py')).read()
ROOT=STAGE
exec(code[code.index('# Print coupon:'):code.index('# A separate STL')])
print('Saved review CAD and updated coupon:',target,flush=True)
