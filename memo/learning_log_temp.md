# LEARNING LOG: Blender Complete Character Tutorial - Part 1

## Session Analysis: Frames 310-400
- **Focus:** Global form adjustment to Reference Images.
- **Actions Observed:**
  - Vertices moved in Edit Mode with Proportional Editing likely active.
  - Matching the "Round Cube" to the character's head outline in Side View (Frame 330) and Front View (Frame 350).
  - Verification of smooth transition from side to front.
- **Key Takeaway:** Do not rush into features (eyes/nose) before the "Head Ball" matches the cranial mass and jaw curve of the reference.

## Session Analysis: Frames 410-500
- **Workflow Evolution:**
  - **Edit Mode -> Sculpt Mode:** Frame 490 and 500 clearly show the transition to Sculpt Mode. The user is using the **Grab Brush** (yellow icon active in toolbar) to push and pull the mesh to match the reference. This is a "Liquid Shaping" technique that is faster than vertex pushing.
- **Visuals:**
  - Frame 410: Flash of the *finished* or *target* topology (useful reference for loops).
  - Frame 490/500: The "Round Cube" is substantial and being molded like clay.
- **Key Takeaway:** Use Sculpt Mode's Grab brush for the initial silhouette matching of the low poly base. It's more organic and efficient.

## Session Analysis: Frames 510-600
- **Workflow Confirmation:**
  - **Hybrid Shaping:** Alternating between Sculpt Mode (for volume) and Edit Mode (for profile precision).
- **Technique:**
  - **Deformation ONLY:** Still no extrusions. The nose, chin, and jaw are formed by pulling existing geometry of the Round Cube. This preserves the quad topology of the sphere/cube without adding complexity yet.
- **Visuals:**
  - Frame 550: Shows the "Face Mask" flattening while keeping the cranium round.
- **Key Takeaway:** Exhaust the deformation potential of the base mesh before adding any new geometry (extrusions/loops).

## Session Analysis: Frames 610-700
- **Major Milestone:**
  - **Neck Extrusion (Frame 660):** The neck is finally extruded from the bottom of the shaped head ball.
- **Order of Operations:**
  1. Shape Head Ball (Front/Side/Persp)
  2. Flatten Face Mask area
  3. Extrude Neck
- **Topology:** The neck appears to be extruded from the central bottom 2x2 (or similar) face patch, maintaining the edge flow.
