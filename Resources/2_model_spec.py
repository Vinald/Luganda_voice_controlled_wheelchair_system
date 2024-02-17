# -*- coding: utf-8 -*-
"""2_model_spec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dXGr0ahhIl6Ao_A8O0LAb0xLG0wdeRMO

## Packages
"""

import os
import json
import math
# from google.colab import drive
import wave
import pathlib

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


import tensorflow as tf
from tensorflow.keras import layers, models
import tensorflow.keras as keras

import librosa
import IPython.display as display

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

"""# Mount google drive
adisamproject@gmail.com
"""

from google.colab import drive
drive.mount('/content/drive')

"""# Audio Inspection and Properties

### Load on audio file
"""

DATASET_PATH = "/content/drive/My Drive/2_Luganda/dataset/ddyo"
example_audio_path = os.path.join(DATASET_PATH, 'Recording_162.wav')
audio_signal, sample_rate = librosa.load(example_audio_path)

audio = wave.open('/content/drive/My Drive/2_Luganda/dataset/ddyo/Recording_162.wav', 'rb')

number_of_channel = audio.getnchannels()
sample_width = audio.getsampwidth()
frame_rate = audio.getframerate()
number_of_frames = audio.getnframes()

print('Number of channels:', number_of_channel)
print('Sample width:',       sample_width)
print('frame rate:',         frame_rate)
print('Number of frames:',   number_of_frames)
print('Parameters:',         audio.getparams())

duration = librosa.get_duration(y=audio_signal, sr=sample_rate)
print(f"Duration: {duration} seconds")
print(f"Sample Rate: {sample_rate} Hz")

plt.figure(figsize=(12, 4))
plt.plot(audio_signal, color='green')
plt.title('Audio Waveform')
plt.xlabel('ddyo')
plt.ylabel('Amplitude')
plt.show()

plt.figure(figsize=(12, 4))
sns.histplot(audio_signal, bins=50, kde=True)
plt.title('Amplitude Distribution')
plt.xlabel('Amplitude')
plt.ylabel('Frequency')
plt.show()

"""### Visualize the audio waveform

# Loading Raw Audio Data

The dataset's audio clips are of 6 classes and stored in six folders corresponding to each speech command:
- `ddyo`
- `kkono`
- `mu maaso`
- `emabega`
- `yimirira`
- `gaali`

### Set the seed value
"""

seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)

DATASET_PATH = "/content/drive/My Drive/2_Luganda/dataset"
data_dir = pathlib.Path(DATASET_PATH)

commands = np.array(tf.io.gfile.listdir(str(data_dir)))
print('Commands:', commands)

"""# Split into Train and validation"""

# Set the desired duration
desired_duration = 2  # in seconds

# Update the output_sequence_length parameter
output_sequence_length = int(desired_duration * sample_rate)

# train_ds, val_ds = tf.keras.utils.audio_dataset_from_directory(
#     directory=data_dir,
#     batch_size=64,
#     validation_split=0.3,
#     seed=0,
#     output_sequence_length=16000,
#     subset='both')

train_ds, val_ds = tf.keras.utils.audio_dataset_from_directory(
    directory=data_dir,
    batch_size=64,
    validation_split=0.2,
    seed=0,
    output_sequence_length=output_sequence_length,
    subset='both'
)

label_names = np.array(train_ds.class_names)
print()
print("label names:", label_names)

"""### The audio clips have a shape of `(batch, samples, channels)`."""

train_ds.element_spec

def squeeze(audio, labels):
  audio = tf.squeeze(audio, axis=-1)
  return audio, labels

train_ds = train_ds.map(squeeze, tf.data.AUTOTUNE)
val_ds = val_ds.map(squeeze, tf.data.AUTOTUNE)

test_ds = val_ds.shard(num_shards=2, index=0)
val_ds = val_ds.shard(num_shards=2, index=1)

for example_audio, example_labels in train_ds.take(1):
  print(example_audio.shape)
  print(example_labels.shape)

"""### Plot a few audio waveforms:"""

label_names[[1,2,3,0,4,5]]

