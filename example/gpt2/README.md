<div align="center">
<img src="https://raw.githubusercontent.com/mlgym/mlgym/master/mlGym.svg" width="400px">
</div>

---

This is the documentation for the implementation of GPT2 in MLGym. Here we will go through all the steps and necessary understandings of the MLGym package required to successfully use it for any other LLM project.

To use your own custom datasets or loss functions, you must first need to build constructable classes which can be imported from the MLGym and create a blueprint which can then be used for working on the model.

The first step is to start with a blueprint. The Blueprint class provides a blueprint for creating all the components for the GymJob.

## Blueprint

For the implementation of GPT2 with MLGym the first step is to create a blueprint object. To do this we import Constructable classes from mlgym package as mentioned in ``gpt2_blueprint.py``.
In ML Gym all user defined custom models, loss functions, optimizers, metrics & prediction functions which are to be used for a Gym Job needs to be registered to a Registry.
For this example we have to register our custom GPT2 model from the hugging face library to the ML Gym Model Registry. For this we have a custom Casual Loss Cross Entropy Loss functions which is not part of the default registry needs to be added to the Loss Registry so it can be used during the Gym Job. We also have a user defined ``wikitext-2-raw-vi-tokenized`` dataset which was built using the ``preprocess_dataset.py`` script and thus needs to be registered with the Dataset Iterator and Splits Registry.

## Dataset

We are using the ``wikitext-2-raw-vi-tokenized`` dataset for training and evaluating the GPT2 model. This dataset needs to be pre processed before we can feed it to the hugging face GPT 2 model so to do that we use the ``preprocess_dataset.py`` script.

## Loss Function

The GPT2 model already has a LM Head but for the implemntation of GPT2 in MLGym, we have to specifically implement the loss function. The loss function Casual Loss Cross Entropy Loss function is implemented in the ``clm_loss_function.py``.