"""Orthographic engineering preview rendered from the saved CAD's triangles."""
import os, json, gzip
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with gzip.open(os.path.join(ROOT, 'revision_support/generated/preview-meshes.json.gz'), 'rt') as f:
    DATA = json.load(f)
S = 2
W, H = 2100, 920
im = Image.new('RGB', (W*S, H*S), '#f4f6f6')
draw = ImageDraw.Draw(im)
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
font = lambda size: ImageFont.truetype(font_path, int(size*S))
def text(x,y,value,size=20,color='#22323a'):
    draw.text((x*S,y*S), value, font=font(size), fill=color)
text(38, 28, 'DREAM V3  /  ENCLOSURE REVISION', 30)
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
        elif name not in ['TopRevised','BaseRevised']:base = np.array([.24,.46,.59])
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

panel(0,'Cover exterior','Raised MINTS icon · rear USB-C collar',
      ['TopRevised','USBRetainingCollar','MintsIcon'],[1,-2.6,1.6])
panel(1,'Cover interior','Stepped logo seat · adjustable USB-C cradle',
      ['TopRevised','USBRetainingCollar','USBClamp','MintsIcon'],[-1,2.8,1.5])
panel(2,'Bottom interior','Reinforced PCB, CozIR and IPS7100 mounts',
      ['BaseRevised'],[.7,-2.6,1.8])
text(38,813,'M3 pockets  Ø4.92 × 3.60 deep     |     M2 pockets  Ø3.83 × 3.40 deep     |     Minimum side clearance  6.51',23)
text(38,858,'Glue-in inserts for White V5. Test the cured fit coupon. USB cable housing fit remains provisional.',19,'#52646c')
im.resize((W,H),Image.Resampling.LANCZOS).save(os.path.join(ROOT,'dreamV3-enclosure-preview.png'))
print('Saved geometry preview')
