"""Prepare uncut base stock for isolated native-fillet development."""
import os,sys,json,math
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part,MeshPart,Mesh
V=App.Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));OUT=os.path.join(ROOT,'v4_support/generated')
P=json.load(open(os.path.join(ROOT,'v4_support/parameters.json')))
D=App.openDocument(os.path.join(ROOT,'dreamV2.FCStd'))
s=open(os.path.join(ROOT,'v4_support/build_enclosure.py')).read()
def source(n):
 o=D.getObject(n);a=o.Shape.copy();a.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(a.Placement);return a
def say(x):print(x,flush=True)
exec(s[s.index('def rounded('):s.index("say('Building enlarged rounded")])
closures=[(x,z) for x in [-56.,56.] for z in [-56.,56.]]
exec(s[s.index("say('Building enlarged base"):s.index("base.exportBrep(os.path.join(OUT,'BaseBeforeFillets.brep'))")])
base.exportBrep(os.path.join(OUT,'BaseBeforeFillets.brep'))
print('Stock edges',len(base.Edges),flush=True)
