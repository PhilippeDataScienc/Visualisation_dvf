# Analyseur DVF - Application Streamlit pour visualiser les données immobilières

Cette application Streamlit permet d'analyser et visualiser les données DVF (Demandes de Valeur Foncière) pour surveiller les tendances du marché immobilier en France. Elle transforme des fichiers CSV bruts en visualisations interactives qui aident à comprendre les prix de l'immobilier par type de bien, nombre de pièces et localisation.

## Screenshot de l'application
![image](https://github.com/user-attachments/assets/9ef02333-faff-474c-be47-25a9a2e289a2)
![image](https://github.com/user-attachments/assets/8a25542b-6fc0-4669-816c-c761435c245b)
![image](https://github.com/user-attachments/assets/b64e0a4f-aedd-4894-9048-a8d3793d8ba9)



## 🚀 Fonctionnalités

- **Chargement flexible des données** : téléchargez des fichiers CSV individuels ou une archive ZIP
- **Filtres interactifs** :
  - Type de bien (maison ou appartement)
  - Nombre de pièces
  - Période temporelle (années)
  - Prix maximum au m²
- **Visualisations dynamiques** :
  - Boxplots des prix au m² par type de bien et nombre de pièces
  - Carte interactive des transactions avec code couleur selon les prix
- **Statistiques et résumés** :
  - Vue d'ensemble des données
  - Répartition par type de bien
  - Tendances temporelles des transactions

## 📋 Prérequis

- Python 3.7+
- Accès aux données DVF ([site officiel](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/))

## 🔧 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/votre-username/analyseur-dvf.git
cd analyseur-dvf
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :
```
streamlit
pandas
plotly
```

## 💻 Utilisation

1. Lancez l'application :
```bash
streamlit run streamlit-dvf-app.py
```

2. Accédez à l'application dans votre navigateur (généralement à l'adresse http://localhost:8501)

3. Téléchargez vos fichiers de données DVF :
   - Téléchargez des fichiers CSV individuels ou une archive ZIP contenant plusieurs fichiers
   - Les fichiers doivent être au format DVF standard (séparateur point-virgule)

4. Utilisez les filtres pour affiner votre analyse

5. Explorez les visualisations dans les onglets dédiés

## 📊 Préparation des données

L'application attend des fichiers CSV au format DVF standard, avec au minimum les colonnes suivantes :
- `date_mutation` : date de la transaction
- `type_local` : type de bien (Appartement ou Maison)
- `valeur_fonciere` : prix de vente
- `surface_reelle_bati` : surface en m²
- `nombre_pieces_principales` : nombre de pièces
- `latitude` et `longitude` : coordonnées géographiques (pour la carte)

## 🗂️ Structure du projet

```
analyseur-dvf/
├── streamlit-dvf-app.py              # Application Streamlit principale
├── requirements.txt    # Dépendances Python
└── README.md           # Ce fichier
```

## 📝 À propos des données DVF

Les données "Demandes de Valeur Foncière" (DVF) sont publiées par la Direction Générale des Finances Publiques et contiennent l'ensemble des transactions immobilières en France. Elles sont accessibles gratuitement sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/).

Ces données comprennent :
- Les ventes de maisons, appartements, terrains
- Le prix des transactions
- Les caractéristiques des biens (surface, nombre de pièces, etc.)
- La localisation précise des biens

## 📜 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

---

Développé avec ❤️ pour simplifier l'analyse des données immobilières françaises.
