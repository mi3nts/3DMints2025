# Regeneration

The current deliverable is `../dreamV3-enclosure.FCStd`; installation and print notes are in `../dreamV3-enclosure-notes.md`.

Keep `../dreamV2.FCStd`, `parameters.json` and `logo_profiles.json` available. These commands use FreeCAD's bundled Python and native geometry kernel:

```sh
/Applications/FreeCAD.app/Contents/Resources/bin/python build_enclosure.py
/Applications/FreeCAD.app/Contents/Resources/bin/python check_enclosure.py
/Applications/FreeCAD.app/Contents/Resources/bin/python save_final.py
/Applications/FreeCAD.app/Contents/Resources/bin/python verify_pockets.py
```

Run them in order from this directory. `check_enclosure.py` examines the actual electronics and supports; read `generated/validation.json` before release. `save_final.py` requires passing clearance/interference results, saves a separate new document, repairs microscopic logo mesh defects, generates the coupon and validates all nine STLs. `verify_pockets.py` probes the saved insert cavities and exports geometry for the preview.

`render_preview.py` uses NumPy and Pillow to render three orthographic views from `generated/preview-meshes.json.gz`. It does not fabricate or replace CAD geometry. The preview is an engineering rendering, not a FreeCAD screenshot.

`clean_mesh.py` records the initial bottom-STL cleanup: rounding tessellated vertices to 0.00001 mm and removing collapsed facets. This cleanup is now included in `build_enclosure.py` when needed.

The custom Design properties in the saved FreeCAD groups are descriptive. To regenerate a different insert fit, edit the M3/M2 pocket dimensions in `parameters.json`. Other structural changes may require editing the generator. Do not use the archived scripts or models in `superseded/` or the obsolete `draft_meshes/` files.
