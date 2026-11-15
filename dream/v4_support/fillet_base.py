"""Native FreeCAD fillets on base stock before its functional cuts."""
import os,sys,math,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
V=A.Vector

def candidates(s):
 # Map oriented face boundaries back to the solid's topological edges.
 face_map={}
 for f in s.Faces:
  for e in f.Edges:face_map.setdefault(e.hashCode(),[]).append(f)
 result=[]
 for i,e in enumerate(s.Edges,1):
  b=e.BoundBox
  if b.YMin<28-1e-5 or b.YMax>43.3001 or e.Length<.8:continue
  if max(abs(b.XMin),abs(b.XMax),abs(b.ZMin),abs(b.ZMax))>64 and not (e.Length<45 and math.hypot(e.CenterOfMass.x-58.4,e.CenterOfMass.z-6.15)<12):continue
  fs=face_map.get(e.hashCode(),[])
  if len(fs)!=2:continue
  kinds=[type(f.Surface).__name__ for f in fs]
  if any(k not in ['Plane','Cylinder','Cone','BSplineSurface'] for k in kinds):continue
  if any(k=='Cylinder' and f.Surface.Radius<3.9 for k,f in zip(kinds,fs)):continue
  try:
   p=e.valueAt((e.FirstParameter+e.LastParameter)/2)
   normals=[]
   for f in fs:
    u,v=f.Surface.parameter(p);normals.append(f.normalAt(u,v))
   dot=max(-1,min(1,normals[0].dot(normals[1])))
   if dot>.998 or dot<-.998:continue
   n1,n2=normals
   tangent=n2-n1*dot; tangent.normalize(); probe=p+tangent*.04
   uv=fs[0].Surface.parameter(probe);concave=fs[0].isPartOfDomain(*uv)
  except Exception:continue
  c=e.CenterOfMass
  result.append(dict(index=i,edge=e,center=list(c),length=e.Length,concave=concave,kinds=kinds,angle=math.degrees(math.acos(dot)),ymin=b.YMin,ymax=b.YMax))
 return result

