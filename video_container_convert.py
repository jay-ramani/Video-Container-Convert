# Command to convert mp4 to mkv
# avconv -i "$f" -codec copy -map 0 "${f}.mkv"

# Command to convert avi to mkv
# mkvmerge -o out.mkv input.avi input.srt
# -------------------------------------------------------------------------------
# Name        : Video Container Convert
# Purpose     : Converts mp4 and avi files to mkv format
#             : Note: Requires a path defined for each tool
# Author      : Jayendran Jayamkondam Ramani
# Created     : 1:44 AM + 5:30 IST 24 July 2018
# Copyright   : (c) Jayendran Jayamkondam Ramani
# Licence     : GPL v3
# Dependencies: Requires the following packages to be installed as pre-requisites
#                   - win10toast (pip install win10toast; for toast notifications)
#                   - pathlib (to get absolute path)
#                   - appdirs (pip install appdirs; to access application/log directions in a platform agnostic manner)
# -------------------------------------------------------------------------------
import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
import time

from pathlib import Path


# Show tool tip/notification/toast message
def show_toast(tooltip_title, tooltip_message):
	# Handle tool tip notification (Linux)/balloon tip (Windows; only OS v10 supported for now)
	tooltip_message = os.path.basename(__file__) + ": " + tooltip_message

	if platform.system() == "Linux":
		os.system("notify-send \"" + tooltip_title + "\" \"" + tooltip_message + "\"")
	else:
		from win10toast import ToastNotifier

		toaster = ToastNotifier()
		toaster.show_toast(tooltip_title, tooltip_message, icon_path = None, duration = 5)


# Use a dictionary to map a file type (key) to its metadata tool (value).
# Assign a blank string to video file types yet unsupported.

# Point to binaries and other supported format dependencies
def dict_tool_metadata_get(input = None, output = None):
	if platform.system() == "Windows":
		binary_ffmpeg = "C:\\ffmpeg\\bin\\ffmpeg.exe",
		binary_mkvmerge = "C:\\Program Files\\MKVToolNix\\mkvmerge.exe"
	else:
		# Since we only support Windows or Linux, the fallback here is obvious
		binary_ffmpeg = "/usr/bin/ffmpeg",
		binary_mkvmerge = "/usr/bin/mkvmerge"

	source_mkvmerge = ("avi", "divx", "flv", "m4v", "mpg", "mpeg", "webm")
	source_ffmpeg = ("mp4", "mts", "m2ts", "wmv")

	dict_keys_source = {
		"mkv": (source_mkvmerge, source_ffmpeg)
	}

	options_mkvmerge = (input, "--verbose", "-o", output)
	options_ffmpeg = ("-hide_banner", "-i", input, "-codec", "copy", output)
	# In case we get subtitle codec not supported errors, use the arguments below to convert to srt
	#options_ffmpeg = ("-hide_banner", "-i", input, "-codec", "copy", "-c:s", "srt", output)
	# If using avconv instead of ffmpeg, use the options below
	#options_avconv = ("-i", input "-codec", "copy", "-map", "0", "-i", output)

	dict_tool_metadata = {
		source_mkvmerge: (binary_mkvmerge, options_mkvmerge),
		source_ffmpeg  : (binary_ffmpeg, options_ffmpeg)
	}

	return dict_keys_source, dict_tool_metadata


def is_supported_platform():
	return platform.system() == "Windows" or platform.system() == "Linux"


# Open a log file to keep track of what we do
def logging_initialize():
	from appdirs import AppDirs

	# Use realpath instead to get through symlinks
	name_script_executable = os.path.basename(os.path.realpath(__file__)).partition(".")[0]
	dirs = AppDirs(name_script_executable, "Jay Ramani")

	try:
		os.makedirs(dirs.user_log_dir, exist_ok = True)
	except PermissionError:
		print("\aNo permission to write log files at \'" + dirs.user_log_dir + "\'!")
	except:
		print("\aUndefined exception!")
		print("Error", sys.exc_info())
	else:
		print("Check logging results at \'" + dirs.user_log_dir + "\'\n")

		# All good. Proceed with logging.
		logging.basicConfig(filename = dirs.user_log_dir + os.path.sep + name_script_executable + " - " +
		                               time.strftime("%Y%m%d%I%M%S%z") + '.log', level = logging.INFO,
		                    format = "%(message)s")
		logging.info("Log beginning at " + time.strftime("%d %b %Y (%a) %I:%M:%S %p %Z (GMT%z)") + " with PID: " + str(
			os.getpid()) + ", started with arguments " + str(sys.argv) + "\n")


