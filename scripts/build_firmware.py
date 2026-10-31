"""
Automated Build Script for STM32F407 Underwater Rocket Firmware
Configures CMake with Ninja, detects local ARM GCC toolchains (including CubeIDE paths),
and builds the production binary.
"""

import os
import sys
import subprocess
import shutil
import glob
from pathlib import Path

def find_arm_gcc() -> str:
    # 1. Check if arm-none-eabi-gcc is in PATH
    which_gcc = shutil.which("arm-none-eabi-gcc")
    if which_gcc:
        return which_gcc

    # 2. Search common STM32CubeIDE directories on Windows
    cube_patterns = [
        "C:/ST/STM32CubeIDE_*/**/arm-none-eabi-gcc.exe",
        "C:/Program Files/STMicroelectronics/**/arm-none-eabi-gcc.exe",
        "C:/Program Files (x86)/GNU Arm Embedded Toolchain/**/arm-none-eabi-gcc.exe"
    ]
    for pattern in cube_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0].replace("\\", "/")

    return ""

def run_build(target_hw: str = "PCB", clean: bool = False):
    firmware_dir = Path(__file__).resolve().parent.parent / "firmware"
    build_dir = firmware_dir / "build"

    print(f"=== SUNGUR UNDERWATER ROCKET FIRMWARE BUILDER ===")
    print(f"Firmware Directory: {firmware_dir}")
    print(f"Target Hardware:    {target_hw}")

    if clean and build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir, ignore_errors=True)

    arm_gcc = find_arm_gcc()
    cmake_args = [
        "cmake",
        "-B", str(build_dir),
        "-S", str(firmware_dir),
        f"-DTARGET_HARDWARE={target_hw}"
    ]

    ninja_available = shutil.which("ninja") is not None
    if ninja_available:
        cmake_args.extend(["-G", "Ninja"])

    if arm_gcc:
        print(f"Detected ARM Toolchain: {arm_gcc}")
        cmake_args.extend([
            f"-DCMAKE_C_COMPILER={arm_gcc}",
            f"-DCMAKE_CXX_COMPILER={arm_gcc.replace('gcc', 'g++')}"
        ])
    else:
        print("Note: arm-none-eabi-gcc not found in standard paths. Falling back to host compiler or configured toolchain.")

    print("\n[1/2] Running CMake configuration...")
    cfg_res = subprocess.run(cmake_args)
    if cfg_res.returncode != 0:
        print("[ERROR] CMake configuration failed.")
        return False

    print("\n[2/2] Compiling firmware...")
    build_cmd = ["cmake", "--build", str(build_dir)]
    build_res = subprocess.run(build_cmd)
    if build_res.returncode != 0:
        print("[ERROR] Compilation failed.")
        return False

    print("\n[SUCCESS] Firmware compiled successfully!")
    return True

if __name__ == "__main__":
    hw = "PCB"
    clean_flag = False
    if "--pertinax" in sys.argv:
        hw = "PERTINAX"
    if "--clean" in sys.argv:
        clean_flag = True

    success = run_build(target_hw=hw, clean=clean_flag)
    sys.exit(0 if success else 1)
