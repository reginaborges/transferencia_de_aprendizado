# -*- coding: utf-8 -*-
"""COVID-19 - Transfer Learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MvgQ052g5s2m54vJncgYiWmLLdX4iUWo

# Importação das bibliotecas
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 2.x
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import numpy as np
tf.__version__

"""# Carregamento da base de dados

Fontes da base de dados:
- https://www.sirm.org/category/senza-categoria/covid-19/
- https://github.com/ieee8023/covid-chestxray-dataset
- https://towardsdatascience.com/detecting-covid-19-induced-pneumonia-from-chest-x-rays-with-transfer-learning-an-implementation-311484e6afc1

Preparação de bases para medicina
- https://medium.com/@hbjenssen/covid-19-radiology-data-collection-and-preparation-for-artificial-intelligence-4ecece97bb5b
"""

from google.colab import drive
drive.mount('/content/drive')

path = "/content/drive/My Drive/covid_dataset.zip"
zip_object = ZipFile(file=path, mode="r")
zip_object.extractall("./")
zip_object.close()

image = tf.keras.preprocessing.image.load_img(r'/content/covid_dataset/train/covid/01E392EE-69F9-4E33-BFCE-E5C968654078.jpeg', target_size=(224,224))

plt.imshow(image);

image = tf.keras.preprocessing.image.load_img(r'/content/covid_dataset/train/normal/NORMAL2-IM-1281-0001.jpeg', target_size=(224, 224))
plt.imshow(image);

train_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
                                   rotation_range = 50,
                                   width_shift_range = 0.2,
                                   height_shift_range = 0.2,
                                   zoom_range = 0.1,
                                   horizontal_flip = True,
                                   vertical_flip = True)

train_generator = train_datagen.flow_from_directory('/content/covid_dataset/train',
                                                    target_size = (224, 224),
                                                    batch_size=16,
                                                    class_mode = 'categorical',
                                                    shuffle = True)

train_generator.n

train_generator.batch_size

step_size_train = train_generator.n // train_generator.batch_size
step_size_train

test_datagen = ImageDataGenerator(preprocessing_function=tf.keras.applications.resnet50.preprocess_input)

test_generator = test_datagen.flow_from_directory('/content/covid_dataset/test',
                                                  target_size=(224,244),
                                                  batch_size=1,
                                                  class_mode = 'categorical',
                                                  shuffle = False)

step_size_test = test_generator.n // test_generator.batch_size
step_size_test

"""# Transfer learning

## Construção do modelo
"""

base_model = tf.keras.applications.ResNet50(weights='imagenet', include_top=False)

base_model.summary()

x = base_model.output

x = tf.keras.layers.GlobalAveragePooling2D()(x)

x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(1024, activation='relu')(x)
x = tf.keras.layers.Dense(512, activation='relu')(x)
preds = tf.keras.layers.Dense(2, activation='softmax')(x)

model = tf.keras.Model(inputs = base_model.input, outputs = preds)

model.summary()

for i, layer in enumerate(model.layers):
  print(i, layer.name)

for layer in model.layers[:175]:
  layer.trainable = False

for layer in model.layers[175:]:
  layer.trainable = True

model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit_generator(generator=train_generator,
                              epochs=20,
                              steps_per_epoch=step_size_train,
                              validation_data = test_generator,
                              validation_steps=step_size_test)

"""# Avaliação

## Gráficos
"""

np.mean(history.history['val_accuracy'])

np.std(history.history['val_accuracy'])

plt.plot(history.history['loss'], label='Training loss')
plt.plot(history.history['val_loss'], label='Validation loss')
plt.title('Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend();

plt.plot(history.history['accuracy'], label='Training accuracy')
plt.plot(history.history['val_accuracy'], label='Validation accuracy')
plt.title('Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend();

"""## Previsões"""

filenames = test_generator.filenames
filenames

len(filenames)

predictions = model.predict_generator(test_generator, steps = len(filenames))

predictions

len(predictions)

predictions2 = []
for i in range(len(predictions)):
  #print(predictions[i])
  predictions2.append(np.argmax(predictions[i]))

predictions2

test_generator.classes

test_generator.class_indices

from sklearn.metrics import accuracy_score, confusion_matrix
accuracy_score(predictions2, test_generator.classes)

cm = confusion_matrix(predictions2, test_generator.classes)
cm

sns.heatmap(cm, annot=True);

"""## Teste com imagem"""

image = tf.keras.preprocessing.image.load_img(r'/content/covid_dataset/test/normal/NORMAL2-IM-1419-0001.jpeg', target_size=(224,224))
plt.imshow(image);

type(image)

image = tf.keras.preprocessing.image.img_to_array(image)
np.shape(image)

type(image)

np.max(image), np.min(image)

image = np.expand_dims(image, axis = 0)
np.shape(image)

image = tf.keras.applications.resnet50.preprocess_input(image)

np.max(image), np.min(image)

predictions = model.predict(image)
print(predictions)

predictions[0]

np.argmax(predictions[0])

list(train_generator.class_indices)

prediction = list(train_generator.class_indices)[np.argmax(predictions[0])]
prediction