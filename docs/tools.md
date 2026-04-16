# LangGraph Tools — Detailed Specification

All tools are registered via `@tool` from `langchain_core.tools` and use async PostgreSQL sessions.
They return JSON-serializable dicts (no SQLAlchemy model objects).

---

## 1. `log_interaction`

**File:** `backend/app/tools/log_interaction.py`

**Purpose:** Capture a new HCP interaction. Automatically extracts `summary`, `sentiment`, and `key_entities` from `raw_notes` via a dedicated Groq extraction prompt.

**Signature:**
```python
log_interaction(
    hcp_name: str,
    raw_notes: str,
    interaction_type: str = "in_person",
    products_discussed: List[str] = []
) -> dict
```

**Returns:**
```json
{
  "interaction_id": "uuid",
  "hcp": "Dr. Priya Sharma",
  "hcp_id": "uuid",
  "summary": "AI-generated 2-3 sentence summary",
  "sentiment": "positive|neutral|negative",
  "key_entities": {
    "drugs_mentioned": [],
    "competitor_products": [],
    "concerns": [],
    "commitments": []
  },
  "interaction_type": "in_person"
}
```

**Example trigger prompt:**
> "Log a meeting I had today with Dr. Sharma about Atorvastatin 20mg — she was very positive and wants samples next week"

---

## 2. `edit_interaction`

**File:** `backend/app/tools/edit_interaction.py`

**Purpose:** Modify fields of an existing interaction. If `raw_notes` changes, re-runs entity extraction.

**Signature:**
```python
edit_interaction(
    interaction_id: str,
    updates: Dict[str, Any]
) -> dict
```

**Updatable fields:** `raw_notes`, `outcome`, `products_discussed`, `interaction_date`, `sentiment`

**Returns:** Updated interaction row with refreshed `summary`, `sentiment`, `key_entities`.

**Example trigger prompt:**
> "Edit interaction abc123 — actually the sentiment was neutral, he wants more clinical data before committing"

---

## 3. `search_hcp`

**File:** `backend/app/tools/search_hcp.py`

**Purpose:** Find HCPs by name, specialty, or hospital using fuzzy ILIKE matching.

**Signature:**
```python
search_hcp(query: str, limit: int = 5) -> List[dict]
```

**Returns:**
```json
[
  {
    "id": "uuid",
    "name": "Dr. Rajesh Patel",
    "specialty": "Endocrinology",
    "hospital": "Fortis Healthcare",
    "city": "Mumbai",
    "email": "r.patel@fortis.in"
  }
]
```

**Example trigger prompt:**
> "Find Dr. Patel" or "Search for cardiologists at Apollo"

---

## 4. `schedule_followup`

**File:** `backend/app/tools/schedule_followup.py`

**Purpose:** Create a follow-up task linked to an interaction and HCP.

**Signature:**
```python
schedule_followup(
    interaction_id: str,
    due_date: str,   # ISO format: YYYY-MM-DD
    description: str
) -> dict
```

**Returns:**
```json
{
  "followup_id": "uuid",
  "interaction_id": "uuid",
  "hcp_id": "uuid",
  "due_date": "2024-02-15",
  "description": "Deliver Atorvastatin samples",
  "status": "pending"
}
```

**Example trigger prompt:**
> "Schedule a follow-up for interaction abc123 for next Tuesday to deliver samples"

---

## 5. `get_interaction_history`

**File:** `backend/app/tools/get_interaction_history.py`

**Purpose:** Retrieve recent interactions for an HCP by UUID or name.

**Signature:**
```python
get_interaction_history(
    hcp_id_or_name: str,
    limit: int = 10
) -> List[dict]
```

**Returns:** List of interaction summaries sorted by most recent first.

**Example trigger prompt:**
> "Show me my last 5 interactions with Dr. Sharma"
> "What's the history with Dr. Patel?"
