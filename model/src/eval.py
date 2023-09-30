import csv
from collections import Counter

Results = dict()
for ds in ['mhercl', 'hipe']:
    Results.setdefault(ds, dict())
    for disambiguation_type in ['dot', 'rep_dyn']:
        Results[ds].setdefault(disambiguation_type, dict())
        for checkdates in ['Yes', 'No']:
            for checktypes in ['Yes', 'No']:
                if ds == 'mhercl':
                    with open('benchmark/v0.1/conll_reconsolidated_advanced_filtering_020823_noduplicates.tsv') as f_gold:
                        reader = csv.reader(f_gold, delimiter='\t', quoting=csv.QUOTE_NONE)
                        rows_gold = [row for row in reader]
                elif ds == 'hipe':
                    with open('benchmark/clef/HIPE-2022-v2.1-hipe2020-test-en.tsv') as f_gold:
                        reader = csv.reader(f_gold, delimiter='\t', quoting=csv.QUOTE_NONE)
                        rows_gold = [row for row in reader]

                with open('model/src/results/predictions_' + ds + "_model-" + disambiguation_type + "_checks-" + '_'.join([checkdates, checktypes]) + '.tsv') as f_pred:
                    reader = csv.reader(f_pred, delimiter='\t', quoting=csv.QUOTE_NONE)
                    rows_pred = [row for row in reader]

                total = 0
                given = 0
                correct = 0
                wrong = 0
                errors = Counter()
                right = Counter()
                for i, (row_gold, row_pred) in enumerate(zip(rows_gold, rows_pred)):
                    if len(row_gold) != 0:
                        if len(row_gold) == 1:
                            if 'document_id' in row_gold[0]:
                                #assert row_gold[0] == row_pred[0]
                                try:
                                    row_gold[0] == row_pred[0]
                                except:
                                    continue
                                    #print()
                        else:
                            if ds == 'mhercl':
                                qid_gold = row_gold[2]
                                qid_pred = row_pred[2]
                            elif ds == 'hipe':
                                qid_gold = row_gold[7]
                                qid_pred = row_pred[7]
                            ent_iob = row_gold[1]
                            if qid_gold != '_' and ent_iob.startswith('B-'):
                                total+=1
                                if qid_pred not in ['_', 'None']:
                                    given+=1
                                    if qid_gold == qid_pred:
                                        correct+=1
                                        right.update([qid_gold])
                                    else:
                                        wrong+=1
                                        #print('\t'.join([qid_gold, qid_pred]))
                                        errors.update([qid_gold])
                print(ds, disambiguation_type, checkdates, checktypes)
                print('Number of anotations:', total)
                print('Given:', given)
                print('Correct:', correct)
                print('Wrong:', wrong)
                precision = correct/total
                recall = correct/given
                f1 = 2 * ((precision*recall) / (precision+recall))
                print('Precision: {:.2f}'.format(precision))
                print('Recall: {:.2f}'.format(recall))
                print('F1: {:.2f}'.format(f1))
                Results[ds][disambiguation_type]['_'.join([checkdates, checktypes])] = [str(round(precision,2)), str(round(recall,2)), str(round(f1,2))]
                print(right.most_common(5))
                print(errors.most_common(5))
                print('\n-----------------------\n')
print('\\textsc{ELD\\textsubscript{dot}} &  $' + '$ & $'.join(Results['mhercl']['dot']['No_No']) + '$\\\\' )
print('\\textsc{ELD\\textsubscript{all}} &  $' + '$ & $'.join(Results['mhercl']['rep_dyn']['No_No']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{time}} &  $' + '$ & $'.join(Results['mhercl']['rep_dyn']['Yes_No']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{type}} &  $' + '$ & $'.join(Results['mhercl']['rep_dyn']['No_Yes']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{time-type}} &  $' + '$ & $'.join(Results['mhercl']['rep_dyn']['Yes_Yes']) + '$\\\\')

print('------')

print('\\textsc{ELD\\textsubscript{dot}} &  $' + '$ & $'.join(Results['hipe']['dot']['No_No'])  + '$\\\\')
print('\\textsc{ELD\\textsubscript{all}} &  $' + '$ & $'.join(Results['hipe']['rep_dyn']['No_No']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{time}} &  $' + '$ & $'.join(Results['hipe']['rep_dyn']['Yes_No']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{type}} &  $' + '$ & $'.join(Results['hipe']['rep_dyn']['No_Yes']) + '$\\\\')
print('\\textsc{ELD\\textsubscript{time-type}} & $' + '$ & $'.join(Results['hipe']['rep_dyn']['Yes_Yes']) + '$\\\\')
