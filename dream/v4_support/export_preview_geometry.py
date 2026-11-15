"""Export validated BRep geometry for visual inspection while CAD files are being saved."""
import os,sys,json,gzip
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support/generated')
with gzip.open(os.path.join(ROOT,'revision_support/generated/preview-meshes.json.gz'),'rt') as f:data={'MintsIcon':json.load(f)['MintsIcon']}
for name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer']:
 s=Part.Shape();s.read(os.path.join(OUT,name+'.brep'));points,faces=s.tessellate(.12)
 data[name]=dict(points=[list(p) for p in points],faces=[list(f) for f in faces])
with gzip.open(os.path.join(OUT,'preview-working.json.gz'),'wt') as f:json.dump(data,f)
print('Preview geometry exported',flush=True)
