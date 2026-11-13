# DREAM V4 — nut-fastened enclosure

Additional revision for Formlabs White Resin V5 at 0.10 mm layer height. V3 is retained unchanged. V4 uses removable, side-loaded hex nuts instead of the V3 glued inserts. Dimensions below are millimetres.

## Files

- `dreamV4-enclosure.FCStd`: complete assembly, with Top, Bottom, MINTS icon and Dream V3 electronics references.
- `dreamV4-Base.FCStd`: base and the three sensor spacers.
- `dreamV4-Top.FCStd`: cover, USB collar/clamp and MINTS icon.
- `dreamV4-NutFitCoupon.FCStd`: fit coupon CAD.
- `dreamV4-print-meshes.zip`: nine individual printable STLs, including the coupon and logo.
- `dreamV4-enclosure-preview.png`: views rendered from the actual CAD geometry.
- `v4_support/`: dimensions, native FreeCAD generator, checks and reports.

The FreeCAD components are editable native BRep solids. The included Python generator reconstructs the geometry from dimensions; this is not a fully constrained Sketcher/PartDesign feature tree. Existing `.form` print jobs belong to the earlier design and have not been updated for V4.

## Hardware and fits

| Location / size | Specified hardware | Nut dimensions | V4 pocket | Screw bore |
|---|---|---|---|---|
| PCB, CozIR and enclosure closure / M3 | [90591A250 nut](https://www.mcmaster.com/90591A250/), [91290A113 screw](https://www.mcmaster.com/91290A113/) | M3×0.5, 5.5 across flats, 2.4 high | 5.80 across flats ×2.70 high | Ø3.40 |
| IPS7100 and USB holder / M2 | [90591A265 nut](https://www.mcmaster.com/90591A265/), [91292A834 screw](https://www.mcmaster.com/91292A834/) | M2×0.4, 4.0 across flats, 1.6 high | 4.30 across flats ×1.90 high | Ø2.40 |

Nut dimensions were checked against the [McMaster DIN 934 catalog](https://www.mcmaster.com/products/hex-nuts/specifications-met~din-934/). The M3 socket head is Ø5.5 ×3 high; the M2 socket head is Ø3.8 ×2 high. These are cylindrical counterbores, not countersinks for flat-head screws. Relief behind each nut leaves 2.2 mm for M3 tips and 3.0 mm for M2 tips beyond the nominal pocket. M3×8 at a PCB post and M2×8 in the USB collar/clamp were checked for clearance. Screw lengths must be chosen for the actual PCB, spacer and nut stack; the user has multiple lengths.

The 0.30 mm across-flats and height allowances are design starting values for cured resin, not guaranteed printer tolerances. The hex seats retain the back faces and two parallel flats; a partial side channel admits the nut. Insertion sweeps fit, and a 30° nut rotation intersects the retaining faces in all 17 seats. This prevents continuous rotation while allowing small fitting play.

Load all nuts before fitting the electronics. The screw captures each nut after insertion. No soldering tip or glue is required. Avoid force-fitting a nut or excessive tightening in cured White V5.

## Base

- All nine PCB/sensor columns have a side-loading hex nut seat and a screw-only top clearance hole.
- Most nut pockets begin 2.4 mm below the mounting face. The close front-left CozIR pocket begins 6.3 mm below it, staggered relative to the adjacent PCB nut because their axes are only 5.18 mm apart. These two channels load from opposite Z directions.
- Each column has an axial cavity extending **62% of its height**, with a solid cap, solid foot and two Ø2.6 wash/drain ports. Ordinary cavity diameter is 4.4 mm. The notched Orange Pi column uses a Ø3.6 cavity offset 1.2 mm away from the slit.
- The central CozIR support at X−10/Z−0.48 now has **two 12 mm wide ×7 mm deep beams** anchored to the left and front base annulus, plus a tapered node reaching Ø16. Previously it relied on one 8 mm wide ×3.5 mm deep cantilever. Rounded beam ends and the wider node distribute the load. This is a structural improvement, not a tested drop/impact rating.
- Its lower drain exits toward +Z so the reinforcing beam does not seal it. All 18 column wash paths were checked open to the exterior.
- The Orange Pi relief is preserved: rounded cut tool X20..35.2, **Y26.6..31.6 (5 mm high)**, Z29..45, edge radius0.7. Its position and width have not moved.
- The base’s enclosure-closure screw heads use Ø6 counterbores; a 3 mm high M3 head sits approximately 0.2 mm below the outside surface.

## Top and USB holder

- The USB retaining collar is recessed into the rear wall. Its outside face is at Z73, coincident with the flat rear enclosure surface; there is 0.20 mm perimeter clearance per side and 0.20 mm depth clearance behind it.
- Two M2 screws retain the collar in side-loaded nuts inside the cradle rails. Ø4.30 ×2.20 counterbores put nominal 2 mm high heads 0.20 mm below the collar face. Nuts remain fully inside the enclosure.
- The inner cable clamp uses another two side-loaded M2 nuts. Its slots allow 6 mm fore/aft travel. Recessed slots also put the screw heads 0.20 mm below the clamp face. The clamp is 4.6 mm thick and has enlarged end margins around its head recesses.
- The cradle remains **provisional for the cable housing**: 18×10 housing clearance, 11×5.5 collar throat. Confirm the actual extension cable housing and plug engagement before printing; the linked cable had no reliable supplied housing dimensions. Packing shims can accommodate a smaller housing.
- Four cover closure posts also use M3 nut traps, so this revision does not require glued inserts.
- Each side has a flowing field of rounded capsule vents. Their angles fan outward like stretched fabric; length varies from approximately 3.5 to4.5, width 2.2, on a 7.5 triangular pitch. The nominal minimum ligament is3 mm. Solid borders and port keep-outs remain around the USB and switch openings. Vent airflow and acoustic performance have not been physically measured.
- The stepped logo seat, 0.9 mm proud MINTS face, 14×6 rear switch access and overall mating footprint are retained from V3.

## Fit coupon and assembly

The coupon has M3 and M2 rows, each with three side-loaded nut blocks. One, two and three dots identify across-flats allowances of 0.20,0.30 and0.40 mm respectively; the two-dot block matches this enclosure. Height allowance is 0.30 mm for all. Print, wash and fully post-cure it using the intended orientation/process before committing to the full parts. Layer height does not specify the achieved XY fit tolerance.

Insert nuts in the base and cover posts, then assemble the PCB and sensor spacers. Slide the USB collar nuts into the rails from the open-base side, place the collar in its rear recess and fit the two M2 screws. Load the clamp nuts from the forward ends of the cradle rails, position the cable and tighten the slotted clamp. Do not obstruct either sensor’s inlet/outlet or the wash ports with packing material.

Use the new V4 STLs in a new PreForm job. Orient and support parts so supports do not fill nut channels, screw counterbores, wash ports, the mating lip or the Orange Pi slit. The supplied STL orientations are export orientations, not validated support layouts.

## Validation and remaining limits

- All seven structural/spacing components are valid, closed, single-solid FreeCAD shapes. The final assembly and both standalone files reopen successfully in FreeCAD’s native engine.
- All nine STL files are watertight, without non-manifold edges or unmatched triangle edges.
- All 17 actual nut envelopes and continuous insertion sweeps fit. Antirotation contact is present; nuts do not collide with each other, including the staggered pair.
- M2 screw-head envelopes fit in the collar and clamp counterbores throughout the clamp’s travel. Cover, base, collar and clamp do not intersect.
- All 715 Dream V3 electronics solids were checked. Conservative minimum enclosure side clearance remains **6.5069 mm**, meeting the 5 mm requirement.
- The only electronics intersection is the existing 14.062 mm³ overlap of the old Orange Pi reference with the preserved slit column. The user previously confirmed the physical Orange Pi sits higher and explicitly requested this slit position. That reference has deliberately not been moved by an invented offset.
- The source IPS `ips7101` solid has a pre-existing invalid geometry condition; its reference envelope is included, but the actual physical fit remains to be confirmed.
- White V5 impact performance, nut pull-out strength and final cable fit require physical testing. The design does not imply a measured strength rating.
- The FreeCAD 1.1.1 macOS GUI encountered its accessibility-related crash while opening the existing assembly. Native FreeCAD saved/reopened and geometry checks succeeded; the preview is rendered from the CAD triangles.

Detailed reports: `v4_support/generated/validation.json` and `fastener-validation.json`. No changes were made to the V3 deliverables.
