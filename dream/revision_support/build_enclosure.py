"""Rebuild the Dream V2 enclosure with FreeCAD's native Part kernel.
Run with FreeCAD Python, or exec this file from FreeCAD's Python console.
Output shapes are assembled into a new document by save_final.py.
All dimensions are millimetres; Y is enclosure depth, +Z is the rear wall.
"""
import sys, os, json, math, time
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart, Mesh
V=App.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'revision_support','generated')
os.makedirs(OUT,exist_ok=True)
SOURCE=os.path.join(ROOT,'dreamV2.FCStd')
D=App.openDocument(SOURCE)
config=os.path.join(ROOT,'revision_support','parameters.json')
P=json.load(open(config))
assert P.get('insert_dimensions_confirmed'), 'Confirm the exact insert dimensions before building.'
log=open(os.path.join(OUT,'build.log'),'w',buffering=1)
def say(x):print(x,flush=True);log.write(x+'\n')
def bbox(s):
 b=s.BoundBox;return [float(v) for v in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]
def source(n):
 o=D.getObject(n);s=o.Shape.copy();s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement);return s

def rounded(w,d,r,y,h):
 s=Part.makeBox(w,h,d,V(-w/2,y,-d/2))
 edges=[e for e in s.Edges if e.BoundBox.YLength>h-.0001 and e.BoundBox.XLength<.0001 and e.BoundBox.ZLength<.0001]
 return s.makeFillet(r,edges)
def fuse(shapes):return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes)>1 else shapes[0]
def cyl(r,h,p,axis=V(0,1,0)):return Part.makeCylinder(r,h,V(*p) if isinstance(p,tuple) else p,axis)
def box(x,y,z,l,h,d):return Part.makeBox(l,h,d,V(x,y,z))
def polygon_xz(pts,y,h):
 wire=Part.makePolygon([V(x,y,z) for x,z in pts]+[V(pts[0][0],y,pts[0][1])]);return Part.Face(wire).extrude(V(0,h,0))
def slot_z(cx,cy,w,h,z,depth,r=1.5):
 s=Part.makeBox(w,h,depth,V(cx-w/2,cy-h/2,z))
 es=[e for e in s.Edges if e.BoundBox.ZLength>depth-.001 and e.BoundBox.XLength<.001 and e.BoundBox.YLength<.001]
 return s.makeFillet(r,es)
def slot_y(cx,cz,w,d,y,h,r=1.):
 s=rounded(w,d,r,y,h);s.translate(V(cx,0,cz));return s

def pocket(pt,axis,kind):
 dia=P[kind+'_pocket_diameter'];depth=P[kind+'_pocket_depth']
 # Glue-in pocket for cured SLA: 0.20 mm diametral allowance, lead-in and screw relief.
 a=cyl(dia/2,depth+.02,pt-axis*.01,axis)
 b=Part.makeCone(dia/2+.25,dia/2,.3,pt-axis*.01,axis)
 c=cyl(1.6 if kind=='M3' else 1.1,8,pt,axis)
 return fuse([a,b,c])

say('Building enlarged rounded shell')
outside=rounded(P['outer_width'],P['outer_depth'],P['outer_corner_radius'],P['top_outer_y'],P['seam_top_y']-P['top_outer_y'])
inside=rounded(P['outer_width']-2*P['wall'],P['outer_depth']-2*P['wall'],P['inner_corner_radius'],P['top_inner_y'],P['seam_top_y']-P['top_inner_y']+1)
# Rounded face edges and internal floor transition reduce stress concentrations.
out_edges=[e for e in outside.Edges if abs(e.BoundBox.YMin-P['top_outer_y'])<1e-5 and e.BoundBox.YLength<1e-5]
outside=outside.makeFillet(1.5,out_edges)
top_shell=outside.cut(inside)
in_edges=[e for e in top_shell.Edges if abs(e.BoundBox.YMin-P['top_inner_y'])<1e-5 and e.BoundBox.YLength<1e-5]
top_shell=top_shell.makeFillet(1.5,in_edges)
closures=[(x,z) for x in [-56.,56.] for z in [-56.,56.]]
closure_solids=[]
for x,z in closures:
 sx=1 if x>0 else -1;sz=1 if z>0 else -1
 rib=polygon_xz([(sx*52,sz*56),(sx*56,sz*52),(sx*67,sz*63),(sx*63,sz*67)],30.,13.)
 closure_solids.extend([cyl(5.5,13,(x,30.,z)),rib.common(outside)])
