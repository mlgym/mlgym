# MLgym 

a python framework for distributed machine learning model training in research.

[![CircleCI](https://circleci.com/gh/le1nux/mlgym.svg?style=svg)](https://circleci.com/gh/le1nux/mlgym)

At its core, MLgym offers functionality to run gridsearches of Pytorch models at scale split over multiple GPUs and centrally store the results using [DashifyML](https://github.com/dashifyML/dashifyML). 

Futhermore, MLgym provides the following key features:

* **Reproducibility** of results due to full experiment specification including dataset, preprocessing routines, model architecture, loss function, metrics and more within a single YAML config.
* Component registry to register custom components with dependencies. For instance one can define a new preprocessing routine component. This component may depend on an iterator component, as specified in the experiment config. During runtime these components are instantiated on the fly.       

**Please note, that at the moment this code should be treated as experimental and is not production ready.** 

## Install

there are two options to install MLgym, the easiest way is to install it from  the pip repository:

```bash
pip install mlgym
``` 

For the latest version, one can directly install it from source by `cd` into the root folder and then running  

```bash
pip install src/
```

## Usage

**NOTE: This framework is still under heavy development and mainly used in research projects. It's most likely not free of bugs and interfaces can still change.**

For usage see this [example](https://github.com/le1nux/mlgym/tree/master/example).

## Copyright

Copyright (c) 2020 Max Lübbering
