#### You probably don't need to read this file ####
General installation instructions for PC-BASIC can be found in `README.md`.
The instructions there cover the most common platforms and use cases. If the
options described there are not applicable or you prefer to install from source,
please consult the notes below.

#### Installation from the Python distribution ####
Download the Python distribution of PC-BASIC and unpack the TGZ archive.
The following packages are needed or recommended when installing PC-BASIC from the Python distribution:

| Package                                                               | OS                 | Status       | Used for
|-----------------------------------------------------------------------|--------------------|--------------|----------------------------------------
| [Python 2.7.12](https://www.python.org/downloads/release/python-2712/)| all                | required     |
| [PyWin32](https://sourceforge.net/projects/pywin32/)                  | Windows            | required     |
| [PySDL2](https://pysdl2.readthedocs.org/en/latest/)                   | all                | recommended  | sound and graphics
| [NumPy](https://sourceforge.net/projects/numpy/files/)                | all                | recommended  | sound and graphics
| [PySerial 2.7](https://sourceforge.net/projects/pyserial/)            | all                | optional     | physical or emulated serial port access
| [PyParallel 0.2](https://sourceforge.net/projects/pyserial/)          | Windows, Linux     | optional     | physical parallel port access
| [Pexpect](http://pexpect.readthedocs.org/en/latest/install.html)      | OSX, Linux, other  | optional     | `SHELL` command
| [PyGame 1.9.3](http://www.pygame.org)                                 | all                | optional     | sound and graphics (PyGame interface)
| [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/)                | all                | experimental | sound (PortAudio engine)

In this list, _other_ refers to operating systems other than Windows, Linux or OSX.

On **Windows**, first install Python 2.7 from the web site linked on top. Most dependencies can then be installed with `pip`:

        pip install pypiwin32 pysdl2 numpy pygame pyaudio

If you require serial and parallel port access, download PySerial and PyParallel from the web site linked above.
Note that PC-BASIC does not currently work with the `pip` version of these packages.

Download `launcher.exe` from the [ANSI|pipe release page](http://github.com/robhagemans/ansipipe/releases/) and place it in the directory where `setup.py` is located.
You can now run pc-basic with the command `launcher python -m pcbasic`. Without ANSI|pipe, PC-BASIC will run but you will
be unable to use the text-based interfaces (options `-t` and `-b`) as they will print only gibberish on the console.

The ANSI|pipe C source is included with PC-BASIC; if you prefer this to downloading the launcher binary, you can compile it from source by running `winbuild.bat`. You will need a working C compiler (MinGW or Microsoft Visual C++) on your system.

On **OSX**, there are several versions of Python 2.7 and all downloads need to match your version and CPU architecture. It's a bit tricky, I'm afraid. The easiest option seems to be installing both Python and PyGame through MacPorts or Homebrew.

On **Linux distributions with APT or DNF** (including Debian, Ubuntu, Mint and Fedora), the install script will automatically install dependencies if it is run with root privileges.

The install script can also be used on **other Unix** systems or when not installing as root. The dependencies can often be installed through your package manager. For example, on Debian-based systems:

        sudo apt-get install python2.7 python-sdl2 python-numpy python-serial python-pexpect python-parallel

On Fedora:

        sudo dnf install python pysdl2 numpy pyserial python-pexpect

On FreeBSD:

        sudo pkg install python27 py27-sdl2 py27-numpy py27-serial py27-pexpect

Note that PyParallel is not available from the Fedora and FreeBSD repos. PyParallel does not support BSD; on Fedora, you'll need to install from source if you need access to physical parallel ports. However, since most modern machines do not actually have parallel ports, you probably don't need it. PyParallel is _not_ needed for printing to a CUPS or Windows printer.


#### External tools ####
On Linux, OSX and other Unix-like systems, PC-BASIC can employ the following
external command-line tools:

| Tool                                      | OS                | Status      | Used for
|-------------------------------------------|-------------------|-------------|---------------------------------
| `lpr`                                     | OSX, Linux, other | essential   | printing to CUPS printers
| `paps`                                    | OSX, Linux, other | recommended | improved Unicode support for CUPS printing
| `pbcopy`                                  | OSX               | essential   | clipboard operation
| `pbpaste`                                 | OSX               | essential   | clipboard operation
| `xsel`                                    | Linux, other      | optional    | more intuitive clipboard operation
| `xclip`                                   | Linux, other      | optional    | more intuitive clipboard operation (alternative to `xsel`)
| `beep`                                    | OSX, Linux, other | optional    | sound in cli/text interface


#### Building from source ####
The Python distribution of PC-BASIC described above contains precompiled documentation and Windows binaries for SDL2, SDL2_gfx and ANSI|pipe.
If you wish to use the source code as-is in the GitHub repo,
you'll need to build these yourself. Compiling the documentation requires the Python modules
[`lxml`](https://pypi.python.org/pypi/lxml/3.4.3) and [`markdown`](https://pypi.python.org/pypi/Markdown).
You'll also need [`git`](https://git-scm.com/), [`setuptools`](https://pypi.python.org/pypi/setuptools) and all the PC-BASIC dependencies listed above.


1. Clone the github repo

        git clone --recursive https://github.com/robhagemans/pcbasic.git

2. Compile the documentation

        python setup.py build_docs

3. Run pcbasic directly from the source directory

        python -m pcbasic


The `--recursive` option is necessary to pull the `ansipipe` submodule; if you omit the option, you will have to get the submodule separately.
To build the supporting binaries for Windows, please refer to the compilation instructions for [SDL2](https://www.libsdl.org/), [SDL2_gfx](http://www.ferzkopp.net/wordpress/2016/01/02/sdl_gfx-sdl2_gfx/) and [ANSI|pipe](http://github.com/robhagemans/ansipipe/). You will need a C compiler such as [MinGW](http://mingw.org/) or [Microsoft Visual Studio](https://www.visualstudio.com/).


#### Building `SDL2_gfx.dll` on Windows with MinGW GCC ###
This plugin is needed if
you want to use the SDL2 interface with smooth scaling. Most Linux distributions will include this with their pysdl2 package.
On Windows, you will need to compile from source. The official distribution includes a solution file for Microsoft Visual Studio;
for those who prefer to use the MinGW GCC compiler, follow these steps:  

1. Download and unpack the SDL2 binary, the SDL2 development package for MinGW and the SDL2_gfx source code archive. Note that the SDL2 development package contains several subdirectories for different architectures. You'll need the 32-bit version in `i686-w64-mingw32/`  

2. Place `SDL2.dll` in the directory where you unpacked the SDL2_gfx source code.  

3. In the MinGW shell, run  

        ./autogen.sh
        ./configure --with-sdl-prefix="/path/to/where/you/put/i686-w64-mingw32/"
        make
        gcc -shared -o SDL2_gfx.dll *.o SDL2.dll

4. Place `sdl2.dll` and `sdl2_gfx.dll` in the `pcbasic\interface` directory.  


#### Installing with Pygame ####
This section covers workarounds for several issues you may run into when using [PyGame](http://pygame.org/).

The 1.9.1 release of PyGame, as currently standard on some distributions, unfortunately still contains a few bugs that
have already been resolved in the upstream PyGame code. This section documents workarounds for these bugs that can be used
until a newer build of PyGame is released with major distributions.

##### X11 clipboard #####
PyGame copy & paste does not work correctly on X11-based systems.
If you run into this, install one of the [`xsel`](http://www.vergenet.net/~conrad/software/xsel/) or
[`xclip`](https://sourceforge.net/projects/xclip/)  utilities and PC-BASIC will work around the issue.

##### Joystick debugging messages ####
A few debugging messages have been left in the production code for joystick handling.
The result is an annoying stream of debug messages on the console that occurs when you use a joystick.
If this bothers you, you will need to install PyGame from source; see below.

##### Segmentation fault #####
Occasionally, you may run into a crash with the following error message:

    Fatal Python error: (pygame parachute) Segmentation Fault
    Aborted (core dumped)

Unfortunately, the only workaround that I know of is to install PyGame from current development sources.

##### Installing PyGame from current development sources #####

1. Install dependencies. These are the packages I needed on Ubuntu 15.04:

        sudo apt-get install mercurial libpython-dev python-numpy ffmpeg libsdl1.2-dev libsdl-ttf2.0-dev libsdl-font1.2-dev libsdl-mixer1.2-dev libsdl-image1.2-dev libportmidi-dev libswscale-dev libavformat-dev libftgl-dev libsmpeg-dev


2. Make a working directory for your build, change into it and get the source

        hg clone https://bitbucket.org/pygame/pygame

3. Configure

        ./configure

    The script will notify you if you're missing dependencies.

4. Compile

        make

5. Install into your `/usr/local` tree

        sudo make install

See also the [PyGame source repository on BitBucket](https://bitbucket.org/pygame/pygame/wiki/VersionControl).
