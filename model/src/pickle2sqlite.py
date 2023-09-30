import pickle
import sqlite3
from tqdm import tqdm

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        #c.execute(create_table_sql)
    except Exception as e:
        print(e)

def annotation2text(annotation_dict, args):
    for k, v in annotation_dict.items():
        if k == 'sent':
            continue
        for kk, vv in v.items():
            if vv is None:
                annotation_dict[k][kk] = ''
    if args.ds == 'mhercl':
        text = '\n'.join(['\t'.join([t['form'], t['ent_iob'], t['ent_qid'], t['lemma'], t['pos']]) for k, t in annotation_dict.items() if k != 'sent'])
    elif args.ds == 'hipe':
        text = '\n'.join(['\t'.join([t['form'], t['NE-COARSE-LIT'], t['NE-COARSE-METO'],t['NE-FINE-LIT'], t['NE-FINE-METO'], t['NE-FINE-COMP'], t['NE-NESTED'], t['ent_qid'], t['NEL-METO'], t['MISC']]) for k, t in
                          annotation_dict.items() if k != 'sent'])
    return text+'\n'

def insert_into_db(doc_id, sent_id, annotation, c):
    annotation_ = annotation2text(annotation)
    c.execute("""INSERT OR IGNORE INTO sents (doc_id, sent_id, sent_text, sent_annotation) VALUES (?, ?, ?, ?)""",
              (doc_id, sent_id, annotation['sent'], annotation_))
    c.execute("""INSERT OR IGNORE INTO docs (doc_id, source_) VALUES (?, ?)""", (doc_id, 'Wikipedia'))



def create_db(db_path):
    sql_create_docs_table = ''' CREATE TABLE IF NOT EXISTS docs (
                                        id INTEGER PRIMARY KEY,
                                        doc_id text UNIQUE NOT NULL,
                                        author text,
                                        title text,
                                        pub_date text,
                                        source_ text                                        
                                    ); '''
    sql_create_sents_table = ''' CREATE TABLE IF NOT EXISTS sents (
                                        id INTEGER PRIMARY KEY,
                                        doc_id text NOT NULL,
                                        sent_id text NOT NULL,
                                        sent_text text,
                                        sent_annotation text
                                    ); '''
    # create a database connection
    conn = create_connection(db_path)
    if conn is not None:
        create_table(conn, sql_create_docs_table)
        create_table(conn, sql_create_sents_table)
        conn.commit()
    else:
        print("Error! cannot create the database connection.")
        raise


def init(fpath):
    with open(fpath, 'rb') as fr:
        Annotations = pickle.load(fr)
    db_path = ''.join(fpath.split('.')[:-1]) + '.db'
    create_db(db_path)
    conn = create_connection(db_path)
    for i, (doc_id, sents) in tqdm(enumerate(Annotations.items()), total=len(Annotations)):
        c = conn.cursor()
        c.execute("SELECT * FROM docs WHERE doc_id = '{0}' LIMIT 1".format(doc_id))
        data = c.fetchone()
        if data is None:
            #c.execute("""INSERT OR IGNORE INTO docs (doc_id, source_) VALUES (?, ?)""", (doc_id, 'Wikipedia'))
            for sent_id, annotation in sents.items():
                insert_into_db(doc_id, sent_id, annotation, c)
        if i % 500 == 0 and i != 0:
            conn.commit()
    conn.commit()
    conn.close()
#init('/media/4TB/rocco/polifonia_corpus/Annotations_Wikipedia-EN_limit-No.pkl')