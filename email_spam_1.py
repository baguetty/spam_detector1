# -*- coding: utf-8 -*-
"""Email spam 1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qG5hHcGm9P_e-9hkddpxYD1LMHY7KQY9

# Load the dataset
"""

import pandas as pd

df = pd.read_csv("spam_ham_dataset.csv")

df.head()

df.info()

#example of a spam email
df["text"][5170]

#example of ham email
df["text"][2]

df.columns

#we dont need the label as it is already indicated with 0 and 1
# 0 = ham
# 1 = spam
#unnamed: 0 is not useful for the training --> DROP!!
df = df.drop(columns=['Unnamed: 0', 'label'])

#wohoo the 2 columns are dropped
df.info()

df.head(5)

# we have to rename the column label_num into target
df.rename(columns={'label_num': 'target'}, inplace=True)
df.head()

"""# EDA"""

target_counts = df['target'].value_counts()
print(target_counts)

df.info()

# as the text is an int we need to change to str
df['text'] = df['text'].apply(lambda x: str(x) if not isinstance(x, str) else x)
df['text'] = df['text'].astype(str)

df.info()

# bar chart for spam vs ham email
import matplotlib.pyplot as plt

target_counts = df['target'].value_counts()

plt.pie(target_counts.values, labels=['Ham (0)', 'Spam (1)'], autopct='%1.1f%%')

plt.title('Distribution of spam and ham email')

plt.show()

# the distribution of spam and ham email is ca va not super imbalance

# text length analysis by no. of sentence and wordcount in a text n so we can sperate into 0 and 1 to see the charaterstic of it

import nltk

nltk.download('punkt_tab')

df['num_words'] = df['text'].apply(lambda x: len(nltk.word_tokenize(x)))
df['num_sentence'] = df['text'].apply(lambda x: len(nltk.sent_tokenize(x)))

df.info()

#ham
df[df['target'] == 0][['num_words', 'num_sentence']].describe()

#spam
df[df['target'] == 1][['num_words', 'num_sentence']].describe()

# in averge, the spam email has more words and more sentences.

import string
special_chars = string.punctuation

df['special_chars'] = df['text'].str.count(f'[{special_chars}]')

avg_spam_special_chars = df[df['target'] == 1]['text'].str.count(f'[{special_chars}]').mean()
avg_ham_special_chars = df[df['target'] == 0]['text'].str.count(f'[{special_chars}]').mean()

print(f"Average special characters in spam emails: {avg_spam_special_chars:.2f}")
print(f"Average special characters in ham emails: {avg_ham_special_chars:.2f}")

#is surprising that there are more special characters in ham email more than spam

import seaborn as sns
correlation_matrix = df[['target', 'special_chars', 'num_words', 'num_sentence']].corr()

plt.figure(figsize=(10, 6))
sns.set(font_scale=1.2)
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt=".2f")
plt.title("Correlation Heatmap", fontsize=16, fontweight='bold')
plt.xticks(rotation=45)

plt.show()

# Emails with more sentences tend to have more words and more special characters.... (seems like a common sense?)
# None of these features individually are strong predictors of whether an email is spam or not (;-;)

"""# Data cleaning

"""

print(df.isnull().sum())
print(df.duplicated().sum())
print(df.info())

# parfait
# there is no missing values/duplicated

df.head()
#as we can see there are subjects in the text, so we need to sperate it from the text column

subjects = []
for i in range(len(df)):
    ln = df["text"][i]
    line = ""
    for i in ln:
        if(i == '\r'):
            break
        line = line + i
    line = line.replace("Subject" , "")
    subjects.append(line)

df['subject'] = subjects
df.info()

# to remove all subject in the text
import re
df["text"] = df["text"].str.replace(r'^subject:.*(\n|$)', '', flags=re.IGNORECASE, regex=True)
#.* → match everything after it (the actual subject content)
#(\n|$) → until the first newline or end of the string

df.head()
#daaaaa and now is sperated

# we also need to :
#change uppercase letters to lowercase: Prevents duplication of word representations
#delete punctuation marks: has no semantic value
#delete stopwords: appear everywhere
#delete numbers: not useful/meaningful

#covert to lowercase letters
df["text"] = df["text"].str.lower()
df["text"][1]

#delete punctuation marks
import string

df["text"] = df["text"].apply(lambda x: x.translate(str.maketrans("", "", string.punctuation)))
df["text"][1]

#delete stopwords
# i found the NLTK online as it is sth ive not learnt yet...
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

df["text"] = df["text"].apply(lambda x: " ".join([word for word in x.split() if word not in stop_words]))

df["text"][1]

#delete numbers
df["text"] = df["text"].str.replace(r'\d+', '', regex=True)
df["text"][1]

#top 10 words
from collections import Counter

spam_texts = df[df['target'] == 1]['text']


all_spam = ' '.join(spam_texts)
words = all_spam.split()


word_counts = Counter(words)


top_10 = word_counts.most_common(10)

for word, freq in top_10:
    print(f"{word}: {freq}")

# we can see in spam email, mostly there are wordings like com,http,www, which are url!!

#do the same for ham email
spam_texts = df[df['target'] == 0]['text']

all_spam = ' '.join(spam_texts)
words = all_spam.split()

word_counts = Counter(words)

top_10 = word_counts.most_common(10)

for word, freq in top_10:
    print(f"{word}: {freq}")

# these words are mostly the short form of some words while texting: pm = private message

df = df.drop(['subject'], axis=1)

df.head()

"""# Preprocess

"""

X = df.drop(["target"], axis =1)
y = df['target']

#split into testing and training set
#as we know the test set is not thaaaaat balance (30% vs 70%), therefore I decided split the data to 70% training, 15% validation and 15% test set

