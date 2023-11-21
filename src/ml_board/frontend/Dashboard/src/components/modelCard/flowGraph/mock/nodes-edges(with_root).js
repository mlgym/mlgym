export const initialNodes = [
  {
    id: "pipeline_details",
    position: {
      x: 800,
      y: 800
    },
    data: {
      label: "pipeline_details"
    },
    type: "input"
  },
  {
    id: "dataset_repository",
    position: {
      x: 0,
      y: 0
    },
    data: {
      label: "dataset_repository"
    },
    type: "output"
  },
  {
    id: "dataset_iterators",
    position: {
      x: 100,
      y: 100
    },
    data: {
      label: "dataset_iterators"
    },
    type: "default"
  },
  {
    id: "splitted_dataset_iterators",
    position: {
      x: 200,
      y: 200
    },
    data: {
      label: "splitted_dataset_iterators"
    },
    type: "default"
  },
  {
    id: "data_collator",
    position: {
      x: 300,
      y: 300
    },
    data: {
      label: "data_collator"
    },
    type: "output"
  },
  {
    id: "data_loaders",
    position: {
      x: 400,
      y: 400
    },
    data: {
      label: "data_loaders"
    },
    type: "default"
  },
  {
    id: "model_registry",
    position: {
      x: 500,
      y: 500
    },
    data: {
      label: "model_registry"
    },
    type: "output"
  },
  {
    id: "model",
    position: {
      x: 600,
      y: 600
    },
    data: {
      label: "model"
    },
    type: "default"
  },
  {
    id: "optimizer",
    position: {
      x: 700,
      y: 700
    },
    data: {
      label: "optimizer"
    },
    type: "output"
  },
  {
    id: "lr_scheduler",
    position: {
      x: 800,
      y: 800
    },
    data: {
      label: "lr_scheduler"
    },
    type: "output"
  },
  {
    id: "loss_function_registry",
    position: {
      x: 900,
      y: 900
    },
    data: {
      label: "loss_function_registry"
    },
    type: "output"
  },
  {
    id: "metric_registry",
    position: {
      x: 1000,
      y: 1000
    },
    data: {
      label: "metric_registry"
    },
    type: "output"
  },
  {
    id: "prediction_postprocessing_registry",
    position: {
      x: 1100,
      y: 1100
    },
    data: {
      label: "prediction_postprocessing_registry"
    },
    type: "output"
  },
  {
    id: "train_component",
    position: {
      x: 1200,
      y: 1200
    },
    data: {
      label: "train_component"
    },
    type: "default"
  },
  {
    id: "trainer",
    position: {
      x: 1300,
      y: 1300
    },
    data: {
      label: "trainer"
    },
    type: "default"
  },
  {
    id: "eval_component",
    position: {
      x: 1400,
      y: 1400
    },
    data: {
      label: "eval_component"
    },
    type: "default"
  },
  {
    id: "evaluator",
    position: {
      x: 1500,
      y: 1500
    },
    data: {
      label: "evaluator"
    },
    type: "default"
  },
  {
    id: "early_stopping_strategy_registry",
    position: {
      x: 1600,
      y: 1600
    },
    data: {
      label: "early_stopping_strategy_registry"
    },
    type: "output"
  },
  {
    id: "early_stopping_strategy",
    position: {
      x: 1700,
      y: 1700
    },
    data: {
      label: "early_stopping_strategy"
    },
    type: "default"
  },
  {
    id: "checkpointing_strategy_registry",
    position: {
      x: 1800,
      y: 1800
    },
    data: {
      label: "checkpointing_strategy_registry"
    },
    type: "output"
  },
  {
    id: "checkpointing_strategy",
    position: {
      x: 1900,
      y: 1900
    },
    data: {
      label: "checkpointing_strategy"
    },
    type: "default"
  }
];

