# MHERCL v0.1 - Benchmark

## Sampling

MHERCL v0.1 is made of manually annotated sentences extrapolated from the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus)'s historical documents. This first release of the benchmark addressed a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. We have selected the sentences for the manual annotation based on four criteria: 
1. Language (English)
2. Source (the [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the [Polifonia Textual Corpus](https://github.com/polifonia-project/Polifonia-Corpus))
3. Being part of the [Filtered AMR Graphs Bank](https://zenodo.org/record/7025779#.ZDls8OxBy3I) (filtered output of the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework)
4. Containing at least one _Named Entity_ recognised by the [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework

## Preliminary Study

As the PKE framework automatically recognises named entities in its text-to-AMR parsing step, we ran a preliminary experiment to evaluate the off-the-shelf performance of the PKE text-to-AMR parser and its embedded entity linker, BLINK. We focused on a sample of $2205$ sentences taken from the _Periodicals_ module of the PTC and on named entities of type person. The results are reported in the Table below.

#### Table reporting statistics about the off-the-shelf quality of [PKE](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework on EL of _person named entities_ in a [PTC](https://github.com/polifonia-project/Polifonia-Corpus) sample.

| #sents      | pNE mentions (#recognised) |   pNE mentions (#linked)    | pNE QID (#found)  |        pNE QID (#not found)   | pNE DoB  (#plausible)  | pNE DoB  (#implausible)|pNE DoB  (#not found)|
|-------|--------------|-------|----------|-----------|------------|--------------|-----------|
| 2205 | 2262         | 2108 | 2006    | 102   | 1199       | 203         | 604     |

### Statistics (unfiltered)

#### MHERCL v0.1 - Dataset Stats (_unfiltered_)

| Dataset | Lang. | #docs | #sents | #tokens |
|---------|-------|-------|--------|---------|
| MHERCL v0.1 (_unfiltered_) | EN    |21|2.181  | 51.457 |


#### MHERCL v0.1 - Mentions Stats (_unfiltered_)

| _unfiltered_      | #mentions | types          | noisy        | linked (yes) | linked (no) |
|-------------------|-----------|----------------|--------------|--------------|-------------|
| all               |2.874      |_not applicable_|530           |1.906          |968          |
| unique            |2.130      |68              |496           |1.028          |1.102|

As summarised in the tables above, the annotators scrutinised 2181 sentences, extrapolated from 21 documents (historical periodicals), in which they annotated 2130 unique named entities belonging to 68 different types. The mentioned types demonstrate MHERCL music domain characterisation. 

1028 out of the 2130 unique named entities could be linked to a QID, while 1102 could not. Therefore, the percentage of "not linked" entities (entities that could not be linked to a QID) in MHERCL v0.1 is 30%. 502 named entities mentions contain errors due to OCR. Therefore, the percentage of noisy entities is 18%. Quantifying the noisy entities is important to facilitate downstream qualitative error analysis of NERC and EL systems and for comparison with other historical datasets.

## Filtering

### Basic filtering

#### Coreference resolution

The [Polifonia Knowledge Extractor](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) pipeline applies coreference resolution to the input sentences. We identified MHERCL v01.'s sentences that were impacted by coreference resolution. We evaluated the coreference resolution output manually. The table below reports the results:

| #sentences impacted | Correct substitutions | Wrong substitutions |
| --- | --- | --- |
| 162 | 102 (63%) | 60 (37%) |

Given the quality of the coreference resolution output, we decided to discard those annotations related to a named entity resulting from the substitution of a pronoun by the application of the coreference resolution.

#### Is the sentence context exhaustive enough to infer the QID?

We asked the annotators to do a second round of checks to make sure that the input sentence alone was exhaustive enough to infer the QID. For those sentences which did not provide enough context to infer the QID, the annotators provided some more sentences from the original document. These are the statistics (# of unique sentences):

| Is the sentence enough to infer the QID? ||
| --- | ---  | 
| yes | 1709 |
| no  |  203 |

We filter out those sentences from the filtered MHERCL v0.1 release. They will be released separately as they can serve for further experiments.

### Advanced filtering

We would like to remove low-quality sentences from our benchmark. We computed four different metrics:

1. We measured the length of the sentence (token numbers) by using SpaCy's `en_core_web_trf`;
2. We measured the annotated named entity length (token numbers) by using SpaCy's `en_core_web_trf`;
3. We calculated the % of the tokens represented by the named entity over the total number of tokens in the sentence;
4. We calculated the % of non-annotated tokens over the total tokens of the sentence (the stats are reported in the table below):

  | Statistic | non annotated tokens ratio (%) |
  |:---------:|:---------------------:|
  | mean  | 0,569256 |
  | std   | 0,357251 |
  | min   | -1,333333 |
  | 25%   | 0,333333 |
  | 50%   | 0,666667 |
  | 75%   | 0,863636 |
  | max   | 1,000000 |

6. We computed perplexity per sentence by using `pyplexity` library and `bigrams-bnc` (the stats are reported in the table below):

  | Statistic | Perplexity         |
  |-----------|--------------------|
  | mean  | 19.783,327042          |
  | std   | 101.641,029893         |
  | min   | 18,431019              |
  | 25%   | 246,208830             |
  | 50%   | 607,175027             |
  | 75%   | 2.466,794106           |
  | max   | 998.751,789474         |
   
We want to leverage the four measurements described above to define a threshold to filter out low-quality sentences.

#### Filter n.1 - Sentences with no named entities annotated
In the first instance, we should take care of those sentences in our dataset in which the annotators did not find any named entities. We want to remove the noisiest ones. The idea is to remove all the sentences of the kind that have =< 15 tokens. With regard to the remaining ones, we want to set a threshold based on perplexity's quartile values. We want to set a threshold at the 50% mark. We keep all the sentences having perplexity within the 50% mark.

#### Filter n.2 - Sentences with named entities annotated and no QID
As a second step, we should take care of those sentences in our dataset in which the annotators found named entities but could not link them to any QID. We want to remove the noisiest ones (the ones in which there is less context). The idea is to remove all the sentences of the kind that have =< 10 tokens. With regard to the remaining ones, we want to set a threshold based on _non-annotated tokens ratio_'s quartile values, calculated on the subset of entries of our benchmark having a named entity recognised but no QID. We want to set a threshold at the 25% mark. We keep all the sentences having _non-annotated tokens ratio_ value within the 25% mark.

#### Filter n.3 - Sentences with named entities annotated and QID
As a third step, we should take care of those sentences in our dataset in which the annotators found named entities and linked them to a QID. We want to remove the noisiest sentences (the ones in which there is less context). The idea is to remove all the sentences of the kind that have =< 10 tokens. With regard to the remaining ones, we want to set a threshold based on _non-annotated tokens ratio_'s quartile values, calculated on the subset of entries of our benchmark having a named entity recognised and linked to a QID. We want to set a threshold at the 25% mark of that subset. We keep all the sentences having _non-annotated tokens ratio_ value within the 25% mark.

### Statistics (_filtered_)

#### MHERCL v0.1 - Dataset Stats (_filtered_)

| Dataset | Lang. | #docs | #sents | #tokens |
|---------|-------|-------|--------|---------|
| MHERCL v0.1 (_filtered_) | EN  |  20 | 718 | 31.028 |


#### MHERCL v0.1 - Mentions Stats (_filtered_)

| _filtered_      | #mentions | types     | noisy        | linked (yes) | linked (no) |
|-------|-----------|-----------|---------------|--------------|-------------|
| all   |1.247 |_not applicable_ |161 |820 |427             |
| unique| 1.007| 49| 158| 427|580|

As summarised in the tables above, the annotators scrutinised 2181 sentences, extrapolated from 20 documents (historical periodicals), in which they annotated 2757 named entities belonging to 65 different types. The mentioned types demonstrate MHERCL music domain characterisation. 

1851 out of the 2757 named entities could be linked to a QID (67%), while 906 (33%) could not. Therefore, the percentage of "not linked" entities (entities that could not be linked to a QID) in MHERCL v0.1 is 30%. 502 named entities mentions contain errors due to OCR. Therefore, the percentage of noisy entities is 18%. Quantifying the noisy entities is important to facilitate downstream qualitative error analysis of NERC and EL systems and for comparison with other historical datasets.

## Annotation Guidelines

The sentences included in the sample described in the previous section underwent manual annotations thanks to the work of two internships (Foreign Languages and Literature undergraduate students) that have received _ad hoc_ training on the NERC and EL annotation task. The annotation work of the internships involved inspecting the sentences and identifying the named entities, eventually linking them to their corresponding WikiData ID (QID). Named entities were recognised and linked following a custom harmonisation of the AMR named entity annotations guidelines [[2]](https://amr.isi.edu/doc/amr-dict.html#named%20entity) and the _impresso_ guidelines, which are tailored for historical documents. In general, we assume a named entity is a real-world thing indicating a unique individual through a proper noun. The types were assigned according to the AMR annotation guidance instructions [[3]](https://www.isi.edu/~ulf/amr/lib/popup/ne-type-selection.html) and selected from the AMR named entity types list [[4]](https://www.isi.edu/~ulf/amr/lib/ne-types.html).

## Inter Annotator Agreement (Entity Linking Only)

We made two annotators independently annotate 18 sentences. We calculated Krippendorff's alpha for nominal metric on the resulting annotations using [Fast Krippendorf](https://github.com/pln-fing-udelar/fast-krippendorff). We obtained the following result: 0.6928783382789316.

## Release

MHERCL v0.1 (_filtered_) is released in tab-separated values (TSV) files (UTF-8 encoded). Its format has been designed to comply with HIPE-2022 data (which is based on IOB and CoNLL-U), facilitating future integration.

## Experiments

### Popularity bias 

MHERCL v0.1 (_filtered_) contains 1.007 unique named entity mentions, 10 of which are linked to 2 QIDs, 907 to 1.

### SotA Neural Entity Linkers 

We passed MHERCL v0.1 (_filtered_) sentences, and its manually annotated (gold) mentions, to SotA entity linkers. Results are summarised in the following table:

| Model  | Precision | Recall | F1 Measure |
|--------|-----------|--------|------------|
|[BLINK](https://github.com/facebookresearch/BLINK)|0.5068273092369477|0.7695121951219512|0.611138014527845|