# Returns the label for a drive/partition/volume. Used to
# easily locate videos on a particular disk/partition/volume
# in the report.
def get_volume_label(path):
	label = ""

	if platform.system() == "Windows":
		# We're on Windows
		drive, _ = os.path.splitdrive(path)

		if drive:
			# Import only when required
			import win32api

			label = (win32api.GetVolumeInformation(drive + os.sep))[0]
	else:
		# We're on one of the Unices. Import only when required.
		import psutil

		label = psutil.disk_partitions()[0].mountpoint

	return label


# Splits the path received into two parts:
# 1. the path received without the file's extension
# 2. the extension alone, lower case converted
def split_root_extension(source_path):
	root, extension = os.path.splitext(source_path)

	# Grab the part after the extension separator, and convert to lower case.
	# This is to ensure we don't skip files with extensions that Windows sets
	# to upper case. This is often the case with files downloaded from servers
	# or torrents.
	extension = (extension.rpartition(os.extsep)[2]).lower()

	return root, extension


def duration_container_get(path_file):
	duration = 0

	if platform.system() == "Windows":
		binary_ffprobe = "C:\\ffmpeg\\bin\\ffprobe.exe"
	else:
		# Since we only support Windows or Linux, the fallback here is obvious
		binary_ffprobe = "/usr/bin/ffprobe"

	print("Executing command: " + binary_ffprobe + "-v " + "error " + "-show_entries " + "format=duration " + "-of " + "default=noprint_wrappers=1:nokey=1 " + "-i " + path_file + "\n")
	logging.info("Executing command: " + binary_ffprobe + "-v " + "error " + "-show_entries " + "format=duration " + "-of " + "default=noprint_wrappers=1:nokey=1 " + "-i " + path_file + "\n")

	try:
		# Strip the output as ffprobe ends the orchestra with a new line character
		duration = subprocess.run((binary_ffprobe, "-v", "error", "-show_entries",
		                           "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
		                           "-i", path_file), stdout = subprocess.PIPE, check = True,
		                          universal_newlines = True).stdout.strip()
	except subprocess.CalledProcessError as error_conversion:
		duration = 0

		print(error_conversion.stderr)
		print(error_conversion.output)
		print("\aError probing duration for \'" + path_file + "\'")
		print("Command that resulted in the exception: " + str(error_conversion.cmd))
		print("Error", sys.exc_info())

		logging.error(error_conversion.stderr)
		logging.error(error_conversion.output)
		logging.info("Command that resulted in the exception: " + str(error_conversion.cmd))
		logging.error(
			"Error probing duration for \'" + path_file + "\' " + str(sys.exc_info()))
	except:
		# Handle any generic exception
		print("Undefined exception")
		print("\aError probing duration of \'" + path_file + "\'")
		print("Error", sys.exc_info())

		logging.error("Undefined exception")
		logging.error("Error probing duration of \'" + path_file + "\': " + str(sys.exc_info()))

		show_toast("Error", "Error probing duration of \'" + path_file + "\'. Check the log.")
	else:
		# Convert the duration in seconds (in decimal) obtained as string to
		# actual float, and convert seconds to nano-seconds for use with
		# total_time_in_hms_get()
		duration_ns = float(duration) * 1000000000

		print("Duration of \'" + path_file + "\': " + total_time_in_hms_get(duration_ns) + ", approximately")
		logging.info("Duration of \'" + path_file + "\': " + total_time_in_hms_get(duration_ns) + ", approximately")

	print("\n")
	logging.info("\n")

	# Convert the float in string to int to ignore the fractional part. This
	# would differ between the source and target container formats in most cases;
	# as a consequence, the duration check in post_process() will otherwise fail.
	return int(float(duration))


