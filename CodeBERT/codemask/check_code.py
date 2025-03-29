import json
import os
import subprocess

# 資料夾路徑
input_path = r"../../data/codemask/pytutor/contract.json"
folder_path = 'generated_code'

param1 = "1"
param2 = "2"


class Data(object):
    def __init__(self, idx, title, input_args):
        self.idx = idx
        self.title = title
        self.input_args = input_args


def read_data(filename):
    """Read input from file."""

    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            js = json.loads(line)
            title = ' '.join(js['title']).replace('\n', ' ')
            print(js)
            break


def main():
    success = 0
    count = 0
    # 遍歷資料夾中的所有子資料夾
    for root, topics, files in os.walk(folder_path):
        for topic in topics:
            for sub_root, sub_folder, sub_files in os.walk(os.path.join(root, topic)):
                for file in sub_files:
                    if file.endswith('.py') is False:
                        continue
                    program_path = os.path.join(sub_root, file)
                    print(f"執行 {program_path} ...")
                    # 執行程式
                    result = subprocess.run(['python', program_path, param1, param2], stdout=subprocess.PIPE)
                    count += 1

                    # 紀錄結果
                    if result.returncode == 0:
                        success += 1

    print(f"成功率: {success / count}")


if __name__ == "__main__":
    # main()
    read_data(input_path)
