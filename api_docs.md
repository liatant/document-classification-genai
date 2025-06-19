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

**Returns full metadata and classification result for a previously uploaded document.**

### 🔸 Request

```bash
curl http://127.0.0.1:8000/documents/Contract
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