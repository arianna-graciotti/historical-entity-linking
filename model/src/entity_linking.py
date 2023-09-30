import tokenizations
import tqdm
import torch
import time
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
import argparse
import spacy
from spacy.tokens import Doc
#from thinc.api import set_gpu_allocator, require_gpu
import csv, os, re
from collections import Counter
from disambiguation import *
from pickle2sqlite import *
from transformers import BertModel, BertTokenizer

def load_vectors(path):
    return KeyedVectors.load_word2vec_format(datapath(path), binary=False)

def pooling(vectors, operation):
    if operation == 'mean':
        if len(vectors) > 1:
            vector = np.mean(vectors, axis=0)
            return vector.tolist()
        else:
            return vectors[0]
    else:
        print(operation, 'not implmented.')
        raise

def map_pos(pos):
    if pos == 'NOUN':
        return 'n'
    if pos == 'VERB':
        return 'v'
    if pos == 'ADJ':
        return 'a'
    if pos == 'ADV':
        return 'r'

def get_candidates(mention, aliases, dates, types, checkdates, checktypes, pubdate, ent_type):
    mention = mention.replace(' ', '_').lower()
    candidates = aliases.get(mention, [])
    if mention.startswith('mr._'):
        candidates += aliases.get(mention[4:], [])
    if mention.startswith('sir_'):
        candidates += aliases.get(mention[4:], [])
    #if candidates == []:
    #    candidates = [aliases[x] for x in aliases if mention in x]
    #    candidates = [y for x in candidates for y in x]
    if checkdates == 'Yes' and ent_type not in ['city', 'city-district', 'country', 'road', 'square', 'county', 'loc', 'local-region', 'continent', 'mountain', 'country-region', 'province']:
        candidates = [cand for cand in candidates if dates.get(cand, 0) < pubdate]
    if checktypes == 'Yes':
        candidates = [cand for cand in candidates if ent_type in types.get(cand, [ent_type])]
    candidates.append('NIL')
    return list(set(candidates))

