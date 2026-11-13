"""Save V4 assembly and separate base/top files; preserve V3 and its electronics."""
import sys,os,json,zipfile,copy,collections,gzip,shutil,hashlib
import xml.etree.ElementTree as ET
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,Mesh,MeshPart
V=A.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support','generated')
P=json.load(open(os.path.join(ROOT,'v4_support','parameters.json')))
report=json.load(open(os.path.join(OUT,'validation.json')))
fast=json.load(open(os.path.join(OUT,'fastener-validation.json')))
clampcheck=json.load(open(os.path.join(OUT,'clamp-update-validation.json')))
assert report['electronics_checked']==715
assert not report['retained_reference_collisions'],report['retained_reference_collisions']
assert report['minimum_side_clearance_conservative']>=5
assert all(v<.001 for v in report['pair_checks'].values())
assert all(c.get('component')=='Part__Feature4149' and c.get('enclosure')=='BaseRevised' and 0<c.get('volume',0)<14.063 for c in report['collisions']),report['collisions']
assert len(fast['nut_checks'])==17
assert not clampcheck['electronics_collisions']
report['shape_checks']['USBClamp']=clampcheck
SOURCE=os.path.join(ROOT,'dreamV3-enclosure.FCStd')
D=A.openDocument(SOURCE);D.Label='DREAM V4 — captured nuts / White V5'
labels={'TopRevised':'Top V4 — flowing vents and flush USB collar','BaseRevised':'Base V4 — captured nuts and braced CozIR mount','USBRetainingCollar':'USB-C flush retaining collar — M2 nuts','USBClamp':'USB-C recessed-head adjustable clamp','CozirSpacer1':'CozIR spacer 1','CozirSpacer2':'CozIR spacer 2','IPSSpacer':'IPS7100 spacer'}
def meta(o,n,v,typ='App::PropertyString'):
 if n not in o.PropertiesList:o.addProperty(typ,n,'V4 Design')
 setattr(o,n,v)
def load(n):
 s=Part.Shape();s.read(os.path.join(OUT,n+'.brep'));return s
for name,label in labels.items():
 o=D.getObject(name);s=load(name)
 assert s.isValid() and s.isClosed() and len(s.Solids)==1,name
 o.Shape=s;o.Label=label
 meta(o,'Generator','v4_support/build_enclosure.py — native FreeCAD BRep; dimensioned rebuild script included')
for g in [D.Top,D.Bottom]:
 for n in ['InsertInstallation','M3Insert','M2Insert','M3PocketDiameter','M3PocketDepth','M2PocketDiameter','M2PocketDepth','NotchedInsertPocket']:
  if n in g.PropertiesList:g.removeProperty(n)
 meta(g,'Version','V4 — separate nut-fastened revision; V3 unchanged')
 meta(g,'Fasteners','M3 nut 90591A250 / M2 nut 90591A265; socket-head screws 91290A113 / 91292A834')
 meta(g,'M3NutSeat','5.80 mm across flats x 2.70 mm high; screw clearance 3.40 mm')
 meta(g,'M2NutSeat','4.30 mm across flats x 1.90 mm high; screw clearance 2.40 mm')
 meta(g,'FitAllowance','0.30 mm across-flats and thickness allowance. Print and post-cure NutFitCoupon first.')
meta(D.Top,'USBFit','Provisional 18 x 10 housing; 11 x 5.5 throat. Collar face Z73 flush with enclosure. M2 heads 0.2 mm recessed. Clamp travel 6 mm.')
meta(D.Top,'Vents','Flowing capsule field: width2.2, length3.5–4.5, varying angle up to42 degrees; 7.5 mm triangular pitch, >=3 mm ligament.')
meta(D.Bottom,'PairedMount','Front-left PCB and CozIR nuts staggered: nut-pocket depths2.4 and6.3 mm; pockets load from opposite Z directions.')
meta(D.Bottom,'HollowColumns','Nine posts hollow along62% of height. Two2.6mm cross-drains per post. Offset1.2mm cavity in notched post preserves Orange Pi notch wall.')
meta(D.Bottom,'CozirReinforcement','Central mount has two12mm-wide x7mm-deep rounded beams, front and left annular anchorage, and a tapered16mm node.')
meta(D.Bottom,'OrangePiSlot','Unchanged from V3: rounded slit Y26.6..31.6, height5mm. Physical Orange Pi is higher than the stored reference, as confirmed by user.')
meta(D.DreamV3,'FitCheck','715 components checked; only retained old Orange Pi reference overlap14.062mm^3. Minimum side clearance6.5069mm. Invalid source ips7101 remains a fit-check limitation.')
D.recompute()
TARGET=os.path.join(ROOT,'dreamV4-enclosure.FCStd');D.saveAs(TARGET)
# Use original view providers/materials for matching object names, retaining colors.
with zipfile.ZipFile(SOURCE) as z:
 gui=ET.fromstring(z.read('GuiDocument.xml'))
 assets={n:z.read(n) for n in z.namelist() if n.startswith(('ShapeAppearance','LineColorArray','PointColorArray')) or n.endswith('Material')}
