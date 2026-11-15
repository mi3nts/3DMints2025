import sys,os,json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
from fillet_base import candidates
out=os.path.join(os.path.dirname(__file__),'generated');r=json.load(open(out+'/fillet-validation.json'))
d=A.openDocument(out+'/BaseFilletHistory.FCStd');s=d.getObject(r['steps'][-1]['name']).Shape
b=Part.Shape();b.read(out+'/BaseAfterFillets.brep')
print('EDGE ORDER MATCH',all(x.CenterOfMass.distanceToPoint(y.CenterOfMass)<1e-5 for x,y in zip(s.Edges,b.Edges)),flush=True)
cs=candidates(s)
for q in cs:
 c=q['center']
 if -62<c[0]<-45 and -10<c[2]<9:print({k:v for k,v in q.items() if k!='edge'},flush=True)
json.dump([{k:v for k,v in q.items() if k!='edge'} for q in cs],open(out+'/remaining-fillet-edges.json','w'),indent=2)
