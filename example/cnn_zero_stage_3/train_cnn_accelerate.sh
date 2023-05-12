 
#!/bin/sh


accelerate launch --config_file /scratch/max/mlgym/example/cnn_zero_stage_3/ac_config.yaml \
                /scratch/max/mlgym/example/cnn_zero_stage_3/run.py --config_path /scratch/max/mlgym/example/cnn_zero_stage_3/run_config.yml
