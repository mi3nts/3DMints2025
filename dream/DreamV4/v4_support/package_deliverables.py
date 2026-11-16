"""Package the current validated print meshes, notes and geometry previews."""
from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parent.parent;g=root/'v4_support/generated'
r=json.loads((g/'validation.json').read_text())
assert r['final_file_reopened']
meshes=sorted(root.glob('dreamV4-*.stl'));assert len(meshes)==9
for name,c in r['mesh_checks'].items():
 assert c['solid'] and not c['nonmanifold'] and c['edge_defects']==0
 assert hashlib.sha256((root/f'dreamV4-{name}.stl').read_bytes()).hexdigest()==c['sha256']
files=meshes+[root/n for n in ['dreamV4-enclosure-notes.md','dreamV4-enclosure-preview.png','dreamV4-design-details.png','dreamV4-bridge-details.png','dreamV4-vent-pattern.png']]
with zipfile.ZipFile(root/'dreamV4-print-meshes.zip','w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in files:z.write(p,p.name)
 z.write(g/'validation.json','validation.json')
with zipfile.ZipFile(root/'dreamV4-print-meshes.zip') as z:
 assert z.testzip() is None
 for p in files:assert z.read(p.name)==p.read_bytes(),p.name
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('dreamV4-*')) if p.is_file() and p.suffix in ['.FCStd','.stl','.zip','.png','.md']}
(g/'deliverable-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Verified and packaged nine current STLs, notes, four previews and validation.')