plt.figure(figsize=(16, 10))
rows = 2
cols = 3
n = rows * cols
for i in range(n):
  plt.subplot(rows, cols, i+1)
  audio_signal = example_audio[i]
  plt.plot(audio_signal)
  plt.title(label_names[example_labels[i]])
  plt.yticks(np.arange(-1.2, 1.2, 0.2))
  plt.ylim([-1.1, 1.1])

def get_spectrogram(waveform):
  # Convert the waveform to a spectrogram via a STFT.
  spectrogram = tf.signal.stft(
      waveform, frame_length=255, frame_step=128)
  # Obtain the magnitude of the STFT.
  spectrogram = tf.abs(spectrogram)
  # Add a `channels` dimension, so that the spectrogram can be used
  # as image-like input data with convolution layers (which expect
  # shape (`batch_size`, `height`, `width`, `channels`).
  spectrogram = spectrogram[..., tf.newaxis]
  return spectrogram

"""### The shapes of a tensorized waveform and the corresponding spectrogram, and play the original audio:"""

for i in range(3):
  label = label_names[example_labels[i]]
  waveform = example_audio[i]
  spectrogram = get_spectrogram(waveform)

  print('Label:', label)
  print('Waveform shape:', waveform.shape)
  print('Spectrogram shape:', spectrogram.shape)
  print('Audio playback')
  display.display(display.Audio(waveform, rate=16000))

"""### Displaying a spectrogram:"""

# Convert the frequencies to log scale and transpose, so that the time is
# represented on the x-axis (columns).
# Add an epsilon to avoid taking a log of zero.

def plot_spectrogram(spectrogram, ax):
  if len(spectrogram.shape) > 2:
    assert len(spectrogram.shape) == 3
    spectrogram = np.squeeze(spectrogram, axis=-1)

  log_spec = np.log(spectrogram.T + np.finfo(float).eps)
  height = log_spec.shape[0]
  width = log_spec.shape[1]
  X = np.linspace(0, np.size(spectrogram), num=width, dtype=int)
  Y = range(height)
  ax.pcolormesh(X, Y, log_spec)

"""### Plot of waveform over time and the corresponding spectrogram."""

fig, axes = plt.subplots(2, figsize=(12, 8))
timescale = np.arange(waveform.shape[0])
axes[0].plot(timescale, waveform.numpy())
axes[0].set_title('Waveform')
axes[0].set_xlim([0, 16000])

plot_spectrogram(spectrogram.numpy(), axes[1])
axes[1].set_title('Spectrogram')
plt.suptitle(label.title())
plt.show()

"""## Create spectrogram datasets from the audio datasets:"""

def make_spec_ds(ds):
  return ds.map(
      map_func=lambda audio,label: (get_spectrogram(audio), label),
      num_parallel_calls=tf.data.AUTOTUNE)

train_spectrogram_ds = make_spec_ds(train_ds)
val_spectrogram_ds = make_spec_ds(val_ds)
test_spectrogram_ds = make_spec_ds(test_ds)

"""Examine the spectrograms for different examples of the dataset:"""

for example_spectrograms, example_spect_labels in train_spectrogram_ds.take(1):
  break

rows = 2
cols = 3
n = rows*cols
fig, axes = plt.subplots(rows, cols, figsize=(16, 9))

for i in range(n):
    r = i // cols
    c = i % cols
    ax = axes[r][c]
    plot_spectrogram(example_spectrograms[i].numpy(), ax)
    ax.set_title(label_names[example_spect_labels[i].numpy()])

plt.show()

"""### `Dataset.cache` and `Dataset.prefetch` operations to reduce read latency while training the model:"""
# Cache, shuffle, and prefetch the training, validation, and test datasets
train_spectrogram_ds = train_spectrogram_ds.cache().shuffle(10000).prefetch(tf.data.AUTOTUNE)
val_spectrogram_ds = val_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)
test_spectrogram_ds = test_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)

# Print the sizes of the train and validation datasets
print(f"Train dataset size: {len(train_spectrogram_ds)}")
print(f"Validation dataset size: {len(val_spectrogram_ds)}")

"""## Model 1"""

# Get the input shape from the example spectrograms
input_shape = example_spectrograms.shape[1:]
print('Input shape:', input_shape)
num_labels = len(label_names)

