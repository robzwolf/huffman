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

    @staticmethod
    def label_len(bl):
        return len(bl.label)

    @staticmethod
    def get_byte(bl):
        return bl.byte

    def __repr__(self):
        # return "ByteLabel(byte={}, label=bitstring:{})".format(self.byte,
        #                                                        bin(self.label)[2:]
        #                                                        if self.label is not None else "None")
        return "ByteLabel(byte={}, label=bitstring:\"{}\")".format(self.byte,
                                                                   self.label if self.label is not None else "None")


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
        # self.byte_labels = sorted(self.byte_labels, key=lambda x: len(bin(x.label)))
        self.byte_labels = sorted(self.byte_labels, key=lambda x: len(x.label))

    def __repr__(self):
        return_string = ""
        for bl in self.byte_labels:
            return_string += "\t{}\n".format(bl)
        return return_string


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

# def bitstring_to_block(bitstring):
#     """
#     Takes any bitstring, e.g. 00110, and converts it to an 8-character bit string, e.g. 0000010.
#     :param bitstring:
#     :return:
#     """


def encode(filename):
    """
    Encodes a file using Huffman coding.
    :type filename: str
    :param filename: The file to encode.
    """

    print("Encoding:", filename)

    # Start time
    t0 = time()

    # Initialise the frequencies list, where the i-th element represents
    # the number of occurrences of the byte represented by i
    freqs = [0] * 256

    # Read the file byte by byte
    with open(filename, "rb") as f:
        try:
            file_contents = f.read()
        except IOError:
            print("Error reading file:", filename)
            sys.exit(1)

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
            # current_label <<= 1

            # Traverse the left tree and append label '0'
            traverse_and_label(tree.left, current_label + "0")

            # Traverse the right tree and append label '1'
            traverse_and_label(tree.right, current_label + "1")

        elif isinstance(tree, Leaf):
            byte_labels.set_byte(tree.byte, current_label)

    traverse_and_label(heap.pop().tree, "")

    # Sort the byte labels by label length
    byte_labels.sort_by_label_len()

    # print(byte_labels)

    # Replace existing codes with new ones, as per canonical Huffman code algorithm
    latest_num = -1
    # Iterate through every occurring byte
    for i in range(num_unique_bytes):
        # Retrieve the current byte_label element
        working_byte_label = byte_labels.byte_labels[i]

        # Increment the codeword by 1
        new_codeword = bin(latest_num + 1)[2:]

        # Append 0 to the codeword until it has the same length as the old codeword
        # while len(bin(new_codeword)[2:]) < len(bin(working_byte_label.label)[2:]):
        new_codeword += (len(working_byte_label.label) - len(new_codeword)) * "0"
        # while len(new_codeword) < len(working_byte_label.label):
        #     new_codeword += "0"

        # Update our counter for the codeword
        latest_num = int(new_codeword, 2)

        # Assign the new codeword to the byte_label
        working_byte_label.label = new_codeword

    # Convert our custom ByteLabels object to a normal dictionary (it's faster)
    codewords = defaultdict(str)
    for byte in byte_labels.byte_labels:
        codewords[byte.byte] = byte.label
    # print(codewords)

    # Convert the input file to one long compressed bitstring of 1s and 0s
    # using "".join because it's much faster than lots of string concatenation
    # encoded_file_contents = "".join([bin(codewords[byte])[2:] for byte in file_contents])
    encoded_file_contents = "".join([codewords[byte] for byte in file_contents])

    # Calculate the necessary number of padding bits (we need to write a
    # multiple of 8 bits to file as we can only write bytes to file)
    number_padding_bits = 8 - (len(encoded_file_contents) % 8)
    b_number_padding_bits = int_to_byte_string(number_padding_bits)

    # Use Method 1 if num_unique_bytes is greater than 128
    # Use Method 2 if num_unique_bytes is less than or equal to 128
    if num_unique_bytes >= 129:
        # Use Method 1
        massive_bitstring = ""
    else:
        # Use Method 2

        # Prepare the byte string that describes the number of unique bytes
        dict_num_bytes = int_to_byte_string(num_unique_bytes)

        # Prepare the codeword lengths byte string
        # dict_label_lengths = "".join([int_to_byte_string(len(bin(byte_label.label)[2:]))
        #                               for byte_label in byte_labels.byte_labels])
        dict_label_lengths = "".join([int_to_byte_string(len(byte_label.label))
                                      for byte_label in byte_labels.byte_labels])

        # Prepare the 'list of occurring bytes' byte string
        dict_occurring_bytes = "".join([int_to_byte_string(byte)
                                        for byte in codewords.keys()])

        # Whack everything into one massive string of bits
        massive_bitstring = "".join([b_number_padding_bits,
                                     dict_num_bytes,
                                     dict_label_lengths,
                                     dict_occurring_bytes,
                                     encoded_file_contents,
                                     "0" * number_padding_bits])

    # Convert the string of 1s and 0s to a list of bytes
    file_output = [int(massive_bitstring[index * 8: index * 8 + 8], base=2)
                   for index in range(int(len(massive_bitstring) / 8))]

    # Derive new .hc filename
    output_filename = filename[:filename.rfind(".")] + ".hc"

    # Read the file byte by byte
    with open(output_filename, "wb") as f:
        f.write(bytes(file_output))

    # End time
    t1 = time()

    print("Wrote encoded file to", output_filename)
    print("Process took " + str(round(t1 - t0, 5)) + " seconds")


