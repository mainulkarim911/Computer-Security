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
from tensorflow.keras import regularizers

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


# add the column labels
columns = (['duration'
,'protocol_type'
,'service'
,'flag'
,'src_bytes'
,'dst_bytes'
,'land'
,'wrong_fragment'
,'urgent'
,'hot'
,'num_failed_logins'
,'logged_in'
,'num_compromised'
,'root_shell'
,'su_attempted'
,'num_root'
,'num_file_creations'
,'num_shells'
,'num_access_files'
,'num_outbound_cmds'
,'is_host_login'
,'is_guest_login'
,'count'
,'srv_count'
,'serror_rate'
,'srv_serror_rate'
,'rerror_rate'
,'srv_rerror_rate'
,'same_srv_rate'
,'diff_srv_rate'
,'srv_diff_host_rate'
,'dst_host_count'
,'dst_host_srv_count'
,'dst_host_same_srv_rate'
,'dst_host_diff_srv_rate'
,'dst_host_same_src_port_rate'
,'dst_host_srv_diff_host_rate'
,'dst_host_serror_rate'
,'dst_host_srv_serror_rate'
,'dst_host_rerror_rate'
,'dst_host_srv_rerror_rate'
,'attack'
,'level'])

df_train=pd.read_csv('H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTrain+.txt',header=None,names=columns)
df_test=pd.read_csv('H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTest+.txt',header=None,names=columns)

# Define the model architecture
""" model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(1, activation='softmax')
]) """
#model = tf.keras.applications.MobileNetV2((10,), classes=20, weights=None)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(units=64, activation='relu', input_shape=(10,), 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(units=128, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=512, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(units=128, activation='relu', 
                          kernel_regularizer=regularizers.L1L2(l1=1e-5, l2=1e-4), 
                          bias_regularizer=regularizers.L2(1e-4),
                          activity_regularizer=regularizers.L2(1e-5)),
    tf.keras.layers.Dropout(0.1),
    tf.keras.layers.Dense(units=1, activation='sigmoid'),
])

# Define the optimizer
optimizer = tf.keras.optimizers.Adam()
model.compile(optimizer='adam', loss=tf.keras.losses.BinaryCrossentropy(from_logits=True), metrics=['accuracy'])

class NSLKDDClient(fl.client.NumPyClient):
    def __init__(self):
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_data()

    def load_data(self):
        # TODO: Implement code to load the NSL-KDD dataset
        # Return the training and test data as numpy arrays
        df_train["binary_attack"]=df_train.attack.map(lambda a: "normal" if a == 'normal' else "abnormal")
        df_train.drop('attack',axis=1,inplace=True)

        df_test["binary_attack"]=df_test.attack.map(lambda a: "normal" if a == 'normal' else "abnormal")
        df_test.drop('attack',axis=1,inplace=True)

        df_train.select_dtypes(['object']).columns

        # Label Encoder
        from sklearn import preprocessing
        le=preprocessing.LabelEncoder()
        clm=['protocol_type', 'service', 'flag', 'binary_attack']
        for x in clm:
            df_train[x]=le.fit_transform(df_train[x])
            df_test[x]=le.fit_transform(df_test[x])
            
        #Spliting the data

        x_train=df_train.drop('binary_attack',axis=1)
        y_train=df_train["binary_attack"]

        x_test=df_test.drop('binary_attack',axis=1)
        y_test=df_test["binary_attack"]  


        from sklearn.feature_selection import mutual_info_classif
        mutual_info = mutual_info_classif(x_train, y_train)
        mutual_info = pd.Series(mutual_info)
        mutual_info.index = x_train.columns
        mutual_info.sort_values(ascending=False)
            

        # I will choose 20 features to select
        from sklearn.feature_selection import SelectKBest
        sel_five_cols = SelectKBest(mutual_info_classif, k=20)
        sel_five_cols.fit(x_train, y_train)
        x_train.columns[sel_five_cols.get_support()]    
            
        col=['service', 'flag', 'src_bytes', 'dst_bytes', 'logged_in',
            'same_srv_rate', 'diff_srv_rate', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate']
        x_train=x_train[col]
        x_test=x_test[col]    


        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        x_train= scaler.fit_transform(x_train)
        x_test= scaler.fit_transform(x_test)
        #print(x_train.shape)
        return x_train, y_train, x_test, y_test

    def get_parameters(self,config):
        # Get the current model weights
        return model.get_weights()

    def fit(self, parameters, config):
        # Set the current model weights to the received parameters
        model.set_weights(parameters)
        # Train the model on the client's data for one epoch
        model.fit(self.x_train, self.y_train, epochs=1, batch_size=32)
        # Get the updated model weights
        updated_parameters = model.get_weights()
        # Return the updated model weights and the number of examples trained on
        return updated_parameters, len(self.x_train), {}

    def evaluate(self, parameters, config):
        # Set the current model weights to the received parameters
        model.set_weights(parameters)
        # Evaluate the model on the client's test data and return the loss and accuracy
        loss, accuracy = model.evaluate(self.x_test, self.y_test)
        return loss, len(self.x_test), {"accuracy": accuracy}

# Define the FLWR client and start it
fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=NSLKDDClient())