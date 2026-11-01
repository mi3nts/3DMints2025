"""Rebuild the SRS Dream V3 update with FreeCAD's native kernel, without its GUI."""
import os,sys,json,gzip
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[2])
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
D=A.openDocument('srs/revision_support/srsv4-before-dreamv3.FCStd')
def bb(shape):
 b=shape.BoundBox
 return [round(x,5) for x in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]
for script in ['build_revision.py','check_geometry.py','check_assembly.py','check_interference.py','save_revision.py']:
 exec(compile(Path('srs/revision_support',script).read_text(),script,'exec'))
A.closeDocument(D.Name)
