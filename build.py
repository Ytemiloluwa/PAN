import os
import sys
import subprocess
import shutil
from setuptools.command.build_ext import build_ext
from setuptools import Extension, setup



# Path to the C++ source directory relative to this script
CPP_SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "cpp_src"))
# Path where the built C++ extension should be placed within the Python package
EXTENSION_DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "src", "fintechx_desktop", "infrastructure"))

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir="", *args, **kwargs):
        Extension.__init__(self, name, sources=[], *args, **kwargs)
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                             ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        # Required for auto-detection of auxiliary "native" targets
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            # Add other CMake flags as needed, e.g., -DCMAKE_BUILD_TYPE=Release
            # f"-DCMAKE_BUILD_TYPE={'Debug' if self.debug else 'Release'}"
            "-DCMAKE_BUILD_TYPE=Release" # Default to Release build
        ]

        build_args = [
            "--config", "Release" # Default to Release build
        ]

        # Set CMAKE_INSTALL_PREFIX to a temporary build directory
        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)
        
        cmake_args += [f"-DCMAKE_INSTALL_PREFIX={build_temp}"]

        print("-" * 10, "Running CMake prepare", "-" * 40)
        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp)

        print("-" * 10, "Running CMake build", "-" * 40)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=self.build_temp)
        
        # --- Copy the built extension to the correct location --- 
        # This part might need adjustment based on CMakeLists install rules and package structure
        # Find the built extension file (e.g., fintechx_native.so or fintechx_native.pyd)
        built_extension_path = None
        for filename in os.listdir(extdir):
            if filename.startswith("fintechx_native") and (filename.endswith(".so") or filename.endswith(".pyd")):
                built_extension_path = os.path.join(extdir, filename)
                break
        
        if built_extension_path and os.path.exists(built_extension_path):
            print(f"Found built extension: {built_extension_path}")
            print(f"Copying to: {EXTENSION_DEST_DIR}")
            os.makedirs(EXTENSION_DEST_DIR, exist_ok=True)
            shutil.copy2(built_extension_path, EXTENSION_DEST_DIR)
            print("Copy successful.")
        else:
             print(f"Warning: Could not find built extension in {extdir} to copy.")

# This setup function is called by `poetry build` or `pip install` when using the build script.
setup(
    name="fintechx_native_build", # Dummy name, actual package info is in pyproject.toml
    ext_modules=[CMakeExtension("fintechx_desktop.infrastructure.fintechx_native", sourcedir=CPP_SOURCE_DIR)],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)

