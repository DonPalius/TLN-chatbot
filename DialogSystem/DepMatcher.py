import spacy
from Utils import load_rules
from spacy.matcher import DependencyMatcher


class DepMatcher:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = DependencyMatcher(self.nlp.vocab)

        # self.matcher.add("Quantity", load_rules("Data/rules_qty.json"))
        self.matcher.add("Is_not_ingredient", load_rules(
            "Data/is_not_ingredient.json"))
        # self.matcher.add("neg_ans", load_rules(
        #     "Data/neg_ans.json"))
        self.matcher.add("yesOrNo", load_rules(
            "Data/yesOrNo.json"))
        self.matcher.add("Is_ingredient", load_rules(
            "Data/is_ingredient.json"))

    def get_matches(self, doc):
        doc = self.nlp(doc)
        matches = self.matcher(doc)

        # TODO add match logic

        for match in matches:
            match[1].sort()

        return [(self.nlp.vocab.strings[match[0]], " ".join([doc[i].text for i in match[1]])) for match in matches]


if __name__ == "__main__":
    d = DepMatcher()
    # print(d.get_matches("the first ingredient is moon water"))
