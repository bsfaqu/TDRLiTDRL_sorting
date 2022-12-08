import json


def get_misc_dec(permutation):
    """
    Computes and returns the misc-decomposition, and misc-encoding of a permutation

    Passes the permutation exactly once and returns a list of tuples
    which contains the border indices, and the type, of each misc-substring
    of a permutation.

    Parameters
    ----------
    permutation: list
        List of n potentially negative elements where
        every element occurs exactly once

    Returns
    -------
    list
        Contains tuples which contain "(c_i,start,end)" where c_i encodes
        the signage of each misc-substring S_i, i.e. p/n. The list is ordered
        by position of the misc-substrings in the input permutation. List indices
        can be immediately sliced, hence start is the first element which is in
        the corresponding misc-substring, and end is the first element which
        is not contained in the substring anymore, or len(permutation).
    """

    misc_dec = []

    # Beginning of current misc
    last_boundary = 0

    # Last element seen
    last_element = permutation[0]

    for i in range(1, len(permutation)):

        # Check if the border of a new misc is reached
        if last_element > permutation[i] or last_element * permutation[i] < 0 or i == len(permutation) - 1:

            # Decide whether it's a positive, or a negative misc
            if last_element > 0:
                misc_dec += [("p", last_boundary, i)]
                last_boundary = i
            else:
                misc_dec += [("n", last_boundary, i)]
                last_boundary = i

        # Check whether the last element constitutes an individual misc
        if i == len(permutation) - 1:
            if last_element > permutation[i] or last_element * permutation[i] < 0:
                if permutation[i] > 0:
                    misc_dec += [("p", last_boundary, i)]
                else:
                    misc_dec += [("n", last_boundary, i)]

        # Remember last seen element
        last_element = permutation[i]

    # adjust last index for easier slicing in transformation
    misc_dec[-1] = (misc_dec[-1][0], misc_dec[-1][1], misc_dec[-1][2] + 1)

    return misc_dec


def get_patterns(k):
    """
    Computes all patterns of length 2^k.

    Checks whether a file containing patterns of length 2^k exist, and if it
    doesn't, computes all patterns up to length 2^k. A list containing all
    patterns length 2^k is returned.

    Parameters
    ----------
    k: int
        Length of patterns to be calculated;
        patterns of length 2^k are considered.

    Returns
    -------
    list
        Contains strings of all patterns of length 2^k. Is ordered by the
        type of patterns, i.e. first the pattern that satisfies pattern Definition (i),
        ... , then patterns that satisfy pattern Definition (iv).
    """

    # TODO: RECURSIVELY GENERATE PATTERNS FOR k-1,...,1 IF PATTERNS FOR k ARE
    # NOT AVAILABLE. --> GENERATE FILES FOR MISSING PATTERNS
    if k == 0:
        return []

    # Test whether a file containing all patterns of length 2^k exists
    try:
        with open("pattern_" + str(k) + ".txt", "r") as patfile:
            patterns = json.load(patfile)
            return patterns
    except FileNotFoundError:
        print("Patterns for k=" + str(k) + " not available.")
        print("Pattern file pattern_" + str(k) + " will be created.")

    patterns = {}

    # Generate all patterns up to length 2^k
    for i in range(1, k + 1):

        patterns[i] = []

        # length of pattern, middle of pattern
        l_full = 2 ** i
        l_half = int(l_full / 2)

        pos, negpos, posneg, reppat = "", "", "", ""

        # Pattern Definition (i)
        pos = pos.join(["p" for _ in range(0, l_full)])

        # Pattern Definition (iii)
        negpos += "".join(["n" for _ in range(0, l_half)])
        negpos += "".join(["p" for _ in range(0, l_half)])

        # Pattern Definition (ii)
        posneg += "".join(["p" for _ in range(0, l_half)])
        posneg += "".join(["n" for _ in range(0, l_half)])

        patterns[i] += [("TDRL", pos), ("riTDRL", posneg), ("liTDRL", negpos)]

        # Pattern Definition (iv)
        if i == 1:
            continue
        else:
            for pat in patterns[i - 1]:
                if pat[1][0] == "p" and pat[1][-1] == "p":
                    continue
                reppat += pat[1]
                reppat += pat[1]
                patterns[i] += [("TDRL", reppat)]
                reppat = ""

    # Save patterns of length 2^k to file pattern_k.txt
    with open("pattern_" + str(k) + ".txt", "w+") as patfile:
        json.dump(patterns[k], patfile)

    return patterns[k]


