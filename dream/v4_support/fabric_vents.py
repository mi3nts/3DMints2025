"""Four-corner fabric-inspired perforations; aesthetic mapping, not a material simulation."""
import math,json,os

def layout():
 rows=[]
 for j in range(7):
  Y=(j-3)/3
  for i in range(11):
   X=(i-5)/5
   # The boundary bows inward between four anchors. The center is left circular.
   x=44*X*(1-.22*(1-Y*Y));y=12+20*Y*(1-.22*(1-X*X))
   tension=.15*max(X**4,Y**4)+.85*X*X*Y*Y
   center=abs(X)<=.21 and abs(Y)<=.34
   major=2.3 if center else 2.3*(1+1.7*tension)
   minor=2.3 if center else 2.3-.4*tension
   angle=math.degrees(math.atan2(Y,X)) if not center else 0.
   # Bounding rectangle of the analytic ellipse, used only for port keep-outs.
   th=math.radians(angle)
   hx=math.hypot(major/2*math.cos(th),minor/2*math.sin(th))
   hy=math.hypot(major/2*math.sin(th),minor/2*math.cos(th))
   rear_blocked=any(x+hx>a and x-hx<b and y+hy>c and y-hy<d for a,b,c,d in [(-42.2,-1.8,.5,25),(13,37,3.905,19.905)])
   rows.append(dict(row=j,col=i,X=X,Y=Y,u=x,y=y,major=major,minor=minor,angle=angle,center_circle=center,rear_blocked=rear_blocked))
 return rows

def build(Part,V,out):
 vents=[];placed=[];profiles=[]
 for q in layout():
  edge=Part.makeCircle(q['major']/2) if q['center_circle'] else Part.Ellipse(V(0,0,0),q['major']/2,q['minor']/2).toShape()
  face=Part.Face(Part.Wire([edge]));face.rotate(V(0,0,0),V(0,0,1),q['angle']);face.translate(V(q['u'],q['y'],0));profiles.append((q,face))
  for wall,side in [('X',-1),('X',1),('Z',-1),('Z',1)]:
   if wall=='Z' and side==1 and q['rear_blocked']:continue
   # Build in local plane, then map local horizontal coordinate to wall footprint.
   f=face.copy();f.translate(V(-q['u'],-q['y'],0));s=f.extrude(V(0,0,12))
   if wall=='X':
    s.rotate(V(0,0,0),V(0,1,0),side*90)
    # Rotation sends local horizontal X to -side Z; reflect the placement likewise
    # so all four corner axes point outward in the wall's own coordinates.
    s.translate(V(side*65,q['y'],-side*q['u']))
   else:
    if side<0:s.rotate(V(0,0,0),V(0,1,0),180)
    s.translate(V(side*q['u'],q['y'],side*65))
   vents.append(s);placed.append(dict(q,wall=wall,side=side))
 minimum=1e9;pair=None
 for i,(q,f) in enumerate(profiles):
  for r,g in profiles[i+1:]:
   if math.hypot(q['u']-r['u'],q['y']-r['y'])>12:continue
   dist=f.distToShape(g)[0]
   if dist<minimum:minimum=dist;pair=[(q['row'],q['col']),(r['row'],r['col'])]
 assert minimum>=2.5,(minimum,pair)
 data=dict(mapping='x=44X[1-0.22(1-Y²)], y=12+20Y[1-0.22(1-X²)]',description='Circular 3x3 center zone; radial ellipses elongate toward four corners. Aesthetic deformation field, not hyperelastic FEA.',minimum_ligament=minimum,limiting_pair=pair,holes=len(placed),major_range=[2.3,6.21],minor_range=[1.9,2.3],layout=placed)
 json.dump(data,open(os.path.join(out,'vent-validation.json'),'w'),indent=2)
 return Part.makeCompound(vents),placed
