import pandas as pd
import re
import pickle
import requests
import blink.main_dense as main_dense
import argparse
import csv
import os
import tqdm

from sklearn.preprocessing import LabelEncoder
os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
# Setting up the device for GPU usage

from torch import cuda
device = 'cuda:0' if cuda.is_available() else 'cpu'

import torch
print(torch.__version__)

print(torch.version.cuda)
print(torch.cuda.is_available()

'''
DATA PREPARATION
'''

clef_hipe_test = pd.read_csv('input/HIPE-2022-v2.1-hipe2020-test-en.tsv', sep='\t')
clef_hipe_test = clef_hipe_test.astype(str)
clef_hipe_test = clef_hipe_test[clef_hipe_test["TOKEN"].str.startswith("#")==False ].reset_index(drop=True)
clef_hipe_test = clef_hipe_test[clef_hipe_test["TOKEN"].str.contains("\t")==False ].reset_index(drop=True)
len(clef_hipe_test[clef_hipe_test["NE-COARSE-LIT"].str.match('^B-')])

def transform_clefconll_to_blinktsv(df):
    df = df.iloc[1:]

    data_to_link = []
    mention = []
    context_left = []
    context_right = []
    in_mention = False
    id_counter = 0

    for index, row in df.iterrows():
        token, ne_coarse_lit, misc = row['TOKEN'], row['NE-COARSE-LIT'], row['MISC']

        # If NoSpaceAfter in MISC, adjust token
        space_after = '' if "NoSpaceAfter" in misc else ' '

        # Start of a mention
        if ne_coarse_lit.startswith('B'):
            if in_mention:
                data_to_link.append({
                    "id": id_counter,
                    "label": "unknown",
                    "label_id": -1,
                    "context_left": ''.join(context_left).lower(),
                    "mention": ''.join(mention).lower(),
                    "context_right": ''.join(context_right).lower()
                })
                id_counter += 1
                mention = []
                context_left = []
                context_right = []

            mention.append(token + space_after)
            in_mention = True

            # Getting the context_left
            prev_index = index - 1
            while prev_index >= df.index[0] and "EndOfSentence" not in df.loc[prev_index, 'MISC']:
                context_left.insert(0, df.loc[prev_index, 'TOKEN'] + (
                    '' if "NoSpaceAfter" in df.loc[prev_index, 'MISC'] else ' '))
                prev_index -= 1

        # Inside a mention
        elif ne_coarse_lit.startswith('I') and in_mention:
            mention.append(token + space_after)

        # Outside a mention
        elif in_mention:
            in_mention = False
            context_right.append(token + space_after)

            # Getting the context_right
            next_index = index + 1
            while next_index <= df.index[-1] and "EndOfSentence" not in df.loc[next_index, 'MISC']:
                context_right.append(
                    df.loc[next_index, 'TOKEN'] + ('' if "NoSpaceAfter" in df.loc[next_index, 'MISC'] else ' '))
                next_index += 1

            data_to_link.append({
                "id": id_counter,
                "label": "unknown",
                "label_id": -1,
                "context_left": ''.join(context_left).lower(),
                "mention": ''.join(mention).lower(),
                "context_right": ''.join(context_right).lower()
            })
            id_counter += 1
            mention = []
            context_left = []
            context_right = []

    return data_to_link


def transform_to_data_to_link_withLabels(df):
    df = df.iloc[1:]

    data_to_link = []
    mention = []
    context_left = []
    context_right = []
    in_mention = False
    id_counter = 0
    current_nel_lit = None

    for index, row in df.iterrows():
        token, ne_coarse_lit, misc, nel_lit = row['TOKEN'], row['NE-COARSE-LIT'], row['MISC'], row['NEL-LIT']

        # If NoSpaceAfter in MISC, adjust token
        space_after = '' if "NoSpaceAfter" in misc else ' '

        # Start of a mention
        if ne_coarse_lit.startswith('B'):
            if in_mention:
                data_to_link.append({
                    "id": id_counter,
                    "label": "unknown",
                    "label_id": current_nel_lit,  # Use the value of NEL-LIT column
                    "context_left": ''.join(context_left).lower(),
                    "mention": ''.join(mention).lower(),
                    "context_right": ''.join(context_right).lower()
                })
                id_counter += 1
                mention = []
                context_left = []
                context_right = []

            mention.append(token + space_after)
            in_mention = True
            current_nel_lit = nel_lit  # Capture the NEL-LIT value for the beginning of the mention

            # Getting the context_left
            prev_index = index - 1
            while prev_index >= df.index[0] and "EndOfSentence" not in df.loc[prev_index, 'MISC']:
                context_left.insert(0, df.loc[prev_index, 'TOKEN'] + (
                    '' if "NoSpaceAfter" in df.loc[prev_index, 'MISC'] else ' '))
                prev_index -= 1

        # Inside a mention
        elif ne_coarse_lit.startswith('I') and in_mention:
            mention.append(token + space_after)

        # Outside a mention
        elif in_mention:
            in_mention = False
            context_right.append(token + space_after)

            # Getting the context_right
            next_index = index + 1
            while next_index <= df.index[-1] and "EndOfSentence" not in df.loc[next_index, 'MISC']:
                context_right.append(
                    df.loc[next_index, 'TOKEN'] + ('' if "NoSpaceAfter" in df.loc[next_index, 'MISC'] else ' '))
                next_index += 1

            data_to_link.append({
                "id": id_counter,
                "label": "unknown",
                "label_id": current_nel_lit,  # Use the value of NEL-LIT column
                "context_left": ''.join(context_left).lower(),
                "mention": ''.join(mention).lower(),
                "context_right": ''.join(context_right).lower()
            })
            id_counter += 1
            mention = []
            context_left = []
            context_right = []

    return data_to_link


data_to_link_noLabels = transform_clefconll_to_blinktsv(clef_hipe_test)
data_to_link_wLabels = transform_to_data_to_link_withLabels(clef_hipe_test)

'''
BLINK EXECUTION
'''
models_path = "models/"  # the path where you stored the BLINK models
output_path = "output/"

config = {
    "test_entities": None,
    "test_mentions": None,
    "interactive": False,
    "top_k": 10,
    "biencoder_model": models_path + "biencoder_wiki_large.bin",
    "biencoder_config": models_path + "biencoder_wiki_large.json",
    "entity_catalogue": models_path + "entity.jsonl",
    "entity_encoding": models_path + "all_entities_large.t7",
    "crossencoder_model": models_path + "crossencoder_wiki_large.bin",
    "crossencoder_config": models_path + "crossencoder_wiki_large.json",
    "fast": False,  # set this to be true if speed is a concern
    "output_path": output_path  # logging directory
}

args = argparse.Namespace(**config)

models = main_dense.load_models(args, logger=None)

_, _, _, _, _, predictions, scores, = main_dense.run(args, None, *models, test_data=data_to_link_noLabels)


def get_wikidata_qid(wikipedia_page):
    wikipedia_api_url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'prop': 'pageprops',
        'ppprop': 'wikibase_item',
        'redirects': 1,
        'format': 'json',
        'titles': wikipedia_page
    }

    response = requests.get(wikipedia_api_url, params=params)
    response.raise_for_status()  # Ensure we got a successful response

    pages = response.json()['query']['pages']

    # The pageprops property contains the wikibase_item, which is the QID
    for page in pages.values():
        return page.get('pageprops', {}).get('wikibase_item')

    return None  # No QID found


