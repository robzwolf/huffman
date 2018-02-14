import huffman

for i in range(1, 9):
    print("\nCalling encode(timing_{}.txt)...".format(i))
    huffman.encode("timing_{}.txt".format(i))