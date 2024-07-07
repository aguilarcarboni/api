import pandas as pd

hf_url = "hf://datasets/BAAI/Infinity-Instruct/3M/train.jsonl"

df = pd.read_json(hf_url, lines=True)
print(df)