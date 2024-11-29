# Mod-D2T dataset : Multi-level and multilingual parallel dependency-based versions of WebNLG+

## Description
This repo contains the code and resources for our INLG'23 short paper "Mod-D2T: A Multi-layer Dataset for Modular Data-to-Text Generation" (Simon Mille, François Lareau, Stamatia Dasiopoulou, Anya Belz).

You can find the paper's **English** data, as well as **French** and **Irish** data, already generated in the "conllu..." folders. Starting from the linguistic structures that can be downloaded in this notebook, you can use the code to recreate the existing data, or to produce variants of the data, e.g. for now without aggregations (at the predicate-argument and/or syntactic level) and/or without REG. Note that the linguistic structures can be obtained from the original WebNLG XML files using the [DCU_TDC WebNLG'23 notebook](https://github.com/mille-s/DCU_TCD_FORGe_WebNLG23).

## How to generate some dataset
0- To avoid mixups, only generate data for **one language in one session**. If you want another language, disconnect and delete the runtime, and restart it.
1- Run the very first cell to setup the local repository.
2- Select general parameters (language and data split) in the first cell of Part 1, and run all cells of Part 1.
3- Select generation parameters (for now, which optional modules you want to apply or not) in the first cell of Part 2, and run all cells of Part 2.
4- Repeat steps 2 and 3 if you are interested in more data split(s) (train, dev and/or test). Only change the split, not the language (see 0 above).
5- Run all cells of Parts 3 and 4 and collect your outputs in your own local "Download" folder.
