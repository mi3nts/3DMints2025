"""Save the verified revision as a new FreeCAD document, preserving source colors.

Run using the Python bundled with FreeCAD. The original document is read only.
"""
import sys, os, json, copy, zipfile, struct, collections
import xml.etree.ElementTree as ET
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A, Part, Mesh, MeshPart

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'revision_support', 'generated')
SOURCE = os.path.join(ROOT, 'dreamV2.FCStd')
TARGET = os.path.join(ROOT, 'dreamV3-enclosure.FCStd')
P = json.load(open(os.path.join(ROOT, 'revision_support', 'parameters.json')))
report = json.load(open(os.path.join(OUT, 'validation.json')))
assert P['insert_dimensions_confirmed']
assert report['electronics_checked'] == 715 and not report['collisions']
assert not report['retained_reference_collisions']
assert report['minimum_side_clearance_conservative'] >= 5
assert all(v < .001 for v in report['pair_checks'].values())
D = A.openDocument(SOURCE)
R = A.newDocument('DreamV3Enclosure')
R.Label = 'DREAM V3 enclosure — White V5 / glued inserts'

def meta(obj, name, value, kind='App::PropertyString', group='Design'):
    obj.addProperty(kind, name, group)
    setattr(obj, name, value)

top = R.addObject('App::DocumentObjectGroup', 'Top')
top.Label = 'Top'
bottom = R.addObject('App::DocumentObjectGroup', 'Bottom')
bottom.Label = 'Bottom'
for group in [top, bottom]:
    meta(group, 'Material', 'Formlabs White Resin V5')
    meta(group, 'LayerHeight', .1, 'App::PropertyLength')
    meta(group, 'InsertInstallation', 'Glue into washed and fully post-cured pockets. No heat-setting.')
    meta(group, 'M3Insert', 'McMaster 94459A769: maximum OD 4.72 mm; length 3.43 mm')
    meta(group, 'M2Insert', 'McMaster 94459A767: maximum OD 3.63 mm; length 3.18 mm')
    meta(group, 'M3PocketDiameter', P['M3_pocket_diameter'], 'App::PropertyLength')
    meta(group, 'M3PocketDepth', P['M3_pocket_depth'], 'App::PropertyLength')
    meta(group, 'M2PocketDiameter', P['M2_pocket_diameter'], 'App::PropertyLength')
    meta(group, 'M2PocketDepth', P['M2_pocket_depth'], 'App::PropertyLength')
    meta(group, 'FitAllowance', '0.20 mm diametral glue allowance; check the cured fit coupon.')
meta(top, 'USBFit', 'Provisional adjustable cradle: 18 x 10 mm housing, 11 x 5.5 mm collar throat. Measure the cable housing.')
meta(top, 'LogoSeat', 'Original logo location. Face 0.9 mm proud. Stepped flange recess, 0.15 mm profile allowance.')
meta(bottom, 'PairedMount', 'Adjacent front-left PCB and CozIR inserts share a reinforced boss and small epoxy reservoir.')
meta(bottom, 'MinimumSideClearance', report['minimum_side_clearance_conservative'], 'App::PropertyLength')

labels = {
    'TopRevised': 'Top — shell, vents, logo seat and rear ports',
    'BaseRevised': 'Bottom — reinforced PCB and sensor supports',
    'USBRetainingCollar': 'USB-C removable retaining collar',
    'USBClamp': 'USB-C adjustable clamp',
    'CozirSpacer1': 'CozIR spacer 1',
    'CozirSpacer2': 'CozIR spacer 2',
    'IPSSpacer': 'IPS7100 spacer',
}
for name, label in labels.items():
    o = R.addObject('Part::Feature', name)
    o.Label = label
    s = Part.Shape()
    s.read(os.path.join(OUT, name + '.brep'))
    assert s.isValid() and s.isClosed() and len(s.Solids) == 1, name
    o.Shape = s
    (top if name in ['TopRevised', 'USBRetainingCollar', 'USBClamp'] else bottom).addObject(o)
    meta(o, 'Generator', 'revision_support/build_enclosure.py; editable BRep solid')

logo = R.addObject('Mesh::Feature', 'MintsIcon')
logo.Label = 'MINTS icon — 0.9 mm proud'
logo_points, logo_faces = D.mintsLogo80P___90CutBase.Mesh.Topology
# Topology coordinates are already global. Bake them before transformations.
# The supplied mesh has microscopic coincident triangles; weld to 0.0001 mm.
logo_points = [tuple(round(v, 4) for v in p) for p in logo_points]
logo_mesh = Mesh.Mesh([tuple(logo_points[i] for i in f) for f in logo_faces])
logo_mesh.removeDuplicatedPoints()
logo_mesh.removeDuplicatedFacets()
logo_mesh.fixDegenerations()
logo_mesh.harmonizeNormals()
assert logo_mesh.isSolid() and not logo_mesh.hasNonManifolds(), 'Logo cleanup'
logo.Mesh = logo_mesh
meta(logo, 'Source', 'mintsLogo80P - 90CutBase; original global placement; microscopic mesh defects welded at 0.0001 mm precision')
meta(logo, 'Protrusion', .9, 'App::PropertyLength')
electronics = R.addObject('App::DocumentObjectGroup', 'DreamV3')
electronics.Label = 'Dream V3'
meta(electronics, 'Source', 'DreamV3 1 from dreamV2.FCStd; global component placements preserved')
meta(electronics, 'FitCheck', '715 positive-volume source parts: no detected enclosure intersections; conservative minimum side clearance 6.5069 mm.')
meta(electronics, 'SourceLimitation', 'Imported ips7101 / Part__Feature4801 has a pre-existing invalid solid; physical fit remains to be checked.')

