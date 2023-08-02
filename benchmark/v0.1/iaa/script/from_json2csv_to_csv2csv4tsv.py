'''
Given a dataframe A, add the following new columns to its left beginning:
"sent", "named entity_asIs (intern)", "named entity (intern)", "type (intern)", "qid (intern)", "Is the sentence enough to infer the QID?", "If not, report the context (specific string)","If not, report the context (broader)","comment (intern)","periodical_issue","sent_n".

Then, row by row, fill them based on the content of the other columns' cells, according to the following rules:
- "sent" should be filled by the content of the cell corresponding to the column "text",
- If "namedEntities_assessments_ocrEntityMention" and "namedEntities_assessments_correctEntityMention" are not empty, then "named entity_asIs (intern)" should be filled with the content of the cell corresponding to the column "namedEntities_assessments_ocrEntityMention"; otherwise, that cell should be skipped;
- if 'namedEntities_assessments_entityMention' is 'correct', then 'named entity (intern)' should be filled with 'namedEntities_entityName';
- if 'namedEntities_assessments_entityMention' is wrong, then 'named entity (intern)' should be filled with 'namedEntities_assessments_correctEntityMention' (if not empty, otherwise skip the cell);
- If 'namedEntities_assessments_entityMention' is blank, then 'named entity (intern)' should be filled with 'missingNamedEntities_name' (if not empty, otherwise skip the cell)
- If 'namedEntities_assessments_assessment' is 'correct', then 'type (intern)' should be filled with 'namedEntities_type';
- If 'namedEntities_assessments_assessment' is wrong, then 'type (intern)' should be filled with 'namedEntities_assessments_entityType' (if not empty, otherwise skip the cell);
- If 'namedEntities_assessments_assessment' is blank, then 'type (intern)' should be filled with 'missingNamedEntities_entityType' (if not empty, otherwise skip the cell);
- If 'wikis_assessments_qidAssessment' is 'correct', then 'qid (intern)' should be filled with 'wikis_qid';
- If 'wikis_assessments_qidAssessment' is wrong, then 'qid (intern)' should be filled with 'wikis_assessments_wikiQid' (if not empty, otherwise skip the cell);
- If 'wikis_assessments_qidAssessment' is blank and 'wikis_assessments_wikiQid' is not empty, then 'qid (intern)' should be filled with 'wikis_assessments_wikiQid';
- If 'wikis_assessments_qidAssessment' is blank and 'wikis_assessments_wikiQid' is empty, 'missingNamedEntities_qid';
- If 'wikis_assessments_sentenceEnough' is empty or 'missing', then 'Is the sentence enough to infer the QID?' should be filled with 'missingNamedEntities_sentenceEnough'.
- 'If not, report the context (specific string)' should be filled with 'wikis_assessments_contextString' (if not empty, otherwise skip the cell)
- 'If not, report the context (broader)' shoudl be filled with 'wikis_assessments_contextBroader'  (if not empty, otherwise skip the cell)'
- 'comment (intern)' should be filled with 'wikis_assessments_comments' (if not empty, otherwise skip the cell)'
- 'periodical_issue' should be filled with 'page_id'
- 'sent_n' should be filled with 'id'
'''

import pandas as pd
import numpy as np

iaa_csv = pd.read_csv('data/iaa_csv.csv')
iaa_csv_faked = pd.read_csv('data/iaa_csv_faked.csv')


