# DREAM enclosure structural review

**Status: review only; insert sizing is pending. Do not print the draft meshes.**

The original `dreamV2.FCStd` is preserved. The proposed structure is saved in `dreamV2-revision-review.FCStd`, containing revised solids, the unchanged logo placement, and a reference copy of the DreamV3 assembly. Original model history remains in the original file. The review solids are rebuilt by `revision_support/build_enclosure.py`; they are not a native sketch-based feature tree.

## Structure and fit

- Rounded 146 x 146 mm enclosure footprint; nominal side walls and top face 4.5 mm. Total original-coordinate depth is 71.2 mm including the retained lower shell. The rear USB collar projects beyond the main footprint.
- 6.507 mm conservative minimum clearance from DreamV3 hardware to the inside side-wall profile, exceeding the requested 5 mm. This measurement excludes intentional mounting contact and the USB/switch guides.
- All 715 positive-volume electronic leaf parts were tested against the seven revised enclosure/fitting solids. No volumetric intersections were detected. Top and base have zero common volume. Retained battery and power-module references also have no detected enclosure intersections.
- The imported IPS7101 source has an existing invalid solid. Its bounding envelope was included conservatively; collision results for that component cannot provide the same assurance as a valid source model. A cured print fit check is required.
- Each revised printable component is a valid closed single solid, and its generated STL is closed. These checks establish geometry integrity, not measured impact strength or a print-process qualification.

## Mechanical changes

- Four PCB mount centers use the actual PCB holes: X +/-37 mm, Z -38 and +37 mm. Nominal posts are 10 mm diameter, with tapered roots. The rear-right post includes a rounded relief for the Orange Pi board edge.
- CozIR external post aligns with its outboard ear, and two shared PCB supports have separate spacing sleeves. External post diameter is 11 mm with a 17 mm tapered foot and two 3.2 mm webs.
- IPS external post follows the supplied sensor's approximately 0.419 degree tilt. Both IPS supports are 11 mm diameter, with reinforced external root and a separate PCB-to-sensor sleeve.
- Cover transitions have 1.5 mm fillets. Round 3 mm vents now use 6.5 mm staggered pitch, giving 3.5 mm nominal ligaments. Corners, closure ribs, seam, and connector regions retain solid borders.
- The interrupted base tongue has 0.35 mm nominal radial mating clearance and clears all four closure ribs. Screw lands are reinforced.
- These changes are intended to improve load distribution and reduce stress concentration. No drop test or FEA was performed, so an impact rating is not claimed.

## USB and switch

- The former bottom USB cut is omitted, restoring that portion of the base.
- A provisional adjustable rear cradle is built into the top cover: 18 x 10 mm housing opening, 11 x 5.5 mm removable collar throat, and a removable clamp with 6 mm axial adjustment.
- Measure the real female connector housing, cable exit and strain relief before printing. The linked cable's exact housing dimensions and usable length were unavailable. Confirm the male plug and cable routing in the physical assembly.
- Switch tool-access slot is 14 x 6 mm and aligned to the slider travel, with a protective recessed guide. The guide ends about 3 mm from the switch tip.

## Raised logo seat

The supplied `mintsLogo80P - 90CutBase` mesh remains in its original placement. Its highest face is Y=-17.9 mm, while the top exterior face remains Y=-17 mm: nominal protrusion is 0.9 mm. Its wider flange occupies Y=-15 to -13 mm.

The revised opening uses the raised logo profile plus 0.15 mm allowance. A wider rear recess starts at Y=-15.15 mm and opens to the enclosure interior, admitting the flange while leaving a retaining shoulder about 1.85 mm thick. The shoulder includes 0.15 mm allowance relative to the flange face for assembly/adhesive. Mesh-profile checks found no logo vertices outside the corresponding clearance profiles through the cover. Adhesive and seating position should retain the original 0.9 mm protrusion.

## Inserts: pending exact pocket sizes

The user selected **White Resin V5 with glued inserts**. Cured SLA resin is thermoset. Follow Formlabs' glue-in method instead of using a heated soldering tip:
https://formlabs.com/uk/blog/adding-screw-threads-3d-printed-parts/

| Reference | Verified thread and length | Thermoplastic hole specification | Status for this model |
|---|---|---|---|
| McMaster 94459A769 | M3 x 0.5; 3.4 mm length | Maximum 4.0 mm straight hole | Maximum insert OD is still needed for the glue-in pocket. |
| McMaster 94180A333, provided as M2 | Actually M3 x 0.5; 6.4 mm length | 0.185 in / 4.699 mm, 8 degree tapered hole | Does not identify the requested M2 hardware. |
| Supplied M2 STEP reference | Approximately 3.571 mm maximum OD x 2.921 mm length | Not used as a heat-set hole specification | Awaiting confirmation to retain this reference or use a corrected M2 part. |

Public McMaster catalog references:
https://www.mcmaster.com/products/94459A170/
https://www.mcmaster.com/products/97164A112/

The current draft pockets are obsolete provisional dimensions from the earlier structural model. They are explicitly marked pending in the review CAD and must be regenerated before printing. The labeled M3 STEP reference (about 3.58 x 2.92 mm) does not match 94459A769. Do not use its envelope to size the final M3 pocket.

Once the correct insert envelopes are known, allow a small slip-fit/adhesive allowance, provide a depth stop and screw-tip clearance, and print a fit coupon using the same orientation, resin, wash, cure and 0.1 mm layer settings before committing to the enclosure. Layer height is not hole-diameter accuracy.

## Form 4BL / White V5 preparation

The nominal parts fit the published 353 x 196 x 350 mm Form 4BL build volume. The STLs are geometry exports, not supported PreForm jobs. Use the current White V5 material profile at 100 micrometres; arrange and support the shells for resin drainage and access to wash the pockets. Do not interpret the STL resting orientation as a validated SLA support orientation.

The supplied White V5 data sheet reports notched Izod 34 J/m after a 5-minute ambient post-cure and 32 J/m after 15 minutes at 60 C, with different strength/elongation values. Follow the current manufacturer processing profile and validate a representative cured sample; more post-cure heat does not automatically mean greater impact resistance. Repeated screw tightening should be limited to the needed clamp load and spread over flat seating surfaces.

## Files and remaining work

- `dreamV2-revision-review.FCStd`: proposed structure, source references, and explicit pending-insert status.
- `revision_support/generated/validation.json`: solid, mesh, clearance and intersection results.
- `revision_support/draft_meshes/`: seven **DRAFT** STL files; not released for printing.
- `revision_support/parameters.json` and `build_enclosure.py`: reproducible dimensions and geometry generator.

Required to finish: M3 94459A769 maximum OD and confirmation of the actual M2 insert; then update the pockets, regenerate and verify solids/meshes, and apply the final revision to a backed-up `dreamV2.FCStd` in FreeCAD.
