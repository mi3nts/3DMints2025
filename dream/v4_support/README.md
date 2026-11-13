# Rebuilding DREAM V4

Use FreeCAD's bundled Python (or its Python console) with the scripts in this directory. Source: `../dreamV2.FCStd`; final document assembly/color reference: `../dreamV3-enclosure.FCStd`. Dimensions: `parameters.json`. The source files are read only.

Run, in order:

1. `build_enclosure.py`
2. `check_enclosure.py`
3. `update_clamp.py` (also records the strengthened clamp's local electronics check)
4. `check_fasteners.py`
5. `finalize_drainage.py` (idempotently checks all eighteen outlet paths)
6. `check_screw_relief.py`
7. `save_final.py`
8. `render_preview.py` using a Python environment with NumPy and Pillow.

`save_final.py` refuses unexpected electronics intersections. The sole documented exception is the obsolete Orange Pi reference position previously confirmed by the user. The CAD uses the requested unchanged five-millimetre slit.

The geometry generator uses native Part solids with explicit dimensional parameters. Saved objects are BRep features, not a Sketcher constraint history. The generator also includes the final central-post drain route and enlarged USB-clamp margins. STL tessellation is0.04 mm linear deflection /0.12 rad angular deflection; the coupon uses0.03 mm. Original logo geometry and its cleaned mesh are retained.

The support scripts and JSON reports record the checks; read `../dreamV4-enclosure-notes.md` for manufacturing and assembly details.
