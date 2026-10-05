import pandas, sklearn, spacy, streamlit, matplotlib, joblib

nlp = spacy.load("en_core_web_sm")
doc = nlp("The servers were returning errors")
print([t.lemma_ for t in doc])
print("Setup OK")