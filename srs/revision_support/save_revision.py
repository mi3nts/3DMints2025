import os,copy,zipfile,xml.etree.ElementTree as ET
root='srs/revision_support'
source=root+'/srsv4-before-dreamv3.FCStd'
target='srs/srsv4.FCStd'
assert validation['base']['valid'] and validation['shell']['valid']
assert not validation['collisions'],validation['collisions']
assert validation['base_shell_new_interference']<.001
assert validation['base']['outside_column_regions_added']<.001
assert validation['base']['outside_column_regions_removed']<.001
assert validation['shell']['change_outside_slots']<.001
assert all(h['obstruction_volume']<.001 for h in validation['hole_clearance'])
exec(open('srs/revision_support/check_ips_fit.py').read())
def meta(o,n,v,typ='App::PropertyString'):
 o.addProperty(typ,n,'Revision');setattr(o,n,v)
# Keep all source features and append the two scoped modifications.
slot_feature=D.addObject('Part::Feature','M3MountSlotTool');slot_feature.Label='Four M3 lateral capsule cutters';slot_feature.Shape=slot_tool
meta(slot_feature,'Width',3.25,'App::PropertyLength');meta(slot_feature,'Length',7.0,'App::PropertyLength')
slotted=D.addObject('Part::Cut','SRSMountSlots');slotted.Label='SRS shell — M3 capsule mounts';slotted.Base=D.Fillet;slotted.Tool=slot_feature;slotted.Refine=True
D.Compound.Links=[slotted if o.Name=='Fillet' else o for o in D.Compound.Links]
D.Fillet311.Label='SRS_Base_Fillet — original reference'
base=D.addObject('Part::Feature','SRSBaseDreamV3');base.Label='SRS_Base_Fillet';base.Shape=revised_base
meta(base,'SourceFeature',D.Fillet311,'App::PropertyLink')
meta(base,'MountPattern','Dream V3; four corner holes: 74 x 75 mm; adjacent fifth mount. Existing bore diameters retained. See hole_centres_local in validation.json.')
meta(base,'Reinforcement','R6 concave column/brace and rear-root reinforcement; rounded integral mounting arms with R0.75 edge rounds. Only PCB column regions modified.')
meta(base,'PCBVerticalOffset',board_vertical_offset,'App::PropertyDistance')
meta(base,'PCBHorizontalOffset',board_horizontal_offset,'App::PropertyDistance')
meta(base,'PCBInPlaneRotation',board_rotation,'App::PropertyAngle')
meta(base,'PCBInwardOffset',board_normal_offset,'App::PropertyDistance')
meta(base,'ScrewReachChange',f'PCB mounting screws need approximately {board_normal_offset:g} mm more reach for the same engagement.')
meta(base,'Generator','revision_support/build_revision.py; properties document the generated BRep and do not regenerate it.')
# One rigid transform moves the PCB assembly. IPS is a separate child at the old sensor pose.
ips=D.Part__Feature4801
D.Part.removeObject(ips)
D.Part.Placement=T
D.Part.Label='Dream V3 PCB assembly'
ips.Placement=ips_target
ips.Label='IPS7100 — separate, original SRS position'
D.DreamV3.Group=[D.Part,ips,D.RetainedAccessories]
D.dreamV1_0_1.Visibility=False
D.Fillet311.Visibility=False
slot_feature.Visibility=False
D.Fillet.Visibility=False
base.Visibility=True
D.Compound.Visibility=False
D.Part.Visibility=True
D.DreamV3.Visibility=True
ips.Visibility=True
# Recompute these two native features explicitly, preserving the cached source history.
assert slotted.recompute()
assert D.Compound.recompute()
for o in [slotted,D.Compound,D.Part,base,slot_feature]:o.purgeTouched()
assert abs(slotted.Shape.Volume-revised_shell.Volume)<.001
assert abs(D.Compound.Shape.Volume-revised_srs.Volume)<.001
assert slotted.Shape.isValid() and base.Shape.isValid()
D.saveAs(root+'/srsv4-updated-headless.FCStd')
# Restore original view providers and their materials, adding providers for new features.
with zipfile.ZipFile(source) as src:
 gui=ET.fromstring(src.read('GuiDocument.xml'))
 data=gui.find('ViewProviderData');providers={p.get('name'):p for p in data.findall('ViewProvider')}
 def visibility(p,v):
  node=p.find("./Properties/Property[@name='Visibility']/Bool")
  if node is not None:node.set('value','true' if v else 'false')
 for n,v in [('dreamV1_0_1',False),('Fillet311',False),('Fillet',False),('Part',True),('DreamV3',True),('Part__Feature4801',True),('Compound',False)]:visibility(providers[n],v)
 for name,template,vis in [('M3MountSlotTool','Extrude190',False),('SRSMountSlots','Fillet',False),('SRSBaseDreamV3','Fillet311',True)]:
  p=copy.deepcopy(providers[template]);p.set('name',name);p.set('expanded','0');p.set('treeRank',str(len(providers)));visibility(p,vis);data.append(p);providers[name]=p
 data.set('Count',str(len(providers)))
 assets={node.get('file'):src.read(node.get('file')) for node in gui.iter() if node.get('file') and node.get('file') in src.namelist()}
 gui_bytes=ET.tostring(gui,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(root+'/srsv4-updated-headless.FCStd') as raw,zipfile.ZipFile(target+'.tmp','w',zipfile.ZIP_DEFLATED) as out:
  # Retain untouched source BReps byte-for-byte instead of resaving kernel flags
  # and floating point normalization from the load/validate cycle.
  original_xml=ET.fromstring(src.read('Document.xml'))
  saved_xml=ET.fromstring(raw.read('Document.xml'))
  saved_objects={o.get('name'):o for o in saved_xml.findall('./ObjectData/Object')}
  restore_shapes={}
  for obj in original_xml.findall('./ObjectData/Object'):
   name=obj.get('name')
   if name in ['Compound','Part__Feature4801']:continue
   a=obj.find("./Properties/Property[@name='Shape']")
   b=saved_objects[name].find("./Properties/Property[@name='Shape']")
   if a is None or b is None:continue
   old=next((q.get('file') for q in a.iter() if q.get('file')),None)
   new=next((q.get('file') for q in b.iter() if q.get('file')),None)
   if old and new:restore_shapes[new]=old
  for n in raw.namelist():
   if n!='GuiDocument.xml' and n not in assets:
    out.writestr(n,src.read(restore_shapes[n]) if n in restore_shapes else raw.read(n))
  out.writestr('GuiDocument.xml',gui_bytes)
  for n,bits in assets.items():out.writestr(n,bits)
os.replace(target+'.tmp',target)
# Keep mesh export separate: the source housing has an invalid T-slot feature.
validation['print_meshes']={}
validation['base_stl_status']='Not exported: standard tessellation has a root gap. CAD verified valid and closed; no print-ready STL supplied.'
validation['housing_stl_status']='Not exported: unchanged source Fillet296 (T-slot) is invalid; full housing mesh is nonmanifold. Source geometry preserved.'
json.dump(validation,open(root+'/validation.json','w'),indent=2)
print('SAVED',target,flush=True)
