# Preserve all pre-existing mating geometry and reject any new base/housing overlap.
original_overlap=healed.common(D.Compound.Shape)
new_overlap=revised_base.common(revised_srs)
new_interference=new_overlap.cut(original_overlap,1e-6).Volume
validation['base_shell_overlap_original']=original_overlap.Volume
validation['base_shell_overlap']=new_overlap.Volume
validation['base_shell_new_interference']=new_interference
print('ASSEMBLY CHECK',original_overlap.Volume,new_overlap.Volume,new_interference,flush=True)
assert new_interference<.001,'Added base-to-housing interference'

shaft_checks=[]
for x,y,r in new_holes:
 shaft=world(Part.makeCylinder(r,6+board_normal_offset,V(x,y,back)))
 v=shaft.common(revised_srs).Volume
 shaft_checks.append(v)
validation['pcb_screw_shaft_housing_intersections']=shaft_checks
print('SCREW CHECK',shaft_checks,flush=True)
assert max(shaft_checks)<.001,'PCB fastener passage obstructed by housing'
