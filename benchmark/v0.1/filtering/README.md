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
| 164 | 111 (52%) | 53 (48%) |

Given the quality of coreference resolution output, we decided to discard those annotations related to a named entity resulting from the substitution of a pronoun by the application of the coreference resolution.

#### Is the sentence enough to infer the QID?
We asked the annotators to do a second-round of checks to make sure that the input sentence alone was enough to infer the QID. For those sentence which did not provide enough context to infer the QID, the annotators provided some more sentences from the original document. These are the statistics:

| Is the sentence enough to infer the QID? ||
| --- | --- | 
| yes | TBD |
| no | TBD |

We filter out those sentences from the filtered MHERCL v0.1 release. They are released separately as they can serve for further experiments.

### Advanced filtering

We would like to remove low quality sentences from our benchmark. We computed 3 measures:

1. We measured the sentences length (token numbers), by using
2. We measured the annotated named entity length (token numbers), by using
3. We calculated the % of the tokens represented by the named entity over the total number of tokens of the sentence
4. We computed perplexity per each sentence.

We want to leverage the 4 measurements described above to define a threshold to filter out low quality sentences.
