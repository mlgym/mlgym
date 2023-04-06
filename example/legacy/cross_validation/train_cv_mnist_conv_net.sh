 
#!/bin/sh


python ../run.py --validation_mode CROSS_VALIDATION \
              --process_count 2 \
              --dashify_logging_path ../../dashify_logging/ \
              --gs_config_path gs_config_cv.yml \
              --evaluation_config_path cv_config.yml \
              --num_epochs 3 \
              --keep_interim_results
