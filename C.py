import tensorflow as tf
import tensorflow_federated as tff
import numpy as np
import pandas as pd

# Define the client dataset using the NSL-KDD dataset
df = pd.read_csv("H:/Study/CS/Project/archive (1)/nsl-kdd/KDDTrain+.txt", header=None)
x_train = df.iloc[:, :-1].values
y_train = df.iloc[:, -1].values

# Define the TFF client data
client_data = tff.simulation.datasets.numpy_clients_from_array(
    x_train, y_train, client_ids=['client{}'.format(i) for i in range(len(y_train))])

# Define the model architecture
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(x_train.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Define the loss function and optimizer
loss_fn = tf.keras.losses.SparseCategoricalCrossentropy()
optimizer = tf.keras.optimizers.Adam()

# Define the TFF Federated computation for client update
@tff.tf_computation(model_type=model, input_types=client_data.element_type)
def client_update(model, dataset):
    # Define the client loss function
    def loss():
        x, y = dataset
        y_pred = model(x)
        return loss_fn(y, y_pred)

    # Define the client optimizer
    def opt():
        return optimizer

    # Use Keras API to train the model on the client data for a single epoch
    model.compile(loss=loss_fn, optimizer=optimizer, metrics=['accuracy'])
    model.fit(dataset.batch(len(dataset)), epochs=1)

    # Return the updated model weights
    return model.weights

# Define the TFF Federated computation for server aggregation
@tff.federated_computation(tff.FederatedType(model.type_signature, tff.server_topology()))
def server_aggregate(model_weights):
    # Compute the mean of the model weights
    return tf.nest.map_structure(lambda *x: tf.reduce_mean(x, axis=0), *model_weights)

# Define the TFF Federated algorithm for training
fed_avg = tff.learning.build_federated_averaging_process(model_fn=lambda: model, client_optimizer_fn=lambda: optimizer)
state = fed_avg.initialize()

# Train the model using Federated Learning
for round_num in range(10):
    # Select a random subset of clients to participate in this round
    sample_clients = np.random.choice(client_data.client_ids, size=10, replace=False)
    # Get the client datasets for the selected clients
    sampled_data = [client_data.create_tf_dataset_for_client(client) for client in sample_clients]
    # Update the global model using the selected clients' data
    state, metrics = fed_avg.next(state, sampled_data, client_update=client_update, server_aggregate=server_aggregate)
    # Print the metrics for this round
    print('Round {}: {}'.format(round_num, metrics))