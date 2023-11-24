#!/bin/sh

# CUDA_VISIBLE_DEVICES='1' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl.py 

CUDA_VISIBLE_DEVICES='1,2' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 

CUDA_VISIBLE_DEVICES='1,2,3' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 

CUDA_VISIBLE_DEVICES='1,2,3,4' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 

CUDA_VISIBLE_DEVICES='1,2,3,4,5' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py

CUDA_VISIBLE_DEVICES='1,2,3,4,5,6' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 

CUDA_VISIBLE_DEVICES='1,2,3,4,5,6,7' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 

CUDA_VISIBLE_DEVICES='0,1,2,3,4,5,6,7' python3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_ddp.py 