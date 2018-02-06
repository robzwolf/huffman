from collections import defaultdict
from time import time
import sys


class Node:
    def __init__(self, cargo, left=None, right=None):
        self.cargo = cargo
        self.left = left
        self.right = right

    def __str__(self):
        return str(self.cargo)


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

# Read the file
with open(filename) as f:
    file_contents = f.read()

# Loop through every character of file_contents
for i in range(len(file_contents)):
    freqs[file_contents[i]] += 1

# End time
t1 = time()

print(freqs)
print("Process took " + str(round(t1-t0,5)) + " seconds")

