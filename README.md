# TDRLiTDRL_sorting
Python program which implements the optimal sorting by TDRL/iTDRL algorithm by Bruno J. Schmidt, Tom Hartmann, and Peter F. Stadler. 

## FoCM Conference Poster

<img width="1000" alt="Screenshot 2023-06-11 173034" src="https://github.com/bsfaqu/TDRLiTDRL_sorting/assets/60860433/970dfc0b-84ea-4422-9f95-8cda41b767aa">

A .pdf version of this poster can also be found within this repository.

## Usage
```
sort.py [-h] [-r RANDOM] [-p PERMUTATION] [-i IDENTITY] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -r RANDOM, --random RANDOM
                        randomly generate a permutation; specify length as argument.
  -p PERMUTATION, --permutation PERMUTATION
                        space separated target permutation, i.e. 3 1 2 -4 -5 -6 7 8.
  -i IDENTITY, --identity IDENTITY
                        space separated identity permutation, i.e. 1 2 3 4 5 6 7 8. This argument is ignored if -p/--permutation is not set.
  -t, --tabular         switches output to tabular
```

## Example

```
python sort.py -p "2 4 7 -8 3 -1 -6 -5"
```

which yields the output 

```
Distance: 3 TDRL/iTDRL
----------------------

Permutation_3: ( 2 4 7 -8 3 -1 -6 -5 )
MISC-Encoding: p n p nn
Pattern      : ppnnppnn

TDRL γ_3: ( 2 4 7 -8  | 3 -1 -6 -5  )
Permutation_3 = γ_3 * Permutation_2

------------------------------------------

Permutation_2: ( 2 3 4 7 -8 -1 -6 -5 )
MISC-Encoding: p nn
Pattern      : ppnn

riTDRL γ_2: ( 2 3 4 7  | 5 6 1 8  )
Permutation_2 = γ_2 * Permutation_1

------------------------------------------

Permutation_1: ( 2 3 4 5 6 7 1 8 )
MISC-Encoding: pp
Pattern      : pp

TDRL γ_1: ( 2 3 4 5 6 7  | 1 8  )
Permutation_1 = γ_1 * Permutation_0

------------------------------------------

Permutation_0: ( 1 2 3 4 5 6 7 8 )
MISC-Encoding: p
Pattern      : p

------------------------------------------
```

The first row of the output always gives the distance, i.e. how many TDRL/iTDRL operations are necessary and sufficient to sort the identity permutation ι into the input permutation π.

The second row always shows the input permutation π (or the randomly generated permutation if -r/--random is specified).

For each output row beyond the first, a permutation, it's misc-encoding, and one of the shortest patterns it's misc-encoding is a subsequence of, is outputted. Furtermore, a TDRL/iTDRL is displayed which yields this permutation when applied to the permutation in the output row below it, i.e. Permutation_3 can be obtained by applying TDRL γ_3 to Permutaton_2. The ```|``` in the TDRL/iTDRL notation corresponds to the border between the left, and the right duplicated copy of the permutation it is applied to, i.e. for TDRL ```TDRL γ_3: ( 2 4 7 -8  | 3 -1 -6 -5  )``` applied to ```( 2 3 4 7 -8 -1 -6 -5 )```, ```2 4 7 -8``` remain in the left copy and ```3 -1 -6 -5``` remain in the right copy. The last row of the output always contains the identity permutation.

```sort.py``` can also be used to optimally sort arbitrary permutations with TDRL/iTDRL by specifying the -i argument. In this case, the permutation ι' specified after -i is sorted into the permutation inputted behind the -p flag.
This is done by computing the optimal sorting scenario to sort ι into ι' ∘ π. In this mode, each output row contains three extra lines which contain the corresponding permutations relabeled by ι' ∘ Permutation_1, ..., Permutation_n, the corresponding relabeled TDRL/iTDRL as well as the misc-encoding of the relabeled permutations. 

## Contact

In case you have any questions, feedback, or things to add just contact me at bruno@bioinf.uni-leipzig.de !
