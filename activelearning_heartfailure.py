# -*- coding: utf-8 -*-
"""ActiveLearning_HeartFailure.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QQoB9w7zJDXGNE9hMjoRGeP-R8QCqxPt
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from sklearn import svm

"""# Data"""

df = pd.read_csv('/content/heart.csv')

# Visualizar as primeiras linhas
df.head()

# DataShape
df.shape

# Informações do dataset
df.info()

"""# Processing

#### Será preciso transformar os tipos Object para Float ou Int
"""

# Para selecionar somente as que são objetos
object_df = df.select_dtypes(include=['object']).copy()
object_df.head()

# Verificar quais e quantas observações possuem em cada classe
for k in object_df:
  print(object_df[k].value_counts(),'\n')

"""### One Hot Encoding"""

# Salvando um data frame que transforma as categóricas em numéricas
Encoded_df = pd.get_dummies(object_df, columns=['Sex', 'ChestPainType', 'RestingECG', 'ExerciseAngina', 'ST_Slope'],
               prefix=['Sex', 'CPT', 'ECG', 'ExerciseAngina', 'ST'])

# Excluindo o que é objeto para colocar o novo dataframe com OneHotEncoding aplicado
df = df.drop(df.select_dtypes(include=['object']), axis=1)

# Conferindo se a operação acima funcionou corretamente
df.info()

# Adicionado o Encoded_df ao df principal
df = pd.concat([df, Encoded_df], axis=1)

"""Normalizando

"""

normalized_df = (df-df.min())/(df.max()-df.min())
df = normalized_df

# Conferindo o novo dataset
df.head()

# Verificando a presença de valores nulos (não assinalados)
df.isnull().sum()

# Descrição do dataset
# Formatar a exibição
pd.options.display.float_format = '{:.2f}'.format
df.describe()

"""Distribuição dos dados

1 → Doença no Coração

0 → Coração Saudável
"""

# Observando a distribuição do target (Doença ou não)
df['HeartDisease'].value_counts()

import seaborn as sns
figure(figsize=(10, 5), dpi=70)
dados = df['HeartDisease'].value_counts()
dados_df = pd.DataFrame({'Target': dados.index,'Values': dados.values})
sns.barplot(x = 'Target', y = 'Values', data=dados_df)

"""Divisão dos dados"""

target = df['HeartDisease']
features = df.drop(['HeartDisease'], axis=1)

X_train, X_test, Y_train, Y_val = train_test_split(features, target, test_size=0.25, stratify=target, random_state=1)

row_number = len(X_train.index) # Só para obter quantas linhas existem na divisão
print('Shape X_train: ', X_train.shape, 
      '\nShape X_test: ', X_test.shape, 
      '\nShape Y_train: ', Y_train.shape, 
      '\nShape Y_val: ', Y_val.shape)

# Definindo o modelo
model = svm.SVC(decision_function_shape='ovr', probability=True, verbose = True, max_iter = 2000)

"""## Training

##### Treinando de pouco a pouco, tomando aleatoriamente os dados de treino
"""

# Ordenando de forma crescente pelo índice
X_train = X_train.sort_index(ascending=True)
Y_train = Y_train.sort_index(ascending=True)

incremento = 10
init = 10;

X_train_sample = X_train.sample(n=incremento, random_state = 10)
Y_train_sample = Y_train.sample(n=incremento, random_state = 10)

X_train_sample = X_train_sample.sort_index(ascending=True)
Y_train_sample = Y_train_sample.sort_index(ascending=True)

row_index = X_train_sample.index.tolist()
X_train.drop(row_index, axis = 0, inplace=True)
Y_train.drop(row_index, axis = 0, inplace=True)

df_acc = pd.DataFrame()
samples_passive = pd.DataFrame()
cont = 0

while(len(X_train) > incremento):
  acc = 0

  # Média da acurácia
  for j in range(1,11,1):  
   model.fit(X_train_sample, Y_train_sample)
   predict = model.predict(X_test)
   acc += accuracy_score(predict, Y_val)
  
  df_acc.loc[cont, 'Accuracy'] = acc/10
  samples_passive.loc[cont, 'Samples'] = len(X_train_sample)

  # Salvando as novas amostras a serem inseridas
  get_x_sample = X_train.sample(n=incremento, random_state = 10)
  get_y_sample = Y_train.sample(n=incremento, random_state = 10)

  # Inserindo as novas amostras no novo conjunto de treinamento
  X_train_sample = X_train_sample.append(get_x_sample, ignore_index = False)
  Y_train_sample = Y_train_sample.append(get_y_sample, ignore_index = False)

  # Retirando as novas amostras do conjunto geral de treino
  row_index = get_x_sample.index.tolist()
  X_train.drop(row_index, axis = 0, inplace=True)
  Y_train.drop(row_index, axis = 0, inplace=True)

  # Ordenando de forma crescente pelo índice
  X_train_sample = X_train_sample.sort_index(ascending=True)
  Y_train_sample = Y_train_sample.sort_index(ascending=True)

  cont += 1;
  # Verificando a acurácia
  print('Acurácia do modelo: {:.2f} '.format(acc/10))

