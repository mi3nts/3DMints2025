"""Update only the four capsule cutters and their two dependent shape caches."""
import os,sys,json,copy,hashlib,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[2]);sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
root=Path('srs/revision_support');target=Path('srs/srsv4.FCStd')
original_bytes=target.read_bytes();original_hash=hashlib.sha256(original_bytes).hexdigest()
backup=root/'srsv4-before-7mm-capsules.FCStd'
if not backup.exists():backup.write_bytes(original_bytes)
D=A.openDocument(str(target));V=A.Vector
old_shell=D.SRSMountSlots.Shape.copy()
slots=[];dimensions=[]
for name in ['Sketch483','Sketch485','Sketch487','Sketch489']:
 ends=[Part.makeCylinder(1.625,7,V(-2,y,-5)) for y in [-1.875,1.875]]
 bridge=Part.makeBox(3.25,3.75,7,V(-3.625,-1.875,-5))
 slot=ends[0].fuse(ends[1]).fuse(bridge).removeSplitter()
 dimensions.append([slot.BoundBox.XLength,slot.BoundBox.YLength])
 assert abs(slot.BoundBox.XLength-3.25)<1e-7 and abs(slot.BoundBox.YLength-7)<1e-7
 slots.append(slot.transformed(D.getObject(name).Placement.toMatrix()))
tool=Part.makeCompound(slots)
D.M3MountSlotTool.Shape=tool;D.M3MountSlotTool.Length=7
D.SRSMountSlots.Shape=old_shell.cut(tool).removeSplitter()
assert D.Compound.recompute()
for o in [D.M3MountSlotTool,D.SRSMountSlots,D.Compound]:o.purgeTouched()
new_shell=D.SRSMountSlots.Shape
assert new_shell.isValid() and new_shell.isClosed() and len(new_shell.Solids)==1
added=new_shell.cut(old_shell,1e-6).Volume
removed=old_shell.cut(new_shell,1e-6)
outside=removed.cut(tool,1e-6).Volume
print('DIFFERENCE',added,outside,'volumes',old_shell.Volume,new_shell.Volume,flush=True)
assert added<.001 and outside<.001
report={'capsule_dimensions_mm':dimensions,'shell_valid_closed_single_solid':True,'material_added_mm3':added,'material_removed_this_update_mm3':removed.Volume,'change_outside_capsules_mm3':outside,'source_sha256':original_hash}
print('GEOMETRY',report,flush=True)
raw=root/'capsules-7mm-headless.FCStd';D.saveAs(str(raw));A.closeDocument(D.Name)
# Preserve all other objects, resources, view providers and document settings exactly.
updates={'M3MountSlotTool':['Shape','Length'],'SRSMountSlots':['Shape'],'Compound':['Shape']}
with zipfile.ZipFile(target) as src,zipfile.ZipFile(raw) as new:
 xml=ET.fromstring(src.read('Document.xml'));newxml=ET.fromstring(new.read('Document.xml'));replacements={}
 for name,properties in updates.items():
  oldprops=xml.find("./ObjectData/Object[@name='%s']/Properties"%name)
  newprops=newxml.find("./ObjectData/Object[@name='%s']/Properties"%name)
  for propname in properties:
   prior=oldprops.find("Property[@name='%s']"%propname)
   updated=copy.deepcopy(newprops.find("Property[@name='%s']"%propname))
   if propname=='Shape':
    oldfile=next(n.get('file') for n in prior.iter() if n.get('file'))
    file_node=next(n for n in updated.iter() if n.get('file'))
    replacements[oldfile]=new.read(file_node.get('file'));file_node.set('file',oldfile)
   index=list(oldprops).index(prior);oldprops.remove(prior);oldprops.insert(index,updated)
 replacements['Document.xml']=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(str(target)+'.tmp','w',zipfile.ZIP_DEFLATED) as out:
  for name in src.namelist():out.writestr(name,replacements.get(name,src.read(name)))
assert hashlib.sha256(target.read_bytes()).hexdigest()==original_hash,'Source changed during update'
os.replace(str(target)+'.tmp',target)
with zipfile.ZipFile(backup) as before,zipfile.ZipFile(target) as after:
 changed=[n for n in before.namelist() if before.read(n)!=after.read(n)]
 assert set(changed)==set(replacements),changed
report['changed_archive_entries']=changed
D=A.openDocument(str(target))
assert D.M3MountSlotTool.Length.Value==7
assert D.SRSMountSlots.Shape.isValid() and D.SRSMountSlots.Shape.isClosed()
assert D.SRSBaseDreamV3.Shape.isValid()
report['saved_file_reopened']=True
report['removed_volume_from_original_circular_holes_mm3']=D.Fillet.Shape.Volume-D.SRSMountSlots.Shape.Volume
A.closeDocument(D.Name)
(root/'capsules-7mm-verification.json').write_text(json.dumps(report,indent=2))
raw.unlink()
print('SAVED AND VERIFIED',report,flush=True)