def get_vectors_el(annotation_dict, input_sentence, aliases, el_keys, el_vectors, ares_vectors, map, dist, model, tokenizer, dates, types, checkdates, checktypes, pubdate):
    tokens = [t['form'] for t in annotation_dict.values()]
    inputs = tokenizer(input_sentence, return_tensors='pt')
    tr_tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    if len(tr_tokens) > 500:
        n_sents = max([t['sent_n'] for t in annotation_dict.values()])
        tr_tokens = []
        for n_sent in range(n_sents):
            tokens_ = [t['form'] for t in annotation_dict.values() if t['sent_n'] == n_sent]
            inputs_ = tokenizer(' '.join(tokens_), return_tensors='pt')
            tr_tokens+= tokenizer.convert_ids_to_tokens(inputs_['input_ids'][0])[1:-1]
            outputs_ = model(**inputs_)
            if n_sent == 0:
                cls = outputs_.last_hidden_state[:, 0, :]
                sep = outputs_.last_hidden_state[:, -1, :]
                last_hidden_states = outputs_.last_hidden_state[:, 1:-1, :]
            else:
                last_hidden_states = torch.concat((last_hidden_states, outputs_.last_hidden_state[:, 1:-1, :]), dim=-2)
        tr_tokens = ['[CLS]'] + tr_tokens + ['[SEP]']
        last_hidden_states = torch.concat((last_hidden_states, sep[None, :]), dim=-2)
        last_hidden_states = torch.concat((cls[None, :], last_hidden_states, ), dim=-2)
    else:
        outputs = model(**inputs)
        last_hidden_states = outputs.last_hidden_state

    a2b, _ = tokenizations.get_alignments(tokens, tr_tokens)
    #tr_vecs = doc._.trf_data.to_dict()['model_output']['last_hidden_state'][0]
    #X = doc._.trf_data.tensors[0][0]
    words = []
    senses = []
    word_vectors = []
    word_indices = []
    sense_vectors = []
    sense_dist = []
    all_senses = []
    all_senses_vectors = []
    all_senses_indices = []
    ent = []
    ents = []
    ent_types = []
    ents_iob = []
    algs = []
    b = 0
    for i, (v, alg) in enumerate(zip(annotation_dict.values(), a2b)):
        if v['ent_iob'].startswith('B-'):
            b=1
            ent = [v['form']]
            ent_iob = v['ent_iob'].split('-')[1]
            algs = alg
            widx = i
        elif v['ent_iob'].startswith('I-'):
            if b == 0:
                return None, None, None, None, None, None, None, None, None, None, None
            ent.append(v['form'])
            algs+=alg
            b=1
        elif (v['ent_iob'] == 'O' and len(ent) != 0) or (i == len(annotation_dict)-1 and len(ent) != 0):
            b=0
            e = '_'.join(ent)
            #candidates = [k for k, v in aliases.items() if e in v]

            candidates = get_candidates(e, aliases, dates, types, checkdates, checktypes, pubdate, ent_iob)
            # el_keys, el_vectors
            if len(candidates) != 0:
                keys = dict()
                for qid in candidates:
                    if qid != 'NIL':
                        keys[qid] = el_keys.get(qid, np.random.random(1536).tolist())
                    else:
                        keys[qid] = np.random.random(1536).tolist()
                #keys = [el_keys.get(qid, None) for qid in candidates]
                el_vectors_ = []
                for key in keys.keys():
                    if key not in [None, 'NIL'] and key in el_keys:
                        el_vectors_.append((key, el_vectors[el_keys[key]['idx']].tolist() + el_vectors[el_keys[key]['idx']].tolist()))
                    elif qid in [None, 'NIL'] or key == [None, 'NIL']:
                        #el_vectors_.append((qid, None))
                    #elif qid == 'NIL':
                        el_vectors_.append((qid, np.random.random(1536).tolist()))
                senses_ = [b[0] for b in el_vectors_]
                if senses_ == []:
                    continue
                try:
                    word_vectors.append(pooling([last_hidden_states[0][ti].tolist() for ti in algs], 'mean'))
                except:
                    word_vectors.append(np.random.random(768).tolist())
                all_senses_indices.append([])
                word_indices.append(widx)
                words.append(e)
                senses.append(senses_)
                for sense, key in zip(senses_, keys):
                    if sense not in all_senses:
                        all_senses.append(sense)
                        all_senses_indices[-1].append(len(all_senses)-1)
                        if key == 'NIL' or el_keys.get(key) == None:
                            all_senses_vectors.append(np.random.random(1536).tolist())
                        else:
                            all_senses_vectors.append(
                                el_vectors[el_keys[key]['idx']].tolist() + el_vectors[el_keys[key]['idx']].tolist())
                    else:
                        all_senses_indices[-1].append(all_senses.index(sense))
                sense_vectors.append([b[1] for b in el_vectors_])
                sense_dist_ = [el_keys.get(b[0])['cnt']+1 if b[0] in el_keys and keys.get(b[0]) != None and b[0] != 'NIL' else 1 for b in el_vectors_]
                sense_dist.append([s/float(sum(sense_dist_)) for s in sense_dist_])
                ents.append(e)
                ent_types.append('entity')
                ents_iob.append(ent_iob)
            ent = []
            algs = []
        if v['ent_iob'] == 'O' and map_pos(v['pos']) in ['n', 'v', 'a', 'r']:
            #print('content word')
