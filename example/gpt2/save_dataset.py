from datasets import load_dataset
datasets = load_dataset(path="wikitext", name="wikitext-2-v1")
datasets.save_to_disk('wikitext-2-v1')