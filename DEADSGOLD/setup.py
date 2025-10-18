
from setuptools import setup, Extension
import os

# You might need to adjust these paths based on your CUDA Toolkit installation
CUDA_PATH = os.environ.get("CUDA_PATH") # Default for Linux
# For Windows, it might be something like "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x"

# Ensure nvcc is in your PATH or specify its full path
# For Windows, you might need to add "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x\bin" to your PATH

# Define the PyCUDA extension module
pycuda_extension = Extension(
    name="pycuda._driver",
    sources=["pycuda/src/cpp/cuda.cpp", "pycuda/src/cpp/bitlog.cpp"], # Example sources, adjust as needed
    include_dirs=[
        os.path.join("CUDA_PATH", "include"),
        # Add other include directories if necessary, e.g., for Boost
    ],
    library_dirs=[
        os.path.join("CUDA_PATH", "lib64"), # Default for Linux
        # For Windows, it might be something like "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.x\lib\x64"
        # Add other library directories if necessary
    ],
    libraries=["cuda", "cudart"], # CUDA runtime and driver libraries
    extra_compile_args=[
        "-O3", "-arch=sm_35", # Adjust architecture for your GPU
        # Add other compiler flags as needed
    ],
    extra_link_args=[
        # Add other linker flags as needed
    ],
    # Define macros if necessary
    define_macros=[
        ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION"),
        # Add other macros as needed
    ],
)

setup(
    name="pycuda",
    version="2023.1.1", # Adjust version as needed
    description="PyCUDA provides easy, Pythonic access to CUDA's GPU computing API.",
    author="Andreas Kloeckner",
    author_email="inform@tiker.net",
    url="https://mathema.tician.de/software/pycuda/",
    packages=["pycuda", "pycuda.tools", "pycuda.driver", "pycuda.gl"], # Adjust packages as needed
    package_dir={"pycuda": "pycuda"}, # Adjust package directory as needed
    ext_modules=[pycuda_extension],
    install_requires=[
        "numpy",
        "pytools>=2011.2",
        "decorator>=3.2.0",
        "Mako",
        "setuptools",
    ], # Adjust dependencies as needed
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ],
)