def transform_dataframe(df):
    # Initialize new columns with empty strings
    new_cols = [
        "sent",
        "named entity_asIs (intern)",
        "named entity (intern)",
        "type (intern)",
        "qid (intern)",
        "Is the sentence enough to infer the QID?",
        "If not, report the context (specific string)",
        "If not, report the context (broader)",
        "comment (intern)",
        "periodical_issue",
        "sent_n"
    ]

    for col in new_cols:
        df[col] = ""

    # Move new columns to the front
    df = df[new_cols + [c for c in df if c not in new_cols]]

    # Apply rules
    df['sent'] = df['text']

    mask = df['namedEntities_assessments_ocrEntityMention'].notnull() & df[
        'namedEntities_assessments_correctEntityMention'].notnull()
    df.loc[mask, 'named entity_asIs (intern)'] = df.loc[mask, 'namedEntities_assessments_ocrEntityMention'].values

    mask = df['namedEntities_assessments_entityMention'] == 'correct'
    df.loc[mask, 'named entity (intern)'] = df.loc[mask, 'namedEntities_entityName'].values
    mask = df['namedEntities_assessments_entityMention'] == 'wrong'
    df.loc[mask, 'named entity (intern)'] = df.loc[mask, 'namedEntities_assessments_correctEntityMention'].values
    mask = df['namedEntities_assessments_entityMention'].isna()
    df.loc[mask, 'named entity (intern)'] = df.loc[mask, 'missingNamedEntities_name'].values

    mask = df['namedEntities_assessments_assessment'] == 'correct'
    df.loc[mask, 'type (intern)'] = df.loc[mask, 'namedEntities_type'].values
    mask = df['namedEntities_assessments_assessment'] == 'wrong'
    df.loc[mask, 'type (intern)'] = df.loc[mask, 'namedEntities_assessments_entityType'].values
    mask = df['namedEntities_assessments_assessment'].isna()
    df.loc[mask, 'type (intern)'] = df.loc[mask, 'missingNamedEntities_entityType'].values

    mask = df['wikis_assessments_qidAssessment'] == 'correct'
    df.loc[mask, 'qid (intern)'] = df.loc[mask, 'wikis_qid'].values
    mask = df['wikis_assessments_qidAssessment'] == 'wrong'
    df.loc[mask, 'qid (intern)'] = df.loc[mask, 'wikis_assessments_wikiQid'].values
    mask = df['wikis_assessments_qidAssessment'].isna() & df['wikis_assessments_wikiQid'].notna()
    df.loc[mask, 'qid (intern)'] = df.loc[mask, 'wikis_assessments_wikiQid'].values
    mask = df['wikis_assessments_qidAssessment'].isna() & df['wikis_assessments_wikiQid'].isna()
    df.loc[mask, 'qid (intern)'] = df.loc[mask, 'missingNamedEntities_qid'].values

    mask = df['wikis_assessments_sentenceEnough'].isna()
    df.loc[mask, 'Is the sentence enough to infer the QID?'] = df.loc[
        mask, 'missingNamedEntities_sentenceEnough'].values

    df['If not, report the context (specific string)'] = df['wikis_assessments_contextString'].values
    df['If not, report the context (broader)'] = df['wikis_assessments_contextBroader'].values
    df['comment (intern)'] = df['wikis_assessments_comments'].values
    df['periodical_issue'] = df['page_id'].values
    df['sent_n'] = df['id'].values

    # Return the transformed DataFrame
    return df


new_iaa_csv = transform_dataframe(iaa_csv)
new_iaa_csv.to_csv('data/new_iaa_csv.csv', float_format='%.0f', index=False)
'''
the 'namedEntities_assessment_user' column has two possible values. 
How can I create two datasets, one for one and one for the other value?
'''

new_iaa_csv_imp = pd.read_csv('data/new_iaa_csv.csv', dtype=object)

new_iaa_csv_imp_d = dict(tuple(new_iaa_csv_imp.groupby('namedEntities_assessments_user')))

user_36136 = new_iaa_csv_imp_d['36136']
user_23628 = new_iaa_csv_imp_d['23628']

user_36136 = new_iaa_csv[new_iaa_csv['namedEntities_assessments_user'] == new_iaa_csv]
user_23628 = new_iaa_csv[new_iaa_csv['namedEntities_assessments_user'] == new_iaa_csv]

user_36136.to_csv('data/user_36136.csv')
user_23628.to_csv('data/user_23628.csv')