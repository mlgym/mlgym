from ml_gym.models.nn.net import NNModel
from typing import Dict
from torch import nn
import torch
import torch.nn.functional as F


class ConvNet(NNModel):

    def __init__(self, prediction_publication_key: str, layer_config: Dict, seed: int = 0):
        super().__init__(seed=seed)
        self.prediction_publication_key = prediction_publication_key
        self.conv_layers = nn.ModuleList([])
        self.fc_layers = nn.ModuleList([])
        for layer in layer_config:
            if layer["type"] == "conv":
                self.conv_layers.append(ConvNet.create_conv_layer_from_config(layer["params"]))
            elif layer["type"] == "fc":
                self.fc_layers.append(ConvNet.create_fc_layer_from_config(layer["params"]))

    @staticmethod
    def create_conv_layer_from_config(layer_dict) -> nn.Module:
        return nn.Conv2d(in_channels=layer_dict["in_channels"],
                         out_channels=layer_dict["out_channels"],
                         kernel_size=layer_dict["kernel_size"],
                         stride=layer_dict["stride"])

    @staticmethod
    def create_fc_layer_from_config(layer_dict) -> nn.Module:
        return nn.Linear(in_features=layer_dict["in_features"],
                         out_features=layer_dict["out_features"])

    def forward_impl(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        output = inputs
        output = self.conv_layers[0](output)
        output = F.relu(output)

        output = self.conv_layers[1](output)
        output = F.relu(output)
        output = F.max_pool2d(output, 2, 2)
        output = F.dropout(output, p=0.25, training=True)

        output = output.view(inputs.shape[0], -1)
        output = self.fc_layers[0](output)
        output = F.relu(output)
        output = F.dropout(output, p=0.5, training=True)
        output = self.fc_layers[1](output)

        return {self.prediction_publication_key: output}

    def forward(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        return self.forward_impl(inputs)