# Normalize the input data
norm_layer = layers.Normalization()
norm_layer.adapt(data=train_spectrogram_ds.map(map_func=lambda spec, label: spec))

# Define the model architecture
model = models.Sequential([
  layers.Input(shape=input_shape),
  layers.Resizing(32, 32),
  norm_layer,
  layers.Conv2D(32, 3, activation='relu'),
  layers.Conv2D(64, 3, activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.25),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dropout(0.5),
  layers.Dense(num_labels),
])

# Print the model summary
model.summary()

"""### Keras model with the Adam optimizer and the cross-entropy loss:"""

# Compile the model with the Adam optimizer and cross-entropy loss
model.compile(
  optimizer=tf.keras.optimizers.Adam(),
  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
  metrics=['accuracy'],
)

"""### Train the model"""

# Train the model for a specified number of epochs
EPOCHS = 10
history = model.fit(
  train_spectrogram_ds,
  validation_data=val_spectrogram_ds,
  epochs=EPOCHS,
  callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
)

"""### Plot the training and validation loss curves to check how your model has improved during training:"""

# Plot the training and validation loss curves
metrics = history.history
plt.figure(figsize=(14,5))
plt.subplot(1,2,1)
plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.ylim([0, max(plt.ylim())])
plt.xlabel('Epoch')
plt.ylabel('Loss [CrossEntropy]')

plt.subplot(1,2,2)
plt.plot(history.epoch, 100*np.array(metrics['accuracy']), 100*np.array(metrics['val_accuracy']))
plt.legend(['accuracy', 'val_accuracy'])
plt.ylim([0, 100])
plt.xlabel('Epoch')
plt.ylabel('Accuracy [%]')

"""### Evaluate the model performance

Run the model on the test set and check the model's performance:
"""

# Evaluate the model on the test set
model.evaluate(test_spectrogram_ds, return_dict=True)

"""### Display a confusion matrix"""

# Generate predictions on the test set
y_pred = model.predict(test_spectrogram_ds)
y_pred = tf.argmax(y_pred, axis=1)

# Get the true labels from the test set
y_true = tf.concat(list(test_spectrogram_ds.map(lambda s,lab: lab)), axis=0)

# Compute the confusion matrix
confusion_mtx = tf.math.confusion_matrix(y_true, y_pred)

# Plot the confusion matrix
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_mtx,
      xticklabels=label_names,
      yticklabels=label_names,
      annot=True, fmt='g')
plt.xlabel('Prediction')
plt.ylabel('Label')
plt.show()

"""### Export the model with preprocessing"""

# Define a class for exporting the model with preprocessing
class ExportModel(tf.Module):
  def __init__(self, model):
  self.model = model

  # Accept either a string-filename or a batch of waveforms.
  # You could add additional signatures for a single wave, or a ragged-batch.
  self.__call__.get_concrete_function(
    x=tf.TensorSpec(shape=(), dtype=tf.string))
  self.__call__.get_concrete_function(
     x=tf.TensorSpec(shape=[None, 16000], dtype=tf.float32))


  @tf.function
  def __call__(self, x):
  # If they pass a string, load the file and decode it.
  if x.dtype == tf.string:
    x = tf.io.read_file(x)
    x, _ = tf.audio.decode_wav(x, desired_channels=1, desired_samples=16000,)
    x = tf.squeeze(x, axis=-1)
    x = x[tf.newaxis, :]

  x = get_spectrogram(x)
  result = self.model(x, training=False)

  class_ids = tf.argmax(result, axis=-1)
  class_names = tf.gather(label_names, class_ids)
  return {'predictions':result,
      'class_ids': class_ids,
      'class_names': class_names}

"""## Model 2"""

# Define the architecture for Model 2
model2 = models.Sequential([
  layers.Input(shape=input_shape),
  layers.Resizing(32, 32),
  norm_layer,
  layers.Conv2D(32, 3, activation='relu'),
  layers.BatchNormalization(),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, activation='relu'),
  layers.BatchNormalization(),
  layers.MaxPooling2D(),
  layers.Dropout(0.25),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dropout(0.5),
  layers.Dense(num_labels),
])

# Print the model summary for Model 2
model2.summary()

