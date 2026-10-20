import sys,os,json,shutil
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'revision_support','generated')
D=A.openDocument(os.path.join(ROOT,'dreamV2.FCStd'));R=A.newDocument('DreamRevisionReview')
R.Label='DREAM structural review - INSERT SIZING PENDING'
g=R.addObject('App::DocumentObjectGroup','EnclosureRevision');g.Label='Structural revision - not ready to print'
for name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer']:
 o=R.addObject('Part::Feature',name);s=Part.Shape();s.read(os.path.join(OUT,name+'.brep'));o.Shape=s;g.addObject(o)
 o.addProperty('App::PropertyString','Status','Revision');o.Status='DRAFT ONLY: insert pockets still have obsolete provisional dimensions. Do not print.'
 o.addProperty('App::PropertyString','Material','Revision');o.Material='Formlabs White Resin V5; glue-in inserts; 0.1 mm layers'
logo=R.addObject('Mesh::Feature','LogoReference');logo.Label='mintsLogo80P - 90CutBase (original placement)';logo.Mesh=D.mintsLogo80P___90CutBase.Mesh.copy()
parts=[]
for o in D.DreamV3_1.OutListRecursive:
 if o.TypeId not in ['Part::Feature','PartDesign::Feature'] or not hasattr(o,'Shape') or not o.Shape.Solids or o.Shape.Volume<.00001:continue
 s=o.Shape.copy();s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement);parts.append(s)
e=R.addObject('Part::Feature','DreamV3Reference');e.Label='DreamV3 1 - unchanged reference';e.Shape=Part.makeCompound(parts)
notes=R.addObject('App::FeaturePython','RevisionInformation')
for n,t in [('Status','NOT READY TO PRINT: awaiting exact M3 maximum OD and M2 selection.'),('InsertInstallation','Glue-in only for cured White Resin V5. Do not use a soldering iron.'),('USB','Provisional adjustable 18 x 10 housing cradle with removable collar and slotted clamp. Measure the actual cable housing before printing.'),('Logo','Original position retained; face 0.9 mm proud; stepped rear pocket with 0.15 mm profile allowance.'),('Validation','715 source parts checked; no detected solid intersections. Minimum conservative side clearance 6.5069 mm. IPS source solid is pre-existing invalid; physical fit still required.'),('SourceFile',os.path.join(ROOT,'dreamV2.FCStd'))]:
 notes.addProperty('App::PropertyString',n,'Revision');setattr(notes,n,t)
R.recompute();path=os.path.join(ROOT,'dreamV2-revision-review.FCStd');R.saveAs(path)
A.closeDocument(R.Name);Q=A.openDocument(path)
for n in ['TopRevised','BaseRevised']:
 s=Q.getObject(n).Shape;print(n,s.isValid(),s.isClosed(),len(s.Solids),flush=True)
print('Saved',path,flush=True)
# Keep provisional meshes out of the production file area.
draft=os.path.join(ROOT,'revision_support','draft_meshes');os.makedirs(draft,exist_ok=True)
for n in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer']:
 p=os.path.join(ROOT,'dreamV2-'+n+'.stl')
 if os.path.exists(p):shutil.move(p,os.path.join(draft,'DRAFT-dreamV2-'+n+'.stl'))
