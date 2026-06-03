# Générateur RSS Facebook gratuit pour Sport Région

Ce dépôt génère automatiquement un fichier `rss.xml` à partir de pages Facebook publiques.

## 1. Créer le dépôt GitHub

Créer un dépôt public, par exemple :

`elan59-facebook-rss`

Puis envoyer tous les fichiers de ce dossier dans le dépôt.

## 2. Activer GitHub Pages

Dans GitHub :

`Settings` → `Pages` → `Build and deployment` → `Source` → `GitHub Actions`

## 3. Lancer une première génération

Dans GitHub :

`Actions` → `Update Facebook RSS` → `Run workflow`

Après exécution, ton flux sera disponible ici :

`https://TON-COMPTE.github.io/NOM-DU-DEPOT/rss.xml`

Exemple :

`https://dvfstore.github.io/elan59-facebook-rss/rss.xml`

## 4. Coller dans Sport Région

Dans Sport Région, ajouter un widget/bloc Flux RSS et coller l'URL du fichier `rss.xml`.

## 5. Ajouter une page Facebook

Modifier `src/generate_feed.py`, section `PAGES` :

```python
PAGES = [
    {
        "name": "USD Athlétisme",
        "url": "https://www.facebook.com/people/USD-Athl%C3%A9tisme/100057378042903/",
    },
    {
        "name": "Gravelines Athlétisme",
        "url": "https://www.facebook.com/people/Gravelines-Athl%C3%A9tisme/61585380171800/",
    },
]
```

## Important

Facebook peut bloquer la récupération automatique. Le script tente plusieurs variantes : `facebook.com`, `m.facebook.com` et `mbasic.facebook.com`.
Si Facebook bloque, le flux reste généré mais indique que la récupération a échoué.
