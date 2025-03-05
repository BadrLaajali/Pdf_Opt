import os
import sys
import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Union, Optional
from PIL import Image
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv
import time
import markdown

# Load environment variables
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("La clé API OpenAI n'a pas été trouvée dans les variables d'environnement.")

client = OpenAI(api_key=api_key)
GPT_MODEL = "gpt-4o-mini"  # Modèle avec capacités de vision

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def log_message(message):
    logger.info(f"[{get_timestamp()}] {message}")

class AdvancedPDFExtractor:
    def __init__(self, output_dir: str = "output", generate_final_summary: bool = True):
        """
        Initialise l'extracteur PDF avancé.
        
        Args:
            output_dir (str): Répertoire de sortie pour les fichiers extraits
            generate_final_summary (bool): Si True, génère un résumé final combinant toutes les analyses
        """
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.markdown_dir = self.output_dir / "markdown"
        self.generate_final_summary = generate_final_summary
        self._setup_directories()
    
    def _setup_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas."""
        self.output_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        self.markdown_dir.mkdir(exist_ok=True)
        log_message(f"Répertoires créés : {self.output_dir}, {self.images_dir}, {self.markdown_dir}")

    def _read_prompt(self) -> str:
        """
        Lit le contenu du fichier prompt.txt.
        
        Returns:
            str: Contenu du prompt
        """
        try:
            prompt_path = Path(__file__).parent / "prompt.txt"
            log_message(f"Lecture du fichier prompt : {prompt_path}")
            
            if not prompt_path.exists():
                raise FileNotFoundError(f"Le fichier prompt.txt n'existe pas dans {prompt_path}")
            
            prompt_content = prompt_path.read_text(encoding='utf-8')
            log_message("Lecture du prompt terminée")
            return prompt_content
            
        except Exception as e:
            error_msg = f"Erreur lors de la lecture du prompt : {str(e)}"
            logger.error(error_msg)
            raise

    def _save_analysis_to_markdown(self, image_path: str, analysis: str) -> str:
        """
        Sauvegarde l'analyse d'une image dans un fichier markdown.
        
        Args:
            image_path (str): Chemin de l'image analysée
            analysis (str): Contenu de l'analyse
            
        Returns:
            str: Chemin du fichier markdown créé
        """
        try:
            # Créer un nom de fichier basé sur le nom de l'image
            image_name = Path(image_path).stem
            markdown_path = self.markdown_dir / f"{image_name}_analysis.md"
            
            # Ajouter l'en-tête avec le titre et la date
            timestamp = get_timestamp()
            header = f"# Analyse du document : {image_name}\n\n"
            header += f"*Document analysé le {timestamp}*\n\n"
            header += "## Résumé chronologique des actions\n\n"
            
            # Écrire le contenu dans le fichier markdown
            content = header + analysis
            markdown_path.write_text(content, encoding='utf-8')
            
            log_message(f"Analyse sauvegardée dans : {markdown_path}")
            return str(markdown_path)
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde de l'analyse : {str(e)}"
            logger.error(error_msg)
            raise

    def _analyze_image_with_openai(self, image_path: str) -> str:
        """
        Analyse une image avec l'API OpenAI Vision.
        
        Args:
            image_path (str): Chemin vers l'image à analyser
        
        Returns:
            str: Chemin du fichier markdown contenant l'analyse
        """
        try:
            log_message(f"Analyse de l'image : {image_path}")
            
            # Encoder l'image en base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            # Lire le prompt depuis le fichier
            system_prompt = self._read_prompt()

            # Préparer les messages pour l'API
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analysez ce document en fournissant une explication chronologique et narrative du contenu. Décrivez le planning, les étapes clés et leur organisation dans le temps. Expliquez comment les différentes phases s'articulent entre elles."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Appeler l'API OpenAI avec le modèle de vision
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                max_tokens=4000,
                temperature=0
            )
            
            analysis = response.choices[0].message.content
            
            # Sauvegarder l'analyse dans un fichier markdown
            markdown_path = self._save_analysis_to_markdown(image_path, analysis)
            
            log_message(f"Analyse de l'image terminée : {image_path}")
            return markdown_path
            
        except Exception as e:
            error_msg = f"Erreur lors de l'analyse de l'image {image_path}: {str(e)}"
            logger.error(error_msg)
            raise

    def _create_final_summary(self, analyses: List[str], output_path: Path) -> str:
        """
        Crée un résumé global à partir de toutes les analyses d'images.
        
        Args:
            analyses (List[str]): Liste des chemins vers les fichiers d'analyse markdown
            output_path (Path): Chemin du fichier de sortie
            
        Returns:
            str: Chemin du fichier de résumé final
        """
        try:
            log_message("Création du résumé global des analyses")
            
            # Collecter tout le contenu des analyses
            all_content = []
            for analysis_path in analyses:
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    all_content.append(f.read())
            
            # Préparer la requête pour l'analyse globale
            combined_content = "\n\n---\n\n".join(all_content)
            
            messages = [
                {
                    "role": "system",
                    "content": """Vous êtes un expert en analyse documentaire. Votre tâche est de créer un résumé global à partir de plusieurs analyses de documents. 

