 
#!/bin/sh


python run.py --validation_mode GRID_SEARCH \
              --process_count 5 \
              --dashify_logging_path dashify_logging/ \
              --text_logging_path general_logging/ \
              --gs_config_path grid_search/gs_config.yml \
              --num_epochs 20 \
              --gpus 0 1 2 3 \
              --keep_interim_results
