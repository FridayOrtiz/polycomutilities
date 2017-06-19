#!/usr/bin/python3
#
# Copyright (C) 2017 Rafael Ortiz <rafael@ortizmail.cc>
#
# This program is free software: you can redistribute and/or modify
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
# CDR Histogram takes in a modified CDR in csv format with the layout:
#
#    mm/dd/yyyy, start_time, end_time, duration, call_rate (Kbps)
#
# and sums it to a histogram of total calls/total bandwidth per
# unit time. The histogram is output as a csv file with the format:
#
#    [FIRST DATE]
#    [ROW OF TIMES]
#    [ROW OF RATES]
#
#    [NEXT DATE]
#    ...etc
#
# The code can also search a directory for .xlsx output
# of RealPresence resource manager CDR Entpoint Usage Reports,
# convert them to CSV (depends on xlsx2csv package) and process
# the entire batch into a single aggregate CSV. 
#
# Max bandwidth utilization can be found by taking the MAX of
# each row of rates. Histograms can be plotted in excel, do
# whatever you want.

import csv # for manipulating CSV files
import os  # for searching the CWD for xlsx, converting them, etc
import re  # regex to check if words slipped into dict keys
import getopt # for the override flag
import sys # for getting args

def getFileName():
    file_name = input('Enter file name to parse: ')
    file_name_str = str(file_name)
    return file_name_str

