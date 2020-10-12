# UPOS and FEATS evaluation script

```
usage: conllu_morpho_eval.py [-h] [-g GOLD] [-p PRED] [-s] [-e] [-w WIDTH]
                             [-f FILTER]

optional arguments:
  -h, --help            show this help message and exit
  -g GOLD, --gold GOLD  Gold (.conllu)
  -p PRED, --pred PRED  Predictions (.conllu)
  -s, --sort            Sort by F1
  -e, --errors          Print errors
  -w WIDTH, --width WIDTH
                        Max line width
  -f FILTER, --filter FILTER
                        Filter words (upos=NOUN;Gender=Masc)
```

The analysed files (gold and predicted) must exactly match each other on the tokenization and sentence segmentation levels.

## Default mode
```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu 
       Metric	 Raw gold	 Raw pred	Precision	   Recall	       F1
     UPOS=ADJ	     1689	     1694	    92.62	    92.90	    92.76
     UPOS=ADP	     2020	     2042	    96.57	    97.62	    97.10
     UPOS=ADV	     1226	     1192	    94.38	    91.76	    93.05
     UPOS=AUX	     1504	     1516	    97.63	    98.40	    98.01
   UPOS=CCONJ	      738	      742	    99.06	    99.59	    99.32
...
```

## Sort features by F1
```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu -s
       Metric	 Raw gold	 Raw pred	Precision	   Recall	       F1
     Abbr=Yes	       15	        0	     0.00	     0.00	     0.00
  Foreign=Yes	        9	        0	     0.00	     0.00	     0.00
   Gender=Fem	       40	        0	     0.00	     0.00	     0.00
  Gender=Masc	      122	        0	     0.00	     0.00	     0.00
  Gender=Neut	      223	        0	     0.00	     0.00	     0.00
...
```

## List annotation errors
```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu -e | grep UPOS=NOUN
    UPOS=NOUN	     4129	     4132	    93.78	    93.85	    93.81  PROPN:3.27 ADJ:0.85 NUM:0.68 VERB:0.65 ADV:0.24 PUNCT:0.12 AUX:0.07 SYM:0.05 SCONJ:0.05 X:0.05 ADP:0.05 DET:0.02 CCONJ:0.02 INTJ:0.02
```

`PROPN:3.27` means that `3.27%` of nouns were predicted as proper nouns.

## Filter words
### Without filter:

```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu | grep 'Number='
  Number=Plur	     1369	     1374	    97.45	    97.81	    97.63
  Number=Sing	     7268	     7272	    97.21	    97.26	    97.24
     Number=_	    16459	    16450	    98.94	    98.89	    98.92
```

### Only for nouns:
```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu -f upos=NOUN | grep 'Number='
Filter: upos=NOUN
  Number=Plur	      905	      896	    98.33	    97.35	    97.83
  Number=Sing	     3224	     3119	    99.26	    96.03	    97.62
     Number=_	        0	      114	     0.00	     0.00	     0.00
```

### Only for proper nouns:
```
$ ./conllu_morpho_eval.py -g en_ewt-ud-test.conllu -p en_ewt-ud-pred.conllu -f upos=PROPN | grep 'Number='
Filter: upos=PROPN
 Number=Plur	       78	       87	    86.21	    96.15	    90.91
 Number=Sing	     1997	     1936	    99.90	    96.85	    98.35
    Number=_	        0	       52	     0.00	     0.00	     0.00
```

### Multiple filters (upos=NOUN and Number=Sing):
```
$ ./conllu_morpho_eval.py -g fi_ftb-ud-test.conllu -p fi_ftb-ud-pred.conllu -f "upos=NOUN;Number=Sing" -e | grep 'Case='
         Case=Abe	        1	        1	   100.00	   100.00	   100.00  
         Case=Abl	       33	       33	    96.97	    96.97	    96.97  Ill:3.03 Ade:0.00
         Case=Ade	      131	      130	    98.46	    97.71	    98.08  Nom:0.76 _:0.76 Abl:0.76 All:0.00 Ela:0.00
         Case=All	       68	       66	   100.00	    97.06	    98.51  Ade:1.47 Ill:1.47
         Case=Ela	      141	      138	    98.55	    96.45	    97.49  Par:2.13 _:0.71 Ade:0.71
         Case=Ess	       74	       75	    98.67	   100.00	    99.33  Ine:0.00
         Case=Gen	      652	      636	    98.27	    95.86	    97.05  _:2.61 Nom:1.38 Par:0.15 Ine:0.00 Tra:0.00
         Case=Ill	      177	      172	    98.26	    95.48	    96.85  _:2.26 Par:1.69 Nom:0.56 All:0.00 Tra:0.00 Abl:0.00
         Case=Ine	      195	      184	   100.00	    94.36	    97.10  _:4.62 Gen:0.51 Ess:0.51
         Case=Nom	      901	      890	    98.54	    97.34	    97.93  _:1.22 Gen:0.89 Par:0.44 Tra:0.11 Ade:0.00 Ill:0.00
         Case=Par	      523	      522	    97.89	    97.71	    97.80  _:1.34 Nom:0.38 Ela:0.38 Gen:0.19 Ill:0.00
         Case=Tra	       29	       27	    96.30	    89.66	    92.86  Gen:3.45 Ill:3.45 _:3.45 Nom:0.00
           Case=_	        0	       51	     0.00	     0.00	     0.00 
```

