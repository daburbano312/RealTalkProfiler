from transformers import pipeline

class TextEmotionAnalyzer:
    def __init__(self):
        self.pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

    def analyze(self, text):
        result = self.pipeline(text)[0][0]
        return {"emotion": result['label'], "score": result['score']}
