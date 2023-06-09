import os
import sys
import timeit
from collections import OrderedDict
from typing import Dict, List, Tuple

import flwr as fl
import numpy as np
import torch

# Import dataset-specific functions
from nsl_kdd import load_data, preprocess, create_model, train, test


# Define Flower client
class NSLClient(fl.client.NumPyClient):
    def __init__(
        self,
        model: torch.nn.Module,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> None:
        self.model = model
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test
        self.y_test = y_test

    def get_parameters(self, config: Dict[str, str]) -> List[np.ndarray]:
        self.model.train()
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]) -> None:
        self.model.train()
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(
        self, parameters: List[np.ndarray], config: Dict[str, str]
    ) -> Tuple[List[np.ndarray], int, Dict]:
        self.set_parameters(parameters)
        train(self.model, self.x_train, self.y_train, epochs=1, batch_size=128)
        return self.get_parameters(config={}), len(self.x_train), {}

    def evaluate(
        self, parameters: List[np.ndarray], config: Dict[str, str]
    ) -> Tuple[float, int, Dict]:
        self.set_parameters(parameters)
        loss, accuracy = test(self.model, self.x_test, self.y_test)
        return float(loss), len(self.x_test), {"accuracy": float(accuracy)}


# Main function
def main() -> None:
    # Load and preprocess data
    x_train, y_train, x_test, y_test = load_data()
    x_train, y_train, x_test, y_test = preprocess(x_train, y_train, x_test, y_test)

    # Create and compile model
    model = create_model()
    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )

    # Start client
    client = NSLClient(model, x_train, y_train, x_test, y_test)
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=client)


if __name__ == "__main__":
    main()