top=fuse([top_shell]+closure_solids)
for x,z in closures:top=top.cut(pocket(V(x,43,z),V(0,-1,0),'M3'))
# Keep the supplied logo placement: face y=-17.9, flange y=-15..-13.
# A small through-profile and a wider rear counterbore form a retaining shoulder.
logo_profiles=json.load(open(os.path.join(ROOT,'revision_support','logo_profiles.json')))
def profile_tool(profiles,y,h):
 shapes=[]
 for a in profiles:
  q=polygon_xz(a['outer'][:-1],y,h)
  for hole in a['holes']:q=q.cut(polygon_xz(hole[:-1],y-.01,h+.02))
  shapes.append(q)
 return fuse(shapes)
logo_face_tool=profile_tool(logo_profiles['face'],-19,6.7)
logo_flange_tool=profile_tool(logo_profiles['flange'],-15.15,2.85)
logo=fuse([logo_face_tool,logo_flange_tool]);top=top.cut(logo)
# Recessed tool access aligned to the slider's complete travel, with a protective guide.
switch_cx=25.;switch_cy=11.905
sw_inner=slot_z(switch_cx,switch_cy,P['switch_slot_width'],P['switch_slot_height'],53.5,22.,1.5)
sw_outer=slot_z(switch_cx,switch_cy,P['switch_slot_width']+4,P['switch_slot_height']+4,54.,15.5,2.5)
top=top.fuse(sw_outer).cut(sw_inner)
# Adjustable female-extension pocket, open toward the removable base for assembly.
usb_x=-22.;usb_y=12.
usb_hole=slot_z(usb_x,usb_y,P['usb_housing_width'],P['usb_housing_height'],49,27,1.)
rails=[box(-38,5,50,7,15,20),box(-13,5,50,7,15,20),box(-38,4,50,32,3,20)]
top=fuse([top]+rails).cut(usb_hole)
# The clamp can slide 6 mm along the female housing; thin packing shims set its height.
for x in [-34.5,-9.5]:top=top.cut(pocket(V(x,20,58),V(0,-1,0),'M2'))
# Front collar retained by two M2 screws into the top cover rear wall/rails.
for x in [-35.,-9.]:top=top.cut(pocket(V(x,12,73),V(0,0,-1),'M2'))
collar=slot_z(usb_x,usb_y,34,16,73.3,2.5,2)
collar=collar.cut(slot_z(usb_x,usb_y,P['usb_throat_width'],P['usb_throat_height'],73,4,2.))
for x in [-35.,-9.]:collar=collar.cut(cyl(1.2,4,(x,12,73),V(0,0,1)))
clamp=box(-38,20.4,53,32,3,10)
for x in [-34.5,-9.5]:clamp=clamp.cut(slot_y(x,58,2.6,8,20,4,1.25))
# Side perforations: 3 mm holes on a 6.5 mm staggered pitch, solid borders at seams,
# corners, mounts, inlet and switch. Holes face the actual component chamber.
say('Rebuilding vent pattern')
vents=[]
for row in range(7):
 y=-5.5+row*P['vent_pitch']*math.sqrt(3)/2
 for col in range(14):
  u=-42.25+col*P['vent_pitch']+(P['vent_pitch']/2 if row%2 else 0)
  if u>44:continue
  for side in [-1,1]:
   vents.append(cyl(1.5,12,V(side*65,y,u),V(side,0,0)))
   # Rear clear zones protect the USB pocket and switch guide.
   if side==1 and ((-42<u<0 and y<26) or (14<u<36 and y<22)):continue
   vents.append(cyl(1.5,12,V(u,y,side*65),V(0,0,side)))
