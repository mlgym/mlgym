#!/bin/sh

CUDA_VISIBLE_DEVICES='1,2' accelerate launch --multi_gpu --gpu_ids 1,2 --num_processes=2 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py 

CUDA_VISIBLE_DEVICES='1,2,3' accelerate launch --multi_gpu --gpu_ids 1,2,3 --num_processes=3 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py 

CUDA_VISIBLE_DEVICES='1,2,3,4' accelerate launch --multi_gpu --gpu_ids 1,2,3,4 --num_processes=4 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py

CUDA_VISIBLE_DEVICES='1,2,3,4,5' accelerate launch --multi_gpu --gpu_ids 1,2,3,4,5 --num_processes=5 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py

CUDA_VISIBLE_DEVICES='1,2,3,4,5,6' accelerate launch --multi_gpu --gpu_ids 1,2,3,4,5,6 --num_processes=6 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py

CUDA_VISIBLE_DEVICES='1,2,3,4,5,6,7' accelerate launch --multi_gpu --gpu_ids 1,2,3,4,5,6,7 --num_processes=7 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py

CUDA_VISIBLE_DEVICES='0,1,2,3,4,5,6,7' accelerate launch --multi_gpu --gpu_ids 0,1,2,3,4,5,6,7 --num_processes=8 /cluster/home/mlgym/example/gpt2/huggingface_impl/gpt2_hug_impl_accelerate.py 