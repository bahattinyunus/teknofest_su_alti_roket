cmake_minimum_required(VERSION 3.20)
project(teknofest_su_alti_roket C CXX ASM)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Target Hardware selection: PCB (final) or PERTINAX (prototype)
option(TARGET_HARDWARE "Hedef donanim tipi (PCB / PERTINAX)" "PCB")

if(TARGET_HARDWARE STREQUAL "PCB")
    add_compile_definitions(HV_PCB)
    message(STATUS "Build Target: Final PCB Architecture (Cemalettin & Gokhan)")
elseif(TARGET_HARDWARE STREQUAL "PERTINAX")
    add_compile_definitions(HV_PERTINAX)
    message(STATUS "Build Target: Pertinax Prototype Board")
endif()

# Compiler optimization & FPU flags for Cortex-M4F
add_compile_options(
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=hard
    -Wall
    -Wextra
    -O2
    -ffunction-sections
    -fdata-sections
)

add_compile_definitions(
    STM32F407xx
    USE_HAL_DRIVER
    ARM_MATH_CM4
    __FPU_PRESENT=1
)

include_directories(
    include
    include/drivers
    include/navigation
    include/mission
    include/fota
)

file(GLOB_RECURSE SOURCES
    "src/*.c"
    "src/*.cpp"
)

add_library(firmware_core STATIC ${SOURCES})

# Target executable (when linked with HAL and FreeRTOS third_party)
# add_executable(${PROJECT_NAME}.elf src/main.cpp ${SOURCES})
