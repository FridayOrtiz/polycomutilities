#!/usr/bin/python
#
# Copyright (C) 2017 Rafael Ortiz <rafael@ortizmail.cc>
#
# This program is free software: you can redistribute it and/or modift
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# 
# This script parses Polycom RealPresence Resource Manager jserver logs
# and turns then into CDR CSVs. I created this script because the built
# in CDR system is completely broken and was not properly capturing calls
# as of version 10, last time I used this.
#
# Run this script from the folder with uncrompressed jserver log files
# and it can pull them all out and convert to a CDR.
#
# Don't forget to change the EOTSTRING variable to the string that marks
# the divider between timestamps and useful data. Manual inspecting the
# jserver log files should make it obvious what string to put here.

import csv
import os
import sys
from operator import itemgetter

EOTSTRING = "RPRM.yourdomain.com RPRM" # The string in the RPRM jserver logs that starts after server time


# Export the parsedLines array as a CSV file
def exportCSV(parsed):
    newFileName = raw_input('New CSV file: ')
    f1 = open(newFileName, 'w')
    writer = csv.writer(f1)
    writer.writerow(['Source Device Name', 'Source Device Aliases', 'Destination Device Name', 'Destination Device Aliases', 'Dial String', 'Start Time', 'End Time', 'Call ID'])
    for values in parsed:
        writer.writerow(values)
    f1.close()

# Ask the user for the name of the file they want to parse
def getFileName():
    file_name = raw_input('Enter file name to parse: ')
    file_name_string = str(file_name)
    return file_name_string

# Find the given string 'char' in the input string 's' and 
# return the index where 'char' starts in the string.
def find_str(s, char):
	index = 0

	if char in s:
		c = char[0]
		for ch in s:
			if ch ==c:
				if s[index:index+len(char)] == char:
					return index
			index += 1
	return -1

# Parse the time of the line from the entire line.
def getTime(s):
	endOfTime = find_str(s, EOTSTRING)
	startOfTime = find_str(s, ">")
	time = s[startOfTime+1:endOfTime]
	return time

# This only execues when filter_active.py is executed rather than imported.
if __name__ == '__main__':
	decision = raw_input('Would you like to (S)pecify a file or s(E)arch the current directory for Jserver.log files? ')

	# Read a specified file
	if decision == 's' or decision == 'S':
		fileName = getFileName()
		with open(fileName) as f:
			content = f.readlines()
	# Search for all Jserver.log.* files and aggregate them
	elif decision == 'e' or decision == 'E':
		content = []
		files = filter(os.path.isfile, os.listdir(os.getcwd()))
		for f in files:
			if "Jserver.log" in f:
					with open(f) as fl:
						print('Reading from ' + f)			
						content = content + fl.readlines()
#		print(files)
	else:
		print('Exiting.')
		sys.exit()

	parsedLines = []
	endTimes = []

	# Check aggregate imported file for lines indicating a call has begun
	# or indicated that a call has been terminated. Add these lines to the
	# parsedLines and endTimes arrays. 
	for line in content:
		if "active call:callIdentifier=" in line:
			relevant_start = find_str(line, "active call:callIdentifier=")
			caller_id = find_str(line, "sourceCallLeg=[")
			destination_id = find_str(line, "destinationCallLeg=[")
			general_info = line[relevant_start:caller_id]
			caller_info = line[caller_id:destination_id]
			destination_info = line[destination_id:]
			time =getTime(line)
#			print(general_info)
#			print(caller_info)
#			print(destination_info)

			callID_start = find_str(general_info, "call:callIdentifier=")
			callID_end = find_str(general_info, ", signalingType=")
			callID = general_info[callID_start+20:callID_end]
#			print(callID)


			parsedLines.append([general_info, caller_info, destination_info, callID, time, time])


		if "terminated call:callIdentifier=" in line:
			relevant_start = find_str(line, "terminated call:callIdentifier=")
			cut = line[relevant_start:]
#			print cut
			time = getTime(line)
#			print(time)

			callID_start = find_str(cut, "call:callIdentifier=")
			callID_end = find_str(cut, ", destinationDeviceIdentifier=")
			callID = cut[callID_start+20:callID_end]

			endTimes.append([cut, time, callID])

#	print(parsedLines)
#	print(endTimes)

	print('Thinking...')

	# Extract relevant information from parsedLines into a more human-readable format.
	for i in range(len(parsedLines)):
		for j in range(len(endTimes)):
			if endTimes[j][2] == parsedLines[i][3]:
				parsedLines[i][5] = endTimes[j][1]
				general_info = parsedLines[i][0]
				caller_info = parsedLines[i][1]
				destination_info = parsedLines[i][2]

				dialStart = find_str(general_info, "originalDialString=")
				dialEnd = find_str(general_info, ", resolvedDialString=")
				dialString = general_info[dialStart+19:dialEnd]

				sNameStart = find_str(caller_info, "deviceName=")
				sNameEnd = find_str(caller_info, ", deviceModel=")
				sName = caller_info[sNameStart+11:sNameEnd]

				sAliasStart = find_str(caller_info, "aliases=")
				sAliasEnd = find_str(caller_info, "destinationCallLeg=")
				sAlias = caller_info[sAliasStart+8:sAliasEnd]

				dNameStart = find_str(destination_info, "deviceName=")
				dNameEnd = find_str(destination_info, ", deviceModel=")
				dName = destination_info[dNameStart+11:dNameEnd]

				dAliasStart = find_str(destination_info, "aliases=")
				dAlias = destination_info[dAliasStart+8:]

				callID = parsedLines[i][3]
				startTime = parsedLines[i][4]
				endTime = parsedLines[i][5]

				parsedLines[i] = [sName, sAlias, dName, dAlias, dialString, startTime, endTime, callID]

	print('    ...sorting...')

	parsedLinesSorted = sorted(parsedLines, key=itemgetter(5)) # sort by startTime

#	print(parsedLines)

	print('        ...exporting...')
	exportCSV(parsedLinesSorted)
	print('...done.')
