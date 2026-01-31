import os
import re
import pdfplumber
import pandas as pd

PDF_FOLDER = "pdfs"
OUTPUT_CSV = "final_output.csv"


def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def extract_records_rule_based(text):
    """
    Extracts structured records (Name, Age, City, Email)
    from unstructured text using multiple pattern styles.
    """
def extract_records_rule_based(text):
    """
    Extracts structured records (Name, Age, City, Email)
    from unstructured text using multiple pattern styles.
    """
    records = []

    # Pattern 1: Label-based format
    pattern1 = re.findall(
        r"Name[:=]\s*(.*?)\s*\|\s*Age[:=]\s*(\d+)\s*\|\s*(?:City|Location)[:=]\s*(.*?)\s*\|\s*(?:Email|Mail ID)[:=]\s*([^\s|]+)",
        text,
        re.IGNORECASE
    )

    # Pattern 2: Sentence format (Name aged 20 at Kochi...)
    pattern2 = re.findall(
        r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\,?\s*(?:aged\s*(\d+)).*?(?:at|in)\s*([A-Z][a-z]+).*?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        text
    )

    # Pattern 3: Slash-separated format
    pattern3 = re.findall(
        r"([A-Z][a-z]+\s[A-Z][a-z]+)\s*/\s*(\d+).*?/\s*([A-Z][a-z]+).*?/\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        text
    )

    # Pattern 4: Key-value format
    pattern4 = re.findall(
        r"Name\s*=\s*([A-Z][a-z]+\s[A-Z][a-z]+).*?Age\s*=\s*(\d+).*?(?:Location|City)\s*=\s*([A-Z][a-z]+).*?(?:Mail ID|Email)\s*=\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        text,
        re.IGNORECASE
    )

    # Pattern 5: Narrative format (Customer Priya Menon lives in Bangalore and she is 19 years old...)
    pattern5 = re.findall(
        r"(?:Customer\s+)?([A-Z][a-z]+\s[A-Z][a-z]+).*?(?:in|at)\s*([A-Z][a-z]+).*?(\d{2}).*?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
        text
    )

    # Add matches
    for match in pattern1:
        records.append(match)

    for match in pattern2:
        records.append(match)

    for match in pattern3:
        records.append(match)

    for match in pattern4:
        records.append(match)

    # Reorder Pattern 5 fields (Name, City, Age, Email → Name, Age, City, Email)
    for match in pattern5:
        name, city, age, email = match
        records.append((name, age, city, email))

    # Remove duplicates while preserving order
    unique_records = list(dict.fromkeys(records))

    return unique_records



def main():
    all_records = []

    if not os.path.exists(PDF_FOLDER):
        print(f"Folder '{PDF_FOLDER}' not found.")
        return

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF file(s). Processing...")

    for file in pdf_files:
        path = os.path.join(PDF_FOLDER, file)
        print(f"Processing: {file}")

        text = extract_text_from_pdf(path)

        if not text.strip():
            print("No extractable text found in this PDF.")
            continue

        records = extract_records_rule_based(text)
        print(f"Extracted {len(records)} record(s)")
        all_records.extend(records)

    if not all_records:
        print("No records extracted from any PDF.")
        return

    df = pd.DataFrame(all_records, columns=["Name", "Age", "City", "Email"])
    df.to_csv(OUTPUT_CSV, index=False)

    print("Extraction complete.")
    print(f"Output saved as: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
