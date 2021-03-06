#!/usr/bin/python

# Created: 28/10/2015
# Daniel Dixey

import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.layers.recurrent import LSTM


class CNN_model(object):

    def __init__(self,
                 batch_size=5,
                 embedding_dims=150,
                 nb_filters=50,
                 filter_length=3,
                 hidden_dims=100,
                 nb_epoch=5,
                 nb_words=1700000,
                 maxlen=200,
                 nb_classes=34):
        # Defining Inputs for the Neural Network
        self.batch_size = batch_size
        self.embedding_dims = embedding_dims
        self.nb_filters = nb_filters
        self.filter_length = filter_length
        self.hidden_dims = hidden_dims
        self.nb_epoch = nb_epoch
        self.nb_words = nb_words
        self.maxlen = maxlen
        self.nb_classes = nb_classes
        self.model = Sequential()

    def build_cnn_rnn(self):
        print('Building model...')
        # efficient embedding layer which maps our vocab indices into
        # embedding_dims dimensions
        self.model.add(Embedding(self.nb_words, self.embedding_dims))
        self.model.add(Dropout(0.25))
        # we add a Convolution1D, which will learn nb_filters word group
        # filters of size filter_length:
        self.model.add(Convolution1D(input_dim=self.embedding_dims,
                                     nb_filter=self.nb_filters,
                                     filter_length=self.filter_length,
                                     border_mode="valid",
                                     activation="relu",
                                     subsample_length=1))
        # we use standard max pooling (halving the output of the previous
        # layer)
        self.model.add(MaxPooling1D(pool_length=2))
        # Convolutional Net to RNN
        self.model.add(LSTM(200))
        self.model.add(Dropout(0.25))
        # We project onto a single unit output layer, and squash to the number
        # of classes
        self.model.add(Dense(self.nb_classes))
        # Softmax Output
        self.model.add(Activation('softmax'))
        # Compiling the Model
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='rmsprop',
                           class_mode="categorical")

    def train(self, X, y):
        print('X_train shape:', X.shape)
        print('Y_train shape:', y.shape)

        # Preprocess the dataset
        X = sequence.pad_sequences(X, maxlen=self.maxlen)
        y = np_utils.to_categorical(y, self.nb_classes)

        self.model.fit(X,
                       y,
                       batch_size=self.batch_size,
                       nb_epoch=self.nb_epoch,
                       show_accuracy=True,
                       validation_split=0.1)

    def predict(self, X):
        # Prediction
        X = sequence.pad_sequences(X, maxlen=self.maxlen)
        y_pred = self.model.predict(X,
                                    batch_size=self.batch_size,
                                    verbose=1)
        return y_pred

    def evaluate(self, X, y):
        # Evaluation Metric
        X = sequence.pad_sequences(X, maxlen=self.maxlen)
        y = np_utils.to_categorical(y, self.nb_classes)
        output = self.model.evaluate(X,
                                     y,
                                     batch_size=self.batch_size,
                                     show_accuracy=False,
                                     verbose=1)
        return output



# Loading Datasets
#X_train = np.load('./Text_Classification/Models/X_train.npy')
#y_train = np.load('./Text_Classification/Models/y_train.npy')
X_train = np.load('./X_train.npy')
y_train = np.load('./y_train.npy')

# Call the class
model = CNN_model()

# Build the RNN
model.build_cnn_rnn()

# Train the Neural Network
model.train(X_train, y_train)

# Loading Datasets
#y_test = np.load('./Text_Classification/Models/y_test.npy')
#X_test = np.load('./Text_Classification/Models/X_test.npy')
y_test = np.load('./y_test.npy')
X_test = np.load('./X_test.npy')

# Testing the Neural Network
evaluation = model.evaluate(X_test, y_test)

print evaluation

# Getting a prediction from the Neural Network
prediction = model.predict(X_test)

# Save the Output to Numpy File for inspection
np.save('./Output.npy')

# Save Model Weights as pickle file
model.model.save_weights("model_weights.pkl")

