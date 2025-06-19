# 📘 API Documentation – Document Understanding Service

## 🔗 Base URL

```
http://127.0.0.1:8000
```

---

## 🔍 `POST /documents/analyze`

**Upload and analyze a PDF document. Returns its classification and metadata.**

### 🔸 Request

```bash
curl -X POST "http://127.0.0.1:8000/documents/analyze" \
  -F "file=@Contract.PDF"
```

Or via Python:

```python
import requests

files = {'file': open('Contract.PDF', 'rb')}
response = requests.post("http://127.0.0.1:8000/documents/analyze", files=files)
print(response.json())
```

### 🔸 Response

```json
{
  "document_id": "abc123",
  "filename": "Contract.PDF",
  "classification": {
    "type": "contract",
    "confidence": 0.67
  },
  "metadata": {
    "parties": ["Company A", "Company B"],
    "effective_date": "March 1, 2023",
    "termination_date": "N/A",
    "key_terms": ["Non-disclosure agreement", "Payment terms"]
  }
}
```

---

## 📄 `GET /documents/{id}`

**Returns full metadata and classification result for a previously uploaded document. The response includes semantic descriptions of fields and Structured to be easily consumable by AI agents, in the format: Key, value, description. For better UX, use the document name (without .pdf) to get its metadata.**

### 🔸 Request

```bash
curl http://127.0.0.1:8000/documents/Contract
```

### 🔸 Response

```json
{
  "document_id": "Contract.PDF",
  "document_type": {
    "value": "contract",
    "description": "A legally binding agreement between parties"
  },
  "classification_confidence": {
    "value": 0.67,
    "description": "Confidence score (0–1) based on how many expected fields were found"
  },
  "extracted_metadata": [
    {
      "field_name": "parties",
      "value": [
        "EMERALD HEALTH NATURALS, INC.",
        "DR. GAETANO MORELLO N.D. INC."
      ],
      "description": "The individuals or organizations bound by the contract"
    },
    {
      "field_name": "effective_date",
      "value": "10 day of January 2019",
      "description": "The date on which the contract becomes legally enforceable"
    },
    {
      "field_name": "termination_date",
      "value": "unknown",
      "description": "The date on which the contract ends"
    },
    {
      "field_name": "key_terms",
      "value": [
        "Scope of Engagement",
        "Services",
        "Reporting and Oversight Responsibility",
        "Commitment of the Contractor"
      ],
      "description": "No description available"
    }
  ]
}
```

---

## ⚙️ `GET /documents/{id}/actions?filter={key}`

**Returns a mock list of actionable items (status, deadline, or priority) for a document.**

### 🔸 Parameters

- `id` – the document name (without `.PDF`)
- `filter` – one of: `status`, `deadline`, `priority`

### 🔸 Examples

#### ✅ Status Filter

```bash
curl "http://127.0.0.1:8000/documents/Contract/actions?filter=status"
```

Response:

```json
{
  "filter": "status",
  "value": "waiting for approval"
}
```

#### 📆 Deadline Filter

```bash
curl "http://127.0.0.1:8000/documents/Contract/actions?filter=deadline"
```

Response:

```json
{
  "filter": "deadline",
  "value": "August 2025"
}
```

#### 🔺 Priority Filter

```bash
curl "http://127.0.0.1:8000/documents/Contract/actions?filter=priority"
```

Response:

```json
{
  "filter": "priority",
  "value": "1"
}
```

---