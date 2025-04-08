import re
from collections import Counter

class KeywordExtractor:
    def __init__(self):
        self.stopwords = set([
            "yo", "tú", "él", "ella", "nosotros", "ustedes", "ellos", "ellas",
            "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
            "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como",
            "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta",
            "me", "mi", "te", "es", "soy", "estoy", "muy", "gracias", "todo", "eso",
            "así", "quien", "cual", "donde", "cuando", "que", "qué"
        ])

    def extract_keywords(self, text, ratio=0.2):
        """
        Extrae 1 palabra clave cada 5 palabras habladas (ratio = 0.2).
        Calcula basado en el total de palabras del texto original.
        """
        all_words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(all_words)

        words_filtered = [w for w in all_words if len(w) > 3 and w not in self.stopwords]
        most_common = Counter(words_filtered).most_common()

        num_keywords = max(1, int(total_words * ratio))
        return [word for word, _ in most_common[:num_keywords]]
