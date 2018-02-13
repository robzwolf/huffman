from time import time
import sys
import heapq

from collections import defaultdict

import struct


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
        return "ByteLabel(byte={}, label=bitstring:{})".format(self.byte,
                                                               bin(self.label)[2:]
                                                               if self.label is not None else "None")


class ByteLabels():
    def __init__(self, byte_labels):
        self.byte_labels = byte_labels

    def set_byte(self, byte, label):
        for bl in self.byte_labels:
            if bl.byte == byte:
                bl.label = label
                return True
        return False

    def sort_by_label_len(self):
        self.byte_labels = sorted(self.byte_labels, key=lambda x: len(bin(x.label)))

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
    # the number of occurrences of the byte represented by i
    freqs = [0] * 256

    # Read the file byte by byte
    with open(filename, "rb") as f:
        file_contents = f.read()
    # print(type(file_contents))

    # Loop through every byte of file_contents and count the frequency
    for i in range(len(file_contents)):
        freqs[file_contents[i]] += 1

    # Make a list of the bytes we intend to encode
    occurring_bytes = [each_byte for each_byte in range(256) if freqs[each_byte] != 0]

    # Define the heap, initially a load of heap elements consisting of only Leaves
    heap = Heap([HeapElement(freqs[byte], Leaf(byte)) for byte in occurring_bytes])

    num_unique_bytes = len(heap)

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

    # Traverse through the tree and work out the label for each byte
    byte_labels = ByteLabels([ByteLabel(byte, None) for byte in occurring_bytes])

    def traverse_and_label(tree, current_label):
        """
        Traverse through a tree and label each leaf appropriately.
        :param tree: The tree to traverse
        :param current_label: The label so far
        """
        if isinstance(tree, Branch):
            # Append the current_label with a zero
            current_label <<= 1

            # Traverse the left tree and append label '0'
            traverse_and_label(tree.left, current_label)

            # Traverse the right tree and append label '1'
            traverse_and_label(tree.right, current_label + 1)

        elif isinstance(tree, Leaf):
            byte_labels.set_byte(tree.byte, current_label)

    traverse_and_label(heap.pop().tree, 0)

    # Sort the byte labels by label length
    byte_labels.sort_by_label_len()

    # Replace existing codes with new ones, as per canonical Huffman code algorithm
    latest_num = -1
    # Iterate through every occurring byte
    for i in range(len(occurring_bytes)):
        # Retrieve the current byte_label element
        working_byte_label = byte_labels.byte_labels[i]

        # Increment the codeword by 1
        new_codeword = latest_num + 1

        # Append 0 to the codeword until it has the same length as the old codeword
        while len(bin(new_codeword)[2:]) < len(bin(working_byte_label.label)[2:]):
            new_codeword <<= 1

        # Update our counter for the codeword
        latest_num = int(bin(new_codeword)[2:], 2)

        # Assign the new codeword to the byte_label
        working_byte_label.label = new_codeword

    # Print canonically relabelled codes
    print("\n Canonically relabelled codewords as as follows:")
    print(byte_labels)

    # Convert our custom ByteLabels object to a normal dictionary (it's faster)
    codewords = defaultdict(int)
    for byte in byte_labels.byte_labels:
        codewords[byte.byte] = byte.label

    # Convert the input file to one long compressed bitstring of 1s and 0s
    # using "".join because it's much faster than lots of string concatenation
    encoded_file_contents = "".join([bin(codewords[byte])[2:] for byte in file_contents])
    print("Length of encoded is", len(encoded_file_contents), "bits")

    def int_to_byte_string(number):
        """
        Takes any integer, e.g. 30, and converts it to an 8-character bit string, e.g. 00011110.
        Convert back by using int(byte, 2).
        :param number: The integer to convert
        :return: An 8-character string of 1s and 0s
        """
        if number > 255:
            return None
        return "0" * (8 - len(bin(number)[2:])) + bin(number)[2:]

    # Calculate the necessary number of padding bits (we need to write a
    # multiple of 8 bits to file as we can only write bytes to file)
    number_padding_bits = 8 - (len(encoded_file_contents) % 8)
    b_number_padding_bits = int_to_byte_string(number_padding_bits)
    # print("Number of padding bits is", number_padding_bits)
    # print("Number of padding bits in binary is", b_number_padding_bits)

    # Use Method 1 if num_unique_bytes is greater than 128
    # Use Method 2 if num_unique_bytes is less than or equal to 128
    # print("Number of unique bytes is", num_unique_bytes)
    if num_unique_bytes >= 129:
        # Use Method 1
        print("Planning to use Method 1")
        massive_bitstring = ""
    else:
        # Use Method 2
        print("Planning to use Method 2")

        # dict_num_bytes = "0" * (8 - len(bin(num_unique_bytes)[2:])) + str(bin(num_unique_bytes)[2:])
        dict_num_bytes = int_to_byte_string(num_unique_bytes)
        # print("dict_num_bytes is", dict_num_bytes)

        # dict_label_lengths = "".join(["0" * (8 - len(bin(len(bin(byte_label.label)[2:]))[2:]))
        #                               + bin(len(bin(byte_label.label)[2:]))[2:] + " "
        #                               for byte_label in byte_labels.byte_labels])
        dict_label_lengths = "".join([int_to_byte_string(len(bin(byte_label.label)[2:]))
                                      for byte_label in byte_labels.byte_labels])
        # print("dict_label_lengths is", dict_label_lengths)

        # dict_occurring_bytes = "".join(["0" * (8 - len(bin(byte)[2:]))
        #                                 + bin(byte)[2:] + " "
        #                                 for byte in occurring_bytes])
        dict_occurring_bytes = "".join([int_to_byte_string(byte)
                                        for byte in occurring_bytes])
        # print("dict_occurring_bytes is", dict_occurring_bytes)

        massive_bitstring = "".join([b_number_padding_bits,
                                     dict_num_bytes,
                                     dict_label_lengths,
                                     dict_occurring_bytes,
                                     encoded_file_contents,
                                     "0" * number_padding_bits])

    # Convert the string of 1s and 0s to a list of bytes
    file_output = [int(massive_bitstring[index * 8: index * 8 + 8], base=2)
                   for index in range(int(len(massive_bitstring) / 8))]

    # Now to write this to file

    # Derive new .hc filename
    output_filename = filename[:filename.rfind(".")] + ".hc"
    print("Output filename is", output_filename)

    # print("massive_bitstring is", massive_bitstring)
    # print("Spaced massive_bitstring is", "".join([massive_bitstring[x]+" " if (x+1)%8==0 else massive_bitstring[x]
    #                                               for x in range(len(massive_bitstring))]))
    print("file_output is", file_output)
    print("bytes(file_output) is", bytes(file_output))
    print("struct thing is", struct.pack("B", int(massive_bitstring)))

    # Read the file byte by byte
    with open(output_filename, "wb") as f:
        # f.write(file_output)
        # f.write(bytearray(int(i, base=16) for i in file_output))
        f.write(bytes(file_output))

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
