import os
import json
from faker import Faker
import re

def replace_values_with_fake(json_data, fake):
    if isinstance(json_data, dict):
        return {key: replace_values_with_fake(value, fake) for key, value in json_data.items()}
    elif isinstance(json_data, list):
        return [replace_values_with_fake(item, fake) for item in json_data]
    elif isinstance(json_data, str):
        if json_data.lower() in ['correct', 'wrong']:
            return json_data
        elif re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', json_data):
            return fake.url()
        elif re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', json_data):
            return fake.email()
        elif re.match(r'^\d+$', json_data):
            num_digits = len(json_data)
            return str(fake.random_number(digits=num_digits, fix_len=True))
        elif re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', json_data):
            return fake.bothify(text='##??##', letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            text = fake.text(max_nb_chars=25)
            tokens = text.split()
            return ' '.join(tokens[:5])
    elif isinstance(json_data, (int, float)):
        return fake.random_number()
    else:
        return json_data


def anonymize_jsons_in_folder(input_folder, output_folder):
    fake = Faker()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            with open(os.path.join(input_folder, filename), 'r') as f_in:
                json_data = json.load(f_in)
                anonymized_json = replace_values_with_fake(json_data, fake)

            with open(os.path.join(output_folder, filename), 'w') as f_out:
                json.dump(anonymized_json, f_out, indent=4)


anonymize_jsons_in_folder('data/hel_results/data_pruned', 'data/hel_results/data_pruned_faked')
