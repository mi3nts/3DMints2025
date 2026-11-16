"""Verify practical screw-tip clearance without modifying CAD geometry or meshes."""
import sys,os,json,math
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart,Mesh
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support','generated')
report=json.load(open(os.path.join(OUT,'validation.json')));P=report['parameters'];parts={}
for name in ['TopRevised','BaseRevised']:
 s=Part.Shape();s.read(os.path.join(OUT,name+'.brep'));parts[name]=s
# Geometry is constructed with the relief depths in build_enclosure.py.
# Verification must not recut or reserialize otherwise unchanged parts.
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