export const initialEdges = [
  {
    id: "pipeline_details-dataset_repository",
    source: "pipeline_details",
    target: "dataset_repository"
  },
  {
    id: "pipeline_details-dataset_iterators",
    source: "pipeline_details",
    target: "dataset_iterators"
  },
  {
    id: "dataset_iterators-dataset_repository",
    source: "dataset_iterators",
    target: "dataset_repository"
  },
  {
    id: "pipeline_details-splitted_dataset_iterators",
    source: "pipeline_details",
    target: "splitted_dataset_iterators"
  },
  {
    id: "splitted_dataset_iterators-dataset_iterators",
    source: "splitted_dataset_iterators",
    target: "dataset_iterators"
  },
  {
    id: "pipeline_details-data_collator",
    source: "pipeline_details",
    target: "data_collator"
  },
  {
    id: "pipeline_details-data_loaders",
    source: "pipeline_details",
    target: "data_loaders"
  },
  {
    id: "data_loaders-splitted_dataset_iterators",
    source: "data_loaders",
    target: "splitted_dataset_iterators"
  },
  {
    id: "data_loaders-data_collator",
    source: "data_loaders",
    target: "data_collator"
  },
  {
    id: "pipeline_details-model_registry",
    source: "pipeline_details",
    target: "model_registry"
  },
  {
    id: "pipeline_details-model",
    source: "pipeline_details",
    target: "model"
  },
  {
    id: "model-model_registry",
    source: "model",
    target: "model_registry"
  },
  {
    id: "pipeline_details-optimizer",
    source: "pipeline_details",
    target: "optimizer"
  },
  {
    id: "pipeline_details-lr_scheduler",
    source: "pipeline_details",
    target: "lr_scheduler"
  },
  {
    id: "pipeline_details-loss_function_registry",
    source: "pipeline_details",
    target: "loss_function_registry"
  },
  {
    id: "pipeline_details-metric_registry",
    source: "pipeline_details",
    target: "metric_registry"
  },
  {
    id: "pipeline_details-prediction_postprocessing_registry",
    source: "pipeline_details",
    target: "prediction_postprocessing_registry"
  },
  {
    id: "pipeline_details-train_component",
    source: "pipeline_details",
    target: "train_component"
  },
  {
    id: "train_component-loss_function_registry",
    source: "train_component",
    target: "loss_function_registry"
  },
  {
    id: "train_component-prediction_postprocessing_registry",
    source: "train_component",
    target: "prediction_postprocessing_registry"
  },
  {
    id: "pipeline_details-trainer",
    source: "pipeline_details",
    target: "trainer"
  },
  {
    id: "trainer-train_component",
    source: "trainer",
    target: "train_component"
  },
  {
    id: "trainer-model",
    source: "trainer",
    target: "model"
  },
  {
    id: "trainer-data_loaders",
    source: "trainer",
    target: "data_loaders"
  },
  {
    id: "pipeline_details-eval_component",
    source: "pipeline_details",
    target: "eval_component"
  },
  {
    id: "eval_component-model",
    source: "eval_component",
    target: "model"
  },
  {
    id: "eval_component-data_loaders",
    source: "eval_component",
    target: "data_loaders"
  },
  {
    id: "eval_component-loss_function_registry",
    source: "eval_component",
    target: "loss_function_registry"
  },
  {
    id: "eval_component-metric_registry",
    source: "eval_component",
    target: "metric_registry"
  },
  {
    id: "eval_component-prediction_postprocessing_registry",
    source: "eval_component",
    target: "prediction_postprocessing_registry"
  },
  {
    id: "pipeline_details-evaluator",
    source: "pipeline_details",
    target: "evaluator"
  },
  {
    id: "evaluator-eval_component",
    source: "evaluator",
    target: "eval_component"
  },
  {
    id: "pipeline_details-early_stopping_strategy_registry",
    source: "pipeline_details",
    target: "early_stopping_strategy_registry"
  },
  {
    id: "pipeline_details-early_stopping_strategy",
    source: "pipeline_details",
    target: "early_stopping_strategy"
  },
  {
    id: "early_stopping_strategy-early_stopping_strategy_registry",
    source: "early_stopping_strategy",
    target: "early_stopping_strategy_registry"
  },
  {
    id: "pipeline_details-checkpointing_strategy_registry",
    source: "pipeline_details",
    target: "checkpointing_strategy_registry"
  },
  {
    id: "pipeline_details-checkpointing_strategy",
    source: "pipeline_details",
    target: "checkpointing_strategy"
  },
  {
    id: "checkpointing_strategy-checkpointing_strategy_registry",
    source: "checkpointing_strategy",
    target: "checkpointing_strategy_registry"
  }
];