###############
            bns = map.get('_'.join([v['lemma'],map_pos(v['pos'])]))
            if bns:
                sense_vectors_ = [(bn, ares_vectors[bn].tolist() if bn in ares_vectors else None) for bn in bns ]
                senses_ = [b[0] for b in sense_vectors_ if b[1] != None]
                if senses_ == []:
                    continue
                try:
                    #word_vectors.append(pooling([tr_vecs[ti].tolist() for ti in doc._.trf_data.align[i].data[0]], 'mean'))
                    #word_vectors.append(pooling([tr_vecs[ti].tolist() for ti in alg], 'mean'))
                    word_vectors.append(pooling([last_hidden_states[0][ti].tolist() for ti in alg], 'mean'))
                except:
                    print('Word Misalignment')
                    continue
                    #return None, None, None, None, None, None, None, None, None, None, None
                all_senses_indices.append([])
                words.append(v['form'])
                ents.append(v['lemma'])
                ent_types.append('concept')
                word_indices.append(i)
                senses.append(senses_)
                for sense in senses_ :
                    all_senses_vectors.append(ares_vectors[sense].tolist())
                    if sense not in all_senses:
                        all_senses.append(sense)
                        all_senses_indices[-1].append(len(all_senses)-1)
                    else:
                        all_senses_indices[-1].append(all_senses.index(sense))
                sense_vectors.append([b[1] for b in sense_vectors_ if b[1] != None])
                sense_dist_ = [dist.get(b[0], 0) + 1 for b in sense_vectors_ if b[1] != None]
                sense_dist.append([s/float(sum(sense_dist_)) for s in sense_dist_])
                #print(bn.get('bn'))
    #return [word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist]
###############

    # len(words), len(word_indices), len(word_vectors), len(senses), len(sense_vectors), len(sense_dist)
    if len(words) == len(word_indices) and len(word_vectors) == len(senses) and len(sense_vectors) == len(sense_dist):
        return [words, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist, ent_types, ents_iob]
    else:
        return None, None, None, None, None, None, None, None, None, None, None


