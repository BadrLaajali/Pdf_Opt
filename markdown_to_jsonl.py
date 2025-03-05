import os
import json
from pathlib import Path

def convert_markdown_to_jsonl(markdown_dir, output_file):
    # Créer le répertoire de sortie si nécessaire
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Liste tous les fichiers markdown triés par numéro de page
    markdown_files = sorted(
        [f for f in os.listdir(markdown_dir) if f.endswith('.md')],
        key=lambda x: int(x.split('_')[1])  # Trie par le numéro de page
    )
    
    with open(output_file, 'w', encoding='utf-8') as jsonl_file:
        for md_file in markdown_files:
            page_num = int(md_file.split('_')[1])  # Extrait le numéro de page
            
            with open(os.path.join(markdown_dir, md_file), 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Crée un objet JSON avec métadonnées
                doc = {
                    'metadata': {
                        'page': page_num,
                        'source': md_file
                    },
                    'text': content  # Le contenu principal est sous la clé "text"
                }
                
                # Écrit l'objet JSON suivi d'un saut de ligne
                jsonl_file.write(json.dumps(doc, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    markdown_dir = 'output/markdown'
    output_file = 'output/json/documents.jsonl'
    
    convert_markdown_to_jsonl(markdown_dir, output_file)
    print(f"Conversion terminée. Fichier JSONL créé : {output_file}")
