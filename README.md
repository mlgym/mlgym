<div align="center">
<img src="https://raw.githubusercontent.com/mlgym/mlgym/master/mlGym.svg" width="400px">
</div>

---

a feature-rich deep learning framework providing full reproducibility of experiments. 


[![CircleCI](https://circleci.com/gh/mlgym/mlgym/tree/master.svg?style=svg)](https://circleci.com/gh/mlgym/mlgym/tree/master)

Reproducibility is a recurring issue in deep learning (research) with models often being implemented in Jupyter notebooks or entire training and evaluation pipelines implemented from scratch with every new project.
The lack of standardization and repetitive boilerplate code of experimental setups impede reproducibility. 


MLgym aims to increase reproducibility by separating the experimental setup from the code and providing the entire infrastructure for e.g., model training, model evaluation, experiment logging, checkpointing and experiment analysis. 

Specifically, MLgym provides an extensible set of machine learning components (e.g., trainer, evaluator, loss functions, etc.). The framework instantiates these components dynamically as specified and parameterized within a configuration file (see here, for an exemplary configuration) describing the entire experiment setup (i.e., training and evaluation pipeline). The separation of experimental setup and code maximizes the replicability and interpretability of ML experiments. The machine learning components cut down the implementational efforts significantly and lets your focus solely on your ideas.  


Additionally, MLgym provides the following key features:

* Component registry to register custom components and their dependencies.

* Warm starts allowing to resume training after crash

* Customizable checkpointing strategies

* MLboard webservice for experiment tracking / analysis (live and offline) by subscribing to the websocket logging environment 

* Large scale, multi GPU training supporting grid search, nested cross validation and cross validation

* Distributed logging via websockets and event sourcing, allowing location-independent logging and full replicability


* Definition of training and evaluation pipeline in a configuration file, achieving separation of experiment setup and code. 


**Please note, that at the moment this code should be treated as experimental and is not production ready.** 

## Install

there are two options to install MLgym, the easiest way is to install the framework from the pip repository:

```bash
pip install mlgym
``` 

For the latest version, one can directly install it from source by `cd` into the root folder and then running  

```bash
pip install src/
```

## Usage

We provide an easy-to-use example that lets you run a MLgym [experiment setup](https://github.com/le1nux/mlgym/tree/master/example/grid_search_example). 

Before running the experiments we need to setup the MLboard logging environment, i.e., the websocket service and the RESTful webservice. MLgym logs the training/evaluation progress and evaluation results via the websocket API, allowing the MLboard frontend to receive live updates. The RESTful webservice provides endpoints to receive checkpoints and experiment setups. For a full specification of both APIs see [here](https://github.com/le1nux/mlgym/tree/master/src/ml_board/README.md).

We start the websocket service and the RESTful webservice on ports 5001 and 5002, respectively. Feel free to choose different ports if desired. 
Similarly, we specify the folder `event_storage` as the local event storage folder. Note, to access the websocket service from a different port, we need to specify the [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) allowed origins. In thise example, we only use the websocket service locally from 127.0.0.1:8080 via the MLboard frontend.   
 
```sh
ml_board_ws_endpoint --host 127.0.0.1 --port 5002 --event_storage_path event_storage --cors_allowed_origins http://127.0.0.1:8080

ml_board_rest_endpoint --port 5001 --event_storage_path event_storage

```
 
Next, we run the experiment setup. We `cd` into the example folder and run `run.py` with the respective config whose path is passed via the parameter `gs_config_path`.
The parameter `process_count` specifies the number of experiments that we run in parallel. `num_epochs` limits the maximum number of epochs to train a model. If the model performance does not improve substantially over time, the checkpointing strategy defined in `gs_config.yml` will stop training prematurely.   

```sh 

cd mlgym/example/grid_search_example

python run.py --process_count 3 \
              --text_logging_path general_logging/ \
              --num_epochs 10 \
              --websocket_logging_servers http://127.0.0.1:5002 \
              --gs_rest_api_endpoint http://127.0.0.1:5001 \
              train \
              --gs_config_path gs_config.yml
```

To visualize the live updates, we run the MLboard frontend. We specify the server host and port that delivers the frontend and the endpoints of the REST webservice and the websocket service. The parameter `run_id` refers to the experiment run that we want to analyze and differs in your case. Each experiment runs is stored in separate folders within the `event_storage` path. The folder names refer to the respective experiment run ids. 

```sh
ml_board --ml_board_host 127.0.0.1 --ml_board_port 8080 --rest_endpoint http://127.0.0.1:5001 --ws_endpoint http://127.0.0.1:5002 --run_id 2022-11-06--17-59-10
```
The script returns the parameterized URL pointing to the respective experiment run: 

```
====> ACCESS MLBOARD VIA http://127.0.0.1:8080?rest_endpoint=http%3A//127.0.0.1%3A5001&ws_endpoint=http%3A//127.0.0.1%3A5002&run_id=2022-11-06--17-59-10

```

Note, that the Flask webservice delivers the compiled react files statically, which is why any changes to the frontend code will not be automatically reflected. As a solution, you can start the MLboard react app directly via yarn and call the URL with the respective URL search params in the browser

```sh
cd mlgym/src/ml_board/frontend/dashboard

yarn start
```

To this day, the MLboard frontend is still under development and not all features have been implemented, yet. Therefore, it is possible analyze the log files directly in the event storage. All messages are logged as specified within the [websocket API](https://github.com/le1nux/mlgym/tree/master/src/ml_board/README.md)

To see the messages live `cd` into the event storage directory and `tail` the `event_storage.log` file. 

```sh 
cd event_storage/2022-11-06--17-59-10/
tail -f event_storage.log
```

## MLboard 

Since MLboard is still under heavy development, we would like to give you a sneak peek about what is going to come in the foreseeable future.

<div align="center">
<img src="assets/ml_board_analysis.gif" width="70%" />
</div>


## Copyright

Copyright (c) 2020 Max Lübbering

For license see: https://github.com/mlgym/mlgym/blob/master/LICENSE