"""Treinando usando Active Learning"""

X_train, X_test, Y_train, Y_val = train_test_split(features, target, test_size=0.25, stratify=target, random_state = 1)

# Definindo o modelo
model = svm.SVC(decision_function_shape='ovr', probability = True, verbose = True, max_iter = 2000)

stop = 0;
cont = 0;
incremento = 10;
init = 10;

df_acc_active = pd.DataFrame()
samples_active = pd.DataFrame()

# É preciso ordenar os índices
X_train = X_train.sort_index(ascending=True)
Y_train = Y_train.sort_index(ascending=True)

X_train_sample = X_train.sample(n = init, random_state = 10)
Y_train_sample = Y_train.sample(n = init, random_state = 10)

# Ordenando em ordem crescente pelos índices
X_train_sample = X_train_sample.sort_index(ascending=True)
Y_train_sample = Y_train_sample.sort_index(ascending=True)

# ---------- Retirando do X_train e Y_train as amostras iniciais que retirei pra treinar, se não depois posso dar pred_proba nas mesmas amostras
get_index = X_train_sample.index.tolist() # ----- Obtendo os índices que foram retirados como amostra do X_train
X_train.drop(get_index, axis=0, inplace=True)
Y_train.drop(get_index, axis=0, inplace=True)

# A métrica de parada do loop é a acurácia máxima obtida na abordagem passiva
while (stop < df_acc['Accuracy'].max()):
  acc_active = 0;
  tam_amostra = len(X_train_sample.index) # Só para obter quantas linhas existem na divisão (Quantas amostras estou usando)
  row_number = len(X_train.index) # Atualizando o número de linhas no meu dataframe de treino

  for j in range(1,11,1):
    model.fit(X_train_sample, Y_train_sample)
    predict = model.predict(X_test)
    acc_active += accuracy_score(predict, Y_val)
  
  df_acc_active.loc[cont, 'Accuracy'] = acc_active/10
  samples_active.loc[cont, 'Samples'] = tam_amostra # Adicionado ao DF a quantidade de amostras usadas

  pred_prob = model.predict_proba(X_train) # Pois agora o X_train já está sem as amostras usadas na 1ª iteração
  new_x_train_sample = X_train.copy()
  new_y_train_sample = Y_train.copy()
  new_x_train_sample['Predict'] = pred_prob[:,0].tolist()

  # Condição para selecionar novos dados
  new_x_train_sample['Predict']  = (new_x_train_sample['Predict'] - 0.5).abs()
  row_index = new_x_train_sample.index[new_x_train_sample['Predict'] < 0.1].tolist() # Obtendo os índices das linhas que o predict é < 0,1
  
  X_train_sample = X_train_sample.append(X_train.loc[row_index[:incremento]], ignore_index=True) # Adicionando 10 linhas do DF X_train no meu X_train_sample 
  Y_train_sample = Y_train_sample.append(Y_train.loc[row_index[:incremento]], ignore_index=True) # Adicionando 10 linhas do DF Y_train no meu Y_train_sample

  # Agora é preciso obter os 10 índices que foram adicionados e retirá-los do X_train
  X_train.drop(row_index[:incremento], axis=0, inplace=True) # Removendo as linhas pelos índices que foram usados como amostra no X_train_sample
  Y_train.drop(row_index[:incremento], axis=0, inplace=True) # Removendo as linhas pelos índices que foram usados como amostra no Y_train_sample   

  print('Acurácia do modelo: {:.2f} '.format(acc_active/10))    
  cont += 1;
  stop = acc_active/10;

"""Comparativo"""

figure(figsize=(12, 8), dpi=70)

# plotting the points 
plt.plot(samples_passive['Samples'], df_acc['Accuracy'], label='Passive')

# plotting the points 
plt.plot(samples_active['Samples'], df_acc_active['Accuracy'], label='Active')  

# Plotting the mean accuracy
plt.axhline(y = df_acc['Accuracy'].mean(), color='g', linestyle = '--', label = 'Mean Accuracy')
 
# giving a title to my graph
plt.title('Passive Learning x Active Learning')

# naming the x axis
plt.xlabel('Training Samples')
# naming the y axis
plt.ylabel('Accuracy')

# Giving a legend to my graph
plt.legend()

# Saving as png
plt.savefig('Comparison.png')

# function to show the plot
plt.show()

