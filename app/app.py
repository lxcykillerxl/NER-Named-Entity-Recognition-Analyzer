from flask import Flask, render_template, request, redirect, url_for, flash
import spacy
from spacy.matcher import PhraseMatcher
import os
import re

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load custom person names
names_file = "names.txt"
if os.path.exists(names_file):
    with open(names_file, "r", encoding="utf-8") as f:
        person_names = [line.strip() for line in f if line.strip()]
else:
    person_names = []
    print("names.txt not found.")

# Load custom place names
places_file = "places.txt"
if os.path.exists(places_file):
    with open(places_file, "r", encoding="utf-8") as f:
        place_names = [line.strip() for line in f if line.strip()]
else:
    place_names = []
    print("places.txt not found.")

# PhraseMatchers for custom NER
person_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
person_matcher.add("CUSTOM_PERSONS", [nlp.make_doc(name) for name in person_names])

place_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
place_matcher.add("CUSTOM_PLACES", [nlp.make_doc(name) for name in place_names])

# Extract names with titles like Mr., Dr., etc.
def extract_named_by_title(doc):
    title_pattern = re.compile(r"^(Mr\.|Mrs\.|Ms\.|Miss|Dr\.|Prof\.|called)$", re.IGNORECASE)
    syntactic_names = set()
    
    for i, token in enumerate(doc):
        # Format like "Mr. Smith"
        if title_pattern.match(token.text):
            if i + 1 < len(doc) and doc[i + 1].pos_ == "PROPN":
                name = f"{token.text} {doc[i + 1].text}"
                syntactic_names.add(name)
        # Format like "mr.smith"
        elif "." in token.text:
            parts = token.text.split(".")
            if len(parts) == 2 and title_pattern.match(parts[0].capitalize() + "."):
                name = f"{parts[0].capitalize()}. {parts[1].capitalize()}"
                syntactic_names.add(name)
    
    return syntactic_names

def extract_person_entities(text):
    doc = nlp(text)
    spacy_persons = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}

    custom_persons = set()
    for match_id, start, end in person_matcher(doc):
        custom_persons.add(doc[start:end].text)

    syntactic_titles = extract_named_by_title(doc)

    all_persons = spacy_persons.union(custom_persons, syntactic_titles)
    return sorted({p.strip() for p in all_persons if p.strip()}), doc

def extract_place_entities(doc):
    spacy_places = {ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")}
    spacy_persons = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}

    custom_places = set()
    for match_id, start, end in place_matcher(doc):
        custom_places.add(doc[start:end].text)

    chunked_places = set()
    current_chunk = []
    known_persons_lower = {p.lower() for p in person_names + list(spacy_persons)}

    for token in doc:
        if token.pos_ == "PROPN":
            current_chunk.append(token)
        else:
            if current_chunk:
                chunk_text = " ".join(t.text for t in current_chunk).strip()
                if chunk_text.lower() not in known_persons_lower:
                    chunked_places.add(chunk_text)
                current_chunk = []
    if current_chunk:
        chunk_text = " ".join(t.text for t in current_chunk).strip()
        if chunk_text.lower() not in known_persons_lower:
            chunked_places.add(chunk_text)

    all_places = spacy_places.union(custom_places, chunked_places)

    # Filter out any places that are actually titled persons
    known_titles = {"Mr.", "Mrs.", "Ms.", "Miss", "Dr.", "Prof.", "called"}
    filtered_places = {place for place in all_places if not any(place.startswith(title) for title in known_titles)}

    return sorted({p.strip() for p in filtered_places if p.strip()})

def evaluate_ner(system_output, gold_standard):
    system_set = set(system_output)
    gold_set = set(gold_standard)
    true_positives = len(system_set & gold_set)
    false_positives = len(system_set - gold_set)
    false_negatives = len(gold_set - system_set)
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0
    return precision, recall

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("input_text", "").strip()
        if not text:
            flash("Please enter text to analyze.", "warning")
            return redirect(url_for("index"))

        persons, doc = extract_person_entities(text)
        places = extract_place_entities(doc)

        # Sample ground truth for evaluation
        gold_persons = ["Dr. Smith", "Jane Smith", "Alice"]
        precision_persons, recall_persons = evaluate_ner(persons, gold_persons)

        return render_template("index.html", input_text=text, persons=persons, places=places,
                               precision_persons=precision_persons, recall_persons=recall_persons,
                               syntax_tree=[(token.text, token.dep_, token.head.text) for token in doc])

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
