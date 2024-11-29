These are the files that we generated for the first version of the French corpus late 2024.

The first block of the [DCU_TCD-FORGe notebook](https://github.com/mille-s/DCU_TCD-FORGe_WebNLG23) was used to convert the input XMLs to the CoNLL format needed by the generator. Then the present MoD-D2T notebook was used to generated the texts and intermediate representations, and convert them to the final CoNLL-U format. FORGe_colab_v6 can be found in the [general M-FleNS repo](https://github.com/mille-s/M-FleNS_NLG-Pipeline/tree/main/code).


| Language | French |
|--------|--------|

| Module | System |
|--------|--------|
| Linguistic structuring | DCU_TCD-FORGe Colab |
| Text planning | FORGe_colab_v6 |
| Lexicalisation | FORGe_colab_v6 |
| Communicative structuring | FORGe_colab_v6 |
| Deep sentence structuring | FORGe_colab_v6 |
| Surface sentence structuring | FORGe_colab_v6 |
| Syntactic aggregation | FORGe_colab_v6 |
| REG | FORGe_colab_v6 |
| Word order and agreement resolution | FORGe_colab_v6 |
| Surface form retrieval | FORGe_colab_v6 |

There were no errors during the generation process and no manual intervention was needed to fix files. However, we detected a few bad generations, which will be fixed in later versions of the dataset.
