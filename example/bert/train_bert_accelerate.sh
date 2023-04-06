 
#!/bin/sh


accelerate launch --multi_gpu --num_processes=5 --gpu_ids 0,1,5,6,7 run.py --config_path /scratch/max/mlgym/example/bert/run_config.yml