def create_dict_id_blink(data_to_link, predictions, scores):
    dict_id = {}

    for i, data in enumerate(data_to_link):
        if not data['mention']:  # Skip if mention value is empty string
            continue
        mention = data['mention']
        id_ = data['id']
        max_score_index = scores[i].index(max(scores[i]))  # Get the index of the highest score
        prediction = predictions[i][max_score_index]

        # Get the QID for the prediction
        qid = get_wikidata_qid(prediction)

        if id_ not in dict_id:
            # dict_id[id_] = {prediction: qid}
            dict_id[id_] = {mention: qid}
        else:
            if prediction not in dict_id[id_]:
                dict_id[id_][mention] = qid
                # dict_id[id_][prediction] = qid
                # dict_id[id_][mention] = dict_id[id_].pop(prediction)
            else:
                if isinstance(dict_id[id_][mention], list):
                    dict_id[id_][mention].append(qid)
                # if isinstance(dict_id[id_][prediction], list):
                # dict_id[id_][prediction].append(qid)
                # dict_id[id_][mention] = dict_id[id_].pop(prediction)
                else:
                    dict_id[id_][mention] = [dict_id[id_][mention], qid]
                    # dict_id[id_][prediction] = [dict_id[id_][prediction], qid]
                    # dict_id[id_][mention] = dict_id[id_].pop(prediction)
    return dict_id


def create_dict_id_clef(data_to_link):
    dict_id = {}

    for i, data in enumerate(data_to_link):
        if not data['mention']:  # Skip if mention value is empty string
            continue
        mention = data['mention']
        id_ = data['id']
        #max_score_index = scores[i].index(max(scores[i]))  # Get the index of the highest score
        #prediction = predictions[i][max_score_index]

        # Get the QID for the prediction
        #qid = get_wikidata_qid(prediction)
        qid = data['label_id']

        if id_ not in dict_id:
            # dict_id[id_] = {prediction: qid}
            dict_id[id_] = {mention: qid}
        else:
            if prediction not in dict_id[id_]:
                dict_id[id_][mention] = qid
                # dict_id[id_][prediction] = qid
                # dict_id[id_][mention] = dict_id[id_].pop(prediction)
            else:
                if isinstance(dict_id[id_][mention], list):
                    dict_id[id_][mention].append(qid)
                # if isinstance(dict_id[id_][prediction], list):
                # dict_id[id_][prediction].append(qid)
                # dict_id[id_][mention] = dict_id[id_].pop(prediction)
                else:
                    dict_id[id_][mention] = [dict_id[id_][mention], qid]
                    # dict_id[id_][prediction] = [dict_id[id_][prediction], qid]
                    # dict_id[id_][mention] = dict_id[id_].pop(prediction)
    return dict_id