# Takes a dictionary, writes a CSV of histogram
def writeCSV(days):
    fn = input('Output file name: ')
    p = re.compile('\D') # regex for any non number
    with open(fn, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key in days:
            if p.match(key[0]) is None: # If the key starts with a number 
                writer.writerow(key)
                day = days[key]
                times = []
                rates = []
                for i in day:
                    times.append(i[0])
                    rates.append(i[1])
                writer.writerow(times)
                writer.writerow(rates)
                writer.writerow('')


# Takes a time of format HH:MM AM/PM and converts it to
# 24h time, HHMM
def convertTime(time):
    x = len(time)
    convTime = ''
    # Time is AM
    if time[x-2:x] == 'AM':
        for el in time[0:x-3]:
            if el == ':' or el == ' ' or el == 'A' or el == 'P' or el == 'M':
                pass
            else:
                convTime = convTime + el
    elif time[x-2:x] == 'PM':
        for el in time[0:x-3]:
            if el == ':' or el == ' ' or el == 'A' or el == 'P' or el == 'M':
                pass
            else:
                convTime = convTime + el
        intTime = int(convTime)
        intTime = intTime + 1200 # Add 12 hours to PM
        convTime = str(intTime)
    print(str(time) + ' converted to ' + convTime)
    return convTime

def flags(argv):
    override = False
    override_value = 0
    average = False
    try:
        opts, args = getopt.getopt(argv,"ho:a",["help","override=", "average"])
    except getopt.GetoptError:
        print('Usage: CDR_histogram.py [options]')
        print('    -h or --help: show this dialogue')
        print('    -o <value> or --override=<value>: override')
        print('        all call data rates with specified value')
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: CDR_histogram.py [options]')
            print('    -h or --help: show this dialogue')
            print('    -o <value> or --override=<value>: override')
            print('        all call data rates with specified value')
            sys.exit()
        elif opt in ("-o", "--override"):
            override = True
            override_value = int(arg)
            print('Overriding call rate with ' + str(arg))
        elif opt in ("-a", "--average"):
            average = True
            print('Average all days into single day.')
    return [override, override_value, average]

# This function executes when the program is executed rather than imported
if __name__ == '__main__':
    [override, override_value, average] = flags(sys.argv[1:])
    decision = input('Would you like to (S)pecify a file or s(E)arch the current directory for .xlsx files? ')

    # arr is the array that all the call data is read into
    arr = []

    # Read a specified file
    if decision == 's' or decision == 'S':
        fn = getFileName()
        fl = None
        with open(fn) as csvfile:
            fl = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in fl:
                arr.append(row)
        raw_file = input('Is this file RAW? (Y/N) ')
        if raw_file == 'Y' or raw_file == 'y':
            print('Removing ' + str(arr[0]))
            del arr[0] # Remove first row with descriptors
            for row in arr:
                print('Removing ' + str(row[0]))
                del row[0] # Remove Name column
                print('Removing ' + str(row[4]))
                del row[4] # Remove Call Number 1
                print('Removing ' + str(row[5]))
                del row[5] # Remove Call Direction
                print('Removing ' + str(row[5]))
                del row[5] # Remove Endpoint Transport Address
    elif decision == 'E' or decision == 'e':
        files = filter(os.path.isfile, os.listdir(os.getcwd()))
        for f in files:
            # Convert all xlsx to CSV
            if '.xlsx' in f:
                os.system('xlsx2csv \"' + f + '\" \"' + f[:len(f)-5] + '.csv\"')
        # Get all files again to grab CSV files
        files = filter(os.path.isfile, os.listdir(os.getcwd()))
        for f in files:
            if '.csv' in f:
                with open(f) as csvfile:
                    fl = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in fl:
                        arr.append(row)
        j = 0
        to_remove = []
        for row in arr:
            if row[0] == 'Name:':
                to_remove.append(j)
            else:
                # If trying to remove something that's not there... don't!
                try:
                    print('Removing ' + str(row[0]))
                    del row[0] # Remove Name column
                    print('Removing ' + str(row[4]))
                    del row[4] # Remove Call Number 1
                    print('Removing ' + str(row[5]))
                    del row[5] # Remove Call Direction
                    print('Removing ' + str(row[5]))
                    del row[5] # Remove Endpoint Transport Address
                except:
                    pass
        j = j+1

# Don't remove them here, let the exception be caught in the end.
# Too much risk in removing a line that shouldn't have been removed
# and skewing data.
#        j = 0
#        for el in to_remove:
#            del arr[el-j] # Remove the info row, shifting index for each one removed
#            j = j+1

    days = {}
    for row in arr:
        j = 0
        for i in row:
            if 'AM' in i or 'PM' in i:
                nTime = convertTime(i)
                row[j] = nTime
            j = j+1
        indx = str(row[0])
        if indx in days:
            days[indx].append(row[1:])
        else:
            days[indx] = [row[1:]]

    # Start by iterating through for each day, an array of tuples.
    # One element has start and end times, and the other element
    # keeps track of data rate, positive for start times and
    # negative for end times. 
    # 
    # For example:
    #    [(1200,512), (1215,-512), (1207,512), (1213,-512)]
    # 
    # Then sort the array based on the first element of the tuple
    # and create a new array with times and sum total data rate
    # 
    # For example:
    #    [(1200,512),(1207,1024),(1213,512),(1215,0)]

#    print(days)

    if average:
        simple_hist = []
        hist = []
        for key in days:
            day = days[key]
            for call in day:
                try:
                    if override:
                        call[3] = override_value
                    tp = (float(call[0]),int(call[3]))
                    simple_hist.append(tp)
                    tp = (float(call[1]),int(call[3]))
                    simple_hist.append(tp)
                except:
                    pass
            simple_hist.sort(key=lambda x:x[0])
            j = 0
            for tp in simple_hist:
                tpl = (tp[0],tp[1])
                if j > 0:
                    tpl = (tpl[0], tpl[1] + hist[j-1][1])
                j = j+1
                hist.append(tpl)
        final = {'111 Combined':hist}
        writeCSV(final)
            
    elif not average:
        for key in days:
            day = days[key]
            simple_hist = []
            for call in day:
                # If some strings/rows escaped being purged then catch them here
                try:
                    if override: # Override value to specified rate
                        call[3] = override_value
                    tp = (float(call[0]),int(call[3]))
                    simple_hist.append(tp)
                    tp = (float(call[1]),0 - int(call[3]))
                    simple_hist.append(tp)
                except:
                    pass
            simple_hist.sort(key=lambda x: x[0])
            #print(simple_hist)
            hist = []
            j = 0
            for tp in simple_hist:
                tpl = (tp[0],tp[1])
                if j > 0:
                    tpl = (tpl[0], tpl[1] + hist[j-1][1])
                j = j+1
                hist.append(tpl)
            days[key] = hist
        writeCSV(days)
        #print(days)
