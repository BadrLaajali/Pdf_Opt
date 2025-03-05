# PDF Optimizer et Analyseur

## Description
Ce projet est un outil avancé d'extraction et d'analyse de documents PDF. Il utilise l'intelligence artificielle (GPT-4) pour analyser le contenu des documents et générer des résumés chronologiques détaillés.

## Fonctionnalités
- Extraction de contenu à partir de fichiers PDF
- Conversion des pages PDF en images
- Analyse intelligente du contenu avec GPT-4
- Génération de résumés chronologiques
- Export des analyses au format Markdown
- Support pour le traitement par lots de documents

## Prérequis
- Python 3.x
- OpenAI API Key

## Installation

1. Clonez le repository :
```bash
git clone [votre-repo-url]
cd Pdf_Opt
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
Créez un fichier `.env` à la racine du projet et ajoutez votre clé API OpenAI :
```
OPENAI_API_KEY=votre_clé_api
```

## Structure du Projet
```
Pdf_Opt/
├── advanced_pdf_extractor.py   # Script principal
├── markdown_to_jsonl.py        # Utilitaire de conversion
├── prompt.txt                  # Template pour l'analyse
├── output/                     # Dossier de sortie
│   ├── images/                 # Images extraites
│   └── markdown/              # Analyses générées
└── pdf/                       # Dossier pour les PDF source
```

## Utilisation
1. Placez vos fichiers PDF dans le dossier `pdf/`
2. Exécutez le script avec les options souhaitées :
```bash
# Analyse simple d'un PDF
python advanced_pdf_extractor.py pdf/nom_du_fichier.pdf

# Analyse sans génération de résumé final
python advanced_pdf_extractor.py pdf/nom_du_fichier.pdf --no-summary

# Exemple avec un fichier spécifique
python advanced_pdf_extractor.py pdf/document.pdf --no-summary
```

### Options disponibles
- `pdf/nom_du_fichier.pdf` : Chemin vers le fichier PDF à analyser (obligatoire, doit être dans le dossier `pdf/`)
- `--no-summary` : Désactive la génération du résumé final

### Paramètres configurables
La classe `AdvancedPDFExtractor` accepte plusieurs paramètres :
- `output_dir` : Répertoire de sortie (par défaut : "output")
- `generate_final_summary` : Génération du résumé final (par défaut : True)

Lors de l'extraction (`extract_from_pdf`) :
- `extract_images` : Extraction des images (par défaut : True)
- `pages` : Liste des pages à extraire (optionnel)
- `image_format` : Format des images extraites (par défaut : "png")
- `dpi` : Résolution des images extraites (par défaut : 300)

Pour le traitement par lots (`process_directory`) :
- `input_dir` : Répertoire contenant les PDF
- `max_pages` : Nombre maximum de pages à traiter par PDF (optionnel)

## Sortie
- Les images extraites sont sauvegardées dans `output/images/`
- Les analyses sont générées dans `output/markdown/`
- Un résumé global est créé si l'option est activée
