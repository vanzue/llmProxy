import json


def dotenv_to_json(dotenv_path, json_path):
    dotenv_data = {}

    with open(dotenv_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                dotenv_data[key] = value

    with open(json_path, 'w') as json_file:
        json.dump(dotenv_data, json_file, indent=4)


# Example usage
dotenv_to_json('.env', 'config.json')
