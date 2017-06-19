# Polycom Utilities



#### filter_active.py
This script parses through RealPresence Resouce Manager jserver.log files and turns them into CDRs.
I made this because built-in CDR reporting at the time was completely broken.

Usage:
'''
user@machine:~$ ./filter_active.py 
Would you like to (S)pecify a file or s(E)arch the current directory for Jserver.log files? E
Thinking...
    ...sorting...
        ...exporting...
New CSV file: export.csv
...done.
'''

#### CDR_histrogram.py
This script takes a properly formated CDR CSV and outputs histogram data for total bandwidth usage over time.
I created this script because there is no easy way to get this data from the existing RealPresence platform, even their special analytics box doesn't give this information last I checked.

Dependencies:
 - xlsx2csv

Usage:
'''
user@machine:~$ ./CDR_histogram.py 
Would you like to (S)pecify a file or s(E)arch the current directory for .xlsx files? E
Removing Source Device Name
Removing Start Time
Removing Call ID
Output file name: output.csv

'''