def subseq_mapping(misc_dec, pattern):
    """
    Returns a subsequence mapping between a misc-decomposition and a pattern.

    This function implements a greedy approach to acquire a subsequence mapping
    between a misc-decomposition, or misc-encoding, and a pattern. Returns an
    empty dictionary if no such mapping exists.

    Parameters
    ----------
    misc_dec: list
        List of tuples which correspond to the misc-substrings of a permutation.
        It is expected that the first value of each tuple contains the corresponding
        character of a permutations misc-encoding, i.e. p/n. Tuples encoding the
        misc-substrings of a permutation have to be ordered by their occurrence
        in the permutation.
    pattern:
        String representing a pattern.

    Returns
    -------
    dict
        Dict which maps characters in the pattern to the misc-decomposition. When
        no mapping can be found, i.e. the misc-encoding is not subsequence of
        pattern, an empty dictionary is returned.
    """
    mapping = {}

    # Index of last seen character in pattern
    last_index_pattern = 0

    # Pass over misc_dec once and search for the next matching character in pattern
    for i in range(0, len(misc_dec)):

        # Iteration starts from the last checked character in pattern.
        for j in range(last_index_pattern, len(pattern)):
            if misc_dec[i][0] == pattern[j]:
                mapping[j] = i
                last_index_pattern = j + 1
                break

    # Check if subsequence mapping is incomplete, i.e. misc_dec is not
    # subsequence of pattern.
    if len(mapping) != len(misc_dec):
        return {}

    return mapping


def oplus(misc_1, misc_2):
    """
    Implements the merge and lexicographically sort function

    This function merges misc_1 and misc_2 such that the resulting string is
    ordered ascendingly, and misc_1 and misc_2 are subsequences of the output
    string. Take note that misc_1 and misc_2 have to be misc-substrings in order
    for the output string to be a misc-substring.

    Parameters
    ----------
    misc_1: list
        First misc-substrings
    misc_2: list
        Second misc-substring
    Returns
    -------
    list
        merged misc-substring which is ordered ascendingly and contains all
        elements from misc_1 and misc_2
    """

    merge_misc = []

    # Stores the current position in misc_1 and misc_2
    index_1 = 0
    index_2 = 0

    # Merges misc_1 and misc_2 similarly to the mergesort merge.
    while len(merge_misc) != len(misc_1) + len(misc_2):

        # End of misc_1 reached.
        if index_1 >= len(misc_1):
            merge_misc += [misc_2[index_2]]
            index_2 += 1

        # End of misc_2 reached.
        elif index_2 >= len(misc_2):
            merge_misc += [misc_1[index_1]]
            index_1 += 1

        # Next element is in misc_1
        elif misc_1[index_1] < misc_2[index_2]:
            merge_misc += [misc_1[index_1]]
            index_1 += 1

        # Last case - next element is in misc_2
        else:
            merge_misc += [misc_2[index_2]]
            index_2 += 1

    return merge_misc


def inverse(perm):
    """
    Implements the inversion of a permutations.



    Parameters
    ----------
    perm: list
        List of integers which represents a string of integers, or a permutation

    Returns
    -------
    list
        Inverse of perm.
    """
    inv_perm = [0 for _ in perm]

    for x in range(0, len(perm)):
        if(perm[x]>0):
            inv_perm[perm[x] - 1] = x + 1
        else:
            inv_perm[-perm[x] - 1] = -x - 1
    return inv_perm


