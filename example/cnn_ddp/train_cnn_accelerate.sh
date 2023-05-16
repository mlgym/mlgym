 
#!/bin/sh


accelerate launch --multi_gpu --num_processes=8 --gpu_ids 0,1,2,3,4,5,6,7 run.py --config_path /scratch/max/mlgym/example/cnn_ddp/run_config.yml
