# SRS / Dream V3 mounting update

The revised CAD is `srsv4.FCStd`. Its original input is preserved in `revision_support/srsv4-before-dreamv3.FCStd`. The original feature history remains in the revised file.

- **srs002:** the four inclined bottom M3 mounting holes are 3.25 × 7 mm capsules, elongated horizontally along each mounting face. This adds ±1.875 mm of lateral shaft travel while retaining the original 3.25 mm width and hole axes. The matching base holes and the rest of the housing are unchanged.
- **Dream V3:** the board is rotated −6° in the original PCB plane about local (−10, 10), then shifted −4 mm along local X, −0.2 mm vertically and 6.5 mm inward. Keeping the old board position caused interference at the switch, Pi board, CozIR and underside connector pins. The PCB column holes now follow the actual Dream V3 pattern: four corners on a 74 × 75 mm rectangle, plus the adjacent fifth mount. Existing bore diameters are retained: 3.25 mm for the four corners and 3.50 mm for the fifth.
- **PCB columns only:** six R6 concave brace-junction reinforcements and two R6 rear-root reinforcements distribute loads. Rounded mounting arms join all five new hole locations to the two existing columns. Their ends have a 4 mm radius and their perimeter edges have 0.75 mm rounds. The seating surfaces extend inward by 6.5 mm. The right mounting arms and lower-left arm have rounded rear reliefs to clear the unchanged housing ribs. The original approximately 0.602 mm PCB-to-seat gap is retained. **PCB mounting screws require approximately 6.5 mm more reach** for the same engagement.
- **IPS7100:** the V3 sensor is separate from the PCB assembly and retains Dream V1's original global position and orientation, including its source geometry. Its existing support and mounting holes are unchanged.

The original base outline, seal/mating surfaces, other sensor supports, T-slot structure and remaining housing features are retained. The supplied battery and power-board reference objects are retained at their original placements; they are not part of the 715-solid Dream V3 board fit check. The old Dream V1 reference remains hidden. The housing remains hidden in the saved base inspection view and can be shown using `srs002`.

The slot dimensions provide designed adjustment, not a guarantee of cured print tolerance. Verify fit on the first fully cured print. No drop test or impact certification is claimed. The supplied IPS electronic model has a pre-existing invalid face/solid; it remains unchanged as a reference. The original printable base also had an orientation/topology error, repaired without changing its surfaces before performing the requested changes.

No revised STL is supplied as print-ready. The unchanged T-slot feature (`Fillet296`) is invalid and produces a nonmanifold housing mesh. The revised base is a valid closed CAD solid, but its standard tessellation leaves a small root gap; attempted mesh repairs did not pass the surface-distance acceptance check. Resolve meshing before printing this revision. Existing STL and PreForm jobs are retained and still represent the older geometry.

Detailed check results are in `revision_support/validation.json`. The preview is `srsv4-DreamV3-preview.png`.

Saved-file verification checked 4,644 source shape payloads. All except the intentionally updated `Compound` and relocated IPS reference are byte-for-byte identical to the input. Both newly revised CAD solids are valid and closed. All 715 migrated electronic objects cleared the housing and base; the five PCB screw passages and separate IPS placement also passed their intersection checks.

The four capsule holes were subsequently extended to 7 mm overall length, with their 3.25 mm width, centres and directions retained. The prior revision is backed up as `revision_support/srsv4-before-7mm-capsules.FCStd`. This update changes only the cutter, slotted shell and compound shape caches; all other archive resources are unchanged.
