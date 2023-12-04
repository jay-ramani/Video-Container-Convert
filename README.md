# Video Container Convert

## What This Is
A Python script that converts source video file's container to a compatible target container.

At present, the script converts any of the below source formats to [Matroska](https://en.wikipedia.org/wiki/Matroska):
* AVI
* DivX
* FLV
* M4V
* MPEG (4 inclusive)
* WebM
* Mts (AVCHD)
* M2ts (Blu-Ray and AVCHD)
* WMV

More target container formats can be customised in the Python script.

Tip: Having video files in Matroska format helps greatly, since adding metadata like title and tags does not require re-enconding the video file, and is a breeze to query metadata. For example, converting mp4 to Matroska (a .mkv extension) can be done without re-encoding the content; it is merely the container that changes.

**Note**: Use a Python 3.6 environment or above for execution.

## External Tools Used
Obviously, [Python](https://www.python.org) is used to interpret the script itself. The probing and conversion code uses external tools ('[ffprobe, ffmpeg](https://www.ffmpeg.org/)' and '[mkvmerge](https://mkvtoolnix.download/)'). `ffprobe` is used to probe and verify the source format, and depending on the source format, use `fffmpeg` or `mkvmerge` to convert the container to Matroska.

## Where to Download the External Tools From
`ffprobe` and `ffmpeg` are part of the open source ffmpeg package available from https://www.ffmpeg.org, and `mkvmerge` is part of the open source MKVToolNix package available from https://mkvtoolnix.download.

## Pre-requisites for Use
Ensure you have these external tools installed and define the path appropriately to `ffmpeg` and `mkvmerge` through the following variables under the respective Operating System checks in the function `dict_tool_metadata_get()` in video_container_convert.py:

```
binary_ffmpeg
binary_mkvmerge
```

For example:
```python
	if platform.system() == "Windows":
		binary_ffmpeg = "C:\\ffmpeg\\bin\\ffmpeg.exe",
		binary_mkvmerge = "C:\\Program Files\\MKVToolNix\\mkvmerge.exe"
	else:
		# Since we only support Windows or Linux, the fallback here is obvious
		binary_ffmpeg = "/usr/bin/ffmpeg",
		binary_mkvmerge = "/usr/bin/mkvmerge"
```

Likewise for ffprobe, in function `duration_container_get()` in the same Python script:

```
binary_ffprobe
```

For example:
```python
	if platform.system() == "Windows":
		binary_ffprobe = "C:\\ffmpeg\\bin\\ffprobe.exe"
	else:
		# Since we only support Windows or Linux, the fallback here is obvious
		binary_ffprobe = "/usr/bin/ffprobe"
```
**Note**: Windows path separators have to be double escaped using another backslash, as shown in the example above. On Linux, unless these tools have already been added to the PATH environment variable, you would have to update the environment, or manually feed the path.

If you'd like a tooltip notification on Windows 10 and above, install [win10toast](https://pypi.org/project/win10toast/) with `pip install win10toast`. Tooltips on Linux are supported natively in the script (thanks to `notify-send`).

## How to Batch Process/Use on Single Files
### Batch Processing Recursively/A Selection Through a Simple Right-Click
  On Windows, create a file called "Video Container Convert - Matroska.cmd", or whatever you like but with a .cmd extension, paste the contents as below, and on the Windows Run window, type "shell:sendto" and copy this file in the directory that opens (this is where your items that show up on right-clicking and choosing 'Send To' appear):
```batch
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
```
  Note: In the 3rd line above, ensure you set the path correctly for your Python installation, and on the 7th line, the path to where you download this Python script to.

  Once you're done with the above, all you have to do is right-click on any file or directory (or even a selection of them!) containing compatible source video files, use 'Send To' to send to the command name saved above ('Video Container Convert - Matroska.cmd', as in the example above), and the script will recursively scan through directories and convert the container.
  
  I've included this .cmd file as well, so feel free to edit and set parameters according to your installation.

  Since Linux (or any Unix like OS) use varies with a lot of desktop envvironments, I'm not going to delve into getting verbose here; you can refer your distribution's documentation to figure it out.

### Batch Processing Recursively Through a Command
```
  python "G:\My Drive\Projects\Video Container Convert\video_container_convert.py" --container mkv <path to a directory containing source files> <path to another directory...> <you get the picture!>
```
### Converting Single Files
  If you'd prefer going Hans Solo, use the command below to act on a single file:
```
  python "G:\My Drive\Projects\Video Container Convert\video_container_convert.py" --container mkv <path to the source file>
```
## Options
* `--container`, or `-c`: Specify which of the supported formats the source is to be converted to
* `--help`, or `-h`: Usage help for command line options

## Reporting a Summary
At the end of its execution, the script presents a summary of files converted, failures (if any) and time taken. This comes in handy when dealing with a large number of files.

## Logging
For a post-mortem, or simply quenching curiosity, a log file is generated with whatever is attempted by the script. This log is generated in the local application data directory (applicable to Windows), under my name (Jay Ramani). For example, this would be `C:\Users\<user login>\AppData\Local\Jay Ramani\video_container_convert`.

## TODO (What's Next)
A GUI front-end to make things easy

## Known Issues
* Subtitle codec not supported error on certain files causing the conversion to fail. For example, with some codecs being compatible only with `mp4` format. This is an inherent flaw with the codec format itself, and the only workaround is to convert the offending subtitle to `srt` format. If one stumbles on this, comment the first statement below, and uncomment the third line instead.

```Python
	options_ffmpeg = ("-hide_banner", "-i", input, "-codec", "copy", output)
	# In case we get subtitle codec not supported errors, use the arguments below to convert to srt
	#options_ffmpeg = ("-hide_banner", "-i", input, "-codec", "copy", "-c:s", "srt", output)
```
The above is a snippet from the function `dict_tool_metadata_get()`.

## Testing and Reporting Bugs
The tagger has been tested on Windows 10, 11 and on Manjaro Linux (XFCE). Would be great if someone can help with testing on other platforms and provide feedback.

To report bugs, use the issue tracker with GitHub.

## End User License Agreement
This software is released under the GNU General Public License version 3.0 (GPL3), and you agree to this license for any use of the software

## Disclaimer
Though not possible, I am not responsible for any corruption of your files. Needless to say, you should always backup before trying anything on your precious data.
