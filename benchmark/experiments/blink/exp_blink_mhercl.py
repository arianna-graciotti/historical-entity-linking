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

# Function to process each row and return the required data structure
def process_row(row):
    #print("Row:", row)  # Print the entire row at the start

    # Step 1: Derive the value of mention
    mention = row['named entity_asIs (intern)'] if (row['named entity_asIs (intern)'] not in ["", "nan"]) else row[
        'named entity (intern)']
    print("Mention:", mention)  # Print the derived mention

    # Original qid_gold value
    qid_gold = "NIL" if (row['qid (intern)'] in ["", "nan"] and mention not in ["", "nan"]) else (
        "" if mention in ["", "nan"] and row['qid (intern)'] in ["", "nan"] else row['qid (intern)'])
    print("QID Gold (before NIL check):", qid_gold)  # Print the derived qid_gold before the NIL check

    if qid_gold:
        if mention:
            # Split the 'sent' column using the mention string
            parts = re.split(re.escape(mention), row['sent'], maxsplit=1)
            context_left = parts[0].strip().lower()
            context_right = parts[1].strip().lower() if len(parts) > 1 else ""
        else:
            context_left = ""
            context_right = ""

        return {
            "id": row['periodical_issue'],
            "label": "unknown",
            "label_id": -1,
            "context_left": context_left,
            "mention": mention.lower(),
            "context_right": context_right
        }
    else:
        return {
            "id": row['periodical_issue'],
            "label": "unknown",
            "label_id": -1,
            "context_left": "",
            "mention": "",
            "context_right": ""
        }

HEL_forBlinkExp = pd.read_csv(
    './input/mhercl_reconsolidated_advancedfiltering.csv',
    sep='\t')

HEL_forBlinkExp = HEL_forBlinkExp.astype(str)

# Apply the process_row function to each row and create the data structure 'data_to_link'
data_to_link = HEL_forBlinkExp.apply(process_row, axis=1).tolist()

# I would like to create a datastructure similar to "data_to_link" but that has the gold QIDs instead of -1 as 'label_id'
fake_data_to_link_withQID = HEL_forBlinkExp.apply(process_row, axis=1).tolist()

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

_, _, _, _, _, predictions, scores, = main_dense.run(args, None, *models, test_data=data_to_link)

'''
#############################
#POPULARITY BIAS EXPERIMENTS#
#############################
'''

'''
I have a list of dictionaries 'filtered_data_to_link'. 
I want to create a new dictionary of dictionaries, 'dict_mentions_gold'. 
In 'dict_mentions_gold', the first-level keys should correspond to the values of the key 'mention' of 
'filtered_data_to_link'. 
The second level key corresponds to the QID, namely the values of the key 'label_id' of 'filtered_data_to_link'.
If, in iterating 'filtered_data_to_link', we happen to encounter a 'mention' that is already a first-level key in 
'dict_mentions_gold', then we have to append another sub-dictionary to that 'mention', which should have, as a second level key, 
its QID, namely the values of the key 'label_id' of 'filtered_data_to_link'.
'''


def sort_dict_by_length(dict_mentions):
    # Sort the dictionary based on the length of the value dictionaries, in descending order
    sorted_dict = sorted(dict_mentions.items(), key=lambda item: len(item[1]), reverse=True)

    # Convert the list of tuples back to a dictionary
    sorted_dict = dict(sorted_dict)

    return sorted_dict


dict_mentions_gold_fake = {}

for item in fake_data_to_link_withQID:
    mention = item['mention']
    qid = item['label_id']

    if mention not in dict_mentions_gold_fake:
        dict_mentions_gold_fake[mention] = {}

    if qid in dict_mentions_gold_fake[mention]:
        dict_mentions_gold_fake[mention][qid] += 1
    else:
        dict_mentions_gold_fake[mention][qid] = 1

sorted_dict_mentions_gold_count = sort_dict_by_length(dict_mentions_gold_fake)

'''
#############################
#BLINK QUALITY EXPERIMENTS#
#############################
'''

'''
I have a list of dictionaries 'data_to_link' , a list of lists 'predictions', a list of lists 'scores'.
The first subdictionary of 'data_to_link' corresponds to the first sublist of 'predictions' and 
to the first sublist of 'scores'. 
I want to create a new dictionary of dictionaries, 'dict_id'. 
In 'dict_id, the first-level keys should correspond to the values of the key 'id' of 'data_to_link'. 
The second level key correspond to the prediction, namely the element of the corresponding sublist 
in 'predictions' that has the highest score according to its corresponding element in the 'scores' sublist. 
The value of the key should be the WikiData QID corresponding to the key, considering that the key is a Wikipedia 
page link.
If, in iterating 'data_to_link', we happen to encounter a 'id' that is already a first-level key in 'dict_id', 
then we have to append another sub-dictionary to that 'id', which should have, as a second level key, 
its prediction, namely the element of the corresponding sublist in 'predictions' that has the highest score according 
to its corresponding 'scores' sublist.
If, in iterating elements of the sublists of 'predictions', we encounter a prediction that is already present in 
my dictionary of dictionaries as a second level key, we should transform the key's value into a list containing 
the already stored QID and the QID(s).
If the key 'mention' has an empty string as a value, that case is skipped.
'''


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

