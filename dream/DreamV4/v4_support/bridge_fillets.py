"""Broad native bridge-to-pillar blends, kept upstream of every functional cut."""
import os,sys,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
V=A.Vector

def rounded_beam(cx,cz,w,d):
 s=Part.makeBox(w,7,d,V(cx-w/2,36.5,cz-d/2))
 es=[e for e in s.Edges if e.BoundBox.YLength>6.999]
 s=s.makeFillet(5.9,es)
 es=[e for e in s.Edges if e.BoundBox.YLength<.001 and abs(e.BoundBox.YMin-36.5)<.001]
 return s.makeFillet(.8,es)

def smooth_bridge_junctions(base,out,log=print):
 path=os.path.join(out,'BridgeFilletHistory.FCStd');reportpath=os.path.join(out,'bridge-fillet-validation.json')
 stamp=dict(volume=base.Volume,area=base.Area,edges=len(base.Edges),policy=1)
 if os.path.exists(path) and os.path.exists(reportpath):
  r=json.load(open(reportpath))
  if r.get('source_stamp')==stamp:
   s=Part.Shape();s.read(os.path.join(out,'BridgeAfterFillets.brep'));return s
 prior=json.load(open(os.path.join(out,'fillet-validation.json')))
 d=A.openDocument(os.path.join(out,'BaseFilletHistory.FCStd'))
 root=d.getObject(prior['steps'][-1]['name'])
 assert abs(root.Shape.Volume-base.Volume)<.001
 steps=[]
 def fillet(obj,indices,r,label):
  f=d.addObject('Part::Fillet','BridgeJunctionFillet');f.Label=label+' — R'+str(r)
  f.Base=obj;f.Edges=[(i,r,r) for i in indices];d.recompute()
  assert not f.Shape.isNull() and f.Shape.isValid() and f.Shape.isClosed() and len(f.Shape.Solids)==1,label
  steps.append(dict(name=f.Name,label=label,radius=r,edges=indices,count=len(indices)))
  log(label+' R'+str(r))
  return f
 beams=[rounded_beam(-27,-.48,46,12),rounded_beam(-10,-24.5,12,53)]
 sideparts=[beams[0],Part.makeCylinder(5.5,15,V(-53.36402,28.3,-.54998),V(0,1,0)),Part.makeCone(5.5,8.5,8,V(-53.36402,35.3,-.54998),V(0,1,0))]
 s=d.addObject('Part::Feature','SideBridgeStock');s.Label='Isolated side bridge junction stock';s.Shape=sideparts[0].multiFuse(sideparts[1:]).removeSplitter()
 assert len(s.Shape.Edges)==52
 side=fillet(s,[8,19,30],1.5,'Bridge to side-pillar fillets')
 midparts=beams+[Part.makeCylinder(5,24.5,V(-10,19,-.48),V(0,1,0)),Part.makeCone(5,8,8,V(-10,28.5,-.48),V(0,1,0)),Part.makeCylinder(10,7,V(-10,36.5,-.48),V(0,1,0))]
 m=d.addObject('Part::Feature','MiddleBridgeStock');m.Label='Middle node — 20 mm diameter, existing 12 mm bridge arms';m.Shape=midparts[0].multiFuse(midparts[1:]).removeSplitter()
 assert len(m.Shape.Edges)==69
 middle=fillet(m,[61,62,63,64,65],2.,'Middle pillar to bridge shoulder')
 middle=fillet(middle,[35,37,48,51],2.,'Both bridge arms to middle node')
 final=d.addObject('Part::MultiFuse','BridgeJointFusion');final.Label='Base with smooth bridge junctions';final.Shapes=[root,side,middle];final.Refine=True
 d.recompute();shape=final.Shape
 assert shape.isValid() and shape.isClosed() and len(shape.Solids)==1
 shape.exportBrep(os.path.join(out,'BridgeAfterFillets.brep'));d.saveAs(path)
 r=dict(source_stamp=stamp,steps=steps,final_feature=final.Name,history=path,middle_node_diameter=20,side_radius=1.5,middle_radius=2.,valid=True,closed=True,solids=1,volume=shape.Volume)
 json.dump(r,open(reportpath,'w'),indent=2);A.closeDocument(d.Name)
 return shape

if __name__=='__main__':
 out=os.path.join(os.path.dirname(__file__),'generated');base=Part.Shape();base.read(os.path.join(out,'BaseAfterFillets.brep'))
 smooth_bridge_junctions(base,out,lambda s:print(s,flush=True))
