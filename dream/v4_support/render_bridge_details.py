"""Orthographic engineering preview rendered from the saved CAD's triangles."""
import os, json, gzip
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with gzip.open(os.environ.get('DREAM_PREVIEW_MESHES',os.path.join(ROOT, 'v4_support/generated/preview-meshes.json.gz')), 'rt') as f:
    DATA = json.load(f)
S = 2
W, H = 2100, 920
im = Image.new('RGB', (W*S, H*S), '#f4f6f6')
draw = ImageDraw.Draw(im)
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font = lambda size: ImageFont.truetype(font_path, int(size*S))
def text(x,y,value,size=20,color='#22323a'):
    draw.text((x*S,y*S), value, font=font(size), fill=color)
text(38, 28, 'DREAM V4  /  BRIDGE JUNCTIONS AND MIDDLE-PILLAR NUT SLOT', 30)
text(38, 74, 'Views rendered from the saved CAD geometry · Dimensions in millimetres', 18, '#52646c')

def panel(index, title, subtitle, names, camera):
    x0, y0, width, height = 22+index*694, 130, 672, 650
    draw.rounded_rectangle((x0*S,y0*S,(x0+width)*S,(y0+height)*S), radius=18*S, fill='white')
    text(x0+22,y0+18,title,24)
    text(x0+22,y0+54,subtitle,16,'#52646c')
    direction = np.array(camera,dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross([0,0,1],direction);right /= np.linalg.norm(right)
    up = np.cross(direction,right)
    basis = np.array([right,up,direction])
    triangles, colors = [], []
    light = direction + right*.35 + up*.7
    light /= np.linalg.norm(light)
    for name in names:
        pts = np.array(DATA[name]['points'])
        faces = np.array(DATA[name]['faces'],dtype=int)
        tri = pts[faces]
        normals = np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        norms = np.linalg.norm(normals,axis=1)
        mask = (norms > 1e-12) & ((normals @ direction) > 0)
        tri = tri[mask]
        normals = normals[mask]/norms[mask,None]
        base = np.array([.84,.86,.84])
        if name == 'MintsIcon':base = np.array([.12,.53,.32])
        elif not name.startswith(('Top','Base')):base = np.array([.24,.46,.59])
        shade = .48 + .52*np.maximum(normals @ light,0)
        rgb = np.clip(base[None,:]*shade[:,None]*255,0,255).astype(np.uint8)
        triangles.append(tri @ basis.T)
        colors.append(rgb)
    tri = np.concatenate(triangles)
    rgb = np.concatenate(colors)
    limits = np.array([tri[:,:,:2].min(axis=(0,1)),tri[:,:,:2].max(axis=(0,1))])
    center = limits.mean(axis=0)
    scale = min((width-48)/(limits[1,0]-limits[0,0]),(height-130)/(limits[1,1]-limits[0,1]))
    coords = (tri[:,:,:2]-center)*np.array([scale,-scale])
    coords += np.array([x0+width/2,y0+94+(height-110)/2])
    coords *= S
    # Z buffering is required for large faces pierced by small vent triangles.
    # Painter sorting would leave false slivers at their overlapping projections.
    pw, ph = width*S, height*S
    pixels = np.array(im.crop((x0*S,y0*S,(x0+width)*S,(y0+height)*S)))
    depths = np.full((ph,pw), -np.inf, dtype=np.float32)
    coords -= np.array([x0*S,y0*S])
    for i, vertices in enumerate(coords):
        xlo,ylo = np.maximum(np.floor(vertices.min(axis=0)).astype(int),[0,0])
        xhi,yhi = np.minimum(np.ceil(vertices.max(axis=0)).astype(int),[pw-1,ph-1])
        if xlo>xhi or ylo>yhi:continue
        a,b,c = vertices
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        yy,xx = np.mgrid[ylo:yhi+1,xlo:xhi+1]
        xx=xx+.5; yy=yy+.5
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        w=1-u-v
        z=u*tri[i,0,2]+v*tri[i,1,2]+w*tri[i,2,2]
        region=depths[ylo:yhi+1,xlo:xhi+1]
        mask=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)&(z>region)
        region[mask]=z[mask]
        pixels[ylo:yhi+1,xlo:xhi+1][mask]=rgb[i]
    im.paste(Image.fromarray(pixels),(x0*S,y0*S))

def crop(name,target,bounds):
    # Clip triangles at the display box so planar faces are not discarded
    # merely because their original CAD tessellation vertices lie outside it.
    pts=np.asarray(DATA[name]['points']);faces=np.asarray(DATA[name]['faces'],dtype=int)
    triangles=pts[faces]
    lo=np.array([b[0] for b in bounds]);hi=np.array([b[1] for b in bounds])
    mask=np.all(triangles.max(axis=1)>=lo,axis=1)&np.all(triangles.min(axis=1)<=hi,axis=1)
    output_points=[];output_faces=[]
    for triangle in triangles[mask]:
        polygon=list(triangle)
        for axis,(lower,upper) in enumerate(bounds):
            for boundary,sign in [(lower,1),(upper,-1)]:
                clipped=[]
                if not polygon:break
                previous=polygon[-1];pd=sign*(previous[axis]-boundary)
                for current in polygon:
                    cd=sign*(current[axis]-boundary)
                    if (cd>=0)!=(pd>=0):
                        clipped.append(previous+(current-previous)*pd/(pd-cd))
                    if cd>=0:clipped.append(current)
                    previous,pd=current,cd
                polygon=clipped
        for j in range(1,len(polygon)-1):
            start=len(output_points)
            output_points.extend([polygon[0].tolist(),polygon[j].tolist(),polygon[j+1].tolist()])
            output_faces.append([start,start+1,start+2])
    DATA[target]={'points':output_points,'faces':output_faces}
crop('BaseRevised','BaseSideBridge', [(-65,-39),(27,44),(-12,11)])
crop('BaseRevised','BaseMiddleBridge', [(-24,3),(18,44),(-15,12)])
panel(0,'Base interior','Bridge joints rounded at both ends',['BaseRevised'],[.7,-2.6,1.8])
panel(1,'Side-pillar bridge joint','Cropped CAD view · R1.5 blend',['BaseSideBridge'],[1,-2.6,1.5])
panel(2,'Middle pillar and M3 nut slot','R2 shoulder and arm blends · side-loading nut',['BaseMiddleBridge'],[-3,-1.5,.8])
text(38,813,'Middle-pillar nut seat: 5.80 mm across flats × 2.70 mm high; screw bore Ø3.40 mm.',23)
text(38,858,'Middle junction widened to Ø20 mm for smooth bridge blends. Functional cuts remain downstream.',20,'#52646c')
im.resize((W,H),Image.Resampling.LANCZOS).save(os.path.join(ROOT,'dreamV4-bridge-details.png'))
print('Saved detail preview')