vent_tool=Part.makeCompound(vents)
top_unvented=top
top=top.cut(vent_tool).removeSplitter()

say('Building enlarged base and keeping battery/power-module compartment')
plate=rounded(146,146,27.5,43.3,5).cut(cyl(45,7,(0,42.3,0)))
# Reuse the original lower shell and its battery border so those fitted parts survive.
base_core=fuse([plate,source('m4_mac_mini_v002'),source('Extrude002'),source('Tube014'),source('Tube015')])
# Raise a shallow tongue around the base. It has 0.35 mm radial mating clearance.
lip_outer=rounded(136.3,136.3,22.65,38.3,5.2)
lip_inner=rounded(131.5,131.5,20.25,38.2,5.5)
lip=lip_outer.cut(lip_inner)
# Interrupted tongue clears the four diagonal closure ribs.
for sx in [-1,1]:
 for sz in [-1,1]:
  lip=lip.cut(box(54 if sx>0 else -74,38,54 if sz>0 else -74,20,6,20))
# Corner screw lands fill the annular plate locally and ensure continuous solid roots.
base_parts=[base_core,lip]
for x,z in closures:base_parts.append(cyl(7,5.2,(x,43.2,z)))
# Four PCB fasteners at measured mounting-hole centers; auxiliary sensor screw supports.
pcb_centers=[(-37.,-38.),(-37.,37.),(37.,-38.),(37.,37.)]
cozir_aux=[(-31.82,-37.98),(-10.,-.48)]
ips_aux=(17.5,-30.6)
base_pockets=[];mounts=[]
for x,z in pcb_centers+cozir_aux:
 base_parts.append(cyl(5,24.5,(x,19,z)));base_pockets.append(pocket(V(x,19,z),V(0,1,0),'M3'))
 mounts.append({'kind':'PCB M3' if (x,z) in pcb_centers else 'CozIR shared PCB M3','point':[x,19,z],'axis':[0,1,0],'OD':10})
# Bridge the original battery opening without covering the battery volume (starts at y=44).
base_parts.extend([box(-49,40,-4.5,44,3.5,8),box(13.5,40,-49,8,3.5,23)])
x,z=ips_aux
base_parts.append(cyl(5.5,24.5,(x,19,z)));base_pockets.append(pocket(V(x,19,z),V(0,1,0),'M2'))
mounts.append({'kind':'IPS shared PCB M2','point':[x,19,z],'axis':[0,1,0],'OD':11})
# Outboard CozIR support, aligned to the mounting ear in the supplied assembly.
cozir_pt=V(-53.36402,8.91,-.54998)
base_parts.append(cyl(5.5,34.6,cozir_pt));base_pockets.append(pocket(cozir_pt,V(0,1,0),'M3'))
# IPS cover has a 0.419-degree tilt in the STEP assembly. Match its support axis and seat.
ips_pt=V(58.39945509,7.755895925,6.15);ips_axis=V(.00730902327467736,.9999732887326392,0)
base_parts.append(cyl(5.5,35.8,ips_pt,ips_axis));base_pockets.append(pocket(ips_pt,ips_axis,'M2'))
mounts.extend([{'kind':'CozIR external M3','point':list(cozir_pt),'axis':[0,1,0],'OD':11},{'kind':'IPS external M2','point':list(ips_pt),'axis':list(ips_axis),'OD':11}])
# Wide tapered feet and two orthogonal webs reinforce tall sensor columns.
for pt in [cozir_pt,ips_pt]:
 x,z=pt.x,pt.z
 base_parts.extend([Part.makeCone(5.5,8.5,8,V(x,35.3,z),V(0,1,0)),box(x-1.6,31,z-8,3.2,12.5,16),box(x-8,31,z-1.6,16,12.5,3.2)])
# Tapered feet distribute PCB support loads into the base.
for x,z in pcb_centers+cozir_aux+[ips_aux]:
 base_parts.append(Part.makeCone(5 if (x,z)!=ips_aux else 5.5,7.5,6,V(x,37.5,z),V(0,1,0)))