def patch_gui(path,names,camera=None):
 root=copy.deepcopy(gui);data=root.find('ViewProviderData')
 for vp in list(data):
  if vp.attrib.get('name') not in names:data.remove(vp)
 data.set('Count',str(len(data)))
 if camera is not None:root.find('Camera').set('settings',camera)
 with zipfile.ZipFile(path) as z:entries={n:z.read(n) for n in z.namelist() if n!='GuiDocument.xml'}
 entries['GuiDocument.xml']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
 entries.update(assets)
 temp=path+'.tmp'
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in entries.items():z.writestr(n,b)
 os.replace(temp,path)
patch_gui(TARGET,{o.Name for o in D.Objects})
standalone=[]
for kind,names in [('Base',['BaseRevised','CozirSpacer1','CozirSpacer2','IPSSpacer']),('Top',['TopRevised','USBRetainingCollar','USBClamp','MintsIcon'])]:
 S=A.newDocument('DreamV4'+kind);S.Label='DREAM V4 '+kind+' — captured nuts'
 for name in names:
  old=D.getObject(name);new=S.addObject(old.TypeId,name);new.Label=old.Label
  if name=='MintsIcon':new.Mesh=old.Mesh.copy()
  else:new.Shape=old.Shape.copy()
  meta(new,'Version','V4; see dreamV4-enclosure-notes.md and v4_support/parameters.json')
 S.recompute();path=os.path.join(ROOT,'dreamV4-'+kind+'.FCStd');S.saveAs(path)
 patch_gui(path,set(names));standalone.append(path);A.closeDocument(S.Name)
# Native coupon document for inspection as well as its printable STL.
S=A.newDocument('DreamV4NutFitCoupon');o=S.addObject('Part::Feature','NutFitCoupon');o.Shape=load('NutFitCoupon');S.recompute();S.saveAs(os.path.join(ROOT,'dreamV4-NutFitCoupon.FCStd'));A.closeDocument(S.Name)
# Logo is unchanged; byte-identical printable mesh.
shutil.copyfile(os.path.join(ROOT,'dreamV3-MintsIcon.stl'),os.path.join(ROOT,'dreamV4-MintsIcon.stl'))
mesh_checks={}
for name in list(labels)+['MintsIcon','NutFitCoupon']:
 path=os.path.join(ROOT,'dreamV4-'+name+'.stl');m=Mesh.Mesh(path);pts,facets=m.Topology
 edges=collections.Counter(tuple(sorted((a,b))) for f in facets for a,b in zip(f,f[1:]+f[:1]))
 stat=dict(solid=m.isSolid(),nonmanifold=m.hasNonManifolds(),edge_defects=sum(v!=2 for v in edges.values()),facets=m.CountFacets,sha256=hashlib.sha256(open(path,'rb').read()).hexdigest())
 assert stat['solid'] and not stat['nonmanifold'] and stat['edge_defects']==0,(name,stat)
 mesh_checks[name]=stat
# Export actual, assembled CAD triangles for honest geometry previews.
preview={}
for name in labels:
 pts,faces=D.getObject(name).Shape.tessellate(.12);preview[name]={'points':[list(p) for p in pts],'faces':[list(f) for f in faces]}
p,f=D.MintsIcon.Mesh.Topology;preview['MintsIcon']={'points':[list(v) for v in p],'faces':[list(v) for v in f]}
with gzip.open(os.path.join(OUT,'preview-meshes.json.gz'),'wt') as f:json.dump(preview,f)
A.closeDocument(D.Name)
for path in [TARGET]+standalone:
 Q=A.openDocument(path)
 for name in labels:
  o=Q.getObject(name)
  if o:assert o.Shape.isValid() and len(o.Shape.Solids)==1,(path,name)
 A.closeDocument(Q.Name)
report.update(final_file=TARGET,standalone_files=standalone,final_file_reopened=True,mesh_checks=mesh_checks,fastener_validation=fast,clamp_update_validation=clampcheck)
json.dump(report,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print(json.dumps(dict(saved=TARGET,standalone=standalone,mesh_checks=mesh_checks),indent=2),flush=True)
