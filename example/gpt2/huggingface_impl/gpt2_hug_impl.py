import datetime
import os
import time
import torch
from transformers import GPT2LMHeadModel, GPT2Config
from typing import Dict
from datasets import load_from_disk
from transformers import DataCollatorForLanguageModeling, GPT2TokenizerFast
from torch.utils.data import DataLoader
import numpy as np
import random

class GPT2():
    def __init__(self, gpt_version: str, learning_rate: float, epochs: int, batch_size: int, dataset_name: str):
        
        config = GPT2Config.from_pretrained(gpt_version, output_hidden_stages=False)
        self.model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained(gpt_version, config=config)
        # Tell pytorch to run this model on the GPU.
        self.device = torch.device("cuda")
        self.model.cuda()
        base_dir = os.path.join(os.sep, *list(os.path.dirname(__file__).split(os.sep)[0:-1]))
        tokenizer = GPT2TokenizerFast(tokenizer_file=os.path.join(base_dir,"tokenizer.json"))
        tokenizer.pad_token = tokenizer.eos_token
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        train_tokenized_dataset = load_from_disk(os.path.join(base_dir, f"{dataset_name}-tokenized", "train"))
        self.train_dataloader = DataLoader(train_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)
    
        test_tokenized_dataset = load_from_disk(os.path.join(base_dir, f"{dataset_name}-tokenized", "test"))
        self.test_dataloader = DataLoader(test_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)
    
        validation_tokenized_dataset = load_from_disk(os.path.join(base_dir, f"{dataset_name}-tokenized", "validation"))
        self.validation_dataloader = DataLoader(validation_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)
        
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr = learning_rate)
    
    def format_time(self, elapsed):
        return str(datetime.timedelta(seconds=int(round((elapsed)))))

    def train(self):
        training_stats = []
        model = self.model.to(self.device)
        device = self.device
        for epoch_i in range(0, self.epochs):
            print("")
            print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, self.epochs))
            print('Training...')

            t0 = time.time()
            total_train_loss = 0
            model.train()

            for step, batch in enumerate(self.train_dataloader):

                b_input_ids = batch['input_ids'].to(device)
                b_labels = batch['input_ids'].to(device)
                b_masks = batch['attention_mask'].to(device)

                model.zero_grad()        

                outputs = model(  b_input_ids,
                            labels=b_labels, 
                            attention_mask = b_masks,
                            token_type_ids=None
                        )

                loss = outputs[0]  

                batch_loss = loss.item()
                total_train_loss += batch_loss

                if step % 20 == 0 and not step == 0:

                    elapsed = self.format_time(time.time() - t0)
                    print('  Batch {:>5,}  of  {:>5,}. Loss: {:>5,}.   Elapsed: {:}.'.format(step, len(self.train_dataloader), batch_loss, elapsed))

                loss.backward()

                self.optimizer.step()

            # Calculate the average loss over all of the batches.
            avg_train_loss = total_train_loss / len(self.train_dataloader)       
        
            # Measure how long this epoch took.
            training_time = time.time() - t0

            print("")
            print(" Average training loss: {0:.2f}".format(avg_train_loss))
            print(" Training epoch took: {:}".format(self.format_time(training_time)))
            training_stats.append({"epoch": epoch_i, 
                                   "train_loss": avg_train_loss, 
                                   "train_time": training_time})

        return training_stats

    def eval(self, dataloader, eval_type:str):
        print("")
        print(f"Running {eval_type}...")
        model = self.model.to(self.device)
        device = self.device

        t0 = time.time()
        model.eval()
        total_eval_loss = 0
        # Evaluate data for one epoch
        for batch in dataloader:

            b_input_ids = batch['input_ids'].to(device)
            b_labels = batch['input_ids'].to(device)
            b_masks = batch['attention_mask'].to(device)
        
            with torch.no_grad():        
                outputs  = model(b_input_ids, 
#                               token_type_ids=None, 
                                attention_mask = b_masks,
                                labels=b_labels)
          
                loss = outputs[0]  
            
            batch_loss = loss.item()
            total_eval_loss += batch_loss

        avg_eval_loss = total_eval_loss / len(dataloader)
        eval_time = time.time() - t0
        # Calcukate Perplexity
        perplexity = torch.exp(avg_eval_loss)
        print(" {} Loss: {0:.2f}".format(eval_type, avg_eval_loss))
        print(" {} Perplexity: {0:.2f}".format(eval_type, perplexity))
        print(" {} took: {:}".format(eval_type, self.format_time(eval_time)))

        return {f"{eval_type}_loss": avg_eval_loss, 
                f"{eval_type}_perplexity": perplexity,
                f"{eval_type}_time": eval_time}
    
    def evaluate(self):
        eval_results = []
        eval_results.append(self.eval(dataloader=self.train_dataloader, eval_type= "train"))
        eval_results.append(self.eval(dataloader=self.test_dataloader, eval_type= "test"))
        eval_results.append(self.eval(dataloader=self.validation_dataloader, eval_type= "validation"))
        return eval_results

if __name__ == '__main__':
    dataset_name = "wikitext-2-raw-v1"
    gpt_version = "gpt2"
    LR = 1e-4
    BATCH_SIZE = 8
    EPOCHS = 20
    # Set the seed value all over the place to make this reproducible.
    seed_val = 42
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)

    gpt2 = GPT2(gpt_version=gpt_version,
                learning_rate=LR,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                dataset_name=dataset_name)
    
    train_stats = gpt2.train()
    eval_stats = gpt2.evaluate()