source_map = {}
def copy_part(src, group):
    o = R.addObject('Part::Feature', src.Name)
    o.Label = src.Label
    s = src.Shape.copy()
    s.Placement = src.getGlobalPlacement().multiply(src.Placement.inverse()).multiply(s.Placement)
    o.Shape = s
    group.addObject(o)
    source_map[o.Name] = src.Name
    return o

for src in D.DreamV3_1.OutListRecursive:
    if src.TypeId not in ['Part::Feature', 'PartDesign::Feature']:
        continue
    if not hasattr(src, 'Shape') or not src.Shape.Solids or src.Shape.Volume < .00001:
        continue
    copy_part(src, electronics)
assert len(electronics.Group) == 715
accessories = R.addObject('App::DocumentObjectGroup', 'RetainedAccessories')
accessories.Label = 'Retained battery and power board references'
electronics.addObject(accessories)
for name in ['Part__Feature3680', 'Adafruit_PowerBoost_1000C_Rev_B_1']:
    copy_part(D.getObject(name), accessories)
R.recompute()
R.saveAs(TARGET)
object_names = [o.Name for o in R.Objects]
A.closeDocument(R.Name)

# Retain per-component source materials without loading the unstable macOS GUI.
# The source view-provider schema and its binary material arrays are kept intact.
with zipfile.ZipFile(SOURCE) as original:
    source_gui = ET.fromstring(original.read('GuiDocument.xml'))
    providers = {p.attrib['name']: p for p in source_gui.findall('.//ViewProvider')}
    root = ET.Element('Document', SchemaVersion='1', HasExpansion='1')
    ET.SubElement(root, 'Expand')
    data = ET.SubElement(root, 'ViewProviderData', Count=str(len(object_names)))
    assets = {}
    def color_material(rgb):
        # One material, version 3, using the exact source binary layout.
        b = bytearray(original.read('ShapeAppearance6923'))
        rgba = (rgb[0] << 24) | (rgb[1] << 16) | (rgb[2] << 8) | 255
        b[8:12] = struct.pack('<I', rgba)
        return bytes(b)
    group_names = ['Top', 'Bottom', 'DreamV3', 'RetainedAccessories']
    for rank, name in enumerate(object_names):
        if name in group_names:
            vp = ET.Element('ViewProvider', name=name, expanded='0', treeRank=str(rank))
            props = ET.SubElement(vp, 'Properties', Count='2', TransientCount='0')
            for propname in ['Visibility', 'ShowInTree']:
                prop = ET.SubElement(props, 'Property', name=propname, type='App::PropertyBool', status='1')
                ET.SubElement(prop, 'Bool', value='true')
        else:
            template = source_map.get(name, 'mintsLogo80P___90CutBase' if name == 'MintsIcon' else 'Fillet007')
            vp = copy.deepcopy(providers[template])
            vp.set('name', name)
            vp.set('expanded', '0')
            vp.set('treeRank', str(rank))
            for node in vp.iter():
                if 'file' in node.attrib:
                    fn = node.attrib['file']
                    assets[fn] = original.read(fn)
            vp.find("./Properties/Property[@name='Visibility']/Bool").set('value', 'true')
            if name not in source_map:
                color = (235, 234, 225) if name in ['TopRevised', 'BaseRevised'] else (64, 117, 149)
                if name == 'MintsIcon':
                    color = (31, 130, 81)
                mat = vp.find("./Properties/Property[@name='ShapeAppearance']/MaterialList")
                fn = name + 'Material'
                assets[fn] = color_material(color)
                mat.set('file', fn)
        data.append(vp)
    rotation = A.Rotation(A.Vector(1, 0, 0), 65).multiply(A.Rotation(A.Vector(0, 0, 1), 25))
    position = A.Vector(0, 15, 0) + rotation.multVec(A.Vector(0, 0, 500))
    camera = ('OrthographicCamera {\n viewportMapping ADJUST_CAMERA\n'
              ' position %g %g %g\n orientation %g %g %g %g\n'
              ' nearDistance 1\n farDistance 2000\n aspectRatio 1\n focalDistance 500\n height 235\n}\n') % (
                  position.x, position.y, position.z,
                  rotation.Axis.x, rotation.Axis.y, rotation.Axis.z, rotation.Angle)
    ET.SubElement(root, 'Camera', settings=camera)
    gui_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
