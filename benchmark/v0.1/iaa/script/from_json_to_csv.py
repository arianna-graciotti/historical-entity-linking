from typing import Dict, List, Any
import os
import csv
import json
import logging
import pandas


#csv_headers = csv_example.columns.tolist()
csv_headers = [
    "id",
    "text",
    "page_id",
    "namedEntities_type",
    "namedEntities_entityName",
    "namedEntities_assessments_user",
    "namedEntities_assessments_assessment",
    "namedEntities_assessments_entityType",
    "namedEntities_assessments_entityMention",
    "namedEntities_assessments_correctEntityMention",
    "namedEntities_assessments_ocrEntityMention",
    "wikis_wiki",
    "wikis_link",
    "wikis_qid",
    "wikis_assessments_user",
    "wikis_assessments_assessment",
    "wikis_assessments_wikiUrl",
    "wikis_assessments_qidAssessment",
    "wikis_assessments_wikiQid",
    "wikis_assessments_sentenceEnough",
    "wikis_assessments_contextString",
    "wikis_assessments_contextBroader",
    "wikis_assessments_comments",
    "missingNamedEntities_user",
    "missingNamedEntities_name",
    "missingNamedEntities_nameOcr",
    "missingNamedEntities_entityType",
    "missingNamedEntities_wiki",
    "missingNamedEntities_qid",
    "missingNamedEntities_sentenceEnough"
]


def flatten_namedentities(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = []
    named_entities = data.get('namedEntities', [])
    # If namedEntities is a dictionary, convert it to a list
    if isinstance(named_entities, dict):
        named_entities = [named_entities]
    # Process each item in namedEntities
    for entity in named_entities:
        for assessment_key, assessment_value in entity.get('assessments', {}).items():
            for wiki in entity.get('wikis', []):
                for wiki_assessment_key, wiki_assessment_value in wiki.get('assessments', {}).items():
                    # Only create a new row if the user of namedEntities_assessments and wikis_assessments is the same
                    if assessment_value.get('user') == wiki_assessment_value.get('user'):
                        record = create_record(data, entity, assessment_value, wiki, wiki_assessment_value)
                        records.append(record)
    return records


# Function to handle the nested 'missingNamedEntities'
def flatten_missingnamedentities(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = []
    missing_named_entities = data.get('missingNamedEntities', {})
    # If missingNamedEntities is a list, convert it to a dictionary
    if isinstance(missing_named_entities, list):
        missing_named_entities = {i: item for i, item in enumerate(missing_named_entities)}
    # Process each item in missingNamedEntities
    for user_key, user_value in missing_named_entities.items():
        for missing_entity in user_value.get('missingNamedEntities', []):
            record = create_record_for_missing(data, user_key, missing_entity)
            records.append(record)
    return records

# Function to create a record for 'namedEntities'
def create_record(data, entity, assessment_value, wiki, wiki_assessment_value):
    record = {}
    record['id'] = data.get('id', '')
    record['text'] = data.get('text', '')
    record['page_id'] = data.get('page_id', '')
    record['namedEntities_type'] = entity.get('type', '')
    record['namedEntities_entityName'] = entity.get('entityName', '')
    record['namedEntities_assessments_user'] = assessment_value.get('user', '')
    record['namedEntities_assessments_assessment'] = assessment_value.get('assessment', '')
    record['namedEntities_assessments_entityType'] = assessment_value.get('entityType', '')
    record['namedEntities_assessments_entityMention'] = assessment_value.get('entityMention', '')
    record['namedEntities_assessments_correctEntityMention'] = assessment_value.get('correctEntityMention', '')
    record['namedEntities_assessments_ocrEntityMention'] = assessment_value.get('ocrEntityMention', '')
    record['wikis_wiki'] = wiki.get('wiki', '')
    record['wikis_link'] = wiki.get('link', '')
    record['wikis_qid'] = wiki.get('qid', '')
    record['wikis_assessments_user'] = wiki_assessment_value.get('user', '')
    record['wikis_assessments_assessment'] = wiki_assessment_value.get('assessment', '')
    record['wikis_assessments_wikiUrl'] = wiki_assessment_value.get('wikiUrl', '')
    record['wikis_assessments_qidAssessment'] = wiki_assessment_value.get('qidAssessment', '')
    record['wikis_assessments_wikiQid'] = wiki_assessment_value.get('wikiQid', '')
    record['wikis_assessments_sentenceEnough'] = wiki_assessment_value.get('sentenceEnough', '')
    record['wikis_assessments_contextString'] = wiki_assessment_value.get('contextString', '')
    record['wikis_assessments_contextBroader'] = wiki_assessment_value.get('contextBroader', '')
    record['wikis_assessments_comments'] = wiki_assessment_value.get('comments', '')
    return record

# Function to create a record for 'missingNamedEntities'
def create_record_for_missing(data, user_key, missing_entity):
    record = {}
    record['id'] = data.get('id', '')
    record['text'] = data.get('text', '')
    record['page_id'] = data.get('page_id', '')
    record['missingNamedEntities_user'] = user_key
    record['missingNamedEntities_name'] = missing_entity.get('name', '')
    record['missingNamedEntities_nameOcr'] = missing_entity.get('nameOcr', '')
    record['missingNamedEntities_entityType'] = missing_entity.get('entityType', '')
    record['missingNamedEntities_wiki'] = missing_entity.get('wiki', '')
    record['missingNamedEntities_qid'] = missing_entity.get('qid', '')
    record['missingNamedEntities_sentenceEnough'] = missing_entity.get('sentenceEnough', '')
    return record

# Function to flatten a single JSON object
def flatten_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = flatten_namedentities(data) + flatten_missingnamedentities(data)
    return records

def setup_logger(log_file_path: str):
    logger = logging.getLogger('json_to_csv')
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    return logger

def process_json_folder(folder_path: str, csv_file_path: str, log_file_path: str):
    # Create a logger
    logger = setup_logger(log_file_path)

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(folder_path, filename), 'r') as f:
                        json_data = json.load(f)
                        records = flatten_json(json_data)
                        for record in records:
                            writer.writerow(record)
                except Exception as e:
                    logger.error(f'Failed to process file {filename}. Error: {e}')

    logger.info('Finished processing JSON files.')




json_folder_path = 'data/hel_results/data_pruned_prova'
csv_file_path = 'data/iaa_csv_faked.csv'
log_file_path = 'logs/process_json_folder.log'

process_json_folder(json_folder_path, csv_file_path, log_file_path)