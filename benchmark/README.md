## MHERCL v0.1 - Benchmark

### Sampling

MHERCL v0.1 is made of manually annotated sentences extrapolated from the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus)'s historical documents. This first release of the benchmark addressed a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. We have selected the sentences for the manual annotation based on four criteria: 
1. Language (English)
2. Source (the [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus))
3. Being part of the [Filtered AMR Graphs Bank](https://zenodo.org/record/7025779#.ZDls8OxBy3I) (filtered output of the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework)
4. Containing at least one _Named Entity_ recognised by the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework

### Annotation Guidelines

The sentences included in the sample described in the previous section underwent manual annotations thanks to the work of two internships (Foreign Languages and Literature undergraduate students) that have received _ad hoc_ training on the NERC and EL annotation task. The annotation work of the internships involved inspecting the sentences and identifying the named entities, eventually linking them to their corresponding WikiData ID (QID). Named entities were recognised and linked following a custom harmonisation of the AMR named entity annotations guidelines [[2]](https://amr.isi.edu/doc/amr-dict.html#named%20entity) and the _impresso_ guidelines, which are tailored for historical documents. In general, we assume a named entity is a real-world thing indicating a unique individual through a proper noun. The types were assigned according to the AMR annotation guidance instructions [[3]](https://www.isi.edu/~ulf/amr/lib/popup/ne-type-selection.html) and selected from the AMR named entity types list [[4]](https://www.isi.edu/~ulf/amr/lib/ne-types.html).

### Statistics

As summarised in the tables above, the annotators scrutinised 2181 sentences, extrapolated from 20 documents (historical periodicals), in which they annotated 2757 named entities belonging to 65 different types. The mentioned types demonstrate MHERCL music domain characterisation. 

1851 out of the 2757 named entities could be linked to a QID (67%), while 906 (33%) could not. Therefore, the percentage of "not linked" entities (entities that could not be linked to a QID) in MHERCL v0.1 is 30%. 502 named entities mentions contain errors due to OCR. Therefore, the percentage of noisy entities is 18%. Quantifying the noisy entities is important to facilitate downstream qualitative error analysis of NERC and EL systems and for comparison with other historical datasets.

### Release

MHERCL v0.1 is released in tab-separated values (TSV) files (UTF-8 encoded). Its format has been designed to comply with HIPE-2022 data (which is based on IOB and CoNLL-U), facilitating future integration.

# MHERCL v0.1 - Benchmark
## Filtering
### Basic filtering
#### Background
MHERCL v0.1 is made of manually annotated sentences extrapolated from the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus)'s historical documents. This first release of the benchmark addressed a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. We have selected the sentences for the manual annotation based on four criteria: 
1. Language (English)
2. Source (the [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus))
3. Being part of the [Filtered AMR Graphs Bank](https://zenodo.org/record/7025779#.ZDls8OxBy3I) (filtered output of the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework)
4. Containing at least one _Named Entity_ recognised by the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor)

#### Coreference resolution
The [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) pipeline applies coreference resolution to the input sentences. We identified MHERCL v01.'s sentences that were impacted by coreference resolution. We evaluated the coreference resolution output manually. The table below reports the results:

| #sentences impacted | Correct substitutions | Wrong substitutions |
| --- | --- | --- |
| 162 | 102 (64%) | 60 (36%) |

Given the quality of the coreference resolution output, we decided to discard those annotations related to a named entity resulting from the substitution of a pronoun by the application of the coreference resolution.

#### Is the sentence enough to infer the QID?
We asked the annotators to do a second round of checks to make sure that the input sentence alone was enough to infer the QID. For those sentences which did not provide enough context to infer the QID, the annotators provided some more sentences from the original document. These are the statistics (# of unique sentences):

| Is the sentence enough to infer the QID? ||
| --- | --- | 
| yes | 1964 |
| no | 158 |

We filter out those sentences from the filtered MHERCL v0.1 release. They will be released separately as they can serve for further experiments.

### Advanced filtering

We would like to remove low-quality sentences from our benchmark. We computed 3 measures:

1. We measured the length of the sentence (token numbers) by using SpaCy's `en_core_web_trf`;
2. We measured the annotated named entity length (token numbers) by using SpaCy's `en_core_web_trf`;
3. We calculated the % of the tokens represented by the named entity over the total number of tokens in the sentence;
4. We calculated the % of non-annotated tokens over the total tokens of the sentence (the stats are reported in the table below):

  | Statistic | % non annotated tokens ratio |
  |:---------:|:---------------------:|
  |   count   |        3052.000000    |
  |   mean    |        0.707145       |
  |    std    |        0.245109       |
  |    min    |       -0.371429       |
  |    25%    |        0.555556       |
  |    50%    |        0.750000       |
  |    75%    |        0.909091       |
  |    max    |        1.000000       |


   
6. We computed perplexity per sentence by using `pyplexity` library and `bigrams-bnc` (the stats are reported in the table below):

  | Statistic | Perplexity         |
  |-----------|--------------------|
  | Count     | 3054.000000        |
  | Mean      | 19935.047878       |
  | Std       | 101720.284950      |
  | Min       | 18.431019          |
  | 25%       | 246.313702         |
  | 50%       | 608.439903         |
  | 75%       | 2466.794106        |
  | Max       | 998751.789474      |
   

We want to leverage the 4 measurements described above to define a threshold to filter out low-quality sentences.

#### Filter n.1 - Sentences with no named entities annotated
At the first instance, we should take care of those sentences in our dataset in which the annotators did not find any named entities. We want to remove the noisiest ones. The idea is to remove all the sentences of the kind that have =< 15 tokens. With regard to the remaining ones, we want to set a threshold based on perplexity's quartile values. We want to set a threshold at the 50% mark (608.44). We keep all the sentences having perplexity =< 608.44.

#### Filter n.2 - Sentences with named entities annotated and no QID
As a second step, we should take care of those sentences in our dataset in which the annotators found named entities, but could not link them to any QID. We want to remove the noisiest ones (the ones in which there is less context). The idea is to remove all the sentences of the kind that have =< 10 tokens. With regard to the remaining ones, we want to set a threshold based on _non-annotated tokens ratio_'s quartile values, calculated on the subset of entries of our benchmark that have a named entity recognised but no QID. We want to set a threshold at the 25% mark (0.453409). We keep all the sentences having _non-annotated tokens ratio_ value => 0.453409.

#### Filter n.3 - Sentences with named entities annotated and QID
As a third step, we should take care of those sentences in our dataset in which the annotators found named entities and linked them to a QID. We want to remove the noisiest sentences (the ones in which there is less context). The idea is to remove all the sentences of the kind that have =< 10 tokens. With regard to the remaining ones, we want to set a threshold based on _non-annotated tokens ratio_'s quartile values, calculated on the subset of entries of our benchmark that have a named entity recognised and linked to a QID. We want to set a threshold at the 25% mark of that subset (0.55556). We keep all the sentences having _non-annotated tokens ratio_ value => 0.55556.

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