dict_id_blink = create_dict_id_blink(data_to_link, predictions, scores)

# unit_test: dict_id_blink_split = create_dict_id(data_to_link_split, predictions, scores)

def count_none_qids(dict_id):
    count = 0
    for id_, sub_dict in dict_id.items():
        for prediction, qid in sub_dict.items():
            if qid is None:
                count += 1
    return count


none_qids_count = count_none_qids(dict_id)
print("Number of None QIDs:", none_qids_count)

'''
I have a csv A. I want to transform it into a dictionary. I want to create a new dictionary of dictionaries, 'dict_id_gold'. 
In 'dict_id_gold', the first-level keys should correspond to the values of the column 'periodical_issue' of the csv A. 
The second level key correspond to the mention, and it should be filled with values from the column 'named entity_asIs 
(intern)' of A, if it is not empty. If it is empty, it should be filled with value from the column 'named entity (intern)'. 
If both are empty, we should skip the case. The value of the key should be the corresponding value in column 'qid (intern)' of A.
If, in iterating csv A, we happen to encounter a 'periodical_issue' that is already a first-level key in 'dict_id', 
then we have to append another sub-dictionary to that key, which should have, as a second level key, values from the column 
'named entity_asIs (intern)' of A, if it is not empty. 
If it is empty, it should be filled with value from the column 'named entity (intern)'. 
If both are empty, we should fill the 'mention' field with an empty string. 
The value of the key should be the corresponding value in column 'qid (intern)' of A.
'''

def create_dict_id_gold(df_gold):
    dict_id_gold = {}

    for index, row in df_gold.iterrows():
        periodical_issue = row['periodical_issue']
        named_entity_asIs = row['named entity_asIs (intern)']
        named_entity = row['named entity (intern)']
        qid = row['qid (intern)']

        # Check for the string "nan" instead of using pd.isnull()
        if named_entity_asIs == "nan" and named_entity == "nan":
            continue

        # Check for the string "nan" instead of using pd.isnull()
        if qid == "nan":
            qid = 'NIL'

        if periodical_issue in dict_id_gold:
            sub_dict = dict_id_gold[periodical_issue]
            mention = named_entity_asIs if named_entity_asIs != "nan" else named_entity
            mention = mention.lower() if mention != "nan" else ""

            sub_dict[mention] = qid
        else:
            sub_dict = {}
            mention = named_entity_asIs if named_entity_asIs != "nan" else named_entity
            mention = mention.lower() if mention != "nan" else ""

            sub_dict[mention] = qid
            dict_id_gold[periodical_issue] = sub_dict

    return dict_id_gold


dict_id_gold = create_dict_id_gold(HEL_forBlinkExp)

'''
I would like to count the lowest-level key, value pairs of each dictionaries (gold, silver) to see if they are comparable
'''


def count_lowest_level_pairs(dict_of_dicts):
    count = 0
    for key, value in dict_of_dicts.items():
        if isinstance(value, dict):
            count += len(value)
    return count


print("Number of lowest-level key-value pairs:", count_lowest_level_pairs(dict_id_gold))

only_in_dict_id_gold = {k: dict_id_gold[k] for k in dict_id_gold if k not in dict_id_blink}
only_in_dict_id_blink = {k: dict_id_blink[k] for k in dict_id_blink if k not in dict_id_gold}

print("Elements only in A:", only_in_dict_id_gold)
print("Elements only in B:", only_in_dict_id_blink)

'''
I have two dictionaries, 'dict_id_gold' and dict_id_blink'. 
They are dictionaries of nested dictionaries. 
I would like to obtain a tsv file out of the two. 
The tsv should have 5 columns: 'periodical_issue', 'mention_gold', 'qid_gold', 'mention_silver', 'qid_silver'. 
The column 'periodical_issue' should contain the first-level key of the dictionaries, which are the same. 
The colum 'mention_gold' should contain the key of the key, value pairs of sub-dictionaries of dictionary 'dict_id_gold' rendered in lower case. 
The column 'qid_gold' should contain the value of the key, value pairs of the sub-dictionaries of dictionary 'dict_id_gold'.  
The colum 'mention_blink' should contain the key of the key, value pairs of sub-dictionaries of dictionary 'dict_id_blink' rendered in lower case. 
The column 'qid_blink' should contain the value of the key, value pairs of the sub-dictionaries of dictionary 'dict_id_blink'. 
'mention_gold' and 'mention_blink' columns should be filled wih the same values whenever it is possible. If that is not possible, or the two sub-dictionaries have different key, value pairs, only the 'mention_gold' and 'qid_gold' columns, or the 'mention_blink' and 'qid_blink' columns should be filled, 
depending on the case. 
'''


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

    with open('output/output_blink.tsv', 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(['periodical_issue', 'mention_gold', 'qid_gold', 'mention_blink', 'qid_blink'])
        writer.writerows(rows)


generate_tsv(dict_id_gold, dict_id_blink)

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


precision, recall, f1 = evaluate_tsv('./output/output_blink.tsv')
print('precision:', precision, 'recall:', recall, 'f1:', f1)