# The post conversion process. If we find a Matroska file, with the same
# (container, not stream) duration as the source file, we assume the
# conversion was successful. We then delete the source file to save space.
def post_process(root, path_file, container_target_extension, list_failed_conversions):
	container_target_name_abs = root + os.extsep + container_target_extension

	# Does the target format file exist? If so, go ahead with the next steps.
	if os.path.isfile(container_target_name_abs):
		duration_target = duration_container_get(container_target_name_abs)
		duration_source = duration_container_get(path_file)

		# Are the container (not stream) durations the same? If so, the conversion
		# is assumed to be successful; delete. Else, leave the source file intact.
		if duration_target == duration_source:
			print("Conversion of \'" + path_file + "\' to \'" + container_target_name_abs + "\' seems to be valid\n")
			logging.info(
				"Conversion of \'" + path_file + "\' to \'" + container_target_name_abs + "\' seems to be valid\n")

			# TODO: This is not a platform safe check. While it works on Windows,
			# it requires to be modified for the Unices, where the upper 8 bits of
			# the 16 bit integer returned needs to be checked for.

			# Successful exit status is zero
			if not os.remove(path_file):
				print("Deleted source file \'" + path_file + "\'\n")
				logging.info("Deleted source file \'" + path_file + "\'\n")
			else:
				print("\aFailed to delete the source file \'" + path_file + "\'\n")
				logging.error("Failed to delete the source file \'" + path_file + "\'\n")
		else:
			print(
				"\aDuration mismatch of \'" + container_target_name_abs + "\' (" + str(duration_target) + "s) with source (" + str(duration_source) + "s). Skipping deleting \'" + path_file + "\'.")
			logging.error(
				"Duration mismatch of \'" + container_target_name_abs + "\' (" + str(duration_target) + "s) with source (" + str(duration_source) + "s). Skipping deleting \'" + path_file + "\'.")

			# If the duration was a mismatch, this is a failed conversion
			list_failed_conversions.append(path_file)

			# Either the source itself is corrupt, or our converted version
			# appears effed up. Don't litter.
			if not os.remove(container_target_name_abs):
				print("Deleted suspicious target file \'" + container_target_name_abs + "\'\n")
				logging.info("Deleted suspicious target file \'" + container_target_name_abs + "\'\n")
			else:
				print("Failed to delete suspicious target file \'" + container_target_name_abs + "\'\n")
				logging.error("Failed to delete suspicious target file \'" + container_target_name_abs + "\'\n")
	else:
		# No target version found. How'd we even get here?
		print("\aTarget file \'" + container_target_name_abs + "\' not found!\n")
		logging.error("Target file \'" + container_target_name_abs + "\' not found!\n")


def conversion_failure_cleanup(path_file, container_target_name_abs, list_failed_conversions):
	# We need to clean up the improperly constructed Matroska format. Check
	# if the file exists in the first place.
	if os.path.isfile(container_target_name_abs):
		# Mop up litter, post the futile conversion
		print("\'" + container_target_name_abs + "\', was improperly done; deleting...")
		logging.info(
			"\'" + container_target_name_abs + "\', was improperly done; deleting...")

		# TODO: This is not a platform safe check. While it works on Windows,
		# it requires to be modified for the Unices, where the upper 8 bits of
		# the 16 bit integer returned needs to be checked for.

		# Successful exit status is zero
		if not os.remove(container_target_name_abs):
			print("Deleted \'" + container_target_name_abs + "\'\n")
			logging.info("Deleted \'" + container_target_name_abs + "\'\n")
		else:
			print("Failed to delete \'" + container_target_name_abs + "\'\n")
			logging.error("Failed to delete \'" + container_target_name_abs + "\'\n")

	list_failed_conversions.append(path_file)

	print_spacer()


# Check if we have enough space to go ahead with the conversion to
# Matroska. In doing so, we check for a ballpark 1.2 times the source
# file, as that's how much maximum or lesser the Matroska version will
# take. Else we report nay to the caller.
def disk_space_check(path_file):
	availability = False

	total, used, free = shutil.disk_usage(os.path.splitdrive(Path(os.path.normpath(path_file)).resolve())[0])

	if free > (1.2 * os.stat(path_file).st_size):
		availability = True

	return availability, free


