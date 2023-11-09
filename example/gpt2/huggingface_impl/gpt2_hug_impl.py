import datetime
import json
import math
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
        self.model.to("cuda")
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

    def run(self):
        run_stats = []
        self.model.to(self.device)
        device = self.device
        for epoch_i in range(0, self.epochs):
            print("")
            print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, self.epochs))
            print('Training...')

            t0 = time.time()
            total_train_loss = 0
            self.model.train()

            for step, batch in enumerate(self.train_dataloader):

                b_input_ids = batch['input_ids'].to(device)
                b_labels = batch['input_ids'].to(device)
                b_masks = batch['attention_mask'].to(device)

                self.model.zero_grad()        

                outputs = self.model(  b_input_ids,
                            labels=b_labels, 
                            attention_mask = b_masks,
                            token_type_ids=None
                        )

                loss = outputs[0]  

                batch_loss = loss.item()
                total_train_loss += batch_loss

                if step % 50 == 0 and not step == 0:

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
            run_stats.append(self.evaluate_and_log(epoch_i=epoch_i,
                                                    avg_train_loss=avg_train_loss,
                                                    training_time=training_time))

        return run_stats

    def eval(self, dataloader, eval_type:str):
        print("")
        print(f"Running evaluation for {eval_type} split...")
        self.model.to(self.device)
        device = self.device

        t0 = time.time()
        self.model.eval()
        total_eval_loss = 0
        # Evaluate data for one epoch
        for step, batch in enumerate(dataloader):

            b_input_ids = batch['input_ids'].to(device)
            b_labels = batch['input_ids'].to(device)
            b_masks = batch['attention_mask'].to(device)
        
            with torch.no_grad():        
                outputs  = self.model(b_input_ids, 
#                               token_type_ids=None, 
                                attention_mask = b_masks,
                                labels=b_labels)
          
                loss = outputs[0]  
            
            batch_loss = loss.item()
            total_eval_loss += batch_loss

            if step % 50 == 0 and not step == 0:

                elapsed = self.format_time(time.time() - t0)
                print('  Batch {:>5,}  of  {:>5,}. Loss: {:>5,}.   Elapsed: {:}.'.format(step, len(self.train_dataloader), batch_loss, elapsed))

        avg_eval_loss = total_eval_loss / len(dataloader)
        # Calcukate Perplexity
        perplexity = math.exp(avg_eval_loss)
        eval_time = time.time() - t0
        print(" {0} Loss: {1:.2f}".format(eval_type, avg_eval_loss))
        print(" {0} Perplexity: {1:.2f}".format(eval_type, perplexity))
        print(" {0} took: {1:}".format(eval_type, self.format_time(eval_time)))

        return avg_eval_loss, perplexity, eval_time
    
    def evaluate_and_log(self, epoch_i:int, avg_train_loss:float, training_time:float):
        total_eval_time = 0.0
        eval_result_payload = {}

        eval_prep = []
        eval_prep.append({"eval_type": "train", "dataloader": self.train_dataloader})
        eval_prep.append({"eval_type": "test", "dataloader": self.test_dataloader})
        eval_prep.append({"eval_type": "validation", "dataloader": self.validation_dataloader})

        eval_result_payload["epoch"] = epoch_i
        eval_result_payload["training_loss"] = avg_train_loss
        eval_result_payload["training_time"] = training_time      
        for eval_t in eval_prep:
            avg_eval_loss, perplexity, eval_time = self.eval(dataloader=eval_t["dataloader"], eval_type= eval_t["eval_type"])
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_loss"] = avg_eval_loss
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_perplexity"] = perplexity
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_time"] = eval_time
            total_eval_time += eval_time

        eval_result_payload["total_eval_time"] = total_eval_time
        return eval_result_payload

if __name__ == '__main__':
    gridsearch_id = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"{gridsearch_id}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    dataset_name = "wikitext-2-raw-v1"
    gpt_version = "gpt2"
    LR = 1e-4
    BATCH_SIZE = 8
    EPOCHS = 1
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
    
    log_stats = gpt2.run()
    with open(log_path, "w") as outfile:
        json.dump(log_stats, outfile)
    