"""Reopen the delivered FCStd, confirm scope, placement, and print mesh integrity."""
import sys,os,json,zipfile,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[2])
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,Mesh
root=Path('srs/revision_support')
def objects_xml(path):
 with zipfile.ZipFile(path) as z:
  xml=ET.fromstring(z.read('Document.xml'))
  return {n.get('name'):n for n in xml.findall('./ObjectData/Object')}
original=objects_xml(root/'srsv4-before-dreamv3.FCStd');updated=objects_xml('srs/srsv4.FCStd')
# Verify original BRep payloads were preserved byte-for-byte in the saved history.
shape_changes=[];checked=0
with zipfile.ZipFile(root/'srsv4-before-dreamv3.FCStd') as before,zipfile.ZipFile('srs/srsv4.FCStd') as after:
 for name,obj in original.items():
  prop=obj.find("./Properties/Property[@name='Shape']")
  newer=updated[name].find("./Properties/Property[@name='Shape']")
  if prop is None or newer is None:continue
  f=next((n.get('file') for n in prop.iter() if n.get('file')),None)
  g=next((n.get('file') for n in newer.iter() if n.get('file')),None)
  if f and g:
   checked+=1
   if before.read(f)!=after.read(g):shape_changes.append(name)
print('Changed original shape payloads',len(shape_changes),shape_changes[:8],'checked',checked,flush=True)
# Compound has the new holes; the IPS reference receives its requested new placement.
assert set(shape_changes)<= {'Compound','Part__Feature4801'},str(shape_changes[:8])
D=A.openDocument('srs/srsv4.FCStd')
base=D.SRSBaseDreamV3.Shape;shell=D.SRSMountSlots.Shape
assert base.isValid() and base.isClosed() and len(base.Solids)==1
assert shell.isValid() and shell.isClosed() and len(shell.Solids)==1
assert D.SRSMountSlots in D.Compound.Links
assert D.Part__Feature4801 not in D.Part.Group
old=D.Part__Feature010.Shape.copy();old.Placement=D.Part__Feature010.getGlobalPlacement().multiply(D.Part__Feature010.Placement.inverse()).multiply(old.Placement)
ips=D.Part__Feature4801.Shape.copy();ips.Placement=D.Part__Feature4801.getGlobalPlacement().multiply(D.Part__Feature4801.Placement.inverse()).multiply(ips.Placement)
err=max((a.Point-b.Point).Length for a,b in zip(old.Vertexes,ips.Vertexes))
assert err<1e-7
meshes={}
for n in ['srsv4-SRS_Base_Fillet-DreamV3']:
 if not Path('srs/'+n+'.stl').exists():
  meshes[n]={'exported':False};continue
 mesh=Mesh.Mesh('srs/'+n+'.stl');meshes[n]={'solid':mesh.isSolid(),'nonmanifold':mesh.hasNonManifolds(),'facets':mesh.CountFacets}
 assert mesh.isSolid() and not mesh.hasNonManifolds()
report={'file_reopened':True,'source_shape_payloads_checked':checked,'changed_source_shape_payloads':shape_changes,'base_valid_closed_single_solid':True,'shell_valid_closed_single_solid':True,'ips_max_vertex_error':err,'meshes':meshes}
json.dump(report,open(root/'saved-file-verification.json','w'),indent=2)
print(json.dumps(report,indent=2),flush=True)
A.closeDocument(D.Name)
