 
#!/bin/sh


python run.py --process_count 21 \
              --num_epochs 100 \
              --websocket_logging_servers http://127.0.0.1:5002 \
              --gs_rest_api_endpoint http://127.0.0.1:5001 \
              train \
              --gs_config_path gs_config.yml
