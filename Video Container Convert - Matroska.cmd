@echo off
cls
set PATH=%PATH%;"C:\Program Files\Python"
set container=mkv
:loop_convert_container
IF %1=="" GOTO completed
python "G:\My Drive\Projects\Video Container Convert\video_container_convert.py" --container %container% %1
SHIFT
GOTO loop_convert_container
:completed
pause