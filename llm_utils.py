import os
import openai
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# Output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


API_KEY = os.getenv("OPENAI_API_KEY")

def classify_and_extract(text: str, doc_id: str, filename: str) -> dict:

    """
    Analyze the given document text and classify it as one of the following types:
    contract, invoice, or earnings report.

    Once the type is chosen (unless it is 'unknown'), also extract the following extended fields:
    - Contract: key_terms — important clauses such as: 'Non-disclosure agreement', 'Termination conditions', 'Jurisdiction', 'Payment terms', or 'Liability clauses'.
      Use your knowledge of legal documents to summarize them even if they're not explicitly labeled.
    - Invoice: line_items — a list of billed services/products with quantities and unit prices.
    - Earnings report: executive_summary — a concise 2–4 sentence overview of company performance, revenue trends, or strategic highlights.

    If the document is classified as 'unknown', return an empty metadata object and omit extended fields.

    Return the result as JSON
    :param text: The text of the document to analyze
    :param doc_id: A unique identifier for the document
    :param filename: The original filename of the document
    :return: A dictionary containing the classification and extracted fields
    """

    prompt = (
    "You are an expert document analyzer. Analyze the following document and classify it as one of the following types: "
    "contract, invoice, or earnings report.\n\n"

    "Use your understanding of the document based on its structure, language, terminology, and layout. "
    "Support your decision using core metadata fields when available, but do not rely solely on them.\n\n"

    "The core fields for each type are:\n"
    "- Contract: parties, effective_date, termination_date\n"
    "- Invoice: vendor, amount, due_date\n"
    "- Earnings report: reporting_period, key_metrics\n\n"

    "Key metrics in earnings reports include financial values such as: revenue, gross profit, net income, operating income, earnings per share (EPS), or EBITDA. "
    "These may appear in-line in the text and not necessarily in a table. "
    "Extract both the names of the metrics and their associated numerical values (e.g., 'revenue': '$12M'). "
    "If values are not exact, approximate or summarize based on the surrounding context.\n\n"

    "If the document clearly resembles one of the types in tone and structure (e.g., financial summaries for earnings reports), "
    "classify it accordingly even if some fields are missing. Only return 'unknown' if there is no strong evidence for any type.\n\n"

    "Once the type is chosen (unless it is 'unknown'), also extract the following extended fields:\n"
    "- Contract: key_terms — a list of the most important legal clauses or obligations. "
    "Do not summarize the contract — instead, extract and list distinct clause names or inferred legal terms. "
    "Examples include: 'Non-disclosure agreement', 'Termination conditions', 'Jurisdiction', 'Payment terms', "
    "'Liability clauses', 'Arbitration', 'Scope of work', 'Renewal policy'. "
    "Use your knowledge of legal language to detect these terms even if they are not explicitly labeled.\n"    "- Invoice: line_items — a list of billed services/products with quantities and unit prices.\n"
    "- Earnings report: executive_summary — a concise 2–4 sentence overview of company performance, revenue trends, or strategic highlights.\n\n"

    "If the document is classified as 'unknown', return an empty metadata object and omit extended fields.\n\n"

    "Return the result as JSON in the format:\n"
    "{\n"
    "  'type': '...',\n"
    "  'metadata': { 'field1': 'value1', ... },\n"
    "  'extended_fields': { 'field': value, ... }  // Only if type is not 'unknown'\n"
    "}\n\n"

    f"Document:\n{text[:2000]}"
)

    print(f"API_KEY loaded: {API_KEY is not None}")
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(content.replace("'", '"'))
        doc_type = parsed.get("type", "unknown").lower()
        metadata = parsed.get("metadata", {})
        extended_fields = parsed.get("extended_fields", {})
        if extended_fields:
            metadata.update(extended_fields)
    except Exception as e:
        doc_type = "unknown"
        metadata = {"error": str(e)}

    expected_fields = {
        "contract": ["parties", "effective_date", "termination_date"],
        "invoice": ["vendor", "amount", "due_date"],
        "earnings report": ["reporting_period", "key_metrics"]
    }

    found_fields = metadata
    expected = expected_fields.get(doc_type, [])
    found = [
        key for key in expected
        if key in found_fields and found_fields[key]
        and str(found_fields[key]).strip().lower() not in {"n/a", "none", "unknown", ""}
    ]
    confidence_ratio = len(found) / len(expected) if expected else 0

    result = {
        "document_id": doc_id,
        "filename": filename,
        "classification": {
            "type": doc_type,
            "confidence": round(confidence_ratio, 2)
        },
        "metadata": metadata
    }

    #output_file = OUTPUT_DIR / f"{doc_id}.json"
    clean_name = Path(filename).stem.replace(" ", "_")
    output_file = OUTPUT_DIR / f"{clean_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result