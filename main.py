from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import uuid
from document_utils import extract_text_from_pdf
from llm_utils import classify_and_extract
import json
from pathlib import Path

app = FastAPI()

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Descriptions for semantic structure
FIELD_DESCRIPTIONS = {
    "parties": "The individuals or organizations bound by the contract",
    "effective_date": "The date on which the contract becomes legally enforceable",
    "termination_date": "The date on which the contract ends",
    "vendor": "The company or person issuing the invoice",
    "amount": "The total amount to be paid",
    "due_date": "The final date by which payment should be made",
    "reporting_period": "The time period covered by the financial report",
    "key_metrics": "Important financial figures such as revenue, profit, EPS, etc.",
    "error": "An error message encountered during parsing or extraction"
}

TYPE_DESCRIPTIONS = {
    "contract": "A legally binding agreement between parties",
    "invoice": "A bill issued to request payment for services or goods",
    "earnings report": "A summary of a company’s financial performance"
}

@app.post("/documents/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    doc_id = str(uuid.uuid4())
    filename = file.filename
    contents = await file.read()

    with open(f"temp_{doc_id}.pdf", "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(f"temp_{doc_id}.pdf")
    
    result = classify_and_extract(text, doc_id=doc_id, filename=filename)
    print(result)
    return JSONResponse(content=result)

@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    path = OUTPUT_DIR / f"{doc_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    filename = raw_data.get("filename", doc_id)
    doc_type = raw_data.get("classification", {}).get("type", "unknown")
    confidence = raw_data.get("classification", {}).get("confidence", None)
    metadata = raw_data.get("metadata", {})

    structured = {
        "document_id": filename,
        "document_type": {
            "value": doc_type,
            "description": TYPE_DESCRIPTIONS.get(doc_type, "Unknown document type")
        },
        "classification_confidence": {
            "value": confidence,
            "description": "Confidence score (0–1) based on how many expected fields were found"
        },
        "extracted_metadata": [
            {
                "field_name": key,
                "value": value,
                "description": FIELD_DESCRIPTIONS.get(key, "No description available")
            }
            for key, value in metadata.items()
        ]
    }

    return JSONResponse(content=structured)


@app.get("/documents/{doc_id}/actions")
async def get_document_actions(
    doc_id: str,
    filter_by: str = Query(..., enum=["status", "deadline", "priority"])
):
    path = OUTPUT_DIR / f"{doc_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    # Mocked filter result based on selected filter_by
    mock_response = {
        "status": "waiting for approval",
        "deadline": "August 2025",
        "priority": "1"
    }

    return {
        "document_id": doc_id,
        "filter": filter_by,
        "value": mock_response.get(filter_by)
    }

