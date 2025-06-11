# NER Analyzer

## Overview
This project is a **Named Entity Recognition (NER) Analyzer** built using Flask and SpaCy. It extracts person and place entities from user-provided text, leveraging SpaCy's default NER capabilities, custom entity matching, and syntactic rules. The application also evaluates the NER performance using precision and recall metrics and provides a basic syntactic dependency analysis of the input text.

## Project Structure
- `app.py`: The main Flask application that handles NER logic, entity extraction, and evaluation.
- `index.html`: The front-end template for user interaction, displaying input forms and NER results.
- `names.txt`: A file containing a list of custom person names for entity matching.
- `places.txt`: A file containing a list of custom place names for entity matching.
- `.venv/`: Virtual environment directory (not tracked in version control).

## Features
- Extracts person and place entities using SpaCy's NER model, custom PhraseMatcher, and syntactic rules (e.g., titles like "Dr. Smith").
- Evaluates NER performance with precision and recall metrics against a sample ground truth.
- Displays syntactic dependency analysis of the input text.
- User-friendly web interface for text input and result visualization.

## Prerequisites
- Python 3.7+
- Virtual environment (recommended)
- Required Python packages:
  - `flask`
  - `spacy`
  - `en_core_web_sm` (SpaCy English model)

## Setup Instructions
1. **Clone the repository** (if applicable) or navigate to the project directory.
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install flask spacy
   python -m spacy download en_core_web_sm
   ```
4. **Prepare the custom entity files**:
   - Ensure `names.txt` contains a list of person names (one per line).
   - Ensure `places.txt` contains a list of place names (one per line).
   - If these files are missing, the app will still run but will skip custom entity matching for the missing file(s).
5. **Run the application**:
   ```bash
   python app.py
   ```
6. Open your browser and navigate to `http://127.0.0.1:5000` to access the web interface.

## Usage
1. Enter the text you want to analyze in the provided text area.
2. Click the "Analyze" button to process the text.
3. View the results, which include:
   - Identified persons and places.
   - Precision and recall metrics for person entities (based on a sample ground truth).
   - Syntactic dependency analysis of the text.

## Example
**Input Text**:  
"Dr. Smith visited New York with Jane Smith and Alice."

**Output**:  
- **Persons**: Dr. Smith, Jane Smith, Alice  
- **Places**: New York  
- **Precision/Recall**: Calculated based on a predefined ground truth (e.g., ["Dr. Smith", "Jane Smith", "Alice"]).  
- **Syntactic Analysis**: Displays token dependencies (e.g., "visited -> nsubj -> Dr. Smith").

## Notes
- The application currently uses a hardcoded ground truth for evaluation (`gold_persons` in `app.py`). You can modify this list to match your use case.
- The `app.secret_key` in `app.py` is set to a placeholder (`"your_secret_key"`). Replace it with a secure key in production.
- The project can be extended by adding more custom entities to `names.txt` and `places.txt` or by enhancing the NER logic.

## Limitations
- Custom entity matching is case-insensitive and may require careful curation of `names.txt` and `places.txt` to avoid false positives.
- The syntactic title extraction (e.g., "Mr. Smith") assumes specific patterns and may not handle all edge cases.
- The evaluation metrics are based on a static ground truth, which may not generalize to all inputs.

## Future Improvements
- Add support for more entity types (e.g., organizations, dates).
- Improve the UI with better styling and interactivity.
- Allow users to upload custom entity files through the web interface.
- Enhance evaluation by allowing dynamic ground truth input.

## Acknowledgments
This project was developed with assistance from **Grok**, an AI created by xAI, which helped in building and structuring the application.