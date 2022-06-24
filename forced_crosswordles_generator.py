"""
FORCED CROSSWORDLE GENERATOR:
This script is essentially a slight modification from the scripts
I have used for generating various puzzles for instant wordle variants.

The working method for the script is essentially:
1. Generate a large hash table, this table will be formatted
table[(word, colouring)] = [list of guessed words that give that colouring when word is the solution]

2. Find all "double" puzzles. These are just 2-liners where the colouring forces the word
equivalently, find all (word, colouring) combinations such that the list in our hash table has length 1.

3. Extend these "double" puzzles by length 1. This step is complicated and has multiple parts.
3.a. Find all valid colourings for the next row. These colourings follow the following two rules:
     i) Greens can only go above other greens
     ii) The number of yellows + greens on the next row is <= the number of yellows + greens on the previous row

3.b. For each of these colourings, use the lookup table to find words that may fill that colouring. These are then filtered via the following rules:
     i) A letter which has appeared on a grey tile in a previous row cannot reappear on a grey tile in this row.
     ii) A letter which appears on a yellow *or* grey tile cannot be above a location where it was placed in a previous row.
     iii) The yellows and greens in this row must be a sublist (i.e.: sequence of items chosen from) the yellows and greens in the previous row.
     (note that, for efficiency, if we find 2 words work, we may discard the colouring immediately)

4. Having found all puzzles of length 3, we may repeat step 3 on those, and repeat over and over for longer and longer puzzles.

Generating these puzzles by induction this way is not easy task, as many such puzzles exist.
Running over the course of a day, this script finished having found the following numbers of puzzles:

Number of rows    Total puzzles      Total common puzzles     Save location
____________________________________________________________________________________
2                 274,130            47,748                   forced_doubles.txt
3                 1,220,955          39,718                   forced_triples.txt
4                 2,786,582          17,358                   forced_quadruples.txt
5                 3,374,366          4,169                    forced_quintuples.txt
6                 1,941,461          440                      forced_sextuples.txt
7                 517,792            14                       forced_septuples.txt
8                 65,610             0                        forced_octuples.txt
9                 3,948              0                        forced_nonuples.txt
10                85                 0                        forced_decuples.txt

(where a "common" puzzle is a puzzle where all words (excluding the final solution) are within the NYT wordle answer list)

Note that there are no forced crosswordle puzzles of length >10, and crosswordle will only load puzzles of length 3 to 6 (inclusive).
"""

# imports for our program
import random

# NYT wordle answer list ("common words")
with open("wordles.txt") as f:
    WORDLES = f.read().split(", ")

# NYT wordle guess list (any word you can enter into a crosswordle row will be in here)
with open("extendedwordles.txt") as f:
    EXTENDED_WORDLE = f.read().split(", ")

# ====================================== BASIC SCRIPTS ===================================== #
# this part of the code is a few basic scripts that are common for any form of wordle variant search.

# utility function for converting a ternary list, e.g. [2, 2, 1, 2, 0], to a decimal number e.g. 231.
def ternarytonum(t):
    num = 0
    for power, n in enumerate(t[::-1]):
        num += n*(3**power)
    return num

# utility function for converting a decimal number e.g. 134 to a ternary list e.g. [1, 1, 2, 2, 2].
def numtoternary(x):
    nums = []
    while x > 0:
        x, r = divmod(x, 3)
        nums.append(r)
    while len(nums) < 5: nums.append(0)
    return nums[::-1]

# function for generating a hash table allowing O(1) lookup of all words that satisfy a given colouring under a given solution
def get_table(words, ext_words):
    table = {}
    for i, sol in enumerate(ext_words):
        if i % 100 == 0: print(i) # this print statement is so a person using the program knows it's not just hanging.
        for guess in ext_words:
            if sol != guess:
                # get the decimal representation of the (ternary) wordle colouring.
                coln = ternarytonum(wordle_colour(guess, sol))
                # store in the format table[(sol, coln)] = [list of guess words that would work] 
                if (sol, coln) in table.keys():
                    table[(sol, coln)].append(guess)
                else:
                    table[(sol, coln)] = [guess]
    return table

# function for getting the (ternary) wordle colouring of a guess under a given solution.
# Green = 2, Yellow = 1, Grey = 0.
def wordle_colour(guess, solution):
    col = [0, 0, 0, 0, 0]
    observed = []
    for pos, letter in enumerate(solution):
        if guess[pos] == solution[pos]:
            col[pos] = 2
        else: observed.append(letter)

    for pos, letter in enumerate(guess):
        if letter in observed and col[pos] != 2:
            observed.remove(letter)
            if solution[pos] != letter:
                col[pos] = 1

    return col

# function for finding "doubles", aka. colourings which are given by only one possible guess under a given solution.
def find_doubles(table):
    doubles = []
    for k in table.keys():
        sol, coln = k
        if len(table[k]) == 1:
            guess = table[k][0]
            doubles.append(([sol, guess], [242, coln]))
    return doubles

# utility function for saving puzzles to a local file
def save_puzzles(puzzles, filename):
    with open(filename, "w") as f:
        s = []
        for (words, nums) in puzzles:
            s.append("|".join(map(lambda il: ",".join(str(i) for i in il), [words, nums])))
        f.write("\n".join(i for i in s))

# ==================================== PUZZLE EXTENSION ==================================== #
# this part of the code is a collection of functions used to extend puzzles by one row

