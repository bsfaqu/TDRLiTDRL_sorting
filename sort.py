from lib import *
import argparse

cli_parser=argparse.ArgumentParser()

cli_parser.add_argument("-r","--random",type=int, help="randomly generate a permutation;" +
                        "\nspecify length as argument.")
cli_parser.add_argument("-p","--permutation",help="space seperated target permutation, " +
                         "\ni.e. 3 1 2 -4 -5 -6 7 8")
cli_parser.add_argument("-i","--identity",help="space seperated identity permutation, " +
                         "\ni.e. 1 2 3 4 5 6 7 8")
cli_parser.parse_args()
input()

# permutation = [-6,-5,-7,-9,-8,4,3,2,1]
permutation=list(rand_perm(100))
for i in range(0,len(permutation)):
    permutation[i]+=1
    r = random.randint(0,10)
    if(r>=2):
        permutation[i]*=-1
t1=time.time()
misc_dec=get_misc_dec(permutation)
k = ceil(log2(len(misc_dec)))
patterns=get_patterns(k)
subseq_map={}

dist=-1
pattern=""

for p in patterns:
    subseq_map=subseq_mapping(misc_dec,p[1])
    if(len(subseq_map)==0):
        continue
    else:
        dist=k
        pattern=p
        break
if(dist==-1):
    dist=k+1
    patterns=get_patterns(dist)
    for p in patterns:
        subseq_map=subseq_mapping(misc_dec,p[1])
        if(len(subseq_map)==0):
            continue
        else:
            pattern=p
            break

print("Input:")
pprint_perm(permutation)
print(pattern)
print("Distance: " + str(dist) + " TDRL/iTDRL")
print("*********************************************")
while(dist!=0):
    misc_dec=get_misc_dec(permutation)
    subseq_map=subseq_mapping(misc_dec,pattern[1])
    trns=transformation(permutation,pattern,misc_dec,subseq_map)
    dist=dist-1
    pprint_perm(trns[0])
    print(trns[1])
    print(trns[2] + ": " + "( " + trns[3] + " | " + trns[4] + " )")
    print("*********************************************")
    permutation=trns[0]
    if(dist!=0):
        pat=trns[1]
        first=pat[0]
        last=pat[-1]
        mid=pat[int(len(pat)/2)]
        if(first=="n" and last=="p" and mid=="p"):
            pattern=("liTDRL",pat)
        elif(first=="p" and last=="n" and mid=="n"):
            pattern=("riTDRL",pat)
        else:
            pattern=("TDRL",pat)
t2=time.time()
print("Sorting Scenario calculated in " + str(t2-t1) + "s.")
