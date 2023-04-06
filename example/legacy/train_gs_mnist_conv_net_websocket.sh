 
#!/bin/sh


python run.py --validation_mode GRID_SEARCH \
              --run_mode TRAIN \
              --process_count 1 \
              --gs_config_path grid_search/gs_config.yml \
              --num_epochs 20 \
              --gpus 0 1 2 3 \
              --websocket_logging_servers http://127.0.0.1:5000
