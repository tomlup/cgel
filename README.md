# cgel

This repo includes code for converting Universal Dependencies-formalism trees into the syntactic formalism from the *Cambridge Grammar of the English Language* (*CGEL*). CGEL gold data in the repo is annotated by Brett Reynolds (@brettrey3 on Twitter, who also runs @DailySyntaxTree).

![Status](https://github.com/nert-nlp/cgel/actions/workflows/validate.yml/badge.svg)

## Datasets
We have two portions of our resulting dataset: a small set of sentences with both gold CGEL and UD trees, and a larger set of trees from EWT with complete CGEL silver parses.

**The gold data resides in 4 files:**

- `datasets/{twitter.cgel, twitter_ud.conllu}`: CGEL gold trees from Twitter with corresponding UD trees (silver from Stanza then manually corrected by Nathan Schneider)
- `datasets/{ewt.cgel, ewt_ud.conllu}`: UD gold trees from EWT train set, with corresponding CGEL trees (manually annotated by Brett Reynolds)

Both portions were revised with the aid of consistency-checking scripts.

Other subdirectories contain older/silver versions of the trees.

To load the CGEL trees for scripting, use the `cgel.py` library.

## Structure
- `cgel.py`: library that implements classes for CGEL trees and the nodes within them, incl. helpful functions for printing and processing trees in PENMAN notation
- `clausetype.py`: enriches UD trees with CGEL clause type features
- `constituent.py`:
- `eval.py`: script for comparing two sets of CGEL annotations with tree edit distance (and derived metrics)
- `iaa.sh`: script that runs `eval.py` on all files involved in our interannotator study (comparing pre- and post-validation trees as well as final adjudicated version)
- `parse_forest.py`: parses original trees made by Brett Reynolds in LaTeX using the `forest` package into machine-readable formats
- `parse.py`: ditto but for trees using the `parsetree` package
- `ud2cgel.py`: converts UD trees (from English EWT treebank) to CGEL format using rule-based system
- `validate_trees.py`: script to check the well-formedness of trees

**Folders**
- `analysis/`: scripts for analysing the datasets, incl. edit distance
- `convertor/`: includes conversion rules in DepEdit script + outputs from conversion, with a simple Flask web interface for local testing in the browser (English text > automatic UD w/ Stanza > CGEL)
- `datasets/`: all the final output datasets, incl. gold UD for the gold CGEL data (more detailed description TBD)
- `figures/`: figures for papers/posters and code for generating them
- `scripts/`: one-off scripts that were used to clean/restructure data
- `trees/`: input trees in LaTeX that were converted into CGEL PENMAN trees

## Tests

To run tests locally:

```sh
$ python -m pytest
```

This will validate the trees and test distance metrics (Levenshtein and TED).

## Resources

__Overview of the project:__

Brett Reynolds, Aryaman Arora, and Nathan Schneider (2023). [Unified Syntactic Annotation of English in the CGEL Framework](https://people.cs.georgetown.edu/nschneid/p/cgeltrees.pdf). *Proc. of the 17th Linguistic Annotation Workshop (LAW-XVII)*, Toronto, Canada.

```bibtex
@inproceedings{cgelbank-law,
    address = {Toronto, Canada},
    title = {Unified Syntactic Annotation of {E}nglish in the {CGEL} Framework},
    author = {Reynolds, Brett and Arora, Aryaman and Schneider, Nathan},
    year = {2023},
    month = jul,
    url = {https://people.cs.georgetown.edu/nschneid/p/cgeltrees.pdf},
    booktitle = {Proc. of the 17th Linguistic Annotation Workshop (LAW-XVII)}
}
```

__Annotation manual:__

Brett Reynolds, Nathan Schneider, and Aryaman Arora (2023). [CGELBank Annotation Manual v1.0](https://arxiv.org/abs/2305.17347). *arXiv*.

__Further analysis:__

Brett Reynolds, Aryaman Arora, and Nathan Schneider (2022). [CGELBank: CGEL as a Framework for English Syntax Annotation](http://arxiv.org/abs/2210.00394). *arXiv*.

Aryaman Arora, Nathan Schneider, and Brett Reynolds (2022). [A CGEL-formalism English treebank](https://docs.google.com/presentation/d/1muLMZyNLspXElkWaOLfGQve64SxbapXkXJpWpgNmFWw/edit). *MASC-SLL* (poster), Philadelphia, USA.