# Compile Model 2
model2.compile(
  optimizer=tf.keras.optimizers.Adam(),
  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
  metrics=['accuracy'],
)

# Train Model 2
EPOCHS = 10
history = model2.fit(
  train_spectrogram_ds,
  validation_data=val_spectrogram_ds,
  epochs=EPOCHS,
  callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
)

# Plot the training and validation loss curves for Model 2
metrics = history.history
plt.figure(figsize=(16,6))
plt.subplot(1,2,1)
plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.ylim([0, max(plt.ylim())])
plt.xlabel('Epoch')
plt.ylabel('Loss [CrossEntropy]')

plt.subplot(1,2,2)
plt.plot(history.epoch, 100*np.array(metrics['accuracy']), 100*np.array(metrics['val_accuracy']))
plt.legend(['accuracy', 'val_accuracy'])
plt.ylim([0, 100])
plt.xlabel('Epoch')
plt.ylabel('Accuracy [%]')

"""### Evaluate Model 2"""

# Evaluate Model 2 on the test set
model2.evaluate(test_spectrogram_ds, return_dict=True)

# Generate predictions on the test set using Model 2
y_pred = model2.predict(test_spectrogram_ds)
y_pred = tf.argmax(y_pred, axis=1)

# Get the true labels from the test set
y_true = tf.concat(list(test_spectrogram_ds.map(lambda s,lab: lab)), axis=0)

# Compute the confusion matrix for Model 2
confusion_mtx = tf.math.confusion_matrix(y_true, y_pred)

# Plot the confusion matrix for Model 2
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_mtx,
      xticklabels=label_names,
      yticklabels=label_names,
      annot=True, fmt='g')
plt.xlabel('Prediction')
plt.ylabel('Label')
plt.show()

"""## Model 3"""

# Define the architecture for Model 3
model3 = models.Sequential([
  layers.Input(shape=input_shape),
  layers.Conv2D(32, 3, activation='relu', dilation_rate=(2, 2)),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, activation='relu', dilation_rate=(2, 2)),
  layers.MaxPooling2D(),
  layers.Conv2D(128, 3, activation='relu', dilation_rate=(2, 2)),
  layers.GlobalAveragePooling2D(),
  layers.Dense(128, activation='relu'),
  layers.Dropout(0.5),
  layers.Dense(num_labels),
])

# Print the model summary for Model 3
model3.summary()

# Compile Model 3
model3.compile(
  optimizer=tf.keras.optimizers.Adam(),
  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
  metrics=['accuracy'],
)

# Train Model 3
EPOCHS = 10
history = model3.fit(
  train_spectrogram_ds,
  validation_data=val_spectrogram_ds,
  epochs=EPOCHS,
  callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
)

# Plot the training and validation loss curves for Model 3
metrics = history.history
plt.figure(figsize=(16,6))
plt.subplot(1,2,1)
plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.ylim([0, max(plt.ylim())])
plt.xlabel('Epoch')
plt.ylabel('Loss [CrossEntropy]')

plt.subplot(1,2,2)
plt.plot(history.epoch, 100*np.array(metrics['accuracy']), 100*np.array(metrics['val_accuracy']))
plt.legend(['accuracy', 'val_accuracy'])
plt.ylim([0, 100])
plt.xlabel('Epoch')
plt.ylabel('Accuracy [%]')

"""### Evaluate Model 3"""

# Evaluate Model 3 on the test set
model3.evaluate(test_spectrogram_ds, return_dict=True)

# Generate predictions on the test set using Model 3
y_pred = model3.predict(test_spectrogram_ds)
y_pred = tf.argmax(y_pred, axis=1)

# Get the true labels from the test set
y_true = tf.concat(list(test_spectrogram_ds.map(lambda s,lab: lab)), axis=0)

# Compute the confusion matrix for Model 3
confusion_mtx = tf.math.confusion_matrix(y_true, y_pred)

# Plot the confusion matrix for Model 3
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_mtx,
      xticklabels=label_names,
      yticklabels=label_names,
      annot=True, fmt='g')
plt.xlabel('Prediction')
plt.ylabel('Label')
plt.show()

"""## Model 4"""