def composition(p1, p2):
    """
    Implements the composition of two permutations.



    Parameters
    ----------
    p1: list
        List of integers which represents a string of integers, or a permutation
    p2: list
        List of integers which represents a string of integers, or a permutation

    Returns
    -------
    list
        Composition of p1 * p2.
    """
    comp_perm = [0 for _ in p1]
    for x in range(0, len(p2)):
        if 0 < p2[x]:
            comp_perm[x] = p1[p2[x] - 1]
        else:
            comp_perm[x] = -p1[-p2[x] - 1]
    return comp_perm


def reverse(permutation):
    """
    Implements the reversion operation (for permutations or strings of integers)

    Returns the input list in reversed order, and with the signage of every
    element switched (i.e. + -> - ; - -> +). Input strings have to be represented
    by a list

    Parameters
    ----------
    permutation: list
        List of integers which represents a string of integers, or a permutation

    Returns
    -------
    list
        List in which the order and signage of the input list is reversed.
    """
    return [-1 * permutation[-i] for i in range(1, len(permutation) + 1)]


def stringify(permutation):
    """
    Returns a string representation for a list (of integers, or any datatype
    which possesses a str() representation)

    Every element in the returned string is separated by a space.

    Parameters
    ----------
    permutation: list
        List which should be stringifies, i.e., which shall be represented
        as a space-separated string.

    Returns
    -------
    str
        String representation of l.
    """
    return "".join([str(x) + " " for x in permutation])


# noinspection PyPep8Naming
def transformation(permutation, pattern, misc_dec, misc_mapping):
    """
    Implements transformation T.

    This function implements the transformation T and decides which case of the
    Definition of the transformation should be invoked depending on the pattern
    supplied. A tuple containing all relevant information of the permutation
    which is obtained after applying T is returned.

    Parameters
    ----------
    permutation: list
        List representation of a permutation of the elements [1:n] which contains
        every element exactly once.
    pattern: tuple
        A tuple that contains the type of pattern, i.e.
        - TDRL for patterns satisfying pattern Definition (i) or (iv)
        - riTDRL for patterns satisfying pattern Definition (ii)
        - liTDRL for patterns satisfying pattern Definition (iii)
        and the string that represents the pattern.
    misc_dec: list
        A List of tuples that represent the misc-decomposition and misc-encoding of
        permutation. Can be acquired via get_misc_dec(permutation).
    misc_mapping:
        Dictionary which maps each character in pattern[1] to a character in the
        misc-encoding of permutation.
    Returns
    -------
    tuple
        Tuple which represents the permutation after the application of T.
        Additional information like the next pattern, and the TDRL/iTDRL which
        inverts T is included as well. The tuple has the shape
        (permutation_after_T, nextpattern, TDRL/iTDRL, L, R).
        permutation_after_T is the permutation after the application of T.
        nextpattern is the pattern the misc-dec of permutation_after_T is subsequence of.
        TDRL/iTDRL is a string which encodes the operation which reverses T, i.e.
        "TDRL", "liTDRL", or "riTDRL"
        L, R is the exact bipartition for TDRL/iTDRL which, applied to the
        permutation_after_T yields the input permutation.
    """

    # Contains the permutation after application of T
    taus = []
    newpat = ""


    L = ""
    R = ""

    # Stores the length, and the middle of pattern
    l_full = len(pattern[1])
    l_half = int(l_full / 2)

    # T is reversible by a TDRL, or is the inverse of a TDRL
    if pattern[0] == "TDRL":

        # Derive pattern T(permutation,pattern) is subsequence of.
        # For TDRL, this is the first half of the input pattern
        newpat = "".join(pattern[1][0:l_half])

        # The taus are sequentially created in this loop and appended to the
        # output permutation.
        for i in range(0, l_half):
            try:
                index_left = misc_dec[misc_mapping[i]][1]
                index_right = misc_dec[misc_mapping[i]][2]
                misc_1 = permutation[index_left:index_right]
            except KeyError:
                misc_1 = []
            try:
                index_left = misc_dec[misc_mapping[l_half + i]][1]
                index_right = misc_dec[misc_mapping[l_half + i]][2]
                misc_2 = permutation[index_left:index_right]
            except KeyError:
                misc_2 = []

            # A string representation for L and R is created sequentially.
            L += stringify(misc_1)
            R += stringify(misc_2)

            # The sorted misc-substrings are appended to the output permutation.
            taus += oplus(misc_1, misc_2)

    # T is reversible by an liTDRL, hence is the inverse of an liTDRL
    elif pattern[0] == "liTDRL":

        # Derive pattern T(permutation,pattern) is subsequence of.
        # For liTDRL this is the last half of the pattern.
        newpat = "".join(pattern[1][l_half:len(pattern[1])])

        # The taus are sequentially created in this loop and appended to the
        # output permutation.
        for i in range(0, l_half):
            try:
                index_left = misc_dec[misc_mapping[l_half - i - 1]][1]
                index_right = misc_dec[misc_mapping[l_half - i - 1]][2]
                misc_1 = permutation[index_left:index_right]
            except KeyError:
                misc_1 = []
            try:
                index_left = misc_dec[misc_mapping[l_half + i]][1]
                index_right = misc_dec[misc_mapping[l_half + i]][2]
                misc_2 = permutation[index_left:index_right]
            except KeyError:
                misc_2 = []

            # A string representation of L and R is created sequentially.
            # According to the definition of T, misc_1 is reversed.
            L += stringify(reverse(misc_1))
            R += stringify(misc_2)

            # The sorted misc-substrings are appended to the output permutation.
            # According to the definition of T, misc_1 is reversed.
            taus += oplus(reverse(misc_1), misc_2)

    # T is reversible by an riTDRL, hence is the inverse of an riTDRL
    elif pattern[0] == "riTDRL":

        # Derive pattern T(permutation,pattern) is subsequence of.
        # For riTDRL, this is the first half of the input pattern
        newpat = "".join(pattern[1][0:l_half])
        for i in range(0, l_half):
            try:
                index_left = misc_dec[misc_mapping[i]][1]
                index_right = misc_dec[misc_mapping[i]][2]
                misc_1 = permutation[index_left:index_right]
            except KeyError:
                misc_1 = []
            try:
                index_left = misc_dec[misc_mapping[l_full - i - 1]][1]
                index_right = misc_dec[misc_mapping[l_full - i - 1]][2]
                misc_2 = permutation[index_left:index_right]
            except KeyError:
                misc_2 = []

            # A string representation of L and R is created sequentially.
            # According to the definition of T, misc_2 is reversed.
            L += stringify(misc_1)
            R += stringify(reverse(misc_2))

            # The sorted misc-substrings are appended to the output permutation.
            # According to the definition of T, misc_1 is reversed.
            taus += oplus(misc_1, reverse(misc_2))

    return taus, newpat, pattern[0], L, R


