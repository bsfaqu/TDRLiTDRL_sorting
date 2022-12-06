import json
from math import log2,ceil
from numpy.random import permutation as rand_perm
import random
import time

def get_misc_dec(permutation):
    misc_dec=[]
    last_boundary=0
    last_element=permutation[0]
    for i in range(1,len(permutation)):
        if(last_element>permutation[i] or last_element*permutation[i]<0 or i==len(permutation)-1):
            if(last_element>0):
                misc_dec+=[("p",last_boundary,i)]
                last_boundary=i
            else:
                misc_dec+=[("n",last_boundary,i)]
                last_boundary=i
        if(i==len(permutation)-1):
            if(last_element>permutation[i] or last_element*permutation[i]<0):
                if(permutation[i]>0):
                    misc_dec+=[("p",last_boundary,i)]
                else:
                    misc_dec+=[("n",last_boundary,i)]
        last_element=permutation[i]
    # adjust last index for easier slicing in transformation
    misc_dec[-1]=(misc_dec[-1][0],misc_dec[-1][1],misc_dec[-1][2]+1)
    return misc_dec

def get_patterns(k):
    try:
        with open("pattern_"+str(k)+".txt","r") as patfile:
            patterns=json.load(patfile)
            return patterns
    except:
        print("Patterns for k=" + str(k) + " not avaliable.")
        print("Pattern file pattern_" + str(k) + " will be created.")
    patterns={}
    for i in range(1,k+1):
        patterns[i]=[]
        l=2**i
        l_half=int(l/2)

        pos,negpos,posneg,reppat="","","",""
        pos=pos.join(["p" for x in range(0,l)])

        negpos+="".join(["n" for x in range(0,l_half)])
        negpos+="".join(["p" for x in range(0,l_half)])

        posneg+="".join(["p" for x in range(0,l_half)])
        posneg+="".join(["n" for x in range(0,l_half)])

        patterns[i]+=[("TDRL",pos),("riTDRL",posneg),("liTDRL",negpos)]
        # print(patterns)
        if(i==1):
            continue
        else:
            for pat in patterns[i-1]:
                if(pat[1][0]=="p" and pat[1][-1]=="p"):
                    continue
                reppat += pat[1]
                reppat += pat[1]
                patterns[i]+=[("TDRL",reppat)]
                reppat=""
    with open("pattern_"+str(k)+".txt","w+") as patfile:
        json.dump(patterns[k],patfile)
    return patterns[k]

def subseq_mapping(misc_dec,pattern):
    # mapping=[]

    mapping={}

    last_index_pattern=0

    for i in range(0,len(misc_dec)):
        for j in range(last_index_pattern,len(pattern)):
            if(misc_dec[i][0]==pattern[j]):
                mapping[j]=i
                last_index_pattern=j+1
                break
    if(len(mapping)!=len(misc_dec)):
        # print(mapping)
        return {}
    return mapping

def oplus(misc_1,misc_2):
    merge_misc=[]
    index_1=0
    index_2=0
    while len(merge_misc)!=len(misc_1)+len(misc_2):
        if(index_1>=len(misc_1)):
            merge_misc+=[misc_2[index_2]]
            index_2+=1
        elif(index_2>=len(misc_2)):
            merge_misc+=[misc_1[index_1]]
            index_1+=1
        elif(misc_1[index_1]<misc_2[index_2]):
            merge_misc+=[misc_1[index_1]]
            index_1+=1
        else:
            merge_misc+=[misc_2[index_2]]
            index_2+=1
    return merge_misc

def reverse(string):
    return [-1*string[-i] for i in range(1,len(string)+1)]

def stringify(l):
    return "".join([str(x)+" " for x in l])

def transformation(permutation,pattern,misc_dec,misc_mapping):
    taus=[]
    newpat=""

    L=""
    R=""

    l = len(pattern[1])
    l_half = int(l/2)

    if(pattern[0]=="TDRL"):
        # print("ENTER TDRLK")
        misc_1=[]
        misc_2=[]
        newpat="".join(pattern[1][0:l_half])
        for i in range(0,l_half):
            try:
                misc_1=permutation[misc_dec[misc_mapping[i]][1]:misc_dec[misc_mapping[i]][2]]
            except:
                misc_1=[]
            try:
                misc_2=permutation[misc_dec[misc_mapping[l_half+i]][1]:misc_dec[misc_mapping[l_half+i]][2]]
            except:
                misc_2=[]
            # print(misc_1)
            # print(misc_2)
            # print("--")
            L+=stringify(misc_1)
            R+=stringify(misc_2)
            taus+=oplus(misc_1,misc_2)
    elif(pattern[0]=="liTDRL"):
        misc_1=[]
        misc_2=[]
        L_copy=[]
        newpat="".join(pattern[1][l_half:len(pattern[1])])
        for i in range(0,l_half):
            try:
                misc_1=permutation[misc_dec[misc_mapping[l_half-i-1]][1]:misc_dec[misc_mapping[l_half-i-1]][2]]
            except:
                misc_1=[]
            try:
                misc_2=permutation[misc_dec[misc_mapping[l_half+i]][1]:misc_dec[misc_mapping[l_half+i]][2]]
            except:
                misc_2=[]
            # print(reverse(misc_1))
            # print(misc_2)
            # print("--")
            L+=stringify(reverse(misc_1))
            R+=stringify(misc_2)
            taus+=oplus(reverse(misc_1),misc_2)
    elif(pattern[0]=="riTDRL"):
        misc_1=[]
        misc_2=[]
        R_copy=[]
        newpat="".join(pattern[1][0:l_half])
        for i in range(0,l_half):
            try:
                misc_1=permutation[misc_dec[misc_mapping[i]][1]:misc_dec[misc_mapping[i]][2]]
            except:
                misc_1=[]
            try:
                misc_2=permutation[misc_dec[misc_mapping[l-i-1]][1]:misc_dec[misc_mapping[l-i-1]][2]]
            except:
                misc_2=[]
            # print(misc_1)
            # print(reverse(misc_2))
            # print("--")
            L+=stringify(misc_1)
            R+=stringify(reverse(misc_2))
            taus+=oplus(misc_1,reverse(misc_2))
    return (taus,newpat,pattern[0],L,R)

def pprint_perm(permutation):
    print( "( " + "".join([str(x)+" " for x in permutation])[0:-1] + " )")

# permutation = [-6,-5,-7,-9,-8,4,3,2,1]
permutation=list(rand_perm(37))
for i in range(0,len(permutation)):
    permutation[i]+=1
    r = random.randint(0,10)
    if(r>=5):
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
    # print(dist)
    # print(permutation)
    misc_dec=get_misc_dec(permutation)
    # print(misc_dec)
    # print(pattern)
    subseq_map=subseq_mapping(misc_dec,pattern[1])
    # print(subseq_map)
    trns=transformation(permutation,pattern,misc_dec,subseq_map)
    # print(trns)
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
