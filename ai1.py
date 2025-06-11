import spacy

def identify_persons(texts):
    try:
        # Load the transformer-based spaCy model for better accuracy
        nlp = spacy.load("en_core_web_trf")  
    except:
        print("Falling back to 'en_core_web_sm' model")
        nlp = spacy.load("en_core_web_sm")  # Use small model if transformer model isn't available

    all_persons = set()  # Use a set to store unique names

    for text in texts:
        doc = nlp(text)

        # Extract persons detected by spaCy
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # Add detected names to the set
        all_persons.update(persons)

    return list(all_persons)

# Example usage
if __name__ == "__main__":
    texts = [
        "Jamal met Umar at the park yesterday.",
        "Jamal met Sakib at the college yesterday.",
        "Ammar and Jamal are working on an IoT project.",
        "Yog met jay at the park yesterday.",
        "raju met Sakib at the park yesterday."
    ]

    result = identify_persons(texts)
    
    # Print each name on a new line
    print("Identified persons:\n" + "\n".join(result))
