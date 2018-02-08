from collections import defaultdict
from time import time
import sys
import heapq


# import argparse


class Node:
    def __init__(self, frequency, tree):
        self.frequency = frequency
        self.tree = tree

    def __repr__(self):
        return """Node (
            {}
            {}
        )""".format(self.frequency, self.tree)


# class Heap:
#     pass


def encode(filename):
    """
    Encodes a file using Huffman coding.
    :param filename: The file to encode.
    :return:
    """

    # Start time
    t0 = time()

    # Initialise the frequencies list, where the i-th element represents
    # the occurrences of the byte represented by i
    freqs = [0] * 256

    # Read the file byte by byte
    with open(filename, "rb") as f:
        file_contents = f.read()

    # Loop through every byte of file_contents and count the frequency
    for i in range(len(file_contents)):
        freqs[file_contents[i]] += 1

    # End time
    t1 = time()

    # Print the frequency of each byte
    for i in range(len(freqs)):
        print(bytes([i]), "=", freqs[i])

    print("Process took " + str(round(t1 - t0, 5)) + " seconds")

    # Make a symbols list of the bytes we intend to encode
    occurring_bytes = (each_byte for each_byte in range(256) if freqs[each_byte] != 0)
    print(*occurring_bytes)


def decode(filename):
    """
    Decodes a file that has been encoded using Huffman coding.
    :param filename: The file to decode
    :return:
    """
    pass


# Parse initial arguments and record appropriately
if len(sys.argv) < 3:
    print("Missing arguments")
    sys.exit(0)
else:
    mode = sys.argv[1]
    filename = sys.argv[2]
    if mode == "-e":
        encode(filename)
    elif mode == "-d":
        decode(filename)
    else:
        print("Invalid mode")
        sys.exit(0)
