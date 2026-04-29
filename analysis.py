import pandas as pd
import matplotlib.pyplot as plt

def analyse_data(df):
    results = {}

    # Préférences
    results['preferences'] = df['preference'].value_counts()

    # Produits
    results['produits'] = df['produit'].value_counts()

    # Fréquence
    results['frequence'] = df['frequence'].value_counts()

    return results


def generate_charts(results):
    # Graphique préférences
    results['preferences'].plot(kind='bar')
    plt.title("Préférences d'achat")
    plt.savefig('static/preference.png')
    plt.close()

    # Graphique produits
    results['produits'].plot(kind='pie', autopct='%1.1f%%')
    plt.title("Produits achetés")
    plt.savefig('static/produits.png')
    plt.close()