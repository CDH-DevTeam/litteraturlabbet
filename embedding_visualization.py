from .views import *
import pandas as pd
pd.options.mode.chained_assignment = None 
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np


def tsne_plot(model):
    "Creates and TSNE model and plots it"
    labels = []
    tokens = []

    # for i in reloaded_word_vectors.key_to_index:
    for word in model.key_to_index:
        tokens.append(model[word])
        labels.append(word)
    
    tokens = np.array(tokens)
    tsne_model = TSNE(perplexity=40, n_components=2, init='pca', n_iter=2500, random_state=23)
    new_values = tsne_model.fit_transform(tokens)

    x = []
    y = []
    for value in new_values:
        x.append(value[0])
        y.append(value[1])
        
    plt.figure(figsize=(16, 16)) 
    for i in range(len(x)):
        plt.scatter(x[i],y[i])
        plt.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plt.show()