 
#!/bin/sh


accelerate launch --multi_gpu --gpu_ids "0,1,3" --num_processes=3  \
                /scratch/max/mlgym/example/cnn_ddp/run.py --config_path /scratch/max/mlgym/example/cnn_ddp/run_config.yml
