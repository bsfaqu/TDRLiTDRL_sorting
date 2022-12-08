from lib import *
import argparse
from math import log2, ceil
from numpy.random import permutation as rand_perm
import random
import time

cli_parser = argparse.ArgumentParser()

cli_parser.add_argument("-r", "--random", type=int, help="randomly generate a permutation;" +
                                                         "\nspecify length as argument.")
cli_parser.add_argument("-p", "--permutation", help="space separated target permutation, " +
                                                    "\ni.e. 3 1 2 -4 -5 -6 7 8. ")
cli_parser.add_argument("-i", "--identity", help="space separated identity permutation, " +
                                                 "\ni.e. 1 2 3 4 5 6 7 8. \nThis argument is ignored if " +
                                                 "-p/--permutation is not set.")
args = cli_parser.parse_args()

permutation = []

# Either take the input permutation, generate a random permutation, or default
# to a permutation containing 37 elements in case neither -p nor -r are set.
if args.permutation:
    split = args.permutation.split(" ")
    permutation = [int(x) for x in split]
elif args.random:
    permutation = list(rand_perm(args.random))

    # we randomly assign each element a +/- with 50/50 probability
    for i in range(0, len(permutation)):
        permutation[i] += 1
        r = random.randint(0, 10)
        if r >= 5:
            permutation[i] *= -1
else:
    permutation = list(rand_perm(37))
    for i in range(0, len(permutation)):
        permutation[i] += 1
        r = random.randint(0, 10)
        if r >= 5:
            permutation[i] *= -1

# If an identity permutation is specified, we alter the input permutation such
# that the output is for optimally sorting identity -> permutation
if args.identity:
    if args.permutation:
        split = args.identity.split(" ")
        identity = [int(x) for x in split]

        # TODO: MAKE INVERSION WORK FOR NEGATIVE ELEMENTS

        # To sort identity to pi we apply the inverse of identity to pi
        # (and the identity itself).
        inv_identity = inverse(identity)
        permutation = composition(inv_identity, permutation)

t1 = time.time()

# The following code follows the pseudocode of Algorithm 1 closely.
misc_dec = get_misc_dec(permutation)
k = ceil(log2(len(misc_dec)))
patterns = get_patterns(k)
subseq_map = {}

dist = -1
pattern = ""

# for the case that d(identity,permutation) is k
for p in patterns:
    subseq_map = subseq_mapping(misc_dec, p[1])
    if len(subseq_map) == 0:
        continue
    else:
        dist = k
        pattern = p
        break

# for the case that d(identity,permutation) is k+1
if dist == -1:
    dist = k + 1
    patterns = get_patterns(dist)
    for p in patterns:
        subseq_map = subseq_mapping(misc_dec, p[1])
        if len(subseq_map) == 0:
            continue
        else:
            pattern = p
            break

print()
print()
print("Permutation_" + str(dist) + ": ", end="")
pprint_perm(permutation)
print("MISC-Encoding: ", end="")
# print("".join([x[0] for x in misc_dec]))
pprint_misc_enc(misc_dec,subseq_map,len(pattern[1]))
print("Pattern      : ", end="")
print(pattern[1])
print("Distance: " + str(dist) + " TDRL/iTDRL")
print()
print("------------------------------------------")

while dist != 0:
    misc_dec = get_misc_dec(permutation)
    subseq_map = subseq_mapping(misc_dec, pattern[1])
    trns = transformation(permutation, pattern, misc_dec, subseq_map)
    dist = dist - 1
    permutation = trns[0]
    print()
    print("Permutation_" + str(dist) + ": ", end="")
    pprint_perm(trns[0])
    print("MISC-Encoding: ", end="")
    misc_dec = get_misc_dec(permutation)
    subseq_map = subseq_mapping(misc_dec, pattern[1])
    pprint_misc_enc(misc_dec, subseq_map, len(trns[1]))
    # print("".join([x[0] for x in misc_dec]))
    print("Pattern      : ", end="")
    print(trns[1])
    print(trns[2] + " γ_" + str(dist+1) + ": " + "( " + trns[3] + " | " + trns[4] + " )")
    print("Permutation_" + str(dist+1) + " = " + "γ_" + str(dist+1) + " ∘ " + "Permutation_" + str(dist))
    print("Distance: " + str(dist) + " TDRL/iTDRL")
    print()
    print("------------------------------------------")
    if dist != 0:
        pat = trns[1]
        first = pat[0]
        last = pat[-1]
        mid = pat[int(len(pat) / 2)]

        # Derive the type of the next pattern.
        if first == "n" and last == "p" and mid == "p":
            pattern = ("liTDRL", pat)
        elif first == "p" and last == "n" and mid == "n":
            pattern = ("riTDRL", pat)
        else:
            pattern = ("TDRL", pat)

# TODO: IMPLEMENT MAPPING BACK OUTPUT IN CASE THE IDENTITY IS SPECIFIED.

t2 = time.time()
print("Sorting Scenario computed in " + str(t2 - t1) + "s.")
