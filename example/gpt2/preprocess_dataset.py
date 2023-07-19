from itertools import chain
from datasets import load_dataset
from transformers import GPT2TokenizerFast, GPT2LMHeadModel, GPT2Config
import accelerate
from accelerate import Accelerator

def main():

    def group_texts(examples):
        # Concatenate all texts.
        concatenated_examples = {k: list(chain(*examples[k])) for k in examples.keys()}
        total_length = len(concatenated_examples[list(examples.keys())[0]])
        # We drop the small remainder, and if the total_length < block_size  we exclude this batch and return an empty dict.
        # We could add padding if the model supported it instead of this drop, you can customize this part to your needs.
        total_length = (total_length // block_size) * block_size
        # Split by chunks of max_len.
        result = {k: [t[i : i + block_size] for i in range(0, total_length, block_size)] for k, t in concatenated_examples.items()}
        result["labels"] = result["input_ids"].copy()
        return result

    
    def tokenize_function(examples):
        return tokenizer(examples[text_column_name])

    accelerator = Accelerator(gradient_accumulation_steps=1)
    tokenizer = GPT2TokenizerFast(tokenizer_file="C:/Users/Moinam/Documents/GitHub/mlgym/example/gpt2/tokenizer.json")
    raw_datasets = load_dataset(path="wikitext", name="wikitext-2-raw-v1")
    column_names = raw_datasets["train"].column_names
    text_column_name = "text" if "text" in column_names else column_names[0]
    block_size = tokenizer.model_max_length
    if block_size > 1024:
        block_size = 1024
    # datasets.save_to_disk('wikitext-2-raw-v1')
    gpt_version: str = "gpt2"
    config = GPT2Config.from_pretrained(gpt_version)
    model = GPT2LMHeadModel._from_config(config)
    embedding_size = model.get_input_embeddings().weight.shape[0]
    if len(tokenizer) > embedding_size:
        model.resize_token_embeddings(len(tokenizer))

    with accelerator.main_process_first():
        tokenized_datasets = raw_datasets.map(tokenize_function, batched=True, num_proc=2, remove_columns=column_names)

    with accelerator.main_process_first():
        llm_datasets = tokenized_datasets.map(group_texts, batched=True, num_proc=2)
    print(llm_datasets)
    llm_datasets.save_to_disk('wikitext-2-raw-v1-tokenized')

if __name__ == "__main__":
    main()
