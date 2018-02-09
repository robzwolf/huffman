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
    occurring_bytes = (each_byte for each_byte in range(256) if freqs[each_byte] != 0)

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



    # def make_codes_helper(self, root, current_code):
    #     if (root == None):
    #         return
    #
    #     if (root.char != None):
    #         self.codes[root.char] = current_code
    #         self.reverse_mapping[current_code] = root.char
    #         return
    #
    #     self.make_codes_helper(root.left, current_code + "0")
    #     self.make_codes_helper(root.right, current_code + "1")
    #
    # def make_codes(self):
    #     root = heapq.heappop(self.heap)
    #     current_code = ""
    #     self.make_codes_helper(root, current_code)

    # For now, let's be simple about it and just have a dictionary
    byte_strings = defaultdict(str)

    def traverse_and_label(tree, current_string):
        if isinstance(tree, Branch):
            print("Current tree is a branch, current_string is", current_string)
            traverse_and_label(tree.left, current_string + "0")
            traverse_and_label(tree.right, current_string + "1")
        elif isinstance(tree, Leaf):
            print("Current tree is a leaf, current_string is", current_string)
            byte_strings[tree.byte] = current_string

    traverse_and_label(heap.pop().tree, "")
    print(byte_strings)


    # Do a depth first search and assign a string to each byte

    # Generate a list of empty strings, where the i-th element is the
    # encoding string for the i-th element in occurring_bytes
    # byte_strings = [""] * num_unique_bytes

    #
    # working_string = ""
    # top_tree = heap.pop().tree
    # working_tree = top_tree
    # read_vertices = []
    # while True:
    #     if isinstance(working_tree, Leaf):
    #         working_string =
    #
    #
    #     break
    # print("\ntop_tree:", top_tree)


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
