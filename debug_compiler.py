import os
import sys
import shutil

print("--- PYTHON DEBUG ---")
print(f"SYS SCRIPT: {sys.argv[0]}")
print(f"CWD: {os.getcwd()}")
print(f"CUDA_HOME env var: {os.environ.get('CUDA_HOME')}")
print(f"CUDA_PATH env var: {os.environ.get('CUDA_PATH')}")

try:
    import torch.utils.cpp_extension
    found_home = torch.utils.cpp_extension._find_cuda_home()
    print(f"Torch found CUDA_HOME at: {found_home}")
except Exception as e:
    print(f"Torch failed to find CUDA_HOME: {e}")
    
try:
    # Try to locate nvcc manually to verify visibility
    nvcc_path = shutil.which("nvcc")
    print(f"shutil.which('nvcc'): {nvcc_path}")
except Exception:
    pass
print("--------------------")
