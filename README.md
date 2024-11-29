# Mod-D2T dataset : Multi-level dependency-based version of WebNLG+

This repo contains the code and resources for our INLG'23 short paper "Mod-D2T: A Multi-layer Dataset for Modular Data-to-Text Generation" (Simon Mille, François Lareau, Stamatia Dasiopoulou, Anya Belz).

Follow instructions in the cells of ModD2T.ipynb to generate the data.

You can find the paper's **English** data, as well as **French** and **Irish** data, already generated in the "conllu..." folders. Starting from the linguistic structures that can be downloaded in this notebook, you can use the code to recreate the existing data, or to produce variants of the data, e.g. for now without aggregations (at the predicate-argument and/or syntactic level) and/or without REG.

The linguistic structures can be obtained from the original WebNLG XML files using the [DCU_TDC WebNLG'23 notebook](https://github.com/mille-s/DCU_TCD_FORGe_WebNLG23).
