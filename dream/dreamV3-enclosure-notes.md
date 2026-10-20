# DREAM V3 enclosure

**New assembly:** `dreamV3-enclosure.FCStd`. Its four top-level items are **Top**, **Bottom**, **MINTS icon**, and **Dream V3**. Top and Bottom contain their removable fittings. Dream V3 contains the 715 electronic solids plus the retained battery and power-board references. The original `dreamV2.FCStd` is preserved.

The enclosure consists of editable FreeCAD BRep solids, with the source electronics and logo included for reference. The original sketch history remains in the original file; the new solids can be regenerated with the scripts in `revision_support`. The custom Design properties document dimensions; changing those properties alone does not regenerate geometry. Edit `parameters.json` and run the generator to change pocket dimensions.

## Confirmed inserts and pockets

Use **glued inserts in washed, fully post-cured White Resin V5**, as agreed. Do not heat-set them into this thermoset resin. Formlabs describes gluing heat-set inserts into SLA parts in its [threaded-insert guidance](https://formlabs.com/uk/blog/adding-screw-threads-3d-printed-parts/).

| Insert | Confirmed maximum outside diameter × length | Enclosure pocket diameter × nominal depth |
|---|---:|---:|
| M3 × 0.5, [McMaster 94459A769](https://www.mcmaster.com/94459A769/) | 4.72 × 3.43 mm | **4.92 × 3.60 mm** |
| M2 × 0.4, [McMaster 94459A767](https://www.mcmaster.com/94459A767/) | 3.63 × 3.18 mm | **3.83 × 3.40 mm** |

Dimensions are taken from the user-provided McMaster drawings. These pockets allow 0.20 mm diametral / 0.10 mm radial clearance for adhesive. They have a 0.3 mm entry chamfer and narrower screw-tip relief. The catalog's 4.0 mm and 3.2 mm heat-setting holes are not used for this glue-in SLA design.

There are 11 M3 pockets (seven PCB/CozIR supports and four cover closures) and six M2 pockets (two IPS supports and four USB fitting attachments). Install the insert tops flush with their seating faces. Select screw lengths to engage the inserts without bottoming out, and keep adhesive out of the threads.

The front-left PCB and adjacent CozIR mounts are only 5.18 mm apart. They share a reinforced boss and a small connecting epoxy reservoir in place of a fragile 0.26 mm resin web. Align both inserts using the PCB mounting pattern while the adhesive cures; prevent adhesive from bonding the PCB or screws.

## Fit coupon

Print `dreamV3-InsertFitCoupon.stl` first with the intended resin, layer height, orientation, wash and cure process. A 0.1 mm layer height does not establish hole-diameter accuracy. Check a fully cured coupon before printing the large shells.

Viewed from the pocket side, place the clipped corner at the lower left:

| Row | Left / one dot | Middle / two dots — enclosure nominal | Right / three dots |
|---|---:|---:|---:|
| Upper, smaller M2 pockets | Ø3.73 mm | **Ø3.83 mm** | Ø3.93 mm |
| Lower, larger M3 pockets | Ø4.82 mm | **Ø4.92 mm** | Ø5.02 mm |

The coupon is 64 × 28 × 8 mm; depths match the enclosure. Inserts should enter without forcing and leave room for the selected adhesive. If the middle pockets are unsuitable after curing, adjust the pocket parameters before printing the enclosure.

## Structure and clearances

- Main footprint: 146 × 146 mm, with 4.5 mm nominal walls/top face and rounded corners. The rear retaining collar protrudes beyond this footprint.
- Minimum conservative side-wall clearance to Dream V3: **6.507 mm**, exceeding 5 mm. Intentional supports and the USB/switch guides are excluded from this wall-clearance measurement.
- PCB posts are Ø10 mm with tapered roots. External CozIR and both IPS supports are Ø11 mm; the tall supports have Ø17 mm tapered feet and two 3.2 mm reinforcing webs. The external IPS seat follows the supplied approximately 0.419° sensor tilt.
- Nominal resin around a straight insert pocket is 2.54 mm at Ø10 M3 posts, 3.04 mm at the Ø11 M3 column, and 3.59 mm at Ø11 M2 supports. Entry chamfers locally reduce this by 0.25 mm.
- Cover transitions use 1.5 mm fillets. Round Ø3 mm vents have 6.5 mm staggered pitch and 3.5 mm nominal ligaments. Corners, seam, closure ribs and rear ports have solid borders.
- The base tongue has 0.35 mm radial mating clearance and clears the closure ribs. The original battery compartment is retained.

These changes improve load distribution and reduce thin sections. No drop test or FEA has been performed; impact resistance is not certified.

## Rear USB-C and switch

The former bottom USB opening is closed. The top cover has a provisional rear female-connector cradle with an 18 × 10 mm housing opening, an 11 × 5.5 mm removable collar throat, and a clamp with 6 mm axial adjustment. Use packing shims as required.

**The actual extension cable housing, strain relief and usable cable length still need measurement.** The adjustable cradle was approved as provisional. Confirm the male plug and cable route in the physical assembly.

The rear switch opening is 14 × 6 mm, aligned with the slider travel. Its recessed guide ends approximately 3 mm from the switch tip for access with a long thin tool.

## MINTS logo

The original global location is retained: the logo face is **0.9 mm proud** of the cover. The smaller visible profile and wider flange have separate clearance cuts, with 0.15 mm profile allowance. The wide recess begins at Y = −15.15 mm, leaving a retaining shoulder approximately 1.85 mm thick.

The original mesh had microscopic duplicate/collapsed triangles. These were welded at 0.0001 mm precision for a watertight logo, preserving its visible geometry and location.

## Verification and printing

The final FreeCAD file was reopened successfully by FreeCAD's native geometry engine. All seven revised mechanical parts are valid, closed, single solids. All nine exported STLs, including the logo and coupon, are watertight with zero nonmanifold or boundary edges.

All 17 insert cavities were probed in the saved CAD for the intended clear diameter/depth and a remaining depth-stop ring. Each passed. `dreamV3-enclosure-preview.png` was rendered from the saved CAD geometry and visually inspected. FreeCAD 1.1.1's desktop interface repeatedly crashed in macOS Qt accessibility handling during opening, so an interactive GUI review could not be completed.

All 715 positive-volume electronic source parts were checked against the seven enclosure/fitting solids: no volumetric intersections were detected. The top and bottom do not overlap. Retained battery/power-board references also have no detected enclosure intersections.

The imported `ips7101` source (`Part__Feature4801`) has a pre-existing invalid solid. Its conservative bounding envelope was included, but its collision result is less reliable than those of valid solids; verify the physical sensor fit.

The STLs are geometry exports, not supported PreForm jobs. Use the White V5 100 µm profile appropriate to your Form 4BL and arrange supports and drainage in PreForm. The exported resting orientation is not a validated SLA print orientation. Follow current Formlabs wash/cure instructions and avoid support marks on insert seats, mating surfaces and the logo shoulder.

Print one of each `dreamV3-*.stl`: TopRevised, BaseRevised, USBRetainingCollar, USBClamp, CozirSpacer1, CozirSpacer2, IPSSpacer and MintsIcon. InsertFitCoupon is the preliminary fit test.

`revision_support/generated/validation.json` records the checks. `revision_support/README.md` explains the regeneration workflow. Earlier review files and draft meshes are superseded.
