import os
import sys
from setuptools import setup, find_packages

# Try to import pybind11 for C++ extension building
ext_modules = []
cmdclass = {}

try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext

    cpp_ext_dir = os.path.join("cyo", "cpp_ext")
    ext_modules = [
        Pybind11Extension(
            "cyo.chaos_crypto_cpp",
            sorted([
                os.path.join(cpp_ext_dir, "bindings.cpp"),
                os.path.join(cpp_ext_dir, "chaos_sequence.cpp"),
                os.path.join(cpp_ext_dir, "encryption.cpp"),
                os.path.join(cpp_ext_dir, "decryption.cpp"),
            ]),
            include_dirs=[cpp_ext_dir],
            cxx_std=17,
            define_macros=[("NDEBUG", None)],  # Release mode
        ),
    ]
    cmdclass = {"build_ext": build_ext}
    print("[setup.py] pybind11 found, C++ extension will be built.")
except ImportError:
    print("[setup.py] pybind11 not found, skipping C++ extension build.")
    print("  Install pybind11 to enable C++ acceleration: pip install pybind11")

setup(
    name="CYO",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    install_requires=["pybind11>=2.11"],
)