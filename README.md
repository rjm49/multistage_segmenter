The multistage segmenter is a replication of the 2012 Interspeech paper by Ann Lee and James Glass.
The segmenter uses weighted finite-state transducers to model segmentation probabilities (that is, the probability of the end of an speech unit)  in speech patterns.  These can them be composed to combine the various probability models.

There are three probability models:
- prosodic: this predicts p(<BREAK>) based on acoustic features such as pauses, energy etc
- language: this predicts p(<BREAK>) based on preceding few words (i.e. n-gram)
- sentence length: this predicts p(<BREAK>) based on the length of the utterance so far

Originally written in 2015/2016, the repository contains an updated version of the code for 2019.
Instead of running python scripts (now deprecated in the "old" dir), the code is now organised as two Jupyter notebooks:
- *TrainProsodic.ipynb* creates the prosodic\_models/eval1-probabilities.dat file, which actually houses log-probs of a <BREAK> as predicted by an SVM or LogisticRegression training step trained on acoustic characteristics of speech
- *CreateModels.ipynb* creates WFST (\*.fst) files for the three models described above.  It also includes cells to compose them into prosodic only (pm\_only), prosodic+language model (pm\_lm), and prosodic+language+sentence-length model (pm\_lm\_slm). It also does shortest path analyses on these compositions to estimate the most likely <BREAK> patterns.

You will need OpenFST and OpenGRM to use these files, and the interface is via calls to the command line rather than the python wrapper which was incomplete for the purposes of ngram model manipulation.

The original 2016 code had a cumbersome batch-processing approach.  The new code is run interactively from notebooks and so iterating over batches can now be avoided.  The code does use relative paths from the original notebook, so run the notebook server using "jupyter notebook" in the top-level (multistage\_segmenter) dir of the repo.

Please address any questions to me at the University of Cambridge.  My email can be found in the NLIP group's personnel pages.
