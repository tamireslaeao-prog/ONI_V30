import sys
try:
    print("Attempting to import nvdiffrast...")
    import nvdiffrast.torch as dr
    print("SUCCESS: nvdiffrast imported successfully!")
    print(f"Location: {dr.__file__}")
except ImportError as e:
    print(f"FAILURE: Could not import nvdiffrast. Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error during import. Error: {e}")
    sys.exit(1)
