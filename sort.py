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
                                                    "\ni.e. 3 1 2 -4 -5 -6 7 8. ", nargs="+")
cli_parser.add_argument("-i", "--identity", help="space separated identity permutation, " +
                                                 "\ni.e. 1 2 3 4 5 6 7 8. \nThis argument is ignored if " +
                                                 "-p/--permutation is not set.", nargs="+")
cli_parser.add_argument("-t", "--tabular", action="store_true", help="switches output to tabular")
args = cli_parser.parse_args()

permutation = []
identity = []

# Either take the input permutation, generate a random permutation, or default
# to a permutation containing 37 elements in case neither -p nor -r are set.
if args.permutation:
    permutation = [int(x) for x in args.permutation]
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
    identity = [int(x) for x in args.identity]

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

# Initial output for tabular and verbose
if args.tabular:
    print("Permutation_k" + "\t" + "TDRL/iTDRL" + "\t" + "γ_k")

    if args.identity:
        # Output relabeled permutation
        pprint_perm(composition(identity, permutation), endl=False)
        print("\t", end="")
    else:
        pprint_perm(permutation, endl=False)
        print("\t", end="")

else:
    # Verbose output for input permutation
    print()
    print()

    print("Distance: " + str(dist) + " TDRL/iTDRL")
    print("----------------------")

    print()
    print("Permutation_" + str(dist) + ": ", end="")
    pprint_perm(permutation)

    print("MISC-Encoding: ", end="")
    pprint_misc_enc(misc_dec, subseq_map, len(pattern[1]))

    print("Pattern      : ", end="")
    print(pattern[1])

    if args.identity:

        # Since we set permutation = identity^-1 * permutation at the beginning,
        # we relabel by identity * permutation.
        print("Permutation_" + str(dist) + ": ", end="")
        pprint_perm(composition(identity, permutation), endl=False)
        print(" (relabeled)")

        print("MISC-Encoding: ", end="")
        print("".join([_[0] for _ in get_misc_dec(composition(identity, permutation))]))

# Sorting the identity into permutation
while dist != 0:

    # Compute the transformation T(permutation, pattern);
    # trns = (permutation, pattern, operation, L, R)
    trns = transformation(permutation, pattern, misc_dec, subseq_map)
    dist = dist - 1

    # assign permutation and misc_dec for next transformation
    permutation = trns[0]
    misc_dec = get_misc_dec(permutation)

    # Derive the next pattern
    if dist != 0:
        pat = trns[1]
        first = pat[0]
        last = pat[-1]
        mid = pat[int(len(pat) / 2)]

        # Derive the type of the next pattern by examining the characters at the beginning, the middle, and end.
        if first == "n" and last == "p" and mid == "p":
            pattern = ("liTDRL", pat)
        elif first == "p" and last == "n" and mid == "n":
            pattern = ("riTDRL", pat)
        else:
            pattern = ("TDRL", pat)

    # Get next subsequence mapping between misc_dec and pattern
    subseq_map = subseq_mapping(misc_dec, pattern[1])


    # Tabular Output.
    if args.tabular:

        if args.identity:
            # L and R are concatenated so that we can relabel them by identity * LR
            l_perm = [int(_) for _ in trns[3].strip().split(" ")]
            r_perm = [int(_) for _ in trns[4].strip().split(" ")]
            comp = composition(identity, l_perm + r_perm)
            left = comp[0:len(l_perm)]
            right = comp[len(l_perm):len(comp)]

            print(trns[2] + "\t" + "( " + stringify(left) + " | " + stringify(right) + " )")

            pprint_perm(composition(identity, trns[0]), endl=False)
            print("\t", end="")
        else:
            print(trns[2] + "\t" + "( " + trns[3] + " | " + trns[4] + " )")
            pprint_perm(permutation, endl=False)
            print("\t", end="")

    # Verbose Output.
    else:

        # Outputs the last part of a verbose output cell for permutation_k+1
        # i.e. the TDRL/iTDLR γ_k+1 which creates permutation_k+1 from current permutation_k
        print()

        # Outputs TDRL/iTDRL : (L|R)
        print(trns[2] + " γ_" + str(dist + 1) + ": " + "( " + trns[3] + " | " + trns[4] + " )")

        if args.identity:
            # L and R are concatenated so that we can relabel them by identity * LR
            l_perm = [int(_) for _ in trns[3].strip().split(" ")]
            r_perm = [int(_) for _ in trns[4].strip().split(" ")]
            comp = composition(identity, l_perm+r_perm)
            left = comp[0:len(l_perm)]
            right = comp[len(l_perm):len(comp)]

            # Outputs TDRL/iTDRL : (L|R) for relabeled L and R
            print( trns[2] + " γ_" + str(dist + 1) + ": " +
                  "( " + stringify(left) + " | " + stringify(right) + " )" + " (relabeled) ")

        print("Permutation_" + str(dist + 1) + " = " + "γ_" + str(dist + 1) + " * " + "Permutation_" + str(dist))
        print()
        print("------------------------------------------")

        # Output for permutation_k
        print()
        print("Permutation_" + str(dist) + ": ", end="")
        pprint_perm(permutation)

        print("MISC-Encoding: ", end="")
        pprint_misc_enc(misc_dec, subseq_map, len(trns[1]))

        print("Pattern      : ", end="")
        print(trns[1])

        # For the case that a different identity is specified, we relabel the output back to the original permutations.
        if args.identity:

            # Since we set permutation = identity^-1 * permutation at the beginning,
            # we relabel by identity * permutation.
            print("Permutation_" + str(dist) + ": ", end="")
            pprint_perm(composition(identity, trns[0]),endl=False)
            print(" (relabeled)")

            # We recompute the misc-decomposition of the relabeled permutation
            print("MISC-Encoding: ", end="")
            print("".join([_[0] for _ in get_misc_dec(composition(identity, trns[0]))]))

# Fill last line of table.
if args.tabular:
    print("\t\t")

# Print last separator and runtime.
else:
    print()
    print("------------------------------------------")
    t2 = time.time()
    print("Sorting Scenario computed in " + str(t2 - t1) + "s.")