# Convert the spectrograms to RGB images
train_spectrogram_ds = train_spectrogram_ds.map(lambda x, y: (tf.image.grayscale_to_rgb(x), y))
val_spectrogram_ds = val_spectrogram_ds.map(lambda x, y: (tf.image.grayscale_to_rgb(x), y))

# Update the input shape for Model 4
input_shape = (124, 129, 3)

# Use MobileNetV2 as the base model for Model 4
base_model = tf.keras.applications.MobileNetV2(
  input_shape=input_shape, include_top=False, weights='imagenet')
base_model.trainable = False

# Define the architecture for Model 4
model4 = models.Sequential([
  base_model,
  layers.GlobalAveragePooling2D(),
  layers.Dense(128, activation='relu'),
  layers.Dropout(0.5),
  layers.Dense(num_labels),
])

# Print the model summary for Model 4
model4.summary()

# Compile Model 4
model4.compile(
  optimizer=tf.keras.optimizers.Adam(),
  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
  metrics=['accuracy'],
)

# Train Model 4
EPOCHS = 10
history = model4.fit(
  train_spectrogram_ds,
  validation_data=val_spectrogram_ds,
  epochs=EPOCHS,
  callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
)

# Plot the training and validation loss curves for Model 4
metrics = history.history
plt.figure(figsize=(16,6))
plt.subplot(1,2,1)
plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.ylim([0, max(plt.ylim())])
plt.xlabel('Epoch')
plt.ylabel('Loss [CrossEntropy]')

plt.subplot(1,2,2)
plt.plot(history.epoch, 100*np.array(metrics['accuracy']), 100*np.array(metrics['val_accuracy']))
plt.legend(['accuracy', 'val_accuracy'])
plt.ylim([0, 100])
plt.xlabel('Epoch')
plt.ylabel('Accuracy [%]')

"""### Evaluate Model 4"""

# Evaluate Model 4 on the validation set
model4.evaluate(val_spectrogram_ds, return_dict=True)

# Generate predictions on the validation set using Model 4
y_pred = model4.predict(val_spectrogram_ds)
y_pred = tf.argmax(y_pred, axis=1)

# Get the true labels from the validation set
y_true = tf.concat(list(val_spectrogram_ds.map(lambda s,lab: lab)), axis=0)

# Compute the confusion matrix for Model 4
confusion_mtx = tf.math.confusion_matrix(y_true, y_pred)

# Plot the confusion matrix for Model 4
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_mtx,
      xticklabels=label_names,
      yticklabels=label_names,
      annot=True, fmt='g')
plt.xlabel('Prediction')
plt.ylabel('Label')
plt.show()

"""# Exporting a model

## Export the model with preprocessing
"""

# Define a class for exporting the model with preprocessing
class ExportModel(tf.Module):
  def __init__(self, model):
  self.model = model

  # Accept either a string-filename or a batch of waveforms.
  # You could add additional signatures for a single wave, or a ragged-batch.
  self.__call__.get_concrete_function(
    x=tf.TensorSpec(shape=(), dtype=tf.string))
  self.__call__.get_concrete_function(
     x=tf.TensorSpec(shape=[None, 16000], dtype=tf.float32))


  @tf.function
  def __call__(self, x):
  # If they pass a string, load the file and decode it.
  if x.dtype == tf.string:
    x = tf.io.read_file(x)
    x, _ = tf.audio.decode_wav(x, desired_channels=1, desired_samples=16000,)
    x = tf.squeeze(x, axis=-1)
    x = x[tf.newaxis, :]

  x = get_spectrogram(x)
  result = self.model(x, training=False)

  class_ids = tf.argmax(result, axis=-1)
  class_names = tf.gather(label_names, class_ids)
  return {'predictions':result,
      'class_ids': class_ids,
      'class_names': class_names}

# Create an instance of the ExportModel class for Model 4
export = ExportModel(model4)

# Test the exported model with a sample input
export(tf.constant(str('own/ddyo/audio #2001.wav')))

"""Save and reload the model, the reloaded model gives identical output:"""

# Save the exported model
tf.saved_model.save(export, "saved")

# Load the saved model
imported = tf.saved_model.load("saved")

# Test the reloaded model with a sample input
imported(waveform[tf.newaxis, :])
