export default {
    dataset_repository: {
        component_type_key: "DATASET_REPOSITORY",
        variant_key: "DEFAULT",
        config: {
            storage_connector_path: "./file_storage/"
        }
    },
    dataset_iterators: {
        component_type_key: "DATASET_ITERATORS",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "repository",
                component_name: "dataset_repository"
            }
        ],
        config: {
            dataset_identifier: "mnist",
            split_configs: [
                {
                    split: "train"
                },
                {
                    split: "test"
                }
            ]
        }
    },
    splitted_dataset_iterators: {
        component_type_key: "SPLITTED_DATASET_ITERATORS",
        variant_key: "RANDOM",
        requirements: [
            {
                name: "iterators",
                component_name: "dataset_iterators",
                subscription: ["train", "test"]
            }
        ],
        config: {
            split_configs: {
                train: {
                    train: 0.7,
                    val: 0.3
                }
            },
            seed: 2
        }
    },
    data_collator: {
        component_type_key: "DATA_COLLATOR",
        variant_key: "DEFAULT",
        config: {
            collator_type: {
                injectable: {
                    id: "id_conv_mnist_standard_collator"
                }
            },
            collator_params: {
                target_publication_key: "target_key"
            }
        }
    },
    data_loaders: {
        component_type_key: "DATA_LOADER",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "iterators",
                component_name: "splitted_dataset_iterators",
                subscription: ["train", "val", "test"]
            },
            {
                name: "data_collator",
                component_name: "data_collator"
            }
        ],
        config: {
            batch_size: 10,
            weigthed_sampling_split_name: "train",
            seeds: [0, 1, 2]
        }
    },
    model_registry: {
        component_type_key: "MODEL_REGISTRY",
        variant_key: "DEFAULT"
    },
    model: {
        component_type_key: "MODEL",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "model_registry",
                component_name: "model_registry",
                subscription: "conv_net"
            }
        ],
        config: {
            model_definition: {
                layer_config: [
                    {
                        params: {
                            in_channels: 1,
                            kernel_size: 3,
                            out_channels: 32,
                            stride: 1
                        },
                        type: "conv"
                    },
                    {
                        params: {
                            in_channels: 32,
                            kernel_size: 3,
                            out_channels: 64,
                            stride: 1
                        },
                        type: "conv"
                    },
                    {
                        params: {
                            in_features: 9216,
                            out_features: 128
                        },
                        type: "fc"
                    },
                    {
                        params: {
                            in_features: 128,
                            out_features: 10
                        },
                        type: "fc"
                    }
                ]
            },
            prediction_publication_keys: {
                prediction_publication_key: "model_prediction_key"
            },
            seed: 2
        }
    },
    optimizer: {
        component_type_key: "OPTIMIZER",
        variant_key: "DEFAULT",
        config: {
            optimizer_key: "ADAM",
            params: {
                lr: 0.01
            }
        }
    },
    lr_scheduler: {
        component_type_key: "LR_SCHEDULER",
        variant_key: "DEFAULT",
        config: {
            lr_scheduler_key: "dummy"
        }
    },
    loss_function_registry: {
        component_type_key: "LOSS_FUNCTION_REGISTRY",
        variant_key: "DEFAULT"
    },
    metric_registry: {
        component_type_key: "METRIC_REGISTRY",
        variant_key: "DEFAULT"
    },
    prediction_postprocessing_registry: {
        component_type_key: "PREDICTION_POSTPROCESSING_REGISTRY",
        variant_key: "DEFAULT"
    },
    train_component: {
        component_type_key: "TRAIN_COMPONENT",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "loss_function_registry",
                component_name: "loss_function_registry"
            },
            {
                name: "prediction_postprocessing_registry",
                component_name: "prediction_postprocessing_registry"
            }
        ],
        config: {
            show_progress: true,
            loss_fun_config: {
                prediction_subscription_key: "model_prediction_key",
                target_subscription_key: "target_key",
                key: "CrossEntropyLoss",
                tag: "cross_entropy_loss"
            }
        }
    },
    trainer: {
        component_type_key: "TRAINER",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "train_component",
                component_name: "train_component"
            },
            {
                name: "model",
                component_name: "model",
                subscription: null
            },
            {
                name: "data_loaders",
                component_name: "data_loaders",
                subscription: "train"
            }
        ]
    },
    eval_component: {
        component_type_key: "EVAL_COMPONENT",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "model",
                component_name: "model",
                subscription: null
            },
            {
                name: "data_loaders",
                component_name: "data_loaders",
                subscription: ["train", "val", "test"]
            },
            {
                name: "loss_function_registry",
                component_name: "loss_function_registry"
            },
            {
                name: "metric_registry",
                component_name: "metric_registry"
            },
            {
                name: "prediction_postprocessing_registry",
                component_name: "prediction_postprocessing_registry"
            }
        ],
        config: {
            cpu_target_subscription_keys: ["target_key"],
            cpu_prediction_subscription_keys: [
                "postprocessing_argmax_key",
                "model_prediction_key"
            ],
            post_processors_config: [
                {
                    key: "ARG_MAX",
                    prediction_subscription_key: "model_prediction_key",
                    prediction_publication_key: "postprocessing_argmax_key"
                }
            ],
            metrics_config: [
                {
                    key: "F1_SCORE",
                    params: {
                        average: "macro"
                    },
                    prediction_subscription_key: "postprocessing_argmax_key",
                    target_subscription_key: "target_key",
                    tag: "F1_SCORE_macro"
                },
                {
                    key: "PRECISION",
                    params: {
                        average: "macro"
                    },
                    prediction_subscription_key: "postprocessing_argmax_key",
                    target_subscription_key: "target_key",
                    tag: "PRECISION_macro"
                },
                {
                    key: "RECALL",
                    params: {
                        average: "macro"
                    },
                    prediction_subscription_key: "postprocessing_argmax_key",
                    target_subscription_key: "target_key",
                    tag: "RECALL_macro"
                }
            ],
            loss_funs_config: [
                {
                    prediction_subscription_key: "model_prediction_key",
                    target_subscription_key: "target_key",
                    key: "CrossEntropyLoss",
                    tag: "cross_entropy_loss"
                }
            ],
            show_progress: false
        }
    },
    evaluator: {
        component_type_key: "EVALUATOR",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "eval_component",
                component_name: "eval_component"
            }
        ]
    },
    early_stopping_strategy_registry: {
        component_type_key: "EARLY_STOPPING_STRATEGY_REGISTRY",
        variant_key: "DEFAULT"
    },
    early_stopping_strategy: {
        component_type_key: "EARLY_STOPPING_STRATEGY",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "early_stopping_strategy_registry",
                component_name: "early_stopping_strategy_registry"
            }
        ],
        config: {
            early_stopping_key: "LAST_K_EPOCHS_IMPROVEMENT_STRATEGY",
            early_stopping_config: {
                min_relative_improvement: 1e-5,
                epochs_window: 5,
                split_name: "val",
                monitoring_key: "F1_SCORE_macro",
                is_increase_task: true
            }
        }
    },
    checkpointing_strategy_registry: {
        component_type_key: "CHECKPOINTING_STRATEGY_REGISTRY",
        variant_key: "DEFAULT"
    },
    checkpointing_strategy: {
        component_type_key: "CHECKPOINTING_STRATEGY",
        variant_key: "DEFAULT",
        requirements: [
            {
                name: "checkpointing_strategy_registry",
                component_name: "checkpointing_strategy_registry"
            }
        ],
        config: {
            checkpointing_key: "SAVE_LAST_EPOCH_ONLY_CHECKPOINTING_STRATEGY"
        }
    }
};