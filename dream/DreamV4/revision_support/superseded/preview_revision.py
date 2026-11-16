import os,json
import FreeCAD as App, Part
ROOT='/Users/rittikpatra/Documents/GitHub/3DMints2025/dream'
D=App.getDocument('DreamRevisionPreview') if 'DreamRevisionPreview' in App.listDocuments() else App.newDocument('DreamRevisionPreview')
App.setActiveDocument(D.Name)
R=D.getObject('EnclosureRevision') or D.addObject('App::DocumentObjectGroup','EnclosureRevision')
R.Label='Enclosure revision - insert dimensions pending'
for o in D.RootObjects:
 if o.Name not in ['EnclosureRevision','mintsLogo80P___90CutBase']:o.Visibility=False
for name in ['TopRevised','BaseRevised','USBRetainingCollar','USBClamp','CozirSpacer1','CozirSpacer2','IPSSpacer']:
 o=D.getObject(name) or D.addObject('Part::Feature',name)
 R.addObject(o)
 s=Part.Shape();s.read(os.path.join(ROOT,'revision_support','generated',name+'.brep'));o.Shape=s
 o.ViewObject.ShapeColor=(.90,.91,.88) if name in ['TopRevised','BaseRevised'] else (.22,.45,.66)
 o.ViewObject.LineColor=(.18,.19,.20);o.ViewObject.DisplayMode='Flat Lines';o.Visibility=True
 if 'Status' not in o.PropertiesList:o.addProperty('App::PropertyString','Status','Revision')
 o.Status='STRUCTURAL PREVIEW. Insert pocket dimensions are not final.'
import Mesh
logo=D.getObject('LogoReference') or D.addObject('Mesh::Feature','LogoReference')
logo.Label='mintsLogo80P - 90CutBase (unchanged placement)'
a=json.load(open('/tmp/logo_mesh.json'))
logo.Mesh=Mesh.Mesh(([tuple(p) for p in a['points']],[tuple(f) for f in a['faces']]))
logo.ViewObject.ShapeColor=(.15,.45,.20)
logo.Visibility=True
R.Visibility=True
Gui.Selection.clearSelection()
view=Gui.activeDocument().activeView()
view.setCameraOrientation(App.Rotation(App.Vector(1,0,0),65).multiply(App.Rotation(App.Vector(0,0,1),35)).Q)
cam=view.getCameraOrientation()
pos=cam.multVec(App.Vector(0,0,500))
view.setCamera('#Inventor V2.1 ascii\nOrthographicCamera { position %g %g %g orientation %g %g %g %g nearDistance 1 farDistance 2000 focalDistance 500 height 230 }' % (pos.x,pos.y,pos.z,cam.Axis.x,cam.Axis.y,cam.Axis.z,cam.Angle))
D.recompute()
D.saveAs(os.path.join(ROOT,'dreamV2-revision-review.FCStd'))
print('Structural review document saved. Insert dimensions pending.')