# main process for extending a puzzle by one row.
def extend_puzzles(puzzles, table):
    extended = []
    for index, puzzle in enumerate(puzzles):
        if index % 1000 == 0 and index > 0: print(index, len(extended)) # print statement to gauge progress during generation.
        words, nums = puzzle
        # step 1: figure out what colourings would be allowed by hard mode for the next line up (regardless of whether they could actually be played).
        cols = valid_colourings(nums[::-1][0])
        # step 2: determine which letters have been used as greys in previous guesses.
        greys = get_greys(words, nums)
        for coln in cols:
            # step 3: for each colouring which would be allowed, search for words which would be playable.
            fwords = filter_colour(coln, greys, words, nums, table)
            if len(fwords) == 1:
                # if only one word is playable, create a new puzzle with that word and our colouring in the final row
                # save this puzzle in the list of puzzles we have extended
                newwords = words + [fwords[0]]
                newnums = nums + [coln]
                extended.append((newwords, newnums))
    return extended

# function for generating all valid colourings based on the colour of the previous line.
def valid_colourings(prevcoln):
    prevcol = numtoternary(prevcoln)
    cols = []
    for coln in range(0, 242):
        if is_valid(coln, prevcol):
            cols.append(coln)
    return cols

# function for checking if a colour is valid, based on the colour of the previous line.
# returns True if a colour is valid, False otherwise.
def is_valid(coln, prevcol):
    newcol = numtoternary(coln)

    #rule 1: green can only appear above other green
    for index, c in enumerate(newcol):
        if c == 2 and prevcol[index] != c:
            return False

    #rule 2: number of greens+yellows on this line <= number of greens+yellows on the previous line.
    if sum(map(lambda x: x > 0, newcol)) > sum(map(lambda x: x > 0, prevcol)):
        return False

    return True

# function for filtering the possible words for a given colour to find words which are playable in that position.
# takes the colour, previous words, previous colourings, hash table, and a list of previously played grey letters.
def filter_colour(coln, greys, words, nums, table):
    sol = words[0]
    prevcoln = nums[::-1][0]
    filtered = []
    if (sol, coln) in table.keys():
        # get the list of words which can be played with this colouring under the solution for further filtering.
        fwords = table[(sol, coln)]
        col = numtoternary(coln)
        
        for word in fwords:
            # for each word in the filterable words, check if it satisfies requirements that will allow it to be played on the next row.
            if is_good_word(word, col, greys, words, words[::-1][0], prevcoln):
                filtered.append(word)
                # we found more than one word satisfying the requirements, we can break from the loop.
                # the outcome will be the same (the colouring being discarded) if we keep going or not.
                if len(filtered) >= 2:
                    break
    return filtered

# function for checking if a word satisfies requirements to be playable on the next row in crosswordle,
# given that row's colour, the greys from all previous rows, the words from previous rows, and the previous word and previous word's colouring.
# if a word satisfies all requirements, return True, otherwise return False.
def is_good_word(word, col, greys, words, prevword, prevcoln):
    nongreys = []
    for index, letter in enumerate(word):
        if col[index] == 0:
            if letter in greys:
                # rule 1: A letter which has already been used as a grey tile in a previous row cannot be reused as a grey tile in this row.
                return False
            if aligned(letter, index, words):
                # rule 2: letters on yellow or grey tiles cannot appear above somewhere that they were placed in a previous row.
                return False
        else:
            nongreys.append(letter)
            if col[index] == 1 and aligned(letter, index, words):
                # rule 2: letters on yellow or grey tiles cannot appear above somewhere that they were placed in a previous row.
                return False
    
    prevnongreys = get_nongreys(prevword, prevcoln)

    # rule 3: yellow and green letters in this row must be a sublist of the yellow and green letters from the previous row.
    if not is_sublist(nongreys, prevnongreys):
        return False

    return True

# utility function for getting the list of all grey letters from previous guesses.
def get_greys(words, nums):
    greys = []
    for word, coln in zip(words, nums):
        for index, letter in enumerate(word):
            col = numtoternary(coln)
            # any letter on a grey tile is added to the list of grey letters.
            # (note that this includes tiles which are otherwise green/yellow,
            #  the inclusion of such letters corresponds to losing the ability to over-use the letter) 
            if col[index] == 0:
                if not letter in greys:
                    greys.append(letter)
    return greys

# utility function to check whether a letter has appeared in a given spot in any previous word.
# returns true if it has, false otherwise.
def aligned(letter, index, words):
    for word in words:
        if word[index] == letter:
            return True

    return False

# utility function for checking whether an array (sub) is a sublist of a larger array (full)
# a sublist is an array which could be constructed by removing elements from the larger array.
# e.g.: [1,2,2] is a sublist of [2,3,1,3,5,6,2], but not a sublist of [2,3,1,3,5,6] (as in that case, the 2nd 2 is missing).
def is_sublist(sub, full):
    for e in sub:
        if e in full:
            full.remove(e)
        else:
            return False
    return True

# utility function for getting all green and yellow letters from a word, given its colouring.
def get_nongreys(word, coln):
    nongreys = []
    col = numtoternary(coln)
    for index, letter in enumerate(word):
        if col[index] != 0:
            nongreys.append(letter)
    return nongreys

# ======================================== EXECUTION ======================================= #
# a simple example script which executes when this file is loaded.

if __name__ == "__main__":
    # step 1: generate colouring hash table for O(1) lookup times
    print("generating hash table")
    table = get_table(WORDLES, EXTENDED_WORDLE)
    print(f"number of colourings: {len(table.keys())}")
    # step 2: find all "double" puzzles
    print("finding 2-row puzzles")
    doubles = find_doubles(table)
    print(f"found {len(doubles)} 2-row puzzles.")
    # step 3: extend doubles to get puzzles of length 3, this can be repeated on the result in the python shell to get puzzles of length 4, 5, 6, etc.
    print("finding triples")
    triples = extend_puzzles(doubles, table)
    print(f"found {len(triples)} 3-row puzzles.")
