from ml_gym.models.nn.net import NNModel
from typing import Dict
import torch
from transformers import AutoConfig, AutoModelForMaskedLM


class BERTLM(NNModel):

    def __init__(self, prediction_publication_key: str, bert_version: str = "bert-base-uncased"):
        super().__init__()
        self.prediction_publication_key = prediction_publication_key
        config = AutoConfig.from_pretrained(bert_version)
        self.model = AutoModelForMaskedLM.from_config(config)

    def forward_impl(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        outputs = self.model(inputs)
        output_dict = {self.prediction_publication_key: outputs.logits}
        return output_dict

    def forward(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        return self.forward_impl(inputs)


if __name__ == '__main__':
    from datasets import load_from_disk
    from transformers import DataCollatorForLanguageModeling, BertTokenizerFast
    from torch.utils.data import DataLoader

    tokenizer = BertTokenizerFast(tokenizer_file="/scratch/max/mlgym/example/transformer/tokenizers/trained_wiki_tokenizer/tokenizer.json")
    chunked_tokenized_dataset = load_from_disk("example/transformer/preprocessed_datasets/chunked_tokenized_dataset_train")
    mlm_probability = 0.15
    batch_size = 30

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=mlm_probability, pad_to_multiple_of=8)

    train_dataloader = DataLoader(chunked_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)

    sample = next(iter(train_dataloader))
    model = BERTLM("")
    prediction = model(sample["input_ids"])
    print("")
