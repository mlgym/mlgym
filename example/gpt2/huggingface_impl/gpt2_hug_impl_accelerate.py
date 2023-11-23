import datetime
import json
import math
import os
import time
import logging
import torch
from transformers import GPT2LMHeadModel, GPT2Config
from datasets import load_from_disk
from transformers import DataCollatorForLanguageModeling, GPT2TokenizerFast
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
import random
from accelerate import Accelerator

class GPT2():
    def __init__(self, gpt_version: str, learning_rate: float, epochs: int, batch_size: int, dataset_name: str, world_size: int, check_path: str, num_batches_epoch: int, logger):
        config = GPT2Config.from_pretrained(gpt_version, output_hidden_stages=False)
        self.model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained(gpt_version, config=config)

        base_dir = os.path.join(os.sep, *list(os.path.dirname(__file__).split(os.sep)[0:-1]))
        tokenizer = GPT2TokenizerFast(tokenizer_file=os.path.join(base_dir,"tokenizer.json"))
        tokenizer.pad_token = tokenizer.eos_token
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        train_tokenized_dataset = load_from_disk(os.path.join(base_dir, "data", f"{dataset_name}-tokenized", "train"))
        self.train_dataloader = DataLoader(train_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)
          
        validation_tokenized_dataset = load_from_disk(os.path.join(base_dir, "data", f"{dataset_name}-tokenized", "validation"))
        self.validation_dataloader = DataLoader(validation_tokenized_dataset, shuffle=True, batch_size=batch_size, collate_fn=data_collator)
        
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr = learning_rate)
        self.check_path = check_path
        self.num_batches_epoch = num_batches_epoch // world_size
        self.accelerator = Accelerator(device_placement=True)
        self.world_size = world_size
        self.logger = logger

        self.train_dataloader, self.validation_dataloader, self.model, self.optimizer = self.accelerator.prepare(      
                                           self.train_dataloader, self.validation_dataloader, self.model, self.optimizer)

    def format_time(self, elapsed):
        return str(datetime.timedelta(seconds=int(round((elapsed)))))
    
    def clm_loss(self, lm_logits, labels):
        loss_fn = torch.nn.CrossEntropyLoss()
        # move labels to correct device to enable model parallelism
        labels = labels.to(lm_logits.device)
        # Shift so that tokens < n predict n
        shift_logits = lm_logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        # Flatten the tokens
        loss = loss_fn(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        return loss
   
    def save_checkpoint(self):
        check_t0 = time.time()
        # model = self.accelerator.unwrap_model(self.model)
        self.accelerator.save_state(self.check_path)
        checkpointing = time.time() - check_t0
        return checkpointing

    def run(self):
        flag_run = True
        epoch_i = 0
        while flag_run:
            t0 = time.time()
            total_train_loss = 0.0
            tfp = 0.0
            tpp = 0.0
            tos = 0.0
            tbp = 0.0
            self.model.train()
            for step, batch in enumerate(self.train_dataloader):
                with self.accelerator.accumulate(self.model):
                    b_input_ids = batch['input_ids']
                    b_labels = batch['input_ids']
                    b_masks = batch['attention_mask']

                    self.model.zero_grad()

                    tfp_t0 = time.time()
                    outputs = self.model( b_input_ids,
                            attention_mask = b_masks,
                            token_type_ids=None
                            )
                    tfp += (time.time() - tfp_t0)
                    logits = outputs.logits

                    tpp_t0 = time.time()
                    loss = self.clm_loss(lm_logits=logits, labels=b_labels)
                    tpp += (time.time() - tpp_t0)

                    batch_loss = loss.item()
                    total_train_loss += batch_loss

                    tbp_t0 = time.time()
                    self.accelerator.backward(loss)
                    tbp += (time.time() - tbp_t0)

                    tos_t0 = time.time()
                    self.optimizer.step()
                    tos += (time.time() - tos_t0)
                
                if step % (self.num_batches_epoch//2) == 0 and not step == 0:
                    if step >= self.num_batches_epoch:
                        el_step = step - ((step//self.num_batches_epoch) * self.num_batches_epoch)
                        if el_step == 0: el_step = self.num_batches_epoch
                    else:
                        el_step = step
                        elapsed = self.format_time(time.time() - t0)
                        print('GPU {:} Batch {:>5,}  of  {:>5,}. Loss: {:>5,}. Elapsed: {:}.'.format(self.accelerator.device.index, el_step, self.num_batches_epoch, batch_loss, elapsed))

                if step % self.num_batches_epoch == 0 and not step == 0:     

                    # Calculate the average loss over all of the batches.
                    avg_train_loss = total_train_loss / self.num_batches_epoch  

                    # Measure how long this epoch took.
                    training_time = time.time() - t0                                                                                      
                        
                    print("GPU {:} Epoch {:} / {:} Average training loss: {:.2f} Training epoch took: {:}".format(self.accelerator.device.index, epoch_i + 1, self.epochs, avg_train_loss, self.format_time(training_time)))

                    # self.accelerator.wait_for_everyone()
                    eval_sats = self.evaluate()
                    self.logger.info(self.log(epoch_i=epoch_i,
                                                avg_train_loss=avg_train_loss,
                                                training_time=training_time,
                                                train_forward_pass=tfp,
                                                train_backward_pass=tbp,
                                                train_opt_step=tos,
                                                train_pp=tpp,
                                                eval_result_payload= eval_sats), main_process_only=False)
                    
                    epoch_i += 1
                    if epoch_i == self.epochs:
                        flag_run = False
                        break
                    t0 = time.time()
                    total_train_loss = 0.0
                    tfp = 0.0
                    tpp = 0.0
                    tos = 0.0
                    tbp = 0.0
                    self.model.train()

    def eval(self, dataloader, eval_type:str):
        self.model.eval()
        t0 = time.time()
        efp = 0.0
        epp = 0.0
        acl = 0.0
        losses = []
        # Evaluate data for one epoch
        for step, batch in enumerate(dataloader):

            b_input_ids = batch['input_ids']
            b_labels = batch['input_ids']
            b_masks = batch['attention_mask']

            with torch.no_grad():
                efp_t0 = time.time()
                outputs = self.model( b_input_ids,
                            attention_mask = b_masks,
                            token_type_ids=None
                        )
                efp += (time.time() - efp_t0)

            logits = outputs.logits
            epp_t0 = time.time()
            loss = self.clm_loss(lm_logits=logits, labels=b_labels)
            epp += (time.time() - epp_t0)

            acl_t0 = time.time()
            losses.append(self.accelerator.gather_for_metrics(loss.repeat(self.num_batches_epoch)))
            acl += (time.time() - acl_t0)
            
        # Calcukate Perplexity
        epp_t0 = time.time()
        losses = torch.cat(losses)
        try:
            avg_eval_loss = torch.mean(losses).item()
        except OverflowError:
            perplexity = float("inf")
        perplexity = math.exp(avg_eval_loss)
        epp = epp + (time.time() - epp_t0)
        eval_time = time.time() - t0
        print("GPU {:} {:} Loss: {:.2f} Perplexity: {:.2f}, time taken: {:}".format(self.accelerator.device.index, eval_type, 
                                                                            avg_eval_loss, perplexity, 
                                                                            self.format_time(eval_time)))
        return avg_eval_loss, perplexity, eval_time, epp, efp, acl
    
    def evaluate(self):
        eval_prep = []
        eval_result_payload = {}
        eval_prep.append({"eval_type": "validation", "dataloader": self.validation_dataloader})
        for eval_t in eval_prep:
            avg_eval_loss, perplexity, eval_time, eval_pp, eval_forward_pass, acl = self.eval(dataloader=eval_t["dataloader"], eval_type= eval_t["eval_type"])
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_loss"] = avg_eval_loss
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_perplexity"] = perplexity
            eval_result_payload[f"eval_time"] = eval_time
            eval_result_payload[f"eval_post_processing"] = eval_pp
            eval_result_payload[f"eval_forward_pass"] = eval_forward_pass
            eval_result_payload[f"eval_aggregate_and_calc"] = acl

        if self.accelerator.is_main_process:
            check_time = self.save_checkpoint()
        else:
            check_time = 0.0
        self.accelerator
        eval_result_payload["checkpointing"] = check_time
        return eval_result_payload
    
    def log(self, epoch_i:int, avg_train_loss:float, training_time:float, train_forward_pass: float, 
            train_backward_pass: float, train_opt_step: float, train_pp: float, eval_result_payload):

        eval_result_payload["rank"] = self.accelerator.device.index
        eval_result_payload["epoch"] = epoch_i
        eval_result_payload["training_loss"] = avg_train_loss
        eval_result_payload["training_time"] = training_time
        eval_result_payload["train_forward_pass"] = train_forward_pass
        eval_result_payload["train_backward_pass"] = train_backward_pass
        eval_result_payload["train_optimizer_step"] = train_opt_step
        eval_result_payload["train_post_processing"] = train_pp
        return eval_result_payload

def log(logs, epochs: int, log_path: str, device_count:int, exp_t0:float):
    df = pd.DataFrame(logs)
    exp_time = time.time() - exp_t0
    result = []
    for epoch_i in range(0,epochs):
        dict = {}
        # dict["experiment_key"] = f"rank_{device_count}"
        for col in df.columns:
            if col == 'epoch':
                dict[col] = epoch_i
            elif col == 'checkpointing':
                dict[col] = df.loc[df['epoch'] == epoch_i, col].max()
            elif col != 'rank':
                dict[col] = df.loc[df['epoch'] == epoch_i, col].mean()
        dict["epoch_time"] = dict['training_time'] + dict['eval_time'] + dict['checkpointing']
        dict["total_experiment_time"] = exp_time
        result.append(dict)
    
    with open(log_path, "w") as outfile:
        json.dump(result, outfile)

if __name__ == '__main__':
    exp_t0 = time.time()
    device_count = torch.cuda.device_count()
    check_path = os.path.join(os.path.dirname(__file__), "checkpoints", f"rank_acc_{device_count}.pth")
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"rank_acc_{device_count}.log")
    # Creating an object
    logging.basicConfig(filename=log_path,
                    filemode='a')
    logger = logging.getLogger(__name__)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    os.makedirs(os.path.dirname(check_path), exist_ok=True)
    LR = 1e-4
    BATCH_SIZE = 8
    NUM_BATCHES_EPOCH = 100
    EPOCHS = 2
    # dataset_name = "wikitext-2-raw-v1"
    DATASET_NAME = "wikitext-103-raw-v1" 
    GPT_VERSION = "gpt2"
    # Set the seed value all over the place to make this reproducible.
    seed_val = 42
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    gpt2 = GPT2(gpt_version=GPT_VERSION,
                learning_rate=LR,
                epochs=EPOCHS,
                batch_size=BATCH_SIZE,
                dataset_name=DATASET_NAME,
                world_size=device_count,
                check_path = check_path,
                num_batches_epoch = NUM_BATCHES_EPOCH,
                logger = logger)
    
    gpt2.run()
    exp_time = time.time() - exp_t0
    logger.info({"total_experiment_time": exp_time})
    # for logs in log_stats:
    #     logs["total_experiment_time"] = exp_time
    # with open(log_path, "w") as outfile:
    #     json.dump(log_stats, outfile)
