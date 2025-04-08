from pysentimiento import create_analyzer

class TextEmotionAnalyzer:
    def __init__(self, lang="es"):
        self.analyzer = create_analyzer(task="emotion", lang=lang)

    def analyze(self, text):
        result = self.analyzer.predict(text)
        return {
            "emotion": result.output,
            "probabilities": result.probas
        }