with zipfile.ZipFile(TARGET) as old:
    entries = {n: old.read(n) for n in old.namelist() if n != 'GuiDocument.xml'}
entries['GuiDocument.xml'] = gui_bytes
entries.update(assets)
temp = TARGET + '.tmp'
with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as out:
    for name, contents in entries.items():
        out.writestr(name, contents)
os.replace(temp, TARGET)

# Print coupon: three glue-clearance options for each insert, with a clipped
# lower-left corner defining the coordinate origin. Hole depth matches the CAD.
coupon = Part.makeBox(64, 28, 8)
triangle = Part.makePolygon([A.Vector(0,0,-1), A.Vector(4,0,-1),
                             A.Vector(0,4,-1), A.Vector(0,0,-1)])
coupon = coupon.cut(Part.Face(triangle).extrude(A.Vector(0,0,10)))
coupon_holes = []
for kind, y in [('M3', 8), ('M2', 20)]:
    depth = P[kind + '_pocket_depth']
    for col, allowance in enumerate([.10, .20, .30]):
        x = 12 + 20 * col
        diameter = round(P[kind + '_insert_OD'] + allowance, 2)
        start = A.Vector(x, y, 8)
        axis = A.Vector(0,0,-1)
        hole = Part.makeCylinder(diameter / 2, depth + .01, start + A.Vector(0,0,.01), axis)
        lead = Part.makeCone(diameter / 2 + .25, diameter / 2, .3, start + A.Vector(0,0,.01), axis)
        relief = Part.makeCylinder(1.6 if kind == 'M3' else 1.1, 6, start, axis)
        coupon = coupon.cut(hole.fuse(lead).fuse(relief))
        # One, two, three shallow dots identify the allowance columns.
        for dot in range(col + 1):
            coupon = coupon.cut(Part.makeCylinder(.55, .5, A.Vector(x + 1.6 * (dot-col/2), y+4.3, 8), axis))
        coupon_holes.append({'insert': kind, 'x': x, 'y': y, 'diameter': diameter, 'depth': depth})
assert coupon.isValid() and len(coupon.Solids) == 1
coupon.exportBrep(os.path.join(OUT, 'InsertFitCoupon.brep'))
cm = MeshPart.meshFromShape(Shape=coupon, LinearDeflection=.025, AngularDeflection=.1, Relative=False)
assert cm.isSolid()
cm.write(os.path.join(ROOT, 'dreamV3-InsertFitCoupon.stl'))
json.dump(coupon_holes, open(os.path.join(OUT, 'coupon-layout.json'), 'w'), indent=2)

# A separate STL of the original logo, in local positive coordinates.
lm = logo_mesh.copy()
tr = A.Matrix()
tr.rotateX(3.141592653589793 / 2)
lm.transform(tr)
bb = lm.BoundBox
lm.translate(-bb.XMin, -bb.YMin, -bb.ZMin)
lm.write(os.path.join(ROOT, 'dreamV3-MintsIcon.stl'))

Q = A.openDocument(TARGET)
assert {o.Name for o in Q.RootObjects} == {'Top', 'Bottom', 'MintsIcon', 'DreamV3'}
for name in labels:
    shape = Q.getObject(name).Shape
    assert shape.isValid() and shape.isClosed() and len(shape.Solids) == 1
mesh_report = {}
for name in list(labels) + ['MintsIcon', 'InsertFitCoupon']:
    mesh = Mesh.Mesh(os.path.join(ROOT, 'dreamV3-' + name + '.stl'))
    pts, facets = mesh.Topology
    edges = collections.Counter(tuple(sorted((a,b))) for f in facets for a,b in zip(f, f[1:]+f[:1]))
    stats = {'solid': mesh.isSolid(), 'nonmanifold': mesh.hasNonManifolds(),
             'facets': mesh.CountFacets, 'edge_defects': sum(v != 2 for v in edges.values())}
    mesh_report[name] = stats
    assert stats['solid'] and not stats['nonmanifold'] and stats['edge_defects'] == 0, (name, stats)
    if name in report['shape_checks']:
        report['shape_checks'][name]['mesh_solid'] = stats['solid']
        report['shape_checks'][name]['mesh_facets'] = stats['facets']
report['final_file'] = TARGET
report['final_roots'] = [o.Name for o in Q.RootObjects]
report['final_file_reopened'] = True
report['mesh_checks'] = mesh_report
report['mesh_cleanup'] = json.load(open(os.path.join(OUT, 'mesh-cleanup.json')))
json.dump(report, open(os.path.join(OUT, 'validation.json'), 'w'), indent=2)
print(json.dumps({'saved': TARGET, 'roots': report['final_roots'], 'meshes': mesh_report}, indent=2), flush=True)
