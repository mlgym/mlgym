 
#!/bin/sh


python run.py --validation_mode CROSS_VALIDATION \
              --process_count 2 \
              --dashify_logging_path dashify_logging/ \
              --text_logging_path general_logging/ \
              --gs_config_path cross_validation/gs_config_cv.yml \
              --evaluation_config_path cross_validation/cv_config.yml \
              --num_epochs 20 \
              --gpus 0\
              --keep_interim_results
