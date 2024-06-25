import json

def convert_to_key_value_string(json_list):
    key_value_pairs = []
    for item in json_list:
        key = item.get('name')
        value = item.get('value')
        key_value_pairs.append(f'{key}={value}')
    return '\n'.join(key_value_pairs)


# Example usage
json_str = '''
[
  {
    "name": "WEBSITES_ENABLE_APP_SERVICE_STORAGE",
    "value": "false",
    "slotSetting": false
  }
]
'''

json_list = json.loads(json_str)
result = convert_to_key_value_string(json_list)
print(result)
