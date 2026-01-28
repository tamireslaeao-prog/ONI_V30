import sys
import os

# 1. Setup Environment
# 1. Setup Environment
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

print("🦁 ONI 3D GENERATOR (LOCAL MODULE)")

try:
    # 2. Import from New Module Structure
    from Modules.InstantMesh import instantmesh_adapter
    print("✅ Module 'Modules.InstantMesh' found.")
except ImportError as e:
    print(f"❌ Module Error: {e}")
    sys.exit(1)

# 3. Define Input (Rick Logo)
# 3. Define Input (Rick Logo)
# Default to a placeholder if no arg provided
input_img = os.path.join(PROJECT_ROOT, "temp", "placeholder.png")
if len(sys.argv) > 1:
    input_img = sys.argv[1]

# 4. Run Generation
try:
    print(f"🚀 Launching Generation for: {os.path.basename(input_img)}")
    instantmesh_adapter.run_instantmesh(input_img)
    print("🏁 Execution Finished.")
except Exception as e:
    print(f"❌ Execution Failed: {e}")
