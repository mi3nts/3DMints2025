# Exact BRep collision check with conservative face-bounding-box pruning.
# A completely contained component is caught by the centre-inside test.
import time
print('FINAL INTERFERENCE BEGIN',flush=True)
def local_bbox(shape):
 q=shape.copy();q.Placement=invW.multiply(q.Placement);return q.BoundBox
faces={name:[local_bbox(f) for f in body.Faces] for name,body in [('base',revised_base),('srs002',revised_srs)]}
collisions=[];invalid=[];checked=0;booleans=0
for name,sh in new_electronics.items():
 if sh.Volume<1e-6:continue
 checked+=1
 local_box=local_bbox(sh)
 if not sh.isValid():invalid.append(name)
 for target,body in [('base',revised_base),('srs002',revised_srs)]:
  if not sh.BoundBox.intersect(body.BoundBox):continue
  intersects_face=any(local_box.intersect(b) for b in faces[target])
  if not intersects_face and not any(body.isInside(solid.CenterOfMass,1e-6,True) for solid in sh.Solids):continue
  booleans+=1
  v=sh.common(body).Volume
  if v>1e-5:
   collisions.append({'object':name,'label':D.getObject(name).Label,'part':target,'volume':v})
   print('COLLISION',collisions[-1],flush=True)
 if checked%100==0:print('Progress',checked,'exact operations',booleans,flush=True)
validation['electronics_checked']=checked
validation['exact_intersection_operations']=booleans
validation['invalid_source_electronics']=invalid
validation['collisions']=collisions
validation['board_offset_local']={'horizontal':board_horizontal_offset,'vertical':board_vertical_offset,'inward':board_normal_offset,'in_plane_rotation_deg':board_rotation,'rotation_centre':[-10,10,0]}
validation['base_shell_overlap']=revised_base.common(revised_srs).Volume
json.dump(validation,open('srs/revision_support/validation.json','w'),indent=2)
print('FINAL INTERFERENCE DONE',checked,booleans,collisions,flush=True)
