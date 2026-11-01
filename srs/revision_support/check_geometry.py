import time
validation={}
print('VALIDATE BEGIN',flush=True)
# Compare geometry to enforce the requested scope.
added=revised_base.cut(healed,1e-6)
removed=healed.cut(revised_base,1e-6)
allowed_local=Part.makeCompound([Part.makeBox(28,110,24,V(-61,-51,back-7)),Part.makeBox(28,110,24,V(13,-51,back-7))])
allowed=allowed_local.transformed(W.toMatrix())
validation['base']={'valid':revised_base.isValid(),'solids':len(revised_base.Solids),'volume':revised_base.Volume,'added_volume':added.Volume,'removed_volume':removed.Volume,'outside_column_regions_added':added.cut(allowed,1e-6).Volume,'outside_column_regions_removed':removed.cut(allowed,1e-6).Volume}
validation['shell']={'valid':revised_shell.isValid(),'solid_count':len(revised_shell.Solids),'removed_volume':D.Fillet.Shape.Volume-revised_shell.Volume,'added_volume':revised_shell.cut(D.Fillet.Shape).Volume,'change_outside_slots':D.Fillet.Shape.cut(revised_shell).cut(slot_tool).Volume,'slot_width':3.25,'slot_length':7.0,'travel_total':3.75}
validation['hole_centres_local']=new_holes
validation['hole_clearance']=[{'x':x,'y':y,'diameter':r*2,'obstruction_volume':s.common(Part.makeCylinder(r-1e-5,6+board_normal_offset,V(x,y,back))).Volume} for x,y,r in new_holes]
oldips=D.Part__Feature010.Shape.copy();oldips.Placement=ips_target
validation['ips']={'max_vertex_error':max((a.Point-b.Point).Length for a,b in zip(oldips.Vertexes,new_electronics['Part__Feature4801'].Vertexes)),'old_bbox':bb(oldips),'new_bbox':bb(new_electronics['Part__Feature4801'])}
print('Geometry checks',validation,flush=True)

json.dump(validation,open('srs/revision_support/final-geometry-check.json','w'),indent=2)
print('FINAL GEOMETRY DONE',flush=True)