def decode(filename):
    """
        Decodes a file that has been encoded using Huffman coding.
        :type filename: str
        :param filename: The file to decode
        :return:
        """

    # Read the file byte by byte
    with open(filename, "rb") as f:
        try:
            file_contents = f.read()
        except IOError:
            print("Error reading file:", filename)
            sys.exit(1)
    print(file_contents)

    # First byte is the number of padding zeros
    number_padding_zeros = int(file_contents[0])
    print("number_padding_zeros", number_padding_zeros)

    # Second byte is the number of occurring bytes
    number_unique_bytes = file_contents[1]
    print("number_unique_bytes", number_unique_bytes)

    # Count the codeword bit lengths for those number_unique_bytes bytes, read the occurring bytes, and
    # associate them with their lengths in a dictionary
    label_length_dict = defaultdict(int)
    for i in range(number_unique_bytes):
        bit_length = file_contents[i+2]
        occurring_byte = file_contents[i+number_unique_bytes+2]
        label_length_dict[occurring_byte] = str(bit_length)
    print(label_length_dict)

    # Read the remaining bytes
    byte_encoded_file_contents = file_contents[2+2*number_unique_bytes:]
    print(byte_encoded_file_contents)

    # Convert the remaining bytes (except the last one) to bits
    encoded_file_contents = "".join([int_to_byte_string(byte_encoded_file_contents[i])
                                     for i in range(len(byte_encoded_file_contents)-1)])

    # Append the last byte after we have removed the padding zeros
    encoded_file_contents += int_to_byte_string(byte_encoded_file_contents[
                                                    len(byte_encoded_file_contents)-1])[:8-number_padding_zeros]
    print(encoded_file_contents)

    # Hackily store the length of the byte_label in the label field
    byte_labels = ByteLabels([ByteLabel(byte, label_length_dict[byte]) for byte in label_length_dict])
    byte_labels.sort_by_label_len()
    print(byte_labels)

    # Replace existing codes with new ones, as per canonical Huffman code algorithm
    latest_num = -1
    # Iterate through every occurring byte
    for i in range(number_unique_bytes):
        # Retrieve the current byte_label element
        working_byte_label = byte_labels.byte_labels[i]

        # Increment the codeword by 1
        new_codeword = bin(latest_num + 1)[2:]

        # Append 0 to the codeword until it has the same length as the old codeword
        # while len(bin(new_codeword)[2:]) < len(bin(working_byte_label.label)[2:]):
        new_codeword += (int(working_byte_label.label) - len(new_codeword)) * "0"
        # while len(new_codeword) < len(working_byte_label.label):
        #     new_codeword += "0"

        # Update our counter for the codeword
        latest_num = int(new_codeword, 2)

        # Assign the new codeword to the byte_label
        working_byte_label.label = new_codeword

    # Convert our custom ByteLabels object to a normal dictionary (it's faster)
    codewords = defaultdict(int)
    for byte in byte_labels.byte_labels:
        codewords[byte.byte] = byte.label
    print(codewords)

# Parse initial arguments and react appropriately
if len(sys.argv) != 3:
    print("Invalid argument format. Use -e or -d, followed by a filename.")
    sys.exit(1)
else:
    mode = sys.argv[1]
    filename = sys.argv[2]
    if mode == "-e":
        encode(filename)
    elif mode == "-d":
        decode(filename)
    else:
        print("Invalid mode, should be -e or -d")
        sys.exit(1)
