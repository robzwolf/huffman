import operator
from time import time
import sys
import heapq
import argparse

from collections import defaultdict


class Heap:
    def __init__(self, heap):
        self.heap = heap
        heapq.heapify(self.heap)

    def push(self, item):
        heapq.heappush(self.heap, item)

    def pop(self):
        return heapq.heappop(self.heap)

    def __len__(self):
        return len(self.heap)

    def __repr__(self):
        return "Heap({})".format(self.heap)


class HeapElement:
    def __init__(self, frequency, tree):
        """
        Make a new HeapElement (i.e. an element in the heap, not to be confused with an element in a tree)
        :param frequency: frequency associated with the element
        :param tree: tree associated with the element, could be a Branch or Leaf
        """
        self.frequency = frequency
        self.tree = tree

    def __lt__(self, other):
        return self.frequency < other.frequency

    def __repr__(self):
        return "\nHeapElement( Frequency: {}, Tree: {} )".format(self.frequency, self.tree)


class Tree:
    """
    A tree can be a branch or a leaf.
    """
    pass


class Leaf(Tree):
    def __init__(self, byte):
        """
        Declare a new leaf. A leaf's cargo is a unique byte.
        :param byte: The byte
        """
        self.byte = byte

    def __repr__(self):
        return "Leaf({})".format(self.byte)


class Branch(Tree):
    def __init__(self, left, right):
        """
        Declare a new branch. A branch has a child left and a child right tree.
        :param left:
        :param right:
        """
        self.left = left
        self.right = right

    def __repr__(self):
        return "Branch( Left: {}, Right: {} )".format(self.left, self.right)


class ByteLabel():
    def __init__(self, byte, label):
        """
        A simple wrapper for a (byte, label) pair.
        :param byte:
        :param label:
        """
        self.byte = byte
        self.label = label

    def label_len(self, bl):
        return len(bl.label)

    def get_byte(self, bl):
        return bl.byte

    def __repr__(self):
        return "ByteLabel(byte={}, label={})".format(self.byte, self.label)


class ByteLabels():
    def __init__(self, byte_labels):
        self.byte_labels = byte_labels

    # def add(self, byte_label):
    #     self.byte_labels.append(byte_label)

    def get_by_label(self, label):
        for bl in self.byte_labels:
            if bl.label == label:
                return bl
        return None

    def get_by_byte(self, byte):
        for bl in self.byte_labels:
            if bl.byte == byte:
                return bl
        return None

    def set_byte(self, byte, label):
        for bl in self.byte_labels:
            if bl.byte == byte:
                bl.label = label
                return True
        return False

    def sort_by_label_len(self):
        self.byte_labels = sorted(self.byte_labels, key=lambda x: len(x.label))

    def sort_by_byte_alphabetically(self):
        self.byte_labels = sorted(self.byte_labels, key=lambda x: x.byte)

    def __repr__(self):
        return_string = ""
        for bl in self.byte_labels:
            return_string += "\t{}\n".format(bl)
        return return_string


def encode(filename):
    """
    Encodes a file using Huffman coding.
    :type filename: str
    :param filename: The file to encode.
    :return:
    """

    print("Encoding:", filename)

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

    # Print the frequency of each byte
    for i in range(len(freqs)):
        print(bytes([i]), "=", freqs[i])

    # Make a list of the bytes we intend to encode
    occurring_bytes = [each_byte for each_byte in range(256) if freqs[each_byte] != 0]

    # Define the heap, initially a load of heap elements consisting of only Leaves
    heap = Heap([HeapElement(freqs[byte], Leaf(byte)) for byte in occurring_bytes])

    print("Initial heap:", heap)
    num_unique_bytes = len(heap)
    print("Length of heap:", num_unique_bytes)

    # Iterate through the heap until we have a huge frequency tree inside a single HeapElement
    while len(heap) > 1:
        smallest = heap.pop()
        second_smallest = heap.pop()
        heap.push(
            HeapElement(
                smallest.frequency + second_smallest.frequency,
                Branch(smallest.tree, second_smallest.tree)
            )
        )
        print("LATEST HEAP IS:", heap)
        print("Length of heap is now:", len(heap))

    # Traverse through the tree and work out the label for each byte
    byte_labels = ByteLabels([ByteLabel(byte, None) for byte in occurring_bytes])
    print("byte_labels:", byte_labels)

    def traverse_and_label(tree, current_label):
        if isinstance(tree, Branch):
            print("Current tree is a branch, current_string is", current_label)
            traverse_and_label(tree.left, current_label + "0")
            traverse_and_label(tree.right, current_label + "1")
        elif isinstance(tree, Leaf):
            print("Current tree is a leaf with byte {}, current_string is".format(tree.byte), current_label)
            byte_labels.set_byte(tree.byte, current_label)

    traverse_and_label(heap.pop().tree, "")

    # Print the byte labels
    print("Normal byte labels are as follows:")
    print(byte_labels)
    # Sort the byte labels by length of codeword (they are already "alphabetically" sorted)
    print("\nCanonically sorted byte labels are as follows:")
    byte_labels.sort_by_label_len()
    print(byte_labels)

    # Replace existing codes with new ones, as per canonical Huffman code algorithm
    latest_num = -1
    for i in range(len(occurring_bytes)):
        working_byte_label = byte_labels.byte_labels[i]
        print("latest_num is currently", latest_num, "and working_byte_label is currently", working_byte_label)
        new_codeword = str(bin(latest_num + 1))[2:]
        while len(new_codeword) < len(working_byte_label.label):
            new_codeword += "0"
        latest_num = int(new_codeword, 2)
        print("Setting {}.label to {}".format(working_byte_label, new_codeword))
        working_byte_label.label = new_codeword

    # Convert the input file to one long compressed string of 1s and 0s
    output = ""
    for byte in file_contents:
        label = byte_labels.get_by_byte(byte).label
        print("byte is {} and has label {}".format(byte, label))
        output += label
    print("output is", output)

    # Now to write this to file

    # Derive new .hc filename
    output_filename = filename[:filename.rfind(".")] + ".hc"
    print(output_filename)

    # End time
    t1 = time()
    print("Process took " + str(round(t1 - t0, 5)) + " seconds")


def decode(filename):
    """
        Decodes a file that has been encoded using Huffman coding.
        :type filename: str
        :param filename: The file to decode
        :return:
        """
    pass


# Parse initial arguments and record appropriately
if len(sys.argv) < 3:
    print("Missing arguments")
    sys.exit(1)
else:
    mode = sys.argv[1]
    filename = sys.argv[2]
    if mode == "-e":
        encode(filename)
    elif mode == "-d":
        decode(filename)
    else:
        print("Invalid mode")
        sys.exit(1)
