import json
import os

def json_to_dotenv(json_file_path, dotenv_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    
    with open(dotenv_file_path, 'w') as dotenv_file:
        for key, value in data.items():
            dotenv_file.write(f'{key}={value}\n')

if __name__ == "__main__":
    json_file_path = 'config.json'  # 输入的 JSON 文件路径
    dotenv_file_path = '.env'       # 输出的 .env 文件路径

    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"Error: The file {json_file_path} does not exist.")
    else:
        json_to_dotenv(json_file_path, dotenv_file_path)
        print(f"Converted {json_file_path} to {dotenv_file_path}")
