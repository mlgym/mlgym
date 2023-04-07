 
#!/bin/sh


python run.py --process_count 1 \
              --gpus 7 \
              --num_epochs 3 \
              --websocket_logging_servers http://127.0.0.1:5002 \
              --gs_rest_api_endpoint http://127.0.0.1:5001 \
              train \
              --gs_config_path /scratch/max/mlgym/example/bert/bert_lm_config.yml
