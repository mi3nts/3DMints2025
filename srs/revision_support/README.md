# SRS Dream V3 revision

The main deliverable is `../srsv4.FCStd`. The exact input file, including its existing uncommitted edits, is preserved as `srsv4-before-dreamv3.FCStd`.

## Stable FreeCAD workflow

The macOS crash report `freecad-2026-10-20-181626.ips` identifies a segmentation fault in `QMacAccessibilityElement dealloc`, called through Qt/macOS accessibility. Desktop automation that reads the app's accessibility tree triggered repeated crashes in this session. The geometry work therefore uses **FreeCAD's bundled Python and native Part kernel without importing FreeCADGui or querying the desktop app**. This avoids that failing accessibility path; it is a workaround, not a patch to FreeCAD.

To regenerate from the preserved input:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/python srs/revision_support/run_revision.py
```

Run from the repository, or use an absolute script path. The script builds, validates, saves the main CAD, preserves the original view providers/materials, and preserves the requested CAD geometry. It stops if fit or geometry checks fail. No print-ready STL is supplied: the unchanged T-slot is invalid and the base tessellation needs further meshing work, as detailed in the notes. When run through Codex's restricted shell, the installed Qt runtime may need an approved process outside the sandbox because its CPU-feature check is blocked inside it.

`build_revision.py` constructs the changes; `check_geometry.py` verifies scope and hole clearance; `check_assembly.py` checks new base/housing interference and PCB screw passage clearance; `check_interference.py` checks the 715 Dream V3 source electronic solids; `save_revision.py` retains the original feature history and adds the revision features. The new base is an editable BRep feature with its original source linked. Its custom properties describe the revision; changing those properties alone does not rebuild the shape. Change the generator and rerun to alter its dimensions. The four capsule cuts are a native Part cut in the existing `srs002` compound.

`render_preview.py` makes the engineering preview from the CAD tessellation. It uses no image generation and no desktop capture.
