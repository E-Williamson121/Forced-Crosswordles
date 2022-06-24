"""
FORCED CROSSWORDLE ANALYSIS:

This script is a companion to the forced crosswordle generator script, and contains some functionality to analyse and filter crosswordles post-generation.
The functionality in this script could be easily extended to allow for more detailed or varied analyses. It exists to provide simple examples.
"""

# imports for our program
import random

# NYtimes wordle answer list ("common words")
with open("wordles.txt") as f:
    WORDLES = f.read().split(", ")

# NYTimes wordle guess list (any word you can enter into a crosswordle row will be in here)
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

# utility function for saving puzzles to a local file
def save_puzzles(puzzles, filename):
    with open(filename, "w") as f:
        s = []
        for (words, nums) in puzzles:
            s.append("|".join(map(lambda il: ",".join(str(i) for i in il), [words, nums])))
        f.write("\n".join(i for i in s))

# utility function for loading puzzles from a local file
def load_puzzles(filename):
    puzzles = []
    with open(filename, "r") as f:
        for i, line in enumerate(f.readlines()):
            wordstr, numstr = tuple(line.split("|"))
            words = wordstr.split(",")
            nums = list(map(int, numstr.split(",")))
            puzzles.append((words, nums))
    return puzzles

# =================================== ANALYSIS FUNCTIONS =================================== #
# functions in this section are some basic utility functions made for post-generation analysis of the dataset in the shell.

# utility function to convert a puzzle to a crosswordle link (useful for play-testing a game without being spoiled on the solution).
def tolink(puzzle):
    words, nums = puzzle
    sol = words[0]
    print(f"https://crosswordle.vercel.app/?puzzle=v1-{','.join(str(i) for i in nums[::-1])}-{sol}")

# utility function to get a random puzzle and convert it to a link.
def get_random_puzzle(puzzles):
    tolink(puzzles[random.randint(0, len(puzzles)-1)])

# utility function for sorting a dictionary by key.
def sort_dict(mydict):
    sorted_dict = {}
    for key in sorted(mydict):
        sorted_dict[key] = mydict[key]
    return sorted_dict

# utility function for making a precomputed lookup of whether words are common or not.
# (useful because "word in WORDLES" ends up being slightly slower when used a lot)
def make_commonness_dict(ext_words, words):
    iscommon = {}
    for word in ext_words:
        iscommon[word] = word in words
    return iscommon

# utility function for taking a list of forced puzzles and filtering for puzzles that will be solvable by the crosswordle checker.
def find_common_puzzles(puzzles):
    common_puzzles = []
    for puzzle in puzzles:
        words, nums = puzzle
        if all(map(lambda x: iscommon[x], words[1:])):
            common_puzzles.append(puzzle)
    return common_puzzles

# analysis function for bucketing a list of puzzles by how many non-grey squares are in the puzzle (usually results in very yellow puzzles)
# returned are both the buckets of puzzles (number_puzzles[N] = [list of puzzles with N non-grey squares])
# and a hash table storing the size of each bucket (number_counts[N] = number of puzzles with N non-grey squares).
def bucket_puzzles_by_coln(puzzles):
    number_puzzles = {}
    number_counts = {}
    for puzzle in puzzles:
        words, nums = puzzle
        s = sum(map(lambda x: sum(map(lambda x: x > 0, numtoternary(x))), nums))
        if s in number_puzzles.keys():
            number_puzzles[s].append(puzzle)
            number_counts[s] += 1
        else:
            number_puzzles[s] = [puzzle]
            number_counts[s] = 1
    return number_puzzles, sort_dict(number_counts)

# analysis function for bucketing a list of puzzles by how much information the puzzle gives. It is assumed one green is worth two yellows.
# returned are both the buckets of puzzles (number_puzzles[N] = [list of puzzles with an information value of N])
# and a hash table storing the size of each bucket (number_counts[N] = number of puzzles with an information value of N).
def bucket_puzzles_by_info(puzzles):
    number_puzzles = {}
    number_counts = {}
    for puzzle in puzzles:
        words, nums = puzzle
        s = sum(map(lambda x: sum(numtoternary(x)), nums))
        if s in number_puzzles.keys():
            number_puzzles[s].append(puzzle)
            number_counts[s] += 1
        else:
            number_puzzles[s] = [puzzle]
            number_counts[s] = 1
    return number_puzzles, sort_dict(number_counts)

# analysis function for bucketing a list of puzzles by how many greens are in the puzzle.
# returned are both the buckets of puzzles (number_puzzles[N] = [list of puzzles with N green squares])
# and a hash table storing the size of each bucket (number_counts[N] = number of puzzles with N green squares).
def bucket_puzzles_by_greens(puzzles):
    number_puzzles = {}
    number_counts = {}
    for puzzle in puzzles:
        words, nums = puzzle
        s = sum(map(lambda x: sum(map(lambda x: x == 2, numtoternary(x))), nums))
        if s in number_puzzles.keys():
            number_puzzles[s].append(puzzle)
            number_counts[s] += 1
        else:
            number_puzzles[s] = [puzzle]
            number_counts[s] = 1
    return number_puzzles, sort_dict(number_counts)

# ======================================== EXECUTION ======================================= #
# the part of the code that executes at runtime.

if __name__ == "__main__":
    # example: load triples from a local file
    print("Loading triples from file.")
    triples = load_puzzles("forced_triples.txt")
    print(f"loaded {len(triples)} 3-row puzzles.")
