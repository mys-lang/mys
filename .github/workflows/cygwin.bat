:: Name:     mycygwininst.cmd
:: Purpose:  Downloads and Installs Cygwin with custom packages
:: Author:   mikepruett3@gmail.com
:: Revision: 20161106 - initial version

@ECHO OFF
SETLOCAL ENABLEEXTENSIONS
SET _script=%~n0
SET _parentdir=%~dp0

:: Check if we are interactive
:: https://steve-jansen.github.io/guides/windows-batch-scripting/part-10-advanced-tricks.html
Set interactive=0
ECHO %CMDCMDLINE% | FINDSTR /L %COMSPEC% >NUL 2>&1
IF %ERRORLEVEL% == 0 SET interactive=1

:: Borrowed Code from - https://stackoverflow.com/questions/7985755/how-to-detect-if-cmd-is-running-as-administrator-has-elevated-privileges
NET SESSION > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO You are NOT running this script as an administator. Exiting...
    EXIT /B 0
)

:: More Borrowed Code from - http://ss64.com/nt/syntax-64bit.html
:: Installed OS
Set _os_bitness=64
IF %PROCESSOR_ARCHITECTURE% == x86 (
    IF NOT DEFINED PROCESSOR_ARCHITEW6432 Set _os_bitness=32
)

:: Select the correct Cygwin Setup Executable to use
IF %_os_bitness% == 64 (
    Set program=setup-x86_64.exe
    Set arch=x86_64
    set _rootdir=%SYSTEMDRIVE%\cygwin64
    set _cachedir=%SYSTEMDRIVE%\cygtmp
) ELSE (
    Set program=setup-x86.exe
    Set arch=x86
    set _rootdir=%SYSTEMDRIVE%\cygwin
    set _cachedir=%SYSTEMDRIVE%\cygtmp
)
Set download=%_cachedir%\%program%
set _site=http://mirrors.kernel.org/sourceware/cygwin

:: Create RootDir and CacheDir, if they dont exist already
IF NOT EXIST %_rootdir% (
    echo Creating %_rootdir%
    mkdir %_rootdir%
)
IF NOT EXIST %_cachedir% (
    echo Creating %_cachedir%
    mkdir %_cachedir%
)
:: Download the Cygwin Setup Executable, if it does not exist
IF NOT EXIST %download% (
    :: Neat cmd to download without any additional tools... (as long as you are using Windows 7 and up!)
    :: https://superuser.com/questions/25538/how-to-download-files-from-command-line-in-windows-like-wget-is-doing
    bitsadmin /transfer myDownloadJob /download /priority normal https://cygwin.com/%program% %download%
    ECHO.
    ECHO Cygwin Setup Executable downloaded to %download%
)

:: Find the location to the Cygwin Setup Executable
IF %_os_bitness% == 64 (
    for /f %%i in ('where /R %_cachedir%\ setup-x86_64.exe') do set setup=%%i
) ELSE (
    for /f %%i in ('where /R %_cachedir%\ setup-x86.exe') do set setup=%%i
)

:: Install Cygwin using Quiet Mode with packages 
START "Installing Cygwin" ^
/WAIT ^
%setup% ^
::--download ^
--site %_site% ^
--root %_rootdir% ^
--quiet-mode ^
--local-package-dir %_cachedir% ^
--packages ^
ccache,^
gcc-g++,^
make,^
python38,^
python38-devel,^
wget

ECHO.
ECHO Cygwin Installed

%_rootdir%\bin\bash --login -c "ln -s /usr/bin/python3.8 /usr/bin/python && cd D:/a/mys/mys && python -m easy_install pip && python -m pip install -r requirements.txt && python -m pip install pylint && export PYTHONUTF8=1 && set -o igncr && export SHELLOPTS && make c-extension -j 4 && make test-parallel-no-coverage -j 4 && ccache -s"

IF %ERRORLEVEL% NEQ 0 (
   EXIT /B 1
)

EXIT /B 0
