import os
import numpy as np
import pandas as pd
import flwr as fl
import tensorflow as tf

# Make TensorFlow log less verbose
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load model and data (NSL-KDD)
nsl_kdd_train_path = "H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTrain+.txt"
nsl_kdd_test_path = "H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTest+.txt"
train_df = pd.read_csv(nsl_kdd_train_path, header=None)
test_df = pd.read_csv(nsl_kdd_test_path, header=None)
n_features = train_df.shape[1] - 1
n_classes = len(train_df.iloc[:, -1].unique())
x_train = train_df.iloc[:, :-1].values.astype(np.float32)
y_train = train_df.iloc[:, -1].values.astype(np.int32)
x_test = test_df.iloc[:, :-1].values.astype(np.float32)
y_test = test_df.iloc[:, -1].values.astype(np.int32)

# Normalize data
x_train = (x_train - np.mean(x_train, axis=0)) / np.std(x_train, axis=0)
x_test = (x_test - np.mean(x_test, axis=0)) / np.std(x_test, axis=0)

# Define Flower client
class NSLKDDClient(fl.client.NumPyClient):
    def get_parameters(self):
        return model.get_weights()

    def fit(self, parameters, config):
        model.set_weights(parameters)
        model.fit(x_train, y_train, epochs=1, batch_size=32)
        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters):
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test)
        return loss, len(x_test), {"accuracy": accuracy}

# Define the model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(n_features,)),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(n_classes, activation="softmax"),
])

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Start Flower client
fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=NSLKDDClient())