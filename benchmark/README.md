## MHERCL v0.1 - Dataset Composition

### Sampling

MHERCL v0.1 is made of manually annotated sentences extrapolated from the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus)'s historical documents. This first release of the benchmark addressed a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. We have selected the sentences for the manual annotation based on four criteria: 
1. Language (English)
2. Source (the [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus))
3. Being part of the [Filtered AMR Graphs Bank](https://zenodo.org/record/7025779#.ZDls8OxBy3I) (filtered output of the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework)
4. Containing at least one _Named Entity_ recognised by the Polifonia Knowledge Extractor framework

### Annotation Guidelines

The sentences included in the sample described in the previous section underwent manual annotations thanks to the work of two internships (Foreign Languages and Literature undergraduate students) that have received _ad hoc_ training on the NERC and EL annotation task. The annotation work of the internships involved inspecting the sentences and identifying the named entities, eventually linking them to their corresponding WikiData ID (QID). Named entities were recognised and linked following a custom harmonisation of the AMR named entity annotations guidelines [[2]](https://amr.isi.edu/doc/amr-dict.html#named%20entity) and the _impresso_ guidelines, which are tailored for historical documents. In general, we assume a named entity is a real-world thing indicating a unique individual through a proper noun. The types were assigned according to the AMR annotation guidance instructions [[3]](https://www.isi.edu/~ulf/amr/lib/popup/ne-type-selection.html) and selected from the AMR named entity types list [[4]](https://www.isi.edu/~ulf/amr/lib/ne-types.html).

### Statistics

As summarised in the tables above, the annotators scrutinised 2181 sentences, extrapolated from 20 documents (historical periodicals), in which they annotated 2757 named entities belonging to 65 different types. The mentioned types demonstrate MHERCL music domain characterisation. 

1851 out of the 2757 named entities could be linked to a QID (67%), while 906 (33%) could not. Therefore, the percentage of "not linked" entities (entities that could not be linked to a QID) in MHERCL v0.1 is 30%. 502 named entities mentions contain errors due to OCR. Therefore, the percentage of noisy entities is 18%. Quantifying the noisy entities is important to facilitate downstream qualitative error analysis of NERC and EL systems and for comparison with other historical datasets.

### Release

MHERCL v0.1 is [released](https://github.com/arianna-graciotti/MHERCL/blob/main/benchmark/v0.1/tsv/conll_100723.zip) in tab-separated values (TSV) files (UTF-8 encoded). Its format has been designed to comply with HIPE-2022 data (which is based on IOB and CoNLL-U), facilitating future integration.

## Experiments

### Scope 

The experiments have been carried out on a subset of MHERCLv0.1 (sub-MHERCLv0.1). Sub-MHERCLv0.1 is composed of 1545 named entity mentions, selected according to their compliance with the following requirements: 
1. it could be linked to a QID
2. its QID could be assigned relying only on the named entity mention's sentence of provenance
3. its sentence of provenance was not impacted by coreference resolution

These 1545 tuples (sentence, named entity mention, QID) are unique. 

### Popularity bias 

Sub-MHERCLv0.1 contains 1032 unique named entity mentions, 13 of which are linked to 2 QIDs, 1019 to 1.

### BLINK 

We passed to BLINK sub-MHERCLv0.1 sentences and already identified (gold) mentions. BLINK's output QIDs and gold QIDs match in 1135 cases (73%), and differ in 410 cases (27%).