Concentrez-vous sur :
1. Les points clés et informations critiques
2. Les liens entre les différentes parties
3. La chronologie globale du projet
4. Les recommandations et points d'attention

Structurez votre réponse en sections claires :
- Résumé Exécutif (2-3 paragraphes)
- Points Clés par Thème
- Chronologie Principale
- Recommandations"""
                },
                {
                    "role": "user",
                    "content": f"Analysez l'ensemble des documents suivants et créez un résumé global en vous concentrant sur les informations les plus importantes :\n\n{combined_content}"
                }
            ]
            
            # Appeler l'API OpenAI pour l'analyse globale
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=messages,
                max_tokens=4000,
                temperature=0
            )
            
            summary = response.choices[0].message.content
            
            # Créer le fichier de résumé final
            timestamp = get_timestamp()
            header = "# Résumé Global du Projet\n\n"
            header += f"*Analyse générée le {timestamp}*\n\n"
            
            # Écrire le résumé dans le fichier
            final_path = output_path.with_suffix('.md')
            content = header + summary
            final_path.write_text(content, encoding='utf-8')
            
            log_message(f"Résumé global sauvegardé dans : {final_path}")
            return str(final_path)
            
        except Exception as e:
            error_msg = f"Erreur lors de la création du résumé global : {str(e)}"
            logger.error(error_msg)
            raise

    def extract_from_pdf(
        self,
        pdf_path: str,
        extract_images: bool = True,
        pages: Optional[List[int]] = None,
        image_format: str = "png",
        dpi: int = 300
    ) -> Dict[str, Union[str, List[Dict]]]:
        """
        Extrait le contenu d'un PDF avec des fonctionnalités avancées.
        
        Args:
            pdf_path (str): Chemin vers le fichier PDF
            extract_images (bool): Si True, extrait aussi les images
            pages (List[int], optional): Liste des pages à extraire (0-based)
            image_format (str): Format des images extraites
            dpi (int): Résolution des images extraites
        
        Returns:
            Dict contenant le texte markdown et les métadonnées
        """
        try:
            pdf_name = Path(pdf_path).stem
            log_message(f"Traitement du PDF : {pdf_path}")
            
            # Liste pour stocker les chemins des analyses
            analyses_paths = []
            
            # Ouvrir le document PDF
            doc = fitz.open(pdf_path)
            
            # Gérer la sélection des pages
            if pages is None:
                pages = list(range(len(doc)))
            
            # Traiter chaque page
            for page_num in pages:
                if page_num >= len(doc):
                    continue
                
                page = doc[page_num]
                
                if extract_images:
                    # Extraire l'image de la page
                    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                    image_path = self.images_dir / f"page_{page_num + 1}.{image_format}"
                    pix.save(str(image_path))
                    
                    # Analyser l'image avec OpenAI
                    analysis_path = self._analyze_image_with_openai(str(image_path))
                    analyses_paths.append(analysis_path)
            
            # Créer le résumé final
            final_summary_path = None
            if self.generate_final_summary:
                final_summary_path = self._create_final_summary(
                    analyses_paths,
                    self.output_dir / f"{pdf_name}_extracted"
                )
            
            doc.close()
            
            return {
                "summary": final_summary_path,
                "analyses": analyses_paths
            }
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement du PDF : {str(e)}"
            logger.error(error_msg)
            raise

def main():
    """Point d'entrée principal du programme."""
    try:
        # Vérifier si le chemin du PDF est fourni en argument
        if len(sys.argv) < 2:
            print("Usage: python advanced_pdf_extractor.py <chemin_pdf> [--no-summary]")
            sys.exit(1)
        
        pdf_path = sys.argv[1]
        generate_summary = "--no-summary" not in sys.argv
        
        # Initialiser et exécuter l'extracteur
        extractor = AdvancedPDFExtractor(generate_final_summary=generate_summary)
        result = extractor.extract_from_pdf(pdf_path)
        
        print("\nAnalyses générées avec succès :")
        for analysis in result["analyses"]:
            print(f"- {analysis}")
        
        if result["summary"]:
            print(f"\nRésumé final généré : {result['summary']}")
            
    except Exception as e:
        print(f"Erreur : {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
