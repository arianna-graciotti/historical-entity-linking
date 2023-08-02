import os
import json

def prune_keys_from_json(json_data, keys_to_prune):
    if isinstance(json_data, dict):
        return {key: prune_keys_from_json(value, keys_to_prune) for key, value in json_data.items() if key not in keys_to_prune}
    elif isinstance(json_data, list):
        return [prune_keys_from_json(item, keys_to_prune) for item in json_data]
    else:
        return json_data

def prune_jsons_in_folder(input_folder, output_folder, keys_to_prune):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            with open(os.path.join(input_folder, filename), 'r') as f_in:
                json_data = json.load(f_in)
                pruned_json = prune_keys_from_json(json_data, keys_to_prune)

            with open(os.path.join(output_folder, filename), 'w') as f_out:
                json.dump(pruned_json, f_out, indent=4)

prune_jsons_in_folder('data/hel_results/data', 'data/hel_results/data_pruned', ['source', 'bleurt', 'amr', 'predicates', 'otherEntities'])
