# Read the file and count frequencies of characters
from collections import defaultdict

# Initialise the frequencies dictionary
freqs = defaultdict(int)

filename = "lorem_ipsum.txt"
# filename = "chinese_poem.txt"
# filename = "emoji.txt"
with open(filename) as f:
    while True:
        c = f.read(1)
        if not c:
            # print("End of file")
            break
        else:
            if c not in freqs:
                freqs[c] = 1
            else:
                freqs[c] += 1
            # print("freqs[" + c + "] =", freqs[c])
        # print("Read a character:", c)

print("freqs dictionary has the following frequencies:")
for char in freqs:
    print(char, ":", freqs[char])

print(freqs)