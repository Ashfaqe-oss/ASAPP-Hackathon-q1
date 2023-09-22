from flask import Flask, request, jsonify,send_file
import pandas as pd
import spacy
from spacy_recognizer import CustomSpacyRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
import warnings
import os
import csv
import io
from redaction import redactortext

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
    texts=request.form.get('inputData')
    txt=list(texts.split(" "))
    analyzed_data = {}
    for text in txt:
        analyze_results = analyze(text=text, language="en")
        x = [r.to_dict() for r in analyze_results]
        if x==[]:
            continue
        x = x[0]
        analyzed_data[text] = x
    result = redactortext(texts,analyzed_data)
    return jsonify(result)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    # file = request.files['file']

    file_ = request.files['file']
    Q_data = pd.read_csv(file_, header=None)
    for  row in Q_data.iterrows():
        texts = str(row[1])
        txt=list(texts.split(" "))
        analyzed_data = {}
        for text in txt:
            analyze_results = analyze(text=text, language="en")
            x = [r.to_dict() for r in analyze_results]
            if x==[]:
                continue
            x = x[0]
            analyzed_data[text] = x
        result = redactortext(texts,analyzed_data)
        # row[2] = result['str']
        # row[3] = result['map']
        print(result)

    output_file_path = 'redacted_output.csv'
    Q_data.to_csv(output_file_path, header=False, index=False)
    # Return the CSV file to the client
    return send_file(output_file_path, as_attachment=True)
    # return "hello"



if __name__ == '__main__':
    app.run(debug=True)