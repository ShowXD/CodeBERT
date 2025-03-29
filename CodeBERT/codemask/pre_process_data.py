import json
import os

DATA_DIR = "../../data/code2nl/CodeSearchNet/python/train.jsonl"
OUTPUT_PATH = "../../data/code2nl/CodeSearchNet/python/txt"


class Data(object):
    """A single training/test example."""

    def __init__(self,
                 idx,
                 source,
                 target,
                 ):
        self.idx = idx
        self.source = source
        self.target = target


def read_data(filename):
    """Read data from filename."""
    examples = []
    with open(filename, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            js = json.loads(line)
            if 'idx' not in js:
                js['idx'] = idx
            code = ' '.join(js['code_tokens']).replace('\n', ' ')
            code = ' '.join(code.strip().split())
            nl = ' '.join(js['docstring_tokens']).replace('\n', '')
            nl = ' '.join(nl.strip().split())
            examples.append(
                Data(
                    idx=idx,
                    source=code,
                    target=nl,
                )
            )
    return examples


# read data file
train_data = read_data(DATA_DIR)
features = []
for data_index, data in enumerate(train_data):
    features.append(data.source)

# write text file
if not os.path.exists(OUTPUT_PATH):
    os.makefiles(OUTPUT_PATH)
with open(os.path.join(OUTPUT_PATH, "train.txt"), "w", encoding="utf-8") as f:
    for code in features:
        f.write(code + "\n")

print(len(features))