dict_id_blink = create_dict_id_blink(data_to_link_noLabels, predictions, scores)
dict_id_clef = create_dict_id_clef(data_to_link_wLabels)

def generate_tsv(dict_gold, dict_blink):
    periodical_issue_set = set(dict_gold.keys()) & set(dict_blink.keys())
    rows = []

    for periodical_issue in periodical_issue_set:
        dict_gold_inner = dict_gold[periodical_issue]
        dict_blink_inner = dict_blink[periodical_issue]

        dict_gold_inner_lower = {k.lower(): v for k, v in dict_gold_inner.items()}
        dict_blink_inner_lower = {k.lower(): v for k, v in dict_blink_inner.items()}

        gold_keys_set = set(dict_gold_inner_lower.keys())
        blink_keys_set = set(dict_blink_inner_lower.keys())

        common_keys = gold_keys_set & blink_keys_set

        if common_keys:
            for key in common_keys:
                mention_gold = key
                qid_gold = dict_gold_inner_lower[key]
                mention_blink = key
                qid_blink = dict_blink_inner_lower[key]
                row = (periodical_issue, mention_gold, qid_gold, mention_blink, qid_blink)
                rows.append(row)
        else:
            for key in gold_keys_set:
                mention_gold = key
                qid_gold = dict_gold_inner_lower[key]
                row = (periodical_issue, mention_gold, qid_gold, None, None)
                rows.append(row)

            for key in blink_keys_set:
                mention_blink = key
                qid_blink = dict_blink_inner_lower[key]
                row = (periodical_issue, None, None, mention_blink, qid_blink)
                rows.append(row)

    with open('output/output_blink_clef.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(['periodical_issue', 'mention_gold', 'qid_gold', 'mention_blink', 'qid_blink'])
        writer.writerows(rows)


generate_tsv(dict_id_clef, dict_id_blink)

'''
PRECISION, RECALL, F1 MEASURES

THIS FUNCTION TAKES AS INPUT THE TSV FILE GENERATED BY THE PREVIOUS FUNCTION AND CALCULATES THE PRECISION, RECALL AND F1 MEASURES.
ALSO, it adds 4 columns to the tsv file: 'true_positive', 'false_positive', 'false_negative', 'true_negative'. It fills the columns' cells accordingly.
1) if qid_gold == 'NIL' and 'qid_blink' == '', then we have a true negative
2) if qid_gold == 'qid_blink', then we have a true positive
3) if qid_gold != 'qid_blink' and qid_gold != 'NIL' and qid_blink != '', then we have a false positive and a false negative
4) if qid_gold != 'qid_blink' and qid_gold != 'NIL' and qid_blink == '', then we have a false negative
5) if qid_gold != 'qid_blink' and qid_gold == 'NIL' and qid_blink != '', then we have a false positive
'''

def evaluate_tsv(filepath):
    df = pd.read_csv(filepath, delimiter='\t')

    # Initialize columns with zeros
    df['true_positive'] = 0
    df['false_positive'] = 0
    df['false_negative'] = 0
    df['true_negative'] = 0

    # Apply the conditions
    for idx, row in df.iterrows():
        if row['qid_gold'] == 'NIL' and row['qid_blink'] == '':
            df.at[idx, 'true_negative'] = 1
        elif row['qid_gold'] == row['qid_blink']:
            df.at[idx, 'true_positive'] = 1
        elif row['qid_gold'] != row['qid_blink'] and row['qid_gold'] != 'NIL' and row['qid_blink'] != '':
            df.at[idx, 'false_positive'] = 1
            df.at[idx, 'false_negative'] = 1
        elif row['qid_gold'] != row['qid_blink'] and row['qid_gold'] != 'NIL' and row['qid_blink'] == '':
            df.at[idx, 'false_negative'] = 1
        elif row['qid_gold'] != row['qid_blink'] and row['qid_gold'] == 'NIL' and row['qid_blink'] != '':
            df.at[idx, 'false_positive'] = 1

    # Calculate precision, recall, and F1
    TP = df['true_positive'].sum()
    FP = df['false_positive'].sum()
    FN = df['false_negative'].sum()
    TN = df['true_negative'].sum()

    precision = TP / (TP + FP) if (TP + FP) != 0 else 0
    recall = TP / (TP + FN) if (TP + FN) != 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

    # Save the updated dataframe
    df.to_csv(filepath, sep='\t', index=False)

    return precision, recall, f1


precision, recall, f1 = evaluate_tsv('./output/output_blink_clef.tsv')
print('precision:', precision, 'recall:', recall, 'f1:', f1)