# Format size in kibi, mebi, gibi etc. for user readability
def sizeof_fmt(num, suffix = 'B'):
	for unit in ('', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'):
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0

	return "%.1f%s%s" % (num, 'Yi', suffix)


# Print a spacer after every file's processing for sifting through the output
# and log
def print_spacer():
	print("----- ----- ----- ----- -----")
	logging.info("----- ----- ----- ----- -----")


# Fetch the converter executable and its options
def container_converter_get(path_file, container_target_name_abs, extension):
	container_converter = options = None

	# Pass the input and output files, so we get them back in an extensible format with
	# a dictionary
	dict_keys_source, dict_tool_metadata = dict_tool_metadata_get(path_file, container_target_name_abs)

	source = None

	for key, value in dict_tool_metadata.items():
		if extension in key:
			source = key

			break

	# Proceed only if a valid source was found for the target container format we received
	if source:
		container_converter, options = dict_tool_metadata[source]

	return container_converter, options


# Converts the video file argument received to Matroska format
def container_format_matroska_set(path_file, list_failed_conversions, container_target_extension):
	root, extension = split_root_extension(path_file)

	container_target_name_abs = root + os.extsep + container_target_extension

	# Proceed only if a target container version of the source file doesn't already
	# exist
	if not os.path.isfile(container_target_name_abs):
		container_converter, options, = container_converter_get(path_file, container_target_name_abs, extension)

		if container_converter is not None and options is not None:
			# Check if disk space is available for creating the video
			# with the new container. Else, report and skip the current
			# file. We still continue as we may have received file(s)
			# on other disks/drives in the next command line argument(s).
			# Use pathlib to get the absolute path; this is vital for
			# shutil.disk_usage, else it will fail.
			availability, free = disk_space_check(path_file)

			if availability:
				container_converter = "".join(container_converter)

				# Check if the metadata tool exists in the path defined
				if os.path.isfile(container_converter):
					# We got a valid tool to write metadata
					output = ""

					# Track conversion start time in nano-seconds
					time_start = time.monotonic_ns()

					try:
						output = subprocess.run((container_converter, *options), stdout = subprocess.PIPE,
						                        check = True, universal_newlines = True)
					except subprocess.CalledProcessError as error_conversion:
						if error_conversion.stderr:
							print(error_conversion.stderr)
							logging.error(error_conversion.stderr)

						if error_conversion.output:
							print(error_conversion.output)
							logging.error(error_conversion.output)
							logging.error(error_conversion.output)

						print("\aError converting \'" + path_file + "\' to Matroska")
						print("Command that resulted in the exception: " + str(error_conversion.cmd))
						print("Error", sys.exc_info())

						logging.info("Command that resulted in the exception: " + str(error_conversion.cmd))
						logging.error(
							"Error converting \'" + path_file + "\' to Matroska" + str(sys.exc_info()))

						conversion_failure_cleanup(path_file, container_target_name_abs, list_failed_conversions)

						show_toast("Error", "Error converting \'" + path_file + "\'. Check the log.")
					# Handle any generic exception
					except:
						print("Undefined exception")
						print("Error converting \'" + path_file + "\'")
						print("Error", sys.exc_info())

						logging.error("Undefined exception")
						logging.error("Error converting \'" + path_file + "\': " + str(sys.exc_info()))

						conversion_failure_cleanup(path_file, container_target_name_abs, list_failed_conversions)

						show_toast("Error", "Error converting \'" + path_file + "\'. Check the log.")
					else:
						# Track conversion end time in nano-seconds
						time_end = time.monotonic_ns()

						container_format_matroska_set.total_time_conversion += time_end - time_start
						container_format_matroska_set.total_count_conversion += 1

						print(
							"\nConversion of \'" + path_file + "\' to " + container_target_extension.capitalize() + " format complete")
						logging.info(
							"\nConversion of \'" + path_file + "\' to " + container_target_extension.capitalize() + " format complete")

						if output:
							print(output)
							logging.info(output)

						post_process(root, path_file, container_target_extension, list_failed_conversions)

					finally:
						print_spacer()
				else:
					print("No metadata tool found at \'" + container_converter + "\'")
					logging.error("No metadata tool found at \'" + container_converter + "\'")

					print_spacer()
			else:
				print(
					"Not enough disk space available in \'" + get_volume_label(
						path_file) + "\'; need " + "{:>1}".format(
						sizeof_fmt(os.stat(path_file).st_size * 1.2)) + ", available " + "{:>1}".format(
						sizeof_fmt(free)) + ". Can't process \'" + path_file + "\'.\n")
				logging.error(
					"Not enough disk space available in \'" + get_volume_label(
						path_file) + "\'; need " + "{:>1}".format(
						sizeof_fmt(os.stat(path_file).st_size * 1.2)) + ", available " + "{:>1}".format(
						sizeof_fmt(free)) + ". Can't process \'" + path_file + "\'.\n")

				print_spacer()


#	else:
#		if extension == container_target_extension:
#			print(
#				"Target \'" + container_target_name_abs + "\' already exists. Skipping file \'" + path_file + "\'...\n")
#			logging.error(
#				"Target \'" + container_target_name_abs + "\' already exists. Skipping file \'" + path_file + "\'...\n")

#			print_spacer()

container_format_matroska_set.total_time_conversion = 0
container_format_matroska_set.total_count_conversion = 0


# Convert the time in nanoseconds passed to hours, minutes and seconds as a string
def total_time_in_hms_get(total_time_ns):
	seconds_raw = total_time_ns / 1000000000
	seconds = round(seconds_raw)
	hours = minutes = 0

	if seconds >= 60:
		minutes = round(seconds / 60)
		seconds = seconds % 60

	if minutes >= 60:
		hours = round(minutes / 60)
		minutes = minutes % 60

	# If the quantum is less than a second, we need show a better resolution. A fractional report matters only when
	# it's less than 1.
	if (not (hours and minutes)) and (seconds_raw < 1 and seconds_raw > 0):
		# Round off to two decimals
		seconds = round(seconds_raw, 2)
	elif (not (hours and minutes)) and (seconds_raw < 60 and seconds_raw > 1):
		# Round off to the nearest integer, if the quantum is less than a minute. A fractional report doesn't matter
		# when it's more than 1.
		seconds = round(seconds_raw)

	return (str(hours) + " hour(s) " if hours else "") + (str(minutes) + " minutes " if minutes else "") + (str(
		seconds) + " seconds")


def stats_print(list_failed_conversions):
	if container_format_matroska_set.total_count_conversion:
		print("Converted a total of " + str(
			container_format_matroska_set.total_count_conversion) + " file(s) in " + total_time_in_hms_get(
			container_format_matroska_set.total_time_conversion) + "\n")
		logging.info("Converted a total of " + str(
			container_format_matroska_set.total_count_conversion) + " file(s) in " + total_time_in_hms_get(
			container_format_matroska_set.total_time_conversion) + "\n")
	else:
			print("No files converted to Matroska format")
			logging.info("No files converted to Matroska format")

	if list_failed_conversions:
		print("\aHere's the list of files that failed to convert to Matroska format:\n")
		logging.info("Here's the list of files that failed to convert to Matroska format:\n")

		for failed_conversion in list_failed_conversions:
			print(failed_conversion)
			logging.info(failed_conversion)


# Parse command line arguments and return option and/or values of action
def cmd_line_parse():
	dict_keys_source, _ = dict_tool_metadata_get()

	parser = argparse.ArgumentParser(
		description = "Encapsulates the source video in one the target container formats specified: %s" % tuple(
			dict_keys_source.keys()),
		add_help = True)

	parser.add_argument("-c", "--container", choices = tuple(dict_keys_source.keys()), required = True,
	                    action = "store",
	                    default = None, dest = "container",
	                    help = "Specify which of the supported formats the source is to be converted to")

	result_parse, files_to_process = parser.parse_known_args()

	return result_parse.container, files_to_process


# Recurse and process files within
def process_dir(path, list_failed_conversions, container_target):
	# If it's a directory, walk through for files below
	for path_dir, _, file_names in os.walk(path):
		for file_name in file_names:
			path_file = os.path.join(path_dir, file_name)
			container_format_matroska_set(path_file, list_failed_conversions, container_target)


def main(argv):
	exit_code = 0

	# We support only Windows and Unix like OSes
	if is_supported_platform():
		logging_initialize()

		# Change to the working directory of this Python script. Else, any dependencies will not be found.
		os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

		print("Changing working directory to \'" + os.path.dirname(os.path.abspath(sys.argv[0])) + "\'...\n")
		logging.info("Changing working directory to \'" + os.path.dirname(os.path.abspath(sys.argv[0])) + "\'...\n")

		container_target, files_to_process = cmd_line_parse()

		if len(files_to_process) >= 1:
			# Remove duplicates from the source path(s)
			files_to_process = [*set(files_to_process)]

			# A list to keep track of files for which conversion to Matroska
			# format failed
			list_failed_conversions = []

			for path in files_to_process:
				if os.path.isdir(path):
					process_dir(path, list_failed_conversions, container_target)
				else:
					# We got a file, do the needful
					container_format_matroska_set(path, list_failed_conversions, container_target)
			# Slows down the script exit, so disabled for now
			# show_completion_toast(argv[0])

			stats_print(list_failed_conversions)
		else:
			print("\aThis program requires at least one argument")
			logging.error("This program requires at least one argument")

			exit_code = 1
	else:
		print("\aUnsupported OS")
		logging.error("Unsupported OS")

		exit_code = 1

	logging.shutdown()

	return exit_code


if __name__ == '__main__':
	main(sys.argv)
