import spacy
from spacy.matcher import DependencyMatcher
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
matcher = DependencyMatcher(nlp.vocab)

pattern = [
    {
        "RIGHT_ID": "anchor_is",
        "RIGHT_ATTRS": {"ORTH": "is"}
    },
    {
        "LEFT_ID": "anchor_is",
        "REL_OP": ">",
        "RIGHT_ID": "is_subject",
        "RIGHT_ATTRS": {"DEP": "nsubj"},
    },
    {
        "LEFT_ID": "anchor_is",
        "REL_OP": ">",
        "RIGHT_ID": "is_attr",
        "RIGHT_ATTRS": {"DEP": "attr"},
    },
   
]

matcher.add("IS", [pattern])
doc = nlp("The first ingredient is moon water, the second ingredient is apple.")
matches = matcher(doc)

print(matches) # [(4851363122962674176, [6, 0, 10, 9])]
# Each token_id corresponds to one pattern dict
displacy.render(doc)
for idx in matches:
  match_id, token_ids = matches[matches.index(idx)]
  
  for i in range(len(token_ids)):
      print(pattern[i]["RIGHT_ID"] + ":", doc[token_ids[i]].text)