def smooth_base(stock,out,log=print):
 import subprocess
 history_path=os.path.join(out,'BaseFilletHistory.FCStd')
 report_path=os.path.join(out,'fillet-validation.json')
 stamp=dict(volume=stock.Volume,area=stock.Area,edges=len(stock.Edges))
 report=json.load(open(report_path)) if os.path.isfile(report_path) else {}
 same=report.get('stock',{}).get('edges')==stamp['edges'] and abs(report.get('stock',{}).get('volume',0)-stamp['volume'])<.0001 and abs(report.get('stock',{}).get('area',0)-stamp['area'])<.0001
 if same and os.path.isfile(history_path) and os.path.isfile(os.path.join(out,'BaseAfterFillets.brep')):
  current=Part.Shape();current.read(os.path.join(out,'BaseAfterFillets.brep'))
  history=report['steps'];done=report.get('completed_groups',[]);failed=report.get('unresolved_groups',[])
  base_name=history[-1]['name'] if history else 'BaseBeforeFillets'
 else:
  doc=A.newDocument('DreamV4BaseFilletHistory');src=doc.addObject('Part::Feature','BaseBeforeFillets');src.Shape=stock
  doc.recompute();doc.saveAs(history_path);A.closeDocument(doc.Name)
  current=stock.copy();history=[];done=[];failed=[];base_name='BaseBeforeFillets'
 def checkpoint():
  json.dump(dict(stock=stamp,steps=history,completed_groups=done,unresolved_groups=failed),open(report_path,'w'),indent=2)
 def apply(label,predicate,radii):
  nonlocal current,base_name
  if label in done:return
  selected=[q for q in candidates(current) if predicate(q)]
  if not selected:done.append(label);checkpoint();return
  indices=[q['index'] for q in selected]
  log('%s: %d edges'%(label,len(indices)))
  success=False
  for radius in radii:
   attempt=os.path.join(out,'fillet-attempt.FCStd');brep=os.path.join(out,'fillet-attempt.brep');result=os.path.join(out,'fillet-attempt-result.json')
   spec=dict(source=history_path,target=attempt,brep=brep,result=result,base=base_name,edges=indices,radius=radius,label=label)
   sp=os.path.join(out,'fillet-attempt-spec.json');json.dump(spec,open(sp,'w'))
   try:
    log('  trying R'+str(radius))
    with open(os.path.join(out,'fillet-worker.log'),'w') as f:
     run=subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'fillet_worker.py'),sp],stdout=f,stderr=subprocess.STDOUT,timeout=75)
    if run.returncode:continue
    data=json.load(open(result));base_name=data['name'];current=Part.Shape();current.read(brep)
    os.replace(attempt,history_path);os.replace(brep,os.path.join(out,'BaseAfterFillets.brep'))
    history.append(dict(name=base_name,label=label,radius=radius,edges=indices,count=len(indices)))
    log('  applied R'+str(radius));success=True;break
   except subprocess.TimeoutExpired:log('  radius timed out; trying a smaller blend')
  if not success:failed.append(dict(label=label,edges=indices))
  done.append(label);checkpoint()
 regions=[('PCB rear left',-37,37,11),('PCB rear right',37,37,11),('PCB front right',37,-38,11),('PCB CozIR paired boss',-34.4,-38,13),('CozIR external',-53.36,-.55,13),('IPS external',58.4,6.15,13),('IPS bridge',17.5,-40,16),('Retained power-board supports',38,-6.02,14),('CozIR brace anchors',-20,-24,40)]
 for label,x,z,r in regions:
  apply(label+' floor roots',lambda q,x=x,z=z,r=r:q['concave'] and q['ymax']-q['ymin']<.001 and q['ymin']>40 and math.hypot(q['center'][0]-x,q['center'][2]-z)<r,[2.,1.5,1.])
 for label,x,z,r in regions:
  if label in ['CozIR external','IPS external']:
   # Thin orthogonal webs: work on their four quadrants separately.
   for sx,sz in [(1,1),(-1,1),(-1,-1),(1,-1)]:
    apply(label+' web '+str((sx,sz)),lambda q,x=x,z=z,r=r,sx=sx,sz=sz:q['concave'] and math.hypot(q['center'][0]-x,q['center'][2]-z)<r and (q['center'][0]-x)*sx>=0 and (q['center'][2]-z)*sz>=0,[.8,.5])
  else:
   apply(label+' transitions',lambda q,x=x,z=z,r=r:q['concave'] and math.hypot(q['center'][0]-x,q['center'][2]-z)<r,[1.5,1.,.75])
 for label,x,z,r in []:
  apply(label+' edge rounds',lambda q,x=x,z=z,r=r:not q['concave'] and math.hypot(q['center'][0]-x,q['center'][2]-z)<r,[.75,.5])
 # Work around tight three-face intersections by selecting the actual planar
 # web edges independently from the small corner patches produced at the roots.
 for label,x,z in [('CozIR external',-53.36402,-.54998),('IPS external',58.39945509,6.15)]:
  apply(label+' exposed planar web rounds',lambda q,x=x,z=z:not q['concave'] and q['kinds']==['Plane','Plane'] and math.hypot(q['center'][0]-x,q['center'][2]-z)<12,[.8,.5])
  apply(label+' straight post-web blends',lambda q,x=x,z=z:q['concave'] and sorted(q['kinds'])==['Cylinder','Plane'] and q['ymin']>=30.99 and q['ymax']<=35.31 and math.hypot(q['center'][0]-x,q['center'][2]-z)<9,[1.,.6])
 apply('Central CozIR node blends',lambda q:q['concave'] and math.hypot(q['center'][0]+10,q['center'][2]+.48)<12,[1.5,1.,.6])
 apply('Long beam outside edges',lambda q:not q['concave'] and q['kinds']==['Plane','Plane'] and q['length']>10 and q['ymax']<40.01,[1.,.75,.5])
 apply('Orthogonal beam inside corners',lambda q:q['concave'] and q['kinds']==['Plane','Plane'] and q['length']>2,[1.,.6])
 apply('Small orthogonal joining corners',lambda q:q['concave'] and q['kinds']==['Plane','Plane'],[.35,.25])
 report=json.load(open(report_path));report['remaining_candidates']=[{k:v for k,v in q.items() if k!='edge'} for q in candidates(current)]
 json.dump(report,open(report_path,'w'),indent=2)
 return current

if __name__=='__main__':
 out=os.path.join(os.path.dirname(__file__),'generated')
 stock=Part.Shape();stock.read(os.path.join(out,'BaseBeforeFillets.brep'))
 cs=candidates(stock);print('Eligible structural edges:',len(cs),flush=True)
 smooth_base(stock,out,lambda x:print(x,flush=True))
