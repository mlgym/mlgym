 
#!/bin/sh


python run.py --validation_mode GRID_SEARCH \
              --process_count 2 \
              --dashify_logging_path dashify_logging/ \
              --text_logging_path general_logging/ \
              --gs_config_path gs_config.yml \
              --num_epochs 20 \
              --gpus 0 1 2 3 