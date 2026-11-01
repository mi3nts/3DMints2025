# Run within the inspection session, which owns the untouched source document D.
import math
V=A.Vector
W=D.dreamV1_0_1.Placement
invW=W.inverse()
original_base=D.Fillet311.Shape.copy()
healed=original_base.copy()
assert healed.fix(1e-7,1e-7,1e-5) and healed.isValid()
local_base=healed.copy(); local_base.Placement=invW.multiply(local_base.Placement)
def world(shape):
 result=shape.copy();result.Placement=W.multiply(result.Placement);return result
def valid(s):return s.isValid() and len(s.Solids)==1
# Local coordinates are the original Dream V1 PCB coordinates.
col_left=D.Box012.Shape.transformed(invW.toMatrix()).BoundBox
col_right=D.Box011.Shape.transformed(invW.toMatrix()).BoundBox
front=col_left.ZMax
back=front-6
board_vertical_offset=-0.2
board_horizontal_offset=-4.0
board_normal_offset=6.5
board_rotation=-6.0
board_pose=A.Placement(V(board_horizontal_offset,board_vertical_offset,board_normal_offset),A.Rotation(V(0,0,1),board_rotation),V(-10,10,0))
nominal_holes=[(-47,-27.5,1.625),(27,-27.5,1.625),(-47,47.5,1.625),(27,47.5,1.625),(-41.82,-27.48,1.75)]
new_holes=[]
for x,y,r in nominal_holes:
 p=board_pose.multVec(V(x,y,0));new_holes.append((p.x,p.y,r))
old_holes=[(-46.979211120916,-27,1.625),(27.020788879084,-27,1.625),(-46.979211120916,47,1.625),(27.020788879084,47,1.625),(-39.979211120916,-25.5,1.75)]
plugs=[Part.makeCylinder(r+0.00001,6,V(x,y,back)) for x,y,r in old_holes]
filled_world=healed.multiFuse([world(q) for q in plugs]).removeSplitter()
print('Filled',valid(filled_world),filled_world.Volume,flush=True)
# Concave quarter-round additions at the inside of the two PCB columns.
# Existing column width, board seating plane and crossmembers are retained.
left=col_left.XMax;right=col_right.XMin
adds=[]
def corner(x,y,sx,sy,r):
 q=Part.makeBox(r,r,6,V(min(x,x+sx*r),min(y,y+sy*r),back))
 return q.cut(Part.makeCylinder(r,6,V(x+sx*r,y+sy*r,back)))
for x,sx in [(left,1),(right,-1)]:
 for y,sy in [(-42,1),(-16,-1),(-8,1)]:adds.append(corner(x,y,sx,sy,6))
# R6 root fillets behind each PCB column; no change to PCB seating faces.
for x in [col_left.XMin,col_right.XMin]:
 q=Part.makeBox(6,6,6,V(x,-50,back-6))
 q=q.cut(Part.makeCylinder(6,6,V(x,-44,back-6),V(1,0,0)))
 adds.append(q)
# Rounded mounting arms join each relocated hole back to its original column.
# Seating plane moves inward while retaining the original 0.602 mm board gap.
# Mounting arms span the column depth; right rear relief clears the housing ribs.
for x,y,r in new_holes:
 anchor=(col_left.XMin+col_left.XMax)/2 if x<0 else (col_right.XMin+col_right.XMax)/2
 depth=6+board_normal_offset-.5
 pad=Part.makeCylinder(4,depth,V(x,y,back+.5)).fuse(Part.makeCylinder(4,depth,V(anchor,y,back+.5)))
 if abs(anchor-x)>1e-6:
  pad=pad.fuse(Part.makeBox(abs(anchor-x),8,depth,V(min(x,anchor),y-4,back+.5)))
 pad=pad.removeSplitter()
 pad=pad.makeFillet(.75,[e for e in pad.Edges if e.BoundBox.ZLength<1e-6])
 if x>0:
  # Relieve only the outer rear of right-hand arms for the existing housing ribs.
  relief=Part.makeBox(30,200,front+.5+50,V(col_right.XMax-1,-100,-50))
  rounding=[e for e in relief.Edges if e.BoundBox.YLength>199 and abs(e.CenterOfMass.x-(col_right.XMax-1))<1e-6 and abs(e.CenterOfMass.z-(front+.5))<1e-6]
  relief=relief.makeFillet(.75,rounding)
  pad=pad.cut(relief).removeSplitter()
 if x<-53:
  # Retain the full front seat while clearing the lower-left housing rib behind it.
  relief=Part.makeBox(200,30,front+.5+50,V(-100,-56.5,-50))
  rounding=[e for e in relief.Edges if e.BoundBox.XLength>199 and abs(e.CenterOfMass.y+26.5)<1e-6 and abs(e.CenterOfMass.z-(front+.5))<1e-6]
  relief=relief.makeFillet(.75,rounding)
  pad=pad.cut(relief).removeSplitter()
 adds.append(pad)