def pprint_perm(permutation, endl=True):
    """
    Prints the canonical one-line representation for a permutation represented
    by a list.



    Parameters
    ----------
    permutation: list
        List of n unique elements which represent a permutation

    Returns
    -------

    """
    if(endl):
        print("( " + "".join([str(x) + " " for x in permutation])[0:-1] + " )")
    else:
        print("( " + "".join([str(x) + " " for x in permutation])[0:-1] + " )", end="")

def pprint_misc_enc(misc_encoding, misc_mapping,pattern_length):
    """
    Prints a subsequence aware, i.e. aligned misc-encoding.

    The alignment, i.e. subsequence matching between a misc-encoding and a pattern is printed
    such that pattern and misc-encoding can be visualized together e.g.
    permutation: p nnp n
    pattern:     ppnnppnn

    Parameters
    ----------
    pattern: str
        String that represents a pattern
    misc_dec: list
        A List of tuples that represent the misc-decomposition and misc-encoding of
        permutation. Can be acquired via get_misc_dec(permutation).
    misc_mapping:
        Dictionary which maps each character in pattern[1] to a character in the
        misc-encoding of permutation.
    pattern_length:
        Length of paramter pattern.
    Returns
    -------
    str
        Canonical one-line representation of the permutation.
    """
    print_string = ""
    keys = misc_mapping.keys()
    for i in range(pattern_length):
        if i in keys:
            print_string += misc_encoding[misc_mapping[i]][0]
        else:
            print_string += " "
    print(print_string)