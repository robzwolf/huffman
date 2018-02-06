from collections import defaultdict
from time import time
import sys
from tree import Tree

# Start time
t0 = time()

# Initialise the frequencies dictionary
freqs = defaultdict(int)

# Get the filename to read from the arguments
if len(sys.argv) < 2:
    print("No filename was specified.")
    sys.exit(0)
else:
    filename = sys.argv[1]


# Read the file and count frequencies of characters
running_total = 0


# Store the file contents
# file_contents = []

# Read the file
with open(filename) as f:
    file_contents = f.read()
# print(file_contents)

# # Loop through every character of the file
# with open(filename) as f:
#     while True:
#         # Read a single character
#         c = f.read(1)
#
#         if not c:
#             # If we've reached the end of the file
#             break
#
#         else:
#             if c not in freqs:
#                 # Set the first occurrence of c to frequency 1
#                 freqs[c] = 1
#
#             else:
#                 # Increment the number of occurrences of c by 1
#                 freqs[c] += 1
#
#         # Keep a track of how many characters were in the file
#         running_total += 1

# Loop through every character of file_contents
for i in range(len(file_contents)):
    freqs[file_contents[i]] += 1

# End time
t1 = time()

print(freqs)
print("Total characters:", "{:,}".format(running_total))
print("Process took " + str(round(t1-t0,5)) + " seconds")

