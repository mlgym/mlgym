 
#!/bin/sh


python run.py --process_count 1 \
              --text_logging_path general_logging/ \
              --num_epochs 10 \
              --websocket_logging_servers http://127.0.0.1:5000 \
              --gs_rest_api_endpoint http://127.0.0.1:5001 \
              train \
              --gs_config_path gs_config.yml
