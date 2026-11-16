# Rebuilding DREAM V4

Use FreeCAD's bundled Python for the CAD scripts. Source geometry is read from `../dreamV2.FCStd`; the full assembly and materials are retained from `../dreamV3-enclosure.FCStd`. Both are read only. Recorded dimensions are in `parameters.json`; the generator and its fillet/vent helper modules define the construction sequence.

Run in order:

1. `build_enclosure.py`
2. `check_enclosure.py`
3. `check_fasteners.py`
4. `check_drainage.py`
5. `update_clamp.py` and `check_screw_relief.py`
6. `save_final.py`
7. `render_preview.py`, `render_details.py` and `render_vent_pattern.py`, plus `render_bridge_details.py`, using Python with NumPy and Pillow.

The builder rounds rib edges before fusion and calls `fillet_base.py` for the broad roots and remaining structural junctions. Each successful operation is stored as a native `Part::Fillet` in `generated/BaseFilletHistory.FCStd`. `fillet_worker.py` isolates kernel failures and each successful stage is checkpointed. The final base contains that editable history followed by a `Part::Cut` with the nut seats, hollow columns, wash ports, screw reliefs and exact five-millimetre Orange Pi slit. The stock and non-base components remain BRep features rather than Sketcher constraints.

The cache is reused only when stock edge count, volume and area agree. Remove/move the generated fillet history and its validation JSON to force a full recomputation after changing the feature sequence or fillet policy. This can take several minutes.

`fabric_vents.py` constructs analytic circles and ellipses using a four-corner geometric deformation field. Its measured minimum ligament is recorded in `generated/vent-validation.json`; this is an aesthetic mapping rather than a latex material simulation.

`prepare_base_stock.py` and `probe_fillet_edges.py` support isolated fillet development. `apply_final_corner_fillets.py` documents the incremental final small-corner update and checks added material against all retained electronics/accessory reference solids. It is unnecessary on a clean rebuild because the builder already includes these final blends. `finalize_drainage.py` is retained from the earlier V4 workflow; use the non-mutating `check_drainage.py` for current builds.

`save_final.py` refuses unexpected electronics intersections. The sole documented exception remains the obsolete Orange Pi reference position previously confirmed by the user. STL tessellation uses0.04 mm linear deflection and0.12 rad angular deflection; the coupon uses0.03 mm. The original cleaned logo mesh is retained.

See `../dreamV4-enclosure-notes.md` for hardware, assembly and manufacturing details. The pre-change V4 is archived under `superseded/`.

`bridge_fillets.py` isolates the side and middle bridge junctions, applies three additional native Fillet features, and fuses them with the existing structural history in `generated/BridgeFilletHistory.FCStd`. The middle node is Ø20 with R2 blends; the side joint uses R1.5. The common functional cut tool is applied afterward, preserving the middle-pillar M3 side slot. `apply_bridge_fillets.py` supports an incremental base-only export; run `check_bridge_changes.py` (conservative complete patch envelopes with source-hash verification), then the fastener, drainage and screw checks before `save_final.py --base-only`. This save mode updates the base and complete assembly while retaining the existing standalone top.
