from time import time

t0 = time()
output_a = ""
for i in range(10000000):
    output_a += str(i)

t1 = time()
print("Took", t1-t0, "seconds to do string concatenation")



t2 = time()
output_b = []
for j in range(10000000):
    output_b.append(str(j))
output_b_str = "".join(output_b)
t3 = time()
print("Took", t3-t2, "seconds to do string joining")

# t0 = time()
# for i in range(10000000):
#     new_codeword = "000110"
#     new_codeword += 5 * "0"
# t1 = time()
# print("Took", t1-t0, "seconds to do += operator")
#
#
# t2 = time()
# for j in range(10000000):
#     new_codeword = "000110"
#     new_codeword = "".join([new_codeword, "".join(["0" for j in range(5)])])
# t3 = time()
# print("Took", t3-t2, "seconds to do .join within .join")