# Forced-Crosswordles
Crosswordle is a wordle variant playable at https://crosswordle.vercel.app. In a crosswordle puzzle, you are given the final answer to a game of wordle, as well as the colours of all prior guesses, and must work to fill the prior rows with a set of guesses (obeying wordle hard mode restrictions) that could have produced these colourings.

*Forced crosswordle* puzzles are crosswordle puzzles where each word in the puzzle is uniquely determined by the words beneath it. This is a subset of the set of crosswordles with a unique solution.

The condition of a crosswordle being *forced* is stronger than the condition of it having a unique solution. Crosswordles with a unique solution may have multiple possibilities early on which are eliminated by "dead ends" further into the puzzle, whereas *forced crosswordles* will have only one possibility at each row. 

The corollary of this is that in a *forced crosswordle*, filling in a row with a valid word is equivalent to being finished with that row, whereas in a *unique crosswordle*, that row may need to be returned to later to avoid a dead end.

This repository contains a pair of python scripts used for generation (forced_crosswordles_generator.py) and analysis (forced_crosswordles_analysis.py) of forced crosswordle puzzles, as well as large .txt files containing the data for all forced crosswordle puzzles of 2-10 rows (inclusive) in length.

Both scripts have been commented and are intended to be relatively customizable (especially so for the analysis script). 

The hope of making this a public repository is that this will allow people to find a bunch of cool puzzles. The analysis filters provided give a good starting point for finding interesting puzzles by sorting them by the number of green tiles, amount of information given, number of tiles which are not grey, and filtering on if the words used are all common words in the NYT wordle answer list, but I'm hoping people will come up with a bunch of other ideas for what characteristics to search for in puzzles that would make them interesting.

Including puzzles of lengths outside the 3-6 rows (inclusive) currently supported by crosswordle is as a generalization, although it may be useful in the event where someone makes a custom crosswordle gui (or crosswordle itself receives an update) which allows these puzzles to be played.
