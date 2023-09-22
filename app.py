from flask import Flask, request, jsonify
import pandas as pd
import spacy
from spacy_recognizer import CustomSpacyRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import warnings
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings('ignore')

# Your helper methods and initialization logic remains the same here...

def analyzer_engine():
    """Return AnalyzerEngine."""

    spacy_recognizer = CustomSpacyRecognizer()

    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_spacy_pii_distilbert"}],
    }

    # Create NLP engine based on configuration
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    registry = RecognizerRegistry()
    # add rule-based recognizers
    registry.load_predefined_recognizers(nlp_engine=nlp_engine)
    registry.add_recognizer(spacy_recognizer)
    # remove the nlp engine we passed, to use custom label mappings
    registry.remove_recognizer("SpacyRecognizer")

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine,
                              registry=registry, supported_languages=["en"])

    # uncomment for flair-based NLP recognizer
    # flair_recognizer = FlairRecognizer()
    # registry.load_predefined_recognizers()
    # registry.add_recognizer(flair_recognizer)
    # analyzer = AnalyzerEngine(registry=registry, supported_languages=["en"])
    return analyzer


def analyze(**kwargs):
    """Analyze input using Analyzer engine and input arguments (kwargs)."""
    if "entities" not in kwargs or "All" in kwargs["entities"]:
        kwargs["entities"] = None
    return analyzer_engine().analyze(**kwargs)


# def anonymizer_engine():
#     """Return AnonymizerEngine."""
#     return AnonymizerEngine()


# def anonymize(text, analyze_results):
#     """Anonymize identified input using Presidio Abonymizer."""
#     if not text:
#         return
#     res = anonymizer_engine().anonymize(text, analyze_results)
#     return res.text


app = Flask(__name__)

@app.route('/')
def mains():
    return 'Hello, World!'

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Service is running"})

@app.route('/detect_pii', methods=['POST'])
def detect_pii():
    # data = request.json
    # texts = data.get('texts', [])

    texts=request.form.get('inputData')
    print(type(texts))
    
    txt=list(texts.split(" "))


    results = []
    for text in txt:
        analyze_results = analyze(text=text, language="en")
        analyzed_data = {
            "text": text,
            "findings": [r.to_dict() for r in analyze_results]
        }
        results.append(analyzed_data)

    return jsonify(results)

# @app.route('/anonymize_pii', methods=['POST'])
# def anonymize_endpoint():
#     data = request.json
#     text = data.get('text')
#     analyze_results = analyze(text=text, language="en")
#     anonymized_text = anonymize(text, analyze_results)
#     return jsonify({"anonymized_text": anonymized_text})


if __name__ == '__main__':
    app.run(debug=True)