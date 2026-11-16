> Superseded by the finalized5mm slit revision. This directory preserves the historical8.7mm review only.

> Historical review snapshot: the user confirmed the higher physical Orange Pi position on November 10, 2026. The finalized files are now ../../dreamV3-enclosure.FCStd and ../../dreamV3-print-meshes.zip.

# Requested slit revision — fit review required

The native FreeCAD file and STL files here include the corrected request:

- Rear-right PCB M3 column at X=37, Z=37.
- New slit bottom Y=31.6, 1 mm toward the column tip from the original upper face Y=32.6.
- New slit height 8.7 mm, an increase of 5 mm from 3.7 mm. New upper face Y=22.9. Negative Y is upward along the column.
- All 11 M3 pockets: diameter4.92 mm, depth4.6 mm.
- All 6 M2 pockets: diameter3.83 mm, depth4.4 mm.
- Coupon depths updated to match. Glue-in installation in White V5 remains unchanged.

## Fit conflict to resolve

The supplied Orange Pi PCB occupies Y=33.8039..35.0939. Replacing the old slit with the new, higher slit restores resin at that old PCB height. A full check of 715 electronic solids found one collision: the Orange Pi PCB overlaps the revised base by14.062 mm^3. No other electronics collision was detected; cover/base and retained battery/power references remain clear.

Confirm whether the physical Orange Pi sits higher than this reference. If it does, the requested geometry can be used as specified, subject to physical fit. Otherwise the opening must extend downward to clear the stored board position, changing the requested lower boundary.

The new slit also meets the lower extension of the deeper M3 pocket. About85.4% of the depth-stop ring remains. The specified3.43 mm insert, mounted flush, remains fully surrounded over its installed length. Do not substitute a longer insert without checking this section. Keep adhesive from leaking into the slit and keep the insert flush rather than sinking it to the deeper floor.

All revised mechanical CAD parts are valid, closed single solids. All nine STLs are closed, manifold meshes. These are geometry checks, not confirmation that the requested slot fits the stored board location. See slot-comparison.png for the exact CAD cross-section.

The published files in the dream folder have been kept at their previous matching revision pending clarification. This directory contains the requested new geometry. The original published revision is also backed up in ../superseded/2026-11-10-before-orange-pi-slot.zip.
