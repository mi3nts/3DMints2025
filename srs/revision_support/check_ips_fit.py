# Check the separately placed IPS reference against the migrated PCB assembly.
ips_shape=new_electronics['Part__Feature4801']
ips_faces=[local_bbox(f) for f in ips_shape.Faces]
ips_hits=[];ips_bools=0
for name,sh in new_electronics.items():
 if name=='Part__Feature4801' or sh.Volume<1e-6 or not sh.BoundBox.intersect(ips_shape.BoundBox):continue
 box=local_bbox(sh)
 if not any(box.intersect(b) for b in ips_faces):continue
 ips_bools+=1
 v=sh.common(ips_shape).Volume
 if v>1e-5:ips_hits.append({'object':name,'label':D.getObject(name).Label,'volume':v})
validation['separate_ips_electronics_intersections']=ips_hits
validation['separate_ips_intersection_operations']=ips_bools
print('SEPARATE IPS FIT',ips_bools,ips_hits,flush=True)
assert not ips_hits,'Separate IPS overlaps the migrated PCB assembly'