# Fuse additions in the source world frame to preserve original surfaces exactly.
reinforced_world=filled_world.multiFuse([world(q) for q in adds]).removeSplitter()
print('Reinforced',valid(reinforced_world),reinforced_world.Volume,flush=True)
cutters=[Part.makeCylinder(r,10+board_normal_offset,V(x,y,back-2)) for x,y,r in new_holes]
revised_base=reinforced_world.cut(Part.makeCompound([world(q) for q in cutters])).removeSplitter()
assert valid(revised_base),'Invalid revised base'
s=revised_base.copy();s.Placement=invW.multiply(s.Placement)
revised_base.exportBrep('srs/revision_support/base-revised.brep')
# Four horizontal tangent slots: 3.25 wide x 7 long, centered on original bores.
slots=[]
for n in ['Sketch483','Sketch485','Sketch487','Sketch489']:
 sk=D.getObject(n);p=sk.Placement
 # capsule along sketch Y, original bore centre (-2,0)
 ends=[Part.makeCylinder(1.625,7,V(-2,t,-5)) for t in [-1.875,1.875]]
 bridge=Part.makeBox(3.25,3.75,7,V(-3.625,-1.875,-5))
 slot=ends[0].fuse(ends[1]).fuse(bridge).removeSplitter()
 slots.append(slot.transformed(p.toMatrix()))
slot_tool=Part.makeCompound(slots)
revised_shell=D.Fillet.Shape.cut(slot_tool).removeSplitter()
assert valid(revised_shell)
revised_srs=Part.makeCompound([revised_shell if x.Name=='Fillet' else x.Shape for x in D.Compound.Links])
revised_shell.exportBrep('srs/revision_support/shell-revised.brep')
slot_tool.exportBrep('srs/revision_support/slot-tool.brep')
print('Slot cut removed',D.Fillet.Shape.Volume-revised_shell.Volume,flush=True)
# Align the new board nominal outline/plane to the old board; keep IPS separate.
target_pcb=W.multiply(board_pose).multiply(A.Placement(V(-102.5,69,0),A.Rotation()))
T=target_pcb.multiply(D.Part__Feature4074.getGlobalPlacement().inverse())
ips_target=D.Part__Feature010.getGlobalPlacement()
new_electronics={}
for o in D.Part.Group:
 if not hasattr(o,'Shape'):continue
 sh=o.Shape.copy()
 delta=ips_target.multiply(o.getGlobalPlacement().inverse()) if o.Name=='Part__Feature4801' else T
 sh.Placement=delta.multiply(o.getGlobalPlacement()).multiply(o.Placement.inverse()).multiply(sh.Placement)
 new_electronics[o.Name]=sh
print('TARGET',target_pcb,'TRANSFORM',T,flush=True)
# Save reproducible CAD-render preview data.
preview={}
for name,sh in [('OriginalBase',original_base),('BaseRevised',revised_base),('PCB',new_electronics['Part__Feature4074']),('IPS',new_electronics['Part__Feature4801'])]:
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.08,AngularDeflection=.25,Relative=False)
 pts,fac=m.Topology;preview[name]={'points':[tuple(p) for p in pts],'faces':fac}
json.dump(preview,gzip.open('srs/revision_support/preview.json.gz','wt'))
print('BUILD DONE',flush=True)
