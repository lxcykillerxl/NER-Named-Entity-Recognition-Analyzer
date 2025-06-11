import tkinter as tk
from tkinter import messagebox, scrolledtext
import spacy
from spacy.matcher import PhraseMatcher

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load person names from names.txt
with open("names.txt", "r", encoding="utf-8") as f:
    person_names = [line.strip() for line in f if line.strip()]

# Load place names from places.txt
with open("places.txt", "r", encoding="utf-8") as f:
    place_names = [line.strip() for line in f if line.strip()]

# Create PhraseMatchers
person_name_docs = [nlp(name) for name in person_names]
person_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
person_matcher.add("CUSTOM_PERSONS", person_name_docs)

place_name_docs = [nlp(name) for name in place_names]
place_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
place_matcher.add("CUSTOM_PLACES", place_name_docs)

def extract_person_entities(text):
    """
    Extract person entities by combining:
      1) SpaCy's PERSON entities
      2) Custom person names from PhraseMatcher
      3) Proper noun chunks not labeled as GPE/LOC/etc.
    """
    doc = nlp(text)
    
    # Collect SpaCy-labeled PERSON entities
    spacy_persons = set()
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            spacy_persons.add(ent.text)
    
    # Identify custom persons using person_matcher
    custom_persons = set()
    matches = person_matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        custom_persons.add(span.text)

    # Proper noun chunking for potential persons
    chunked_persons = set()
    current_chunk = []
    
    for token in doc:
        if token.pos_ == "PROPN":
            # Flush if labeled as something other than PERSON (e.g., GPE, LOC)
            if token.ent_type_ not in ("PERSON", ""):
                if current_chunk:
                    chunk_text = " ".join(t.text for t in current_chunk)
                    chunked_persons.add(chunk_text)
                    current_chunk = []
                continue
            current_chunk.append(token)
        else:
            if current_chunk:
                chunk_text = " ".join(t.text for t in current_chunk)
                chunked_persons.add(chunk_text)
                current_chunk = []
    
    # Flush remaining chunk
    if current_chunk:
        chunk_text = " ".join(t.text for t in current_chunk)
        chunked_persons.add(chunk_text)
    
    # Combine all sets
    all_persons = spacy_persons.union(custom_persons, chunked_persons)
    
    # Clean up
    all_persons = {p.strip() for p in all_persons if p.strip()}
    return sorted(all_persons)

def extract_place_entities(text):
    """
    Extract place entities by combining:
      1) SpaCy's GPE and LOC entities
      2) Custom place names from PhraseMatcher
      3) Proper noun chunks not labeled as PERSON
    """
    doc = nlp(text)
    
    # Collect SpaCy-labeled GPE and LOC entities
    spacy_places = set()
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            spacy_places.add(ent.text)
    
    # Identify custom places using place_matcher
    custom_places = set()
    matches = place_matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        custom_places.add(span.text)

    # Proper noun chunking for potential places
    chunked_places = set()
    current_chunk = []
    
    for token in doc:
        if token.pos_ == "PROPN":
            # Flush if labeled as PERSON
            if token.ent_type_ not in ("GPE", "LOC", ""):
                if current_chunk:
                    chunk_text = " ".join(t.text for t in current_chunk)
                    chunked_places.add(chunk_text)
                    current_chunk = []
                continue
            current_chunk.append(token)
        else:
            if current_chunk:
                chunk_text = " ".join(t.text for t in current_chunk)
                chunked_places.add(chunk_text)
                current_chunk = []
    
    # Flush remaining chunk
    if current_chunk:
        chunk_text = " ".join(t.text for t in current_chunk)
        chunked_places.add(chunk_text)
    
    # Combine all sets
    all_places = spacy_places.union(custom_places, chunked_places)
    
    # Clean up
    all_places = {p.strip() for p in all_places if p.strip()}
    return sorted(all_places)

def evaluate_ner(system_output, gold_standard):
    """
    Computes precision & recall for identified entities against a gold standard.
    """
    system_set = set(system_output)
    gold_set = set(gold_standard)
    true_positives = len(system_set & gold_set)
    false_positives = len(system_set - gold_set)
    false_negatives = len(gold_set - system_set)
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0
    return precision, recall

def analyze_text():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter text to analyze.")
        return

    # Extract entities
    entities_persons = extract_person_entities(text)
    entities_places = extract_place_entities(text)

    # Example gold standard for persons (can be updated dynamically)
    gold_standard_persons = ["John Doe", "Jane Smith", "Alice"]
    precision_persons, recall_persons = evaluate_ner(entities_persons, gold_standard_persons)

    # Display results
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)

    if entities_persons:
        output_text.insert(tk.END, "Identified Persons:\n")
        for ent in entities_persons:
            output_text.insert(tk.END, f" - {ent}\n")
    else:
        output_text.insert(tk.END, "No persons detected.\n")

    output_text.insert(tk.END, f"\nPrecision (Persons): {precision_persons:.2f}\nRecall (Persons): {recall_persons:.2f}\n")

    if entities_places:
        output_text.insert(tk.END, "\nIdentified Places:\n")
        for ent in entities_places:
            output_text.insert(tk.END, f" - {ent}\n")
    else:
        output_text.insert(tk.END, "\nNo places detected.\n")

    output_text.config(state="disabled")

# Tkinter GUI Setup
root = tk.Tk()
root.title("NER System with Custom Persons and Places")
root.geometry("600x650")
root.configure(bg="#2c3e50")

label_font = ("Helvetica", 12, "bold")
text_font = ("Consolas", 11)
fg_color = "#ecf0f1"
bg_color = "#34495e"

input_label = tk.Label(root, text="Enter Text:", bg=root["bg"], fg=fg_color, font=label_font)
input_label.pack(pady=(10, 0))

input_text = scrolledtext.ScrolledText(root, height=10, width=70, font=text_font, bg=bg_color, fg=fg_color, wrap=tk.WORD)
input_text.pack(padx=10, pady=5)

analyze_button = tk.Button(root, text="Analyze", command=analyze_text,
                           font=label_font, bg="#1abc9c", fg="white", relief=tk.RAISED)
analyze_button.pack(pady=10)

output_label = tk.Label(root, text="Output:", bg=root["bg"], fg=fg_color, font=label_font)
output_label.pack(pady=(20, 0))

output_text = scrolledtext.ScrolledText(root, height=12, width=70, font=text_font,
                                        bg=bg_color, fg=fg_color, wrap=tk.WORD, state="disabled")
output_text.pack(padx=10, pady=5)

root.mainloop()