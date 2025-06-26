import subprocess
import sys

def download_spacy_model(model_name="en_core_web_sm"):
    try:
        import spacy
        spacy.load(model_name)
        print(f"SpaCy model '{model_name}' is already installed.")
    except OSError:
        print(f"SpaCy model '{model_name}' not found. Downloading...")
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", model_name], check=True)
            print(f"SpaCy model '{model_name}' downloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading spaCy model '{model_name}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred during download: {e}")

if __name__ == "__main__":
    download_spacy_model()
