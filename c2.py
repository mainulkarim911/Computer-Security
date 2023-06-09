import flwr as fl
import tensorflow as tf
import numpy as np

from typing import Tuple, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from torch import Tensor
from torchvision.datasets import CIFAR10
import flwr as fl
import tensorflow as tf

#loading and importing data 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split,StratifiedKFold,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV,RandomizedSearchCV
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import make_scorer, roc_auc_score
import scipy
from scipy import stats
import warnings
warnings.filterwarnings("ignore")
from sklearn.preprocessing import StandardScaler


# Define the model architecture
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(120,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])
# Define the optimizer
optimizer = tf.keras.optimizers.Adam()

def load_nsl_kdd_data():
        # TODO: Implement code to load the NSL-KDD dataset
        # Return the training and test data as numpy arrays
        column_names = [
        "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
        "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
        "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
        "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
        "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
        "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
        "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
        "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
        "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "attack_type", "difficulty_level"
        ]

        # Load the training and test data using pandas
        train_df = pd.read_csv("H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTrain+.txt", header=None, names=column_names)
        test_df = pd.read_csv("H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTest+.txt", header=None, names=column_names)

        # Convert the attack types to binary labels (0 for normal, 1 for attack)
        attack_types = train_df["attack_type"].unique()
        attack_map = {}
        for i, attack_type in enumerate(attack_types):
            if attack_type == "normal":
                attack_map[attack_type] = 0
            else:
                attack_map[attack_type] = 1
        train_df["attack"] = train_df["attack_type"].map(attack_map)
        test_df["attack"] = test_df["attack_type"].map(attack_map)

        # Remove unused columns and convert categorical variables to one-hot encoding
        categorical_columns = ["protocol_type", "service", "flag"]
        for column in categorical_columns:
            train_df[column] = pd.Categorical(train_df[column])
            test_df[column] = pd.Categorical(test_df[column])
            train_one_hot = pd.get_dummies(train_df[column], prefix=column)
            test_one_hot = pd.get_dummies(test_df[column], prefix=column)
            train_df = pd.concat([train_df, train_one_hot], axis=1)
            test_df = pd.concat([test_df, test_one_hot], axis=1)
        train_df.drop(columns=["attack_type", "difficulty_level"] + categorical_columns, inplace=True)
        test_df.drop(columns=["attack_type", "difficulty_level"] + categorical_columns, inplace=True)

        # Convert the data to numpy arrays
        x_train = train_df.drop(columns=["attack"]).values.astype(np.float32)
        y_train = train_df["attack"].values.astype(np.int32)
        x_test = test_df.drop(columns=["attack"]).values.astype(np.float32)
        y_test = test_df["attack"].values.astype(np.int32)
        return x_train, y_train, x_test, y_test

class NSLKDDClient(fl.client.NumPyClient):
    def __init__(self):
        # Load the NSL-KDD data
        self.x_train, self.y_train, self.x_test, self.y_test = load_nsl_kdd_data()

        # Define the shape of the input data and number of classes
        self.input_shape = (self.x_train.shape[1],)
        self.num_classes = len(np.unique(self.y_train))

        # Define the model architecture
        self.model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation="relu", input_shape=self.input_shape),
            tf.keras.layers.Dense(self.num_classes, activation="softmax")
        ])

    def get_parameters(self,config):
        return self.model.get_weights()

    def fit(self, parameters, config):
        self.model.set_weights(parameters)
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        self.model.fit(
            self.x_train,
            self.y_train,
            epochs=config["epochs"],
            batch_size=config["batch_size"]
        )
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test)
        return loss, len(self.x_test), {"accuracy": accuracy}

# Define the FLWR client and start it
fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=NSLKDDClient())