These are the files that we generated for the Pan-DL'23 paper. The online version of the [DCU_TCD-FORGe generation pipeline](https://github.com/mille-s/DCU_TCD-FORGe_WebNLG23) was used. FORGe_colab_v4 can be found in the [M-FleNS repo](https://github.com/mille-s/M-FleNS_NLG-Pipeline/tree/main/code).

| Language | Irish |
|--------|--------|

| Module | System |
|--------|--------|
| Linguistic structuring | DCU_TCD-FORGe Colab |
| Text planning | FORGe_colab_v4 |
| Lexicalisation | FORGe_colab_v4 |
| Communicative structuring | FORGe_colab_v4 |
| Deep sentence structuring | FORGe_colab_v4 |
| Surface sentence structuring | FORGe_colab_v4 |
| Syntactic aggregation | FORGe_colab_v4 |
| REG | FORGe_colab_v4 |
| Word order and agreement resolution | FORGe_colab_v4 |
| Surface form retrieval | FORGe_colab_v4 |

Had to process some files manually as 5 inputs gave issues when using Colab (issue not happening with local pipeline):
- Error(s) found in DMorphLin en_train-edit_ga_10200-10499: [291]
- Error(s) found in DMorphLin en_train-edit_ga_11100-11399: [262]
- Manually found in DMorphLin en_train-edit_ga_11700-11999: [56]
- Error(s) found in DMorphLin en_train-edit_ga_12300-12599: [253]
- Error(s) found in DMorphLin en_train-edit_ga_12900-13199: [165]
