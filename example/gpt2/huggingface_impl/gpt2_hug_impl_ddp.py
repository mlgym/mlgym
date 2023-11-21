import datetime
import json
import math
import os
import time
from typing import Union
import torch
from transformers import GPT2LMHeadModel, GPT2Config
from datasets import load_from_disk
from transformers import DataCollatorForLanguageModeling, GPT2TokenizerFast
from torch.utils.data import DataLoader
import numpy as np
import pandas as pd
import random
import torch.distributed as dist
from torch.utils.data.distributed import DistributedSampler
import torch.multiprocessing as mp

class GPT2():
    def __init__(self, gpt_version: str, learning_rate: float, epochs: int, batch_size: int, dataset_name: str, rank: int, world_size: int, check_path: str, num_batches_epoch: int):
        self.setup(rank, world_size)
        config = GPT2Config.from_pretrained(gpt_version, output_hidden_stages=False)
        self.model: GPT2LMHeadModel = GPT2LMHeadModel.from_pretrained(gpt_version, config=config)

        self.device = rank
        self.model.to(self.device)
        self.model= torch.nn.parallel.DistributedDataParallel(self.model, device_ids=[rank])

        base_dir = os.path.join(os.sep, *list(os.path.dirname(__file__).split(os.sep)[0:-1]))
        tokenizer = GPT2TokenizerFast(tokenizer_file=os.path.join(base_dir,"tokenizer.json"))
        tokenizer.pad_token = tokenizer.eos_token
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

        train_tokenized_dataset = load_from_disk(os.path.join(base_dir, "data", f"{dataset_name}-tokenized", "train"))
        self.train_dataloader = self.prepare(rank = rank, world_size= world_size, dataset= train_tokenized_dataset, 
                                             data_collator= data_collator, batch_size= batch_size)
    
        validation_tokenized_dataset = load_from_disk(os.path.join(base_dir, "data", f"{dataset_name}-tokenized", "validation"))
        self.validation_dataloader = self.prepare(rank = rank, world_size= world_size, dataset= validation_tokenized_dataset,
                                                  data_collator=data_collator, batch_size= batch_size)
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr = learning_rate)
        self.check_path = check_path
        self.num_batches_epoch = num_batches_epoch // world_size
        self.world_size = world_size
    
    def setup(self, rank, world_size):
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'
        backend = "nccl"
        dist.init_process_group(backend, rank=rank, world_size=world_size)
        torch.cuda.set_device(rank)
    
    def cleanup(self):
        dist.destroy_process_group()

    def prepare(self, rank, world_size, dataset, batch_size, data_collator, pin_memory=False, num_workers=0):
        sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank, shuffle=False, drop_last=False)
        dataloader = DataLoader(dataset, batch_size=batch_size, pin_memory=pin_memory, num_workers=num_workers, drop_last=False, shuffle=False, sampler=sampler, collate_fn=data_collator)
        return dataloader

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

    def gather_loss_across_gpus(self, logits: Union[torch.Tensor, None], labels: Union[torch.Tensor, None]
                            ) -> float:
        loss = 0.0
        group = dist.group.WORLD
        group_size = torch.distributed.get_world_size(group)
        gather_logits_tensor = [torch.zeros_like(logits) for _ in
                       range(group_size)]
        gather_labels_tensor = [torch.zeros_like(labels) for _ in
                       range(group_size)]
        dist.all_gather(gather_logits_tensor, logits)
        dist.all_gather(gather_labels_tensor, labels)
        for i in range(0, len(gather_logits_tensor)):
            loss += self.clm_loss(lm_logits=gather_logits_tensor[i], labels= gather_labels_tensor[i])
        return loss
    
    def save_checkpoint(self, epoch_i):
        check_t0 = time.time()
        torch.save({
        'epoch': epoch_i,
        'model_state_dict': self.model.module.state_dict(),
        'optimizer_state_dict': self.optimizer.state_dict()
        }, self.check_path)
        checkpointing = time.time() - check_t0
        return checkpointing

    def run(self):
        run_stats = []
        self.model.to(self.device)
        device = self.device
        flag_run = True
        epoch_i = 0
        while flag_run:
            t0 = time.time()
            total_train_loss = 0.0
            # total_cl_loss = 0.0
            tfp = 0.0
            tpp = 0.0
            tos = 0.0
            tbp = 0.0
            # tag = 0.0
            self.model.train()
            self.train_dataloader.sampler.set_epoch(epoch_i)
            for step, batch in enumerate(self.train_dataloader):

                b_input_ids = batch['input_ids'].to(device)
                b_labels = batch['input_ids'].to(device)
                b_masks = batch['attention_mask'].to(device)

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

                if step % (self.num_batches_epoch//2) == 0 and not step == 0:
                    if step >= self.num_batches_epoch:
                        el_step = step - ((step//self.num_batches_epoch) * self.num_batches_epoch)
                        if el_step == 0: el_step = self.num_batches_epoch
                    else:
                        el_step = step
                    elapsed = self.format_time(time.time() - t0)
                    print('GPU {:}  Batch {:>5,}  of  {:>5,}. Loss: {:>5,}. Elapsed: {:}.'.format(self.device, el_step, self.num_batches_epoch, batch_loss, elapsed))

                tbp_t0 = time.time()
                loss.backward()
                tbp += (time.time() - tbp_t0)

                tos_t0 = time.time()
                self.optimizer.step()
                tos += (time.time() - tos_t0)

                # tag_t0 = time.time()
                # cl_loss = self.gather_loss_across_gpus(logits, b_labels)
                # total_cl_loss += cl_loss.item()
                # tag += (time.time() - tag_t0)

                if step % self.num_batches_epoch == 0 and not step == 0:     

                    # Calculate the average loss over all of the batches.
                    avg_train_loss = total_train_loss / self.num_batches_epoch  

                    # Measure how long this epoch took.
                    training_time = time.time() - t0                                                                                      

                    # if self.device == 0:
                    #     checkpointing = self.save_checkpoint(epoch_i=epoch_i)
                        # # Calculate the average loss over all of the batches in all gpus.
                        # avg_cl_train_loss = total_cl_loss / (self.num_batches_epoch * self.world_size)
                        # print("Epoch {:} / {:} Average training loss: {:.2f} Training epoch took: {:}".format(epoch_i + 1, self.epochs,
                        #                                                             avg_cl_train_loss, self.format_time(training_time)))

                        # run_stats.append(self.evaluate_and_log( epoch_i=epoch_i,
                        #                                     avg_train_loss=avg_cl_train_loss,
                        #                                     training_time=training_time,
                        #                                     train_forward_pass=tfp,
                        #                                     train_backward_pass=tbp,
                        #                                     train_opt_step=tos,
                        #                                     train_pp=tpp,
                        #                                     aggregate_and_calc_loss= 0.0))
                        
                    print("GPU {:} Epoch {:} / {:} Average training loss: {:.2f} Training epoch took: {:}".format(self.device, epoch_i + 1,
                                                                                   self.epochs, avg_train_loss, self.format_time(training_time)))

                    run_stats.append(self.evaluate_and_log( epoch_i=epoch_i,
                                                            avg_train_loss=avg_train_loss,
                                                            training_time=training_time,
                                                            train_forward_pass=tfp,
                                                            train_backward_pass=tbp,
                                                            train_opt_step=tos,
                                                            train_pp=tpp,
                                                            aggregate_and_calc_loss= 0.0))
                    
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

        self.cleanup()
        return run_stats

    def eval(self, dataloader, eval_type:str):
        self.model.to(self.device)
        device = self.device
        self.model.eval()
        t0 = time.time()
        total_eval_loss = 0
        efp = 0.0
        epp = 0.0
        # Evaluate data for one epoch
        for step, batch in enumerate(dataloader):

            b_input_ids = batch['input_ids'].to(device)
            b_labels = batch['input_ids'].to(device)
            b_masks = batch['attention_mask'].to(device)
        
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
            
            batch_loss = loss.item()
            total_eval_loss += batch_loss

        avg_eval_loss = total_eval_loss / len(dataloader)
        # Calcukate Perplexity
        epp_t0 = time.time()
        perplexity = math.exp(avg_eval_loss)
        epp = epp + (time.time() - epp_t0)
        eval_time = time.time() - t0
        print("GPU {:} {:} Loss: {:.2f} Perplexity: {:.2f}, time taken: {:}".format(self.device, eval_type, 
                                                                            avg_eval_loss, perplexity, 
                                                                            self.format_time(eval_time)))
        return avg_eval_loss, perplexity, eval_time, epp, efp
    
    def evaluate_and_log(self, epoch_i:int, avg_train_loss:float, training_time:float, train_forward_pass: float, 
                         train_backward_pass: float, train_opt_step: float, train_pp: float,
                         aggregate_and_calc_loss: float):
        eval_result_payload = {}

        eval_prep = []
        eval_prep.append({"eval_type": "validation", "dataloader": self.validation_dataloader})

        eval_result_payload["rank"] = self.device
        eval_result_payload["epoch"] = epoch_i
        eval_result_payload["training_loss"] = avg_train_loss
        eval_result_payload["training_time"] = training_time
        eval_result_payload["train_forward_pass"] = train_forward_pass
        eval_result_payload["train_backward_pass"] = train_backward_pass
        eval_result_payload["train_optimizer_step"] = train_opt_step
        eval_result_payload["train_post_processing"] = train_pp
        # eval_result_payload["train_aggregate_and_calc_loss"] = aggregate_and_calc_loss
        for eval_t in eval_prep:
            avg_eval_loss, perplexity, eval_time, eval_pp, eval_forward_pass = self.eval(dataloader=eval_t["dataloader"], eval_type= eval_t["eval_type"])
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_loss"] = avg_eval_loss
            eval_result_payload[f"eval_{eval_t['eval_type']}_split_perplexity"] = perplexity
            eval_result_payload[f"eval_time"] = eval_time
            eval_result_payload[f"eval_post_processing"] = eval_pp
            eval_result_payload[f"eval_forward_pass"] = eval_forward_pass
        
        if self.device == 0:
            check_time = self.save_checkpoint(epoch_i=epoch_i)
        else:
            check_time = 0.0
        dist.barrier()
        eval_result_payload["checkpointing"] = check_time
        return eval_result_payload

def main(rank, world_size, gpt_version, lr, epochs, batch_size, dataset_name, check_path, num_batches_epoch, conn):
    gpt2 = GPT2(gpt_version=gpt_version,
                learning_rate=lr,
                epochs=epochs,
                batch_size=batch_size,
                dataset_name=dataset_name,
                rank=rank,
                world_size=world_size,
                check_path = check_path,
                num_batches_epoch = num_batches_epoch)
    
    log_stats = gpt2.run()
    conn.send(log_stats)

def log(logs, epochs: int, log_path: str, device_count:int, exp_t0:float):
    df = pd.DataFrame(logs)
    exp_time = time.time() - exp_t0
    result = []
    for epoch_i in range(0,epochs):
        dict = {}
        dict["experiment_key"] = f"rank_{device_count}"
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
    check_path = os.path.join(os.path.dirname(__file__), "checkpoints", f"rank_ddp_{device_count}.pth")
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"rank_ddp_{device_count}.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    os.makedirs(os.path.dirname(check_path), exist_ok=True)
    LR = 1e-4
    BATCH_SIZE = 8
    NUM_BATCHES_EPOCH = 1000
    EPOCHS = 1
    # dataset_name = "wikitext-2-raw-v1"
    DATASET_NAME = "wikitext-103-raw-v1" 
    GPT_VERSION = "gpt2"
    # Set the seed value all over the place to make this reproducible.
    seed_val = 42
    random.seed(seed_val)
    np.random.seed(seed_val)
    torch.manual_seed(seed_val)
    torch.cuda.manual_seed_all(seed_val)
    parent_conn, child_conn = mp.Pipe()
    mp.spawn(
        main,
        args=(device_count, 
              GPT_VERSION, 
              LR, 
              EPOCHS, 
              BATCH_SIZE, 
              DATASET_NAME, 
              check_path, 
              NUM_BATCHES_EPOCH, 
              child_conn, ),
        nprocs=device_count,
        join=True
    )
    log_stats = []
    while parent_conn.poll():
        for record in parent_conn.recv():
            log_stats.append(record)
    log(logs=log_stats, epochs = EPOCHS, log_path=log_path, device_count=device_count, exp_t0=exp_t0)
