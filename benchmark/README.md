# MHERCL v0.1 - Benchmark

## Exploratory Study

As the PKE framework automatically recognises named entities in its text-to-AMR parsing step, we ran a preliminary experiment to evaluate the off-the-shelf performance of the PKE text-to-AMR parser and its embedded entity linker, BLINK. We focused on a sample of 2205 sentences taken from the _Periodicals_ module of the PTC and on named entities of type person (pNE). The results are reported in the Table below and shared in a [TSV file](benchmark/preliminary_study/ptc_sample_pne_preliminary_study.tsv) in this repository.

#### Table reporting statistics about the off-the-shelf quality of [PKE](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework on EL of _person named entities_ in a [PTC](https://github.com/polifonia-project/Polifonia-Corpus) sample.

| #sents      | pNE mentions (#recognised) |   pNE mentions (#linked)    | pNE QID (#found)  |        pNE QID (#not found)   | pNE DoB  (#plausible)  | pNE DoB  (#implausible)|pNE DoB  (#not found)|
|-------|--------------|-------|----------|-----------|------------|--------------|-----------|
| 2205 | 2262         | 2108 | 2006    | 102   | 1199       | 203         | 604     |

## Sampling

The annotated sentences of MHERCL v0.1 were extrapolated from the [Polifonia Textual Corpus (PTC)](https://github.com/polifonia-project/Polifonia-Corpus). They originate from a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. They were processed through the [Polifonia Knowledge Extractor (PKE)](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) and are part of the [Filtered AMR Graphs Bank] (https://zenodo.org/record/7025779\#.ZDls8OxBy3I).

## Annotation Guidelines

MHERCL v0.1 sentences are manually annotated. The annotations focus on Named Entities Recognition, Classification and Linking. Thanks to the work of two interns (Foreign Languages and Literature undergraduate students, both Italian native speakers, one graduating in English and Spanish Language and Literature, the other graduating in Russian and Spanish) who have received training on the NERC and EL annotation task. 

Generally, the annotation work was performed under the criteria that a named entity is a real-world thing indicating a unique individual through a proper noun. The annotation work of the interns involved inspecting the sentences and identifying the named entities, eventually linking them to their corresponding Wikidata ID (QID).

|named entity type   |#occurrences|
|------------------------------|------------------------|
| person                       | 621                  |
| city                         | 143                  |
| music                        | 68                   |
| country                      | 42                   |
| organization                 | 39                   |
| opera                        | 38                   |
| building                     | 29                   |
| work-of-art                  | 28                   |
| road                         | 22                   |
| publication                  | 19                   |
| worship-place                | 19                   |
| book                         | 14                   |
| theatre                      | 12                   |
| city-district                | 11                   |
| company                      | 9                    |
| nan                          | 9                    |
| school                       | 7                    |
| theater                      | 7                    |
| university                   | 5                    |
| magazine                     | 4                    |
| government-organization      | 4                    |
| festival                     | 3                    |
| college                      | 3                    |
| street                       | 3                    |
| facility                     | 3                    |
| local-region                 | 3                    |
| museum                       | 3                    |
| symphony                     | 2                    |
| square                       | 2                    |
| newspaper                    | 2                    |
| concert                      | 2                    |
| county                       | 2                    |
| person                       | 2                    |
| mountain                     | 2                    |
| religious-group              | 2                    |
| persona                      | 1                    |
| thing                        | 1                    |
| empire                       | 1                    |
| hotel                        | 1                    |
| state                        | 1                    |
| event                        | 1                    |
| province                     | 1                    |
| country-region               | 1                    |
| military                     | 1                    |
| song                         | 1                    |
| institution                  | 1                    |
| person (fictional character) | 1                    |
| continent                    | 1                    |
| journal                      | 1                    |
| language                     | 1                    |
| Grand total       | 1199         |

Named entities were recognised, classified and linked following the [AMR named entity annotations guidelines](https://amr.isi.edu/doc/amr-dict.html\#named\%20entity).
The types were assigned according to the [AMR annotation guidance instructions](https://www.isi.edu/~ulf/amr/lib/popup/ne-type-selection.html) and extrapolated from the [AMR named entity types list](https://www.isi.edu/~ulf/amr/lib/ne-types.html). 

A full list of the types used for NEs classification is in the table below.

## Inter-annotator Agreement

| #sents | #tokens (Tot.) | # matching tokens (Annotated) | # unmatching tokens (Annotated) | Krippendorf's alpha |
|--------------------------|----------------------------------|------------------------------------------|------------------|--------------------|
| 27 | 472        | 40                 | 8              | 0,82 |


Inter-annotator agreement (IAA) measures the reliability of human annotations by estimating consistency among annotators. To measure IAA, we made two annotators independently annotate 27 sentences. We calculated Krippendorff's alpha for nominal metric on the resulting annotations using [Fast Krippendorf](https://github.com/pln-fing-udelar/fast-krippendorff). We opted for Krippendorff's alpha for its flexibility and resilience in handling missing values. We obtained the following result: 0.82654. 

## Statistics

#### MHERCL v0.1 - Dataset Stats

| Dataset                     | Lang. | #docs | #sents | #tokens |
|-----------------------------|-------|--------|---------|----------|
| MHERCL v0.1 | EN    | 21   | 715   | 15.734 |


#### MHERCL v0.1 - Named Entities Superficial Mentions Stats


|        | #mentions | #types | noisy    | NIL      |
|--------|-----------|---------|----------|----------|
| all    | 1.199   | -       | 0,125  | 0,3403|
| unique | 975     | 49    | 0,1527 | 0,4051 |

As summarised in the tables above, MHERCL v0.1 is made of 715 sentences, extrapolated from 21 documents (historical periodicals). MHERCL v0.1 includes 975 unique named entities belonging to49$ different types. On the total of annotated named entity mentions, 34% could not be linked to a QID. Those are cases in which the annotators could not identify a Wikidata entry corresponding to the named entity mention. Those cases are annotated with the label NIL. On the total of annotated named entity mentions, 12,5% are _noisy_, namely impacted by errors due to OCR.


## Format

```#document_date:1873
#sent_text:A native of Parma, ateighteen years of age ‘Jong was received into the Conservatory of Music of that town, where ‘Jong soon made himself.a name as the most promising pupil of the institution.
A	O	_	a	DET
native	O	_	native	NOUN
of	O	_	of	ADP
Parma	B-city	Q2683	Parma	PROPN
,	O	_	,	PUNCT
ateighteen	O	_	ateighteen	NUM
years	O	_	year	NOUN
of	O	_	of	ADP
age	O	_	age	NOUN
‘	O	_	'	PUNCT
Jong	B-person	NIL	Jong	PROPN
was	O	_	be	AUX
received	O	_	receive	VERB
into	O	_	into	ADP
the	O	_	the	DET
Conservatory	B-school	Q1439627	Conservatory	PROPN
of	I-school	Q1439627	of	ADP
Music	I-school	Q1439627	Music	PROPN
of	O	_	of	ADP
that	O	_	that	DET
town	O	_	town	NOUN
,	O	_	,	PUNCT
where	O	_	where	SCONJ
‘	O	_	'	PUNCT
Jong	B-person	NIL	Jong	PROPN
soon	O	_	soon	ADV
made	O	_	make	VERB
himself.a	O	_	himself.a	PRON
name	O	_	name	NOUN
as	O	_	as	ADP
the	O	_	the	DET
most	O	_	most	ADV
promising	O	_	promising	ADJ
pupil	O	_	pupil	NOUN
of	O	_	of	ADP
the	O	_	the	DET
institution	O	_	institution	NOUN
.	O	_	.	PUNCT


