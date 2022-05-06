# Top level SConstruct file for stm32plus and all the examples.
# Modified for PlatformIO builder script by ForteFibre
"""
Usage: scons mode=<MODE> mcu=<MCU> (hse=<HSE> / hsi=<HSI>) [float=hard] [examples=no]

  <MODE>: debug/fast/small.
    debug = -O0
    fast  = -O3
    small = -Os

  <MCU>: f1hd/f1cle/f1mdvl/f042/f051/f030/f4.
    f030   = STM32F030 series.
    f042   = STM32F042 series.
    f051   = STM32F051 series.
    f1hd   = STM32F103HD series.
    f1cle  = STM32F107 series.
    f1md   = STM32100 medium density series.
    f1mdvl = STM32100 medium density value line series.
    f4     = STM32F407/f417 series (maintained for backwards compatibility)
    f405   = STM32F405
    f407   = STM32F407
    f415   = STM32F417
    f417   = STM32F417
    f427   = STM32F427
    f437   = STM32F437
    f429   = STM32F429
    f439   = STM32F439

  <HSE or HSI>:
    Your external (HSE) or internal (HSI) oscillator speed in Hz. Some of the ST standard
    peripheral library code uses the HSE_VALUE / HSI_VALUE #define that we set here. Select
    either the 'hse' or 'hsi' option, not both.

  [float=hard]:
    Optional flag for an F4 build that will cause the hardware FPU to be
    used for floating point operations. Requires the "GNU Tools for ARM Embedded
    Processors" toolchain. Will not work with Code Sourcery Lite.

  [examples=no]:
    Optional flag that allows you to build just the library without the examples. The
    default is to build the library and the examples.

  [lto=yes]:
    Use link-time optimization, GCC feature that can substantially reduce binary size

  Examples:
    scons mode=debug mcu=f1hd hse=8000000                       // debug / f1hd / 8MHz
    scons mode=debug mcu=f1cle hse=25000000                     // debug / f1cle / 25MHz
    scons mode=debug mcu=f1mdvl hse=8000000                     // debug / f1mdvl / 8MHz
    scons mode=fast mcu=f1hd hse=8000000 install                // fast / f1hd / 8MHz
    scons mode=small mcu=f4 hse=8000000 -j4 float=hard install  // small / f407 or f417 / 8Mhz
    scons mode=debug mcu=f4 hse=8000000 -j4 install             // debug / f407 or f417 / 8Mhz
    scons mode=debug mcu=f051 hse=8000000 -j4 install           // debug / f051 / 8Mhz

  Additional Notes:
    The -j<N> option can be passed to scons to do a parallel build. On a multicore
    CPU this can greatly accelerate the build. Set <N> to approximately the number
    of cores that you have.

    The built library will be placed in the stm32plus/build subdirectory.

    If you specify the install command-line option then that library will be installed
    into the location given by INSTALLDIR, which defaults to /usr/local/arm-none-eabi.
    The library, headers, and examples will be installed respectively, to the lib,
    include, and bin subdirectories of INSTALLDIR.

    It is safe to compile multiple combinations of mode/mcu/hse as the compiled object
    code and library are placed in a unique directory name underneath stm32plus/build.
    It is likewise safe to install multiple versions of the library and examples.
"""

from os.path import realpath

Import('env')

board = env.BoardConfig()
global_env = DefaultEnvironment()
#
# set CCFLAGS/ASFLAGS/LINKFLAGS
#


def setFlags(cpu, libdef):
    global global_env
    cpuopt = "-mcpu=cortex-"+cpu

    env.Append(
        CCFLAGS=[cpuopt],
        CPPDEFINES=[("STM32PLUS_"+libdef, "")]
    )
    env.Append(ASFLAGS=cpuopt)
    env.Append(LINKFLAGS=cpuopt)

    global_env.Append(
        CCFLAGS=[cpuopt],
        CPPDEFINES=[("STM32PLUS_"+libdef, "")]
    )
    global_env.Append(ASFLAGS=cpuopt)
    global_env.Append(LINKFLAGS=cpuopt)

#
# set the F4-specific hard float option
#


def floatOpt():
    global float
    global global_env
    if float == "hard":
        env.Append(CCFLAGS=["-mfloat-abi=hard"])
        env.Append(LINKFLAGS=["-mfloat-abi=hard", "-mfpu=fpv4-sp-d16"])
        global_env.Append(CCFLAGS=["-mfloat-abi=hard"])
        global_env.Append(LINKFLAGS=["-mfloat-abi=hard", "-mfpu=fpv4-sp-d16"])
    else:
        float = None

    return

# get the required args and validate


mode = 'small'
mcu = board.get("build.mcu", "")

# hse or hsi

osc = board.get("build.hse_clock", "")
if osc:
    osc_type = "e"
    osc_def = "HSE_VALUE"
else:
    osc = board.get("build.hsi_clock", "")
    assert osc, "HSE or HSI value must be provided"
    if osc:
        osc_type = "i"
        osc_def = "HSI_VALUE"


float = board.get("build.float", "hard")

# set the include directories

global_env.Append(CPPPATH=[
    realpath("../lib/include"),
    realpath("../lib/fwlib/f4/cmsis/Include/"),
    realpath("../lib/fwlib/f4/cmsis/Device/ST/STM32F4xx/Include"),
    realpath("../lib/fwlib/f4/stdperiph/inc"),
    realpath("../lib/usblib/device/core/inc"),
    realpath("../lib/usblib/hal/inc"),
])
env.Append(CPPPATH=[
    realpath("../lib/include"),
    realpath("../lib/fwlib/f4/cmsis/Include/"),
    realpath("../lib/fwlib/f4/cmsis/Device/ST/STM32F4xx/Include"),
    realpath("../lib/fwlib/f4/stdperiph/inc"),
    realpath("../lib/usblib/device/core/inc"),
    realpath("../lib/usblib/hal/inc"),
])
# create the C and C++ flags that are needed. We can't use the extra or pedantic errors on the ST library code.

env.Replace(CCFLAGS=[
    "-Wall",
    "-Werror",
    "-Wno-implicit-fallthrough",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-exceptions",
    "-mthumb",
    "-gdwarf-2",
    "-pipe",
    "-Wno-attributes"
])
env.Replace(CXXFLAGS=[
    "-Wextra",
    "-pedantic-errors",
    "-fno-rtti",
    "-std=gnu++14",
    "-fno-threadsafe-statics",
    "-Wno-deprecated-copy",
    "-Wno-cast-function-type",
    "-Wno-address-of-packed-member",
    "-Wno-class-memaccess"
])
env.Append(CPPDEFINES=[(osc_def, osc)])
global_env.Append(CPPDEFINES=[(osc_def, osc)])
env.Append(LINKFLAGS=["-Xlinker", "--gc-sections",
           "-mthumb", "-g3", "-gdwarf-2"])

env.Replace(AS="$CC", ASCOM="$ASPPCOM")

# add on the MCU-specific definitions

if mcu.startswith("stm32f407") or mcu.startswith("stm32f405"):
    setFlags("m4", "F407")
    floatOpt()
else:
    assert False, "unsupported mcu"

# add on the mode=specific optimisation definitions

if mode == "debug":
    env.Append(CCFLAGS=["-O0", "-g3"])
elif mode == "fast":
    env.Append(CCFLAGS=["-O3"])
elif mode == "small":
    env.Append(CCFLAGS=["-Os"])
else:
    assert False, "unsupported mode"
