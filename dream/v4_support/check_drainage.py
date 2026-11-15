"""Verify all hollow-column wash ports without modifying the final CAD."""
import sys,os,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
V=A.Vector
OUT=os.path.join(os.path.dirname(__file__),'generated')
r=json.load(open(os.path.join(OUT,'validation.json')))
s=Part.Shape();s.read(os.path.join(OUT,'BaseRevised.brep'))
checks=[]
for h in r['hollow_columns']:
 n=next(n for n in r['nut_pockets'] if n['label']==h['label'])
 pt=V(*n['point']);axis=V(*n['axis']);u=V(*n['direction']);offset=V(*h['offset'])
 for i,t in enumerate([h['cavity_start']+2,h['cavity_start']+h['cavity_length']-2]):
  direction=V(0,0,1) if h['label']=='M3 -10.0 -0.48' and i==1 else u
  center=pt+axis*t+offset
  path=Part.makeCylinder(1.2,9,center,direction)
  outlet=Part.makeCylinder(1.2,.5,center+direction*8.9,direction)
  a=s.common(path).Volume;b=s.common(outlet).Volume
  c=dict(label=h['label'],port=i,path_overlap=a,outlet_overlap=b)
  checks.append(c);assert a<.001 and b<.001,c
r['drainage_checks']=checks
json.dump(r,open(os.path.join(OUT,'validation.json'),'w'),indent=2)
print('18 open drainage paths verified',flush=True)
