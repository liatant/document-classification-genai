# 📄 Document Classification API

This FastAPI app allows uploading PDF documents and classifies them as:
- 📘 Contract
- 🧾 Invoice
- 📊 Earnings Report

It uses OpenAI GPT to:
- Classify the document
- Extract relevant metadata
- Provide a confidence score based on extracted fields

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

## 🚀 Run the Server

```bash
uvicorn main:app --reload
```

Then go to: http://127.0.0.1:8000/docs

## 🌐 Environment

OPENAI_API_KEY=your-openai-api-key-here (I can send my key if needed)
---

## 📡 Endpoints

### `POST /documents/analyze`
Upload a PDF for classification and metadata extraction.

### `GET /documents/{id}`
Get metadata of a processed document. Each document has a unique ID. For better UX, use the document name (without `.pdf`) to get its metadata.

### `GET /documents/{id}/actions`
Get actionable items with optional filters: `status`, `deadline`, `priority`. *(Mocked values)*

---

## 🧠 Explanation of the Approach

### 📄 Text Extraction
PDF content is extracted using the **PyMuPDF** package, which reads page-level text into a string for LLM processing.

### 🧪 Zero-Shot Classification and Metadata Extraction
We use **GPT-3.5-turbo** in a zero-shot setting with a carefully designed prompt. The model is instructed to:

- Classify the document using its general knowledge of layout, terminology, and tone.
- Validate or revise its decision using core metadata fields:

| Document Type   | Core Metadata Fields                         |
|-----------------|----------------------------------------------|
| Contract        | `parties`, `effective_date`, `termination_date` |
| Invoice         | `vendor`, `amount`, `due_date`              |
| Earnings Report | `reporting_period`, `key_metrics` (e.g., revenue, net income) |

If the document lacks sufficient signals, the model returns `"unknown"`.

After classification, extended fields are extracted:

- Contract → `key_terms`
- Invoice → `line_items`
- Earnings Report → `executive_summary`

🧩 This hybrid logic improves robustness by first applying semantic understanding and then validating with structured cues.

### ❓ Why Zero-Shot?
- Core features guide better than a few static examples.
- GPT's general understanding is strong if instructions are clear.

---

## 🧬 Model Selection

After experimenting with local and hosted models, GPT-3.5-turbo was chosen due to:
- ✅ High accuracy and semantic robustness
- 💰 Lower cost compared to GPT-4
- ⚡ Acceptable latency

---

### 🎯 Confidence Score
Calculated as the ratio of non-empty, valid core fields to total expected fields. `"n/a"`, `"unknown"`, and `"none"` are treated as missing.

---

## 🤖 AI-Powered Features for Factify

### 🔹 Feature 1: Temporal Document Analytics & Comparison

**Use Case:**  
Compare documents from the **same vendor/party** over time. Understand financial and contractual evolution across versions.

**Examples:**
- Invoices → detect rising vendor prices or changing due dates
- Contracts → track modified clauses like payment terms
- Earnings Reports → visualize revenue/profit trends quarterly

**Technical Approach:**
1. **Group by Entity**: Use fuzzy matching or NER to link same vendors/companies
2. **Time Series Creation**: Sort by `effective_date`, `reporting_period`, or invoice date
3. **Semantic Diffing**: Embed key_terms or summaries → cosine similarity highlights clause changes
4. **Visualization + Narration**:
   - Plot revenue growth or term shifts
   - Use LLM to generate summaries: e.g., “Net income dropped by 17% vs Q2”

**Business Value:**
- 📈 Strategic insight from repeated vendors
- ✅ Audit compliance over time
- 🤝 Improved negotiation using document history
- 📊 Feed leadership dashboards with real document data

---

### 🔹 Feature 2: AI-Driven Workflow Trigger Engine

**Use Case:**  
Turn extracted metadata into **triggers** that automate workflows or risk flags.

**Examples:**
- Invoice amount > $10K → alert procurement
- Contract missing `termination_date` → notify legal
- Earnings report mentions “loss” → notify CFO

**Technical Approach:**
- Rule Engine over structured fields (amount, date, etc.)
- LLM embeddings over `executive_summary` for alert keywords
- Integration with Slack/email via webhooks or pub/sub events

**Business Value:**
- 🚨 Real-time insight into risks
- 🔄 Automate notifications and escalation
- ⏱️ Save manual time, reduce oversight

---

## 🔒 Production Considerations

### 🛡️ API Failures
- Catch exceptions → default to `"unknown"`
- Log errors
- If agreed, search the core fields in the documents to classify and extract metadata, to provide initial results, and later on try again using the API

### 🔁 Caching Strategy
- Cache input hash (SHA256) of PDF text
- Reuse result if already analyzed

---

## 💰 Cost Estimate

- Input: ~2000 characters → ~500 tokens
- Output: same (max)
- GPT-3.5 price: $0.0005 / 1K tokens
- ✅ Cost per document: **~$0.0005**
