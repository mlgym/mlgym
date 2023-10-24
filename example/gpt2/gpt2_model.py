from ml_gym.models.nn.net import NNModel
import torch
from transformers import GPT2LMHeadModel, GPT2Config
from typing import Dict

gpt_version: str = "gpt2"
class GPT2LLM(NNModel):

    def __init__(self, prediction_publication_key: str, gpt_version: str = gpt_version):
        super().__init__()
        self.prediction_publication_key = prediction_publication_key
        config = GPT2Config.from_pretrained(gpt_version, output_hidden_stages=False)
        self.model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained(gpt_version, config=config)

    def forward_impl(self, inputs: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        outputs = self.model(**inputs)
        output_dict = {self.prediction_publication_key: outputs.logits}
        return output_dict

    def forward(self, inputs: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        return self.forward_impl(inputs)


if __name__ == '__main__':
    from datasets import load_from_disk
    from transformers import DataCollatorForLanguageModeling, GPT2TokenizerFast
    from torch.utils.data import DataLoader
    tokenizer = GPT2TokenizerFast(tokenizer_file="/cluster/home/mlgym/example/gpt2/tokenizer.json")
    tokenizer.pad_token = tokenizer.eos_token
    chunked_tokenized_dataset = load_from_disk("/cluster/home/mlgym/example/gpt2/wikitext-2-raw-v1-tokenized/train")
    batch_size = 30

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    train_dataloader = DataLoader(chunked_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)

    sample = next(iter(train_dataloader))
    model = GPT2LLM("")
    prediction = model(sample["input_ids"])
    print("")