def get_map(lang):
    if lang == 'en':
        with open('model/vocabs/babelnet_synsets.tsv', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            rows = [r for r in reader]
        map = dict()
        for row in rows:
            words = row[1].strip('][').split(', ')
            synset = row[0]
            for word in words:
                map.setdefault('_'.join([word, synset[-1]]),[])
                map['_'.join([word, synset[-1]])].append(synset)
    else:
        with open('model/vocabs/'+ lang+'_map.tsv', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            rows = [r for r in reader]
        map = dict()
        for row in rows:
            map.setdefault(row[0], dict())
            map[row[0]].setdefault('bn', [])
            map[row[0]].setdefault('wn', [])
            map[row[0]].setdefault('wn2020', [])
            map[row[0]]['bn'].append(row[1])
            for wn in row[2].strip('][').split(','):
                wn = wn.strip()
                if wn.startswith('wn2020:'):
                    map[row[0]]['wn2020'].append(wn)
                if wn.startswith('wn:'):
                    map[row[0]]['wn'].append(wn)
    return map

def get_dist():
    with open('model/vocabs/semcor_map.tsv', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = [r for r in reader]
    dist = Counter([r[1] for r in rows])
    return dist



# def annotate_and_print(it_par, nlp, Texts, lang, limit, conn, ares_vectors, map, dist, model, tokenizer):
#     save_n = 0
#     for par in tqdm(nlp.pipe(it_par, batch_size=50)):
#         save_n+=1
#         word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist = get_vectors_el(par, ares_vectors, map, dist, model, tokenizer)
#         if word_indices == None:
#             continue
#         if len(word_vectors) == 0:
#             continue
#         if len(all_senses_vectors) == 0:
#             continue
#         P = wsdg(par, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist)
#         annotation = dict()
#         annotation['sent'] = par.text
#         for i, token in enumerate(par):
#             if 'bn__' in token.text:
#                 page_id = token.text
#                 continue
#             if 'sent_' in token.text:
#                 sent_id = token.text
#                 continue
#             #annotation.setdefault(sent_id, dict())
#             #annotation[sent_id]['sent'] = sent.text
#
#
#             token_id = 'token_' + str(i)
#             annotation.setdefault(token_id, dict())
#             if token.text == '\n':
#                 continue
#             else:
#                 annotation[token_id]['form'] = token.text
#                 annotation[token_id]['lemma'] = token.lemma_
#                 annotation[token_id]['pos'] = token.pos_
#                 annotation[token_id]['offset'] = ''
#                 if i in word_indices:
#                     sense_idx = P[word_indices.index(i)].argmax()
#                     annotation[token_id]['offset'] = all_senses[sense_idx]
#                 annotation[token_id]['ent_type'] = token.ent_type_
#                 annotation[token_id]['ent_iob'] = token.ent_iob_
#         if sent_id != '' and page_id != 0:
#
#             c = conn.cursor()
#             #insert_into_db(page_id, sent_id, annotation, c)
#             sent_id = ''
#             page_id = ''


def load_el_vectors(path):
    import torch
    vectors_keys = dict()
    with open(path + 'keys.tsv') as f:
        for idx, line in enumerate(f):
            key, *other = line.rstrip().split('\t')
            cnt = int(other[0]) if len(other) else -1
            vectors_keys[key] = {'idx' : idx, 'cnt' : cnt}

    embeddings = torch.load(path+'vectors.pt', map_location='cpu')
    next(iter(vectors_keys.items()))
    return [vectors_keys, embeddings]

def load_wikip_wikid(path):
    wikipedia_wikidata = dict()
    with open(path+'wikipedia_wikidata.tsv') as f:
        for line in f:
            wiki_id, wiki_title, qid = line.rstrip().split('\t')
            wikipedia_wikidata[wiki_title] = qid
    return wikipedia_wikidata

def load_wikid_wikip(path):
    wikidata_wikipedia = dict()
    with open(path+'wikipedia_wikidata.tsv') as f:
        for line in f:
            wiki_id, wiki_title, qid = line.rstrip().split('\t')
            if qid not in wikidata_wikipedia:
                wikidata_wikipedia[qid] = wiki_title
    return wikidata_wikipedia

def splitCamel(mention):
    words = [[mention[0]]]
    for c in mention[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)
    words = [''.join(word) for word in words]
    return '_'.join(words).lower()

def get_dates():
    dates = dict()
    with open('model/vocabs/wikidata_dates.tsv') as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [line for line in reader]
    for line in lines:
        if line[1].isnumeric():
            dates[line[0]] = int(line[1])
    return dates

def get_types():
    dates = dict()
    with open('model/vocabs/wikidata_dates.tsv') as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [line for line in reader]
    for line in lines:
        if '-' in line[2]:
            dates.setdefault(line[0], [])
            for t in [l[2:].lower() for l in line[2].split(',')]:
                if t not in dates[line[0]]:
                    dates[line[0]].append(t)
    return dates

def load_aliases(path):
    aliases = dict()
    with open(path+'data/alias/alias.en') as f:
        for line in f:
            line = line.strip().replace(' || ', ' ||| ').split("|||")
            qid = line[0].strip()
            for a in line[2:]:
                a = a.strip().replace(' ', '_').lower()
                aliases.setdefault(a, [])
                if a not in aliases[a] + ['']:
                    aliases[a].append(qid)
    with open(path + 'data/alias/babelnet_qids.tsv') as f:
        for line in f:
            line_ = line.strip().split('\t')
            qid = line_[0].strip()
            mentions = [m for m in line_[1].strip('][').split(', ') if m not in ['']]
            for a in mentions:
                a = a.strip().replace(' ', '_').lower()
                aliases.setdefault(a, [])
                if a not in aliases[a] + ['']:
                    aliases[a].append(qid)
    with open(path + 'wikipedia_wikidata.tsv') as f:
        for line in f:
            line = line.strip().split('\t')
            qid = line[2]
            #if qid[0] not in ['Q','q']:
            #    print()
            if line[1] not in ['']:
                mention = splitCamel(line[1])
                aliases.setdefault(mention, [])
                if qid not in aliases[mention]:
                    aliases[mention].append(qid)
    return aliases

def wikidata_entity(wikipedia_wikidata : dict, wikipedia_wikidata_lower : dict, mention):
    mention = mention.replace(" ", "_")
    if mention in wikipedia_wikidata:
        return wikipedia_wikidata[mention]
    if mention.lower() in wikipedia_wikidata_lower:
        return wikipedia_wikidata_lower[mention]
    return None

def get_aliases(wikipedia_wikidata):
    aliases = dict()
    for k, v in wikipedia_wikidata.items():
        aliases.setdefault(v, [])
        aliases[v].append(k)
    return aliases

def annotation2dict(annotation, args):
    annotation_dict = {}
    if args.ds == 'hipe':
        nlp = spacy.load(args.spacy_model)
        nlp.add_pipe('sentencizer')
        sent = [t[0] for t in annotation]
        doc = Doc(nlp.vocab, sent)
        sents = nlp(doc)
        spacy_annotation = [[(t.pos_, t.lemma_, sent_num) for t in sent] for sent_num, sent in enumerate(sents.sents)]
        spacy_annotation_flatten = [t for sent in spacy_annotation for t in sent ]
    for i, tok_ann in enumerate(annotation):
        token_id = 'token_'+str(i)
        if args.ds == 'mhercl':
            annotation_dict.setdefault(token_id, dict())
            annotation_dict[token_id]['form'] = tok_ann[0]
            annotation_dict[token_id]['lemma'] = tok_ann[3]
            annotation_dict[token_id]['pos'] = tok_ann[4]
            annotation_dict[token_id]['ent_qid'] = tok_ann[2]
            annotation_dict[token_id]['ent_iob'] = tok_ann[1]
        elif args.ds == 'hipe':
            annotation_dict.setdefault(token_id, dict())
            annotation_dict[token_id]['form'] = tok_ann[0]
            annotation_dict[token_id]['NE-COARSE-LIT'] = tok_ann[1]
            annotation_dict[token_id]['ent_iob'] = tok_ann[1]
            annotation_dict[token_id]['NE-COARSE-METO'] = tok_ann[2]
            annotation_dict[token_id]['NE-FINE-LIT'] = tok_ann[3]
            annotation_dict[token_id]['NE-FINE-METO'] = tok_ann[4]
            annotation_dict[token_id]['NE-FINE-COMP'] = tok_ann[5]
            annotation_dict[token_id]['NE-NESTED'] = tok_ann[6]
            annotation_dict[token_id]['NEL-LIT'] = tok_ann[7] # corresponds to ent_qid
            annotation_dict[token_id]['ent_qid'] = tok_ann[7]  # corresponds to ent_qid
            annotation_dict[token_id]['NEL-METO'] = tok_ann[8]
            annotation_dict[token_id]['MISC'] = tok_ann[9]
            annotation_dict[token_id]['lemma'] = spacy_annotation_flatten[i][1]
            annotation_dict[token_id]['pos'] = spacy_annotation_flatten[i][0]
            annotation_dict[token_id]['sent_n'] = spacy_annotation_flatten[i][2]
    return annotation_dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ares_path', type=str, default='/media/rocco/34b2975e-ad76-46e8-b024-3729a4fc15ac/rocco2/rocco/polifonia_corpus/sense_embeddings/ares_embedding/ares_bert_base_multilingual.txt')
    parser.add_argument('--entity_linking_data_path', type=str,
                        default='/media/rocco/34b2975e-ad76-46e8-b024-3729a4fc15ac/rocco2/rocco/polifonia_corpus/entity_linking/')
    parser.add_argument('--base_data_path', type=str,
                        default='/media/rocco/34b2975e-ad76-46e8-b024-3729a4fc15ac/rocco2/rocco/python/Polifonia_Corpus_Data/Polifonia_Books_Corpus')
    parser.add_argument('--spacy_model', type=str,
                        default='en_core_web_sm') #fr_core_news_lg #'es_core_news_lg'
    parser.add_argument('--limit', type=str, default='No')
    parser.add_argument('--ds', type=str, default='mhercl')
    parser.add_argument('--checkdates', type=str, default='No')
    parser.add_argument('--disambiguation_type', type=str, default='rep_dyn')
    return parser.parse_args()

def get_hel_sents(path):
    with open(path) as f:
        reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
        rows = [row for row in reader]
    sent = []
    for i, row in enumerate(rows):
        if row == [] or i == len(rows):
            if sent != []:
                yield sent
                sent = []
        else:
            sent.append(row)

if __name__ == '__main__':
    args = parse_args()
    lang = args.spacy_model.split('_')[0]
    load = False
    aliases = load_aliases(args.entity_linking_data_path)
    el_keys, el_vectors = load_el_vectors(args.entity_linking_data_path)
    ares_vectors = load_vectors(args.ares_path)
    map = get_map(lang)
    dist = get_dist()
    dates = get_dates()
    types = get_types()

    #set_gpu_allocator("pytorch")
    #require_gpu(0)
    model = BertModel.from_pretrained('bert-base-multilingual-cased')
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model.eval()
    if load == True:
        print('LOADING VECTORS...')
        wikipedia_wikidata = load_wikip_wikid(args.entity_linking_data_path)
        wikidata_wikipedia = load_wikid_wikip(args.entity_linking_data_path)
    print('LINKING...')
    for ds in ['mhercl', 'hipe']:
        args.ds = ds
        for disambiguation_type in ['dot', 'rep_dyn']:
            args.disambiguation_type = disambiguation_type
            for checkdates in ['Yes', 'No']:
                args.checkdates = checkdates
                for checktypes in ['Yes', 'No']:
                    args.checktypes = checktypes
                    if args.ds == 'mhercl':
                        sents = get_hel_sents('benchmark/v0.1/conll_reconsolidated_advanced_filtering_020823_noduplicates.tsv')
                        start = 3
                    elif args.ds == 'hipe':
                        sents = get_hel_sents('benchmark/clef/HIPE-2022-v2.1-hipe2020-test-en.tsv')
                    with open('model/src/results/predictions_' + args.ds + "_model-" + args.disambiguation_type + "_checks-" + '_'.join([checkdates, args.checktypes]) + '.tsv', 'w') as fw, open('model/src/results/candidates_' + args.ds + "_model-" + args.disambiguation_type + "_checks-" + '_'.join([checkdates, args.checktypes]) + '.tsv', 'w') as f_cand:
                        f_cand.write('\t'.join(['Token', 'Gold annotation', 'Candidates', 'Prediction', 'Gold ann in candidates?', 'Correct?', 'sent id', 'sent date'])+'\n')
                    with open('model/src/results/predictions_' + args.ds + "_model-" + args.disambiguation_type + "_checks-" + '_'.join([checkdates, args.checktypes]) + '.tsv', 'w') as fw, open('model/src/results/candidates_' + args.ds + "_model-" + args.disambiguation_type + "_checks-" + '_'.join([checkdates, args.checktypes]) + '.tsv', 'a') as f_cand:

                        for sent in tqdm(sents):
                            if args.ds == 'mhercl':
                                sent_id = sent[0][0]
                                if sent_id in ['#document_id:TheHarmonicon__1832-012.txt_996']:
                                    print()
                                pubdate = sent[1][0]
                                try:
                                    year = int(pubdate.split(':')[1][:4])
                                except:
                                    year = 3000
                                    print('Wrong year', pubdate)
                                input_sentence = sent[2][0].split('#sent_text:')[1]
                                annotation_dict = annotation2dict([t for t in sent[3:]], args)
                            #annotation_dict = annotation2dict(sent[2].split('\n'))
                            elif args.ds == 'hipe':
                                sent_id = sent[0][0]
                                if 'sn82014385-1810-05-30-a-i0001' in sent_id:
                                    print()
                                pubdate = sent[1][0]
                                try:
                                    year = int(pubdate.split(' = ')[1][:4])
                                except:
                                    year = 3000
                                    print('Wrong year', pubdate)
                                input_sentence = ' '.join([t[0] for t in sent[11:]])
                                annotation_dict = annotation2dict([t for t in sent[11:]], args)
                            if len(annotation_dict) == 0:
                                continue
                            #print('GET VECTORS')
                            t0 = time.time()
                            ents, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist, ent_types, ents_iob = get_vectors_el(
                                annotation_dict, input_sentence, aliases, el_keys, el_vectors, ares_vectors, map, dist, model, tokenizer, dates, types, checkdates, args.checktypes, year)
                            #print('--X', time.time()-t0)
                            if ents == None:
                                P = None
                            elif 'entity' in ent_types and len(all_senses_vectors) != 0:
                                if args.disambiguation_type == 'dot':
                                    P = dot(annotation_dict, word_indices, word_vectors, senses, sense_vectors, all_senses,
                                             all_senses_vectors,
                                             all_senses_indices, sense_dist)
                                else:
                                    P = wsdg(annotation_dict, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors,
                                         all_senses_indices, sense_dist)
                            else:
                                P = np.array([])
                            for i, (token_id, token) in enumerate(annotation_dict.items()):
                                if word_indices != None:
                                    if annotation_dict[token_id]['ent_iob'] == 'O':
                                        b=0
                                    if i in word_indices and P.size != 0:
                                        sense_idx = P[word_indices.index(i)].argmax()
                                        b=1
                                        candidates = [all_senses[idx] for idx in all_senses_indices[word_indices.index(i)]]
                                        answer = all_senses[sense_idx]
                                        gold_annotation = token['ent_qid']
                                        mention = token['form']
                                        for mention_id in range(i+1, 1000):
                                            if 'token_' + str(mention_id) in annotation_dict:
                                                if annotation_dict['token_' + str(mention_id)]['ent_iob'].startswith('I-'):
                                                    mention += ' ' + annotation_dict['token_' + str(mention_id)]['form']
                                                else:
                                                    break
                                            else:
                                                break
                                        if gold_annotation.startswith('Q') or gold_annotation.startswith('N'):
                                            f_cand.write('\t'.join([mention, gold_annotation, ' '.join(candidates), answer, str(gold_annotation in candidates), str(gold_annotation == answer), sent_id, pubdate, token['ent_iob']])+'\n')
                                        annotation_dict[token_id]['candidates'] = candidates
                                        annotation_dict[token_id]['ent_qid'] = all_senses[sense_idx]
                                    if b == 1 and annotation_dict[token_id]['ent_iob'].startswith('I-'):
                                        annotation_dict[token_id]['ent_qid'] = all_senses[sense_idx]
                                else:
                                    if gold_annotation.startswith('Q') or gold_annotation.startswith('N'):
                                        mention = token['form']
                                        for mention_id in range(i, 1000):
                                            if annotation_dict['token_' + str(mention_id)]['ent_iob'].startswith('I-'):
                                                mention += ' ' + annotation_dict['token_' + str(mention_id)]['form']
                                            else:
                                                break
                                        f_cand.write('\t'.join([mention, gold_annotation, ' '.join(candidates), 'None',
                                                                str(gold_annotation in candidates), str(gold_annotation == answer), sent_id, pubdate, token['ent_iob']]) + '\n')
                                    annotation_dict[token_id]['ent_qid'] = 'None'
                                    print(annotation_dict[token_id], 'ent_qid = None')
                                assert token['form'] == annotation_dict[token_id]['form']
                            annotation_text = annotation2text(annotation_dict, args)
                            if args.ds == 'mhercl':
                                fw.write(sent[0][0] + '\n')
                                fw.write(sent[1][0] + '\n')
                                fw.write(sent[2][0] + '\n')
                                fw.write(annotation_text + '\n')
                            elif args.ds == 'hipe':
                                fw.write(sent[0][0] + '\n')
                                fw.write(sent[1][0] + '\n')
                                fw.write(sent[2][0] + '\n')
                                fw.write(sent[3][0] + '\n')
                                fw.write(sent[4][0] + '\n')
                                fw.write(sent[5][0] + '\n')
                                fw.write(sent[6][0] + '\n')
                                fw.write(sent[7][0] + '\n')
                                fw.write(sent[8][0] + '\n')
                                fw.write(sent[9][0] + '\n')
                                fw.write(sent[10][0] + '\n')
                                fw.write(annotation_text + '\n')