from sklearn.model_selection import train_test_split

X_train, X_rem, y_train, y_rem = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

X_val, X_test, y_val, y_test = train_test_split(X_rem, y_rem, test_size=0.5, random_state=42, stratify=y_rem)

# Separate columns
X_text = X["text"]
X_extra = X[["num_words", "num_sentence","special_chars"]]

import numpy as np

spam_emails = df[df['target'] == 1]['text']
spam_email_lengths = [len(email.split()) for email in spam_emails]

max_length = int(np.percentile(spam_email_lengths, 95))
print(max_length)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

max_words = 10000

tokenizer = Tokenizer(num_words=max_words, oov_token="<OOV>")
tokenizer.fit_on_texts(X_text)

X_train_sequences = tokenizer.texts_to_sequences(X_train["text"])
X_val_sequences = tokenizer.texts_to_sequences(X_val["text"])
X_test_sequences = tokenizer.texts_to_sequences(X_test["text"])

import tensorflow as tf

vect = tf.keras.layers.TextVectorization(
    max_tokens=5000,
    output_mode='int',
    output_sequence_length=100
)

vect.adapt(X_train['text'].to_numpy())

X_train_vect = vect(X_train["text"].to_numpy())
X_val_vect = vect(X_val["text"].to_numpy())
X_test_vect = vect(X_test["text"].to_numpy())

#make sure is well done
print(type(X_train_vect))
print(X_train_vect.shape)
print(X_train_vect[:5])

from sklearn.preprocessing import StandardScaler

X_train_extra = X_train[["num_words", "num_sentence", "special_chars"]]
X_val_extra = X_val[["num_words", "num_sentence", "special_chars"]]
X_test_extra = X_test[["num_words", "num_sentence", "special_chars"]]

scaler = StandardScaler()
scaler.fit(X_train_extra)


X_train_extra_scaled = scaler.transform(X_train_extra)
X_val_extra_scaled = scaler.transform(X_val_extra)
X_test_extra_scaled = scaler.transform(X_test_extra)

X_train_extra_scaled = pd.DataFrame(X_train_extra_scaled, columns=X_train_extra.columns, index=X_train_extra.index)
X_val_extra_scaled = pd.DataFrame(X_val_extra_scaled, columns=X_val_extra.columns, index=X_val_extra.index)
X_test_extra_scaled = pd.DataFrame(X_test_extra_scaled, columns=X_test_extra.columns, index=X_test_extra.index)

# #now lets combine the X_extra and the X_train_vect tgh
# import tensorflow as tf

# X_train_pp = tf.concat([X_train_vect, X_train_extra_scaled], axis=1)
# X_val_pp = tf.concat([X_val_vect, X_val_extra_scaled], axis=1)
# X_test_pp = tf.concat([X_test_vect, X_test_extra_scaled], axis=1)
#trial5: get rid of the X_extra n train to see if there is less overfitting

from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()

y = label_encoder.fit_transform(df['target'])

df['target'] = y

df.head()

print(X_train_pp.shape)
print(X_train_pp.dtype)
#ok the dtype now is int64 :)))))

#embedding layers: turning words into vector
import tensorflow as tf

vocab_size = vect.vocabulary_size()

embedding_layer = tf.keras.layers.Embedding(
  input_dim=vocab_size,
  output_dim=50,
  mask_zero=True
)

"""# Model"""

#LSTM: Best for context/sequence but slower training
# we use sigmoid for binary classification as it will produce value between 0 to 1

model = tf.keras.models.Sequential([
    tf.keras.layers.InputLayer(input_shape=(max_length,)),
    embedding_layer,
    tf.keras.layers.LSTM(32, return_sequences=False, kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    tf.keras.layers.Dropout(0.7),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.summary()

#trial4: dropout from 0.5 --> 0.6
#trial6: dropour from 0.6 --> 0.7

#trial1:at first i put 0.2 as the drop out, but then i change to 0.5 due to overfitting
#trial2:still overfitting so i cnahge to LTSM from 64 to 32 (less layers) --> less complexe

from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Precision, Recall

binary_ce = tf.keras.losses.BinaryCrossentropy()
learning_rate = 0.001

model.compile(optimizer = Adam(learning_rate=learning_rate),
              loss = binary_ce,
              metrics = [Precision(), Recall()])

from tensorflow.keras.callbacks import EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=3)

#trail3: adding a early stopping so it stops training when it starts to increase, preventing the model from overfitting to the training data.
#trial 3: BATCH SIZE= 32, epochs = 20

history = model.fit(X_train_vect, y_train,
                    batch_size = 32,
                    epochs = 20,
                    validation_data=(X_val_vect, y_val))

import matplotlib.pyplot as plt

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper right')
plt.show()

y_pred_labels = model.predict(X_val_vect)

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

y_pred = model.predict(X_val_vect)

y_pred_labels = (y_pred > 0.3).astype(int)

accuracy = accuracy_score(y_val, y_pred_labels)
precision = precision_score(y_val, y_pred_labels)
recall = recall_score(y_val, y_pred_labels)
f1 = f1_score(y_val, y_pred_labels)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

y_pred_probs_test = model.predict(X_test_vect)
y_pred_labels_test = (y_pred_probs_test > 0.3).astype(int)


from sklearn.metrics import f1_score
f1_test = f1_score(y_test, y_pred_labels_test)
print(f"F1 Score on Test Set: {f1_test}")

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


cm = confusion_matrix(y_test, y_pred_labels_test)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
plt.xlabel("Predicted Labels")
plt.ylabel("True Labels")
plt.title("Confusion Matrix")
plt.show()