# The closely spaced front-left PCB and CozIR holes share a wide obround boss.
# Their 5.18 mm center spacing would leave a brittle 0.26 mm resin web between
# 4.92 mm pockets. Join that small region into an epoxy reservoir instead.
base_parts.append(slot_y(-34.41,-37.99,15.18,10,19,24.5,4.99))
base=fuse(base_parts)
# Clearance notch for the Orange Pi board edge at the rear-right PCB column.
relief=box(20,32.6,29,15.2,3.7,16)
relief=relief.makeFillet(.7,relief.Edges)
base=base.cut(relief)
for h in base_pockets:base=base.cut(h)
base=base.cut(box(-35.1,18.99,-38.44,1.6,P['M3_pocket_depth']+.02,.9))
for x,z in closures:
 base=base.cut(cyl(1.7,8,(x,42,z))).cut(cyl(3.0,2.5,(x,46,z)))
base=base.removeSplitter()
# Removable spacing sleeves between the PCB and the sensor underside.
spacers=[]
for i,(x,z) in enumerate(cozir_aux):
 s=cyl(3.25,17.49-8.91,(x,8.91,z)).cut(cyl(1.8,10,(x,8.5,z)))
 spacers.append(('CozirSpacer'+str(i+1),s))
x,z=ips_aux
s=cyl(3.2,17.49-8.09,(x,8.09,z)).cut(cyl(1.3,10,(x,8,z)))
spacers.append(('IPSSpacer',s))

shapes={'TopShell':top_shell,'TopUnvented':top_unvented,'VentPattern':vent_tool,'LogoSeatTool':logo,'TopRevised':top,'BaseRevised':base,'USBRetainingCollar':collar,'USBClamp':clamp,**dict(spacers)}
report={'parameters':P,'mounts':mounts,'shape_checks':{},'insert_basis':'User-supplied McMaster drawings: M3 94459A769 OD4.72 x L3.43, M2 94459A767 OD3.63 x L3.18. Glue-in pockets with 0.20 diametral allowance; original mislabeled insert references superseded.','usb_fit':'Provisional 18 x 10 mm housing pocket, 11 x 5.5 mm collar throat, removable slotted clamp. Connector dimensions were not supplied.'}
for name,s in shapes.items():
 s.exportBrep(os.path.join(OUT,name+'.brep'))
 if name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp'] or 'Spacer' in name:
  check={'valid':s.isValid(),'closed':s.isClosed(),'solids':len(s.Solids),'volume':s.Volume,'bbox':bbox(s)}
  report['shape_checks'][name]=check;say(name+' '+str(check))
  # Neutral export orientation; PreForm support/drainage orientation is not validated.
  ps=s.copy()
  if name=='BaseRevised':ps.rotate(V(0,0,0),V(1,0,0),-90)
  elif name!='USBRetainingCollar':ps.rotate(V(0,0,0),V(1,0,0),90)
  b=ps.BoundBox;ps.translate(V(-b.XMin,-b.YMin,-b.ZMin))
  mesh=MeshPart.meshFromShape(Shape=ps,LinearDeflection=.04,AngularDeflection=.12,Relative=False)
  if not mesh.isSolid() or mesh.hasNonManifolds():
   points,facets=mesh.Topology
   points=[tuple(round(v,5) for v in p) for p in points]
   mesh=Mesh.Mesh([tuple(points[i] for i in f) for f in facets])
   mesh.removeDuplicatedPoints();mesh.removeDuplicatedFacets();mesh.fixDegenerations();mesh.harmonizeNormals()
  assert mesh.isSolid() and not mesh.hasNonManifolds(), name+' STL is not watertight'
  mesh_dir=ROOT if P.get('insert_dimensions_confirmed',False) else os.path.join(ROOT,'revision_support','draft_meshes')
  os.makedirs(mesh_dir,exist_ok=True)
  prefix='' if P.get('insert_dimensions_confirmed',False) else 'DRAFT-'
  mesh.write(os.path.join(mesh_dir,prefix+'dreamV3-'+name+'.stl'))
  check.update({'mesh_solid':mesh.isSolid(),'mesh_facets':mesh.CountFacets})
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
say('Finished geometry build')
