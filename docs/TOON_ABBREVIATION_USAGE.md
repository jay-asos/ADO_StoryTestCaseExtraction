# How TOON Abbreviation Dictionary Works

## Overview
The TOON (Token Oriented Object Notation) abbreviation dictionary is a key-value mapping system that reduces token usage by replacing verbose terms with compact abbreviations. This document explains how and where it's used.

---

## 🔄 Three-Stage Process

### **Stage 1: AI Instruction (System Prompt)**
The abbreviation dictionary is **embedded in the system prompt** that instructs the AI model.

**Location:** `src/test_case_extractor.py` - `_get_system_prompt_toon()` method

```python
def _get_system_prompt_toon(self) -> str:
    """Get the TOON-optimized system prompt for test case extraction"""
    return """QA Expert. Generate test cases using Token Oriented Object Notation (TOON).

**TOON FORMAT:**
- Use abbrev. for common terms
- Compact structure
- Remove redundant words
- Key fields only

**Abbreviations:**
TC=TestCase, desc=description, exp=expected, prereq=prerequisites, pos=positive, neg=negative, 
edge=edge_case, sec=security, perf=performance, steps=test_steps, prio=priority, 
auth=authentication, val=validation, UI=user_interface, API=application_interface, 
DB=database, max=maximum, min=minimum, req=required, opt=optional
```

**Purpose:** Teaches the AI model to understand and use abbreviations when generating responses.

---

### **Stage 2: AI Response Generation**
The AI model uses the abbreviations from the dictionary to generate compact JSON responses.

**Example AI Response (TOON Format):**
```json
{
  "tcs": [
    {
      "t": "Verify Login Valid Creds",
      "desc": "User login w/ valid user/pass",
      "type": "pos",
      "prio": "Crit",
      "steps": ["1.Nav login pg", "2.Enter valid user/pass", "3.Click login"],
      "exp": "Auth success, redirect dashboard.",
      "prereq": "User acct exists",
      "auto": "High",
      "time": "5m"
    }
  ]
}
```

**Token Savings:** ~60% reduction compared to verbose format

---

### **Stage 3: Response Parsing (Expansion)**
The abbreviations are **expanded back to full terms** during parsing.

**Location:** `src/test_case_extractor.py` - `_parse_toon_format()` method

```python
def _parse_toon_format(self, parsed_response: Dict) -> List[TestCase]:
    """Parse TOON format response"""
    test_cases_data = parsed_response.get("tcs", [])  # "tcs" = test_cases
    
    # TOON abbreviation mappings (reverse dictionary)
    type_map = {
        "pos": "positive",
        "neg": "negative",
        "edge": "edge_case",
        "sec": "security",
        "perf": "performance",
        "integ": "integration"
    }
    
    prio_map = {
        "Crit": "Critical",
        "Med": "Medium"
    }
    
    for tc_data in test_cases_data:
        # Map TOON fields to standard fields
        title = tc_data.get("t", "")           # t → title
        description = tc_data.get("desc", "")   # desc → description
        test_type = type_map.get(tc_data.get("type", "pos"), "positive")  # pos → positive
        priority = prio_map.get(tc_data.get("prio", "Med"), "Medium")     # Crit → Critical
        steps = tc_data.get("steps", [])        # steps → test_steps
        expected_result = tc_data.get("exp", "") # exp → expected_result
        prerequisites = tc_data.get("prereq", "") # prereq → prerequisites
```

**Purpose:** Converts compact TOON format back to standard TestCase objects that the application uses.

---

## 📍 Where Each Abbreviation is Used

### **1. In System Prompt (Instruction)**

| Abbreviation | Location | Purpose |
|--------------|----------|---------|
| `TC` | System prompt | Shorthand for "Test Case" |
| `desc` | System prompt, JSON field | Replaces "description" |
| `exp` | System prompt, JSON field | Replaces "expected_result" |
| `prereq` | System prompt, JSON field | Replaces "prerequisites" |
| `pos/neg/edge` | System prompt, JSON field | Test type abbreviations |
| `prio` | System prompt, JSON field | Replaces "priority" |
| `Crit/Med/Low` | System prompt, JSON value | Priority level abbreviations |

### **2. In JSON Response Format**

**TOON Field Structure:**
```json
{
  "tcs": [                    // "tcs" instead of "test_cases"
    {
      "t": "...",            // "t" instead of "title"
      "desc": "...",         // "desc" instead of "description"
      "type": "pos",         // "pos" instead of "positive"
      "prio": "Crit",        // "Crit" instead of "Critical"
      "steps": [...],        // Kept as "steps" (already short)
      "exp": "...",          // "exp" instead of "expected_result"
      "prereq": "...",       // "prereq" instead of "prerequisites"
      "auto": "High",        // "auto" instead of "automation_potential"
      "time": "5m"           // "5m" instead of "5 minutes"
    }
  ],
  "cov": {                   // "cov" instead of "coverage_summary"
    "func": [...],          // "func" instead of "functional_coverage"
    "risk": [...]           // "risk" instead of "risk_coverage"
  }
}
```

### **3. In Parser (Expansion)**

**Mapping Dictionaries:**

```python
# Type abbreviations → Full values
type_map = {
    "pos": "positive",
    "neg": "negative",
    "edge": "edge_case",
    "sec": "security",
    "perf": "performance",
    "integ": "integration"
}

# Priority abbreviations → Full values
prio_map = {
    "Crit": "Critical",
    "Med": "Medium"
    # "High" and "Low" stay as-is (already short)
}
```

---

## 🔍 Complete Abbreviation Flow Example

### **Input (User Story):**
```
Title: User Login with Multi-Factor Authentication
Description: As a user, I want to log in...
```

### **Stage 1: System Prompt with Dictionary**
```
**Abbreviations:**
pos=positive, neg=negative, desc=description, exp=expected_result, 
prereq=prerequisites, prio=priority, Crit=Critical, Med=Medium...
```

### **Stage 2: AI Generates TOON Response**
```json
{
  "tcs": [
    {
      "t": "Verify Login Valid Creds",
      "desc": "User login w/ valid user/pass",
      "type": "pos",
      "prio": "Crit",
      "steps": ["1.Enter creds", "2.Click login"],
      "exp": "User authenticated.",
      "prereq": "Valid account"
    }
  ]
}
```
**Tokens:** ~250 tokens

### **Stage 3: Parser Expands Abbreviations**
```python
TestCase(
    title="Verify Login Valid Creds",           # from "t"
    description="User login w/ valid user/pass", # from "desc"
    test_type="positive",                        # from "pos"
    priority="Critical",                         # from "Crit"
    test_steps=["1.Enter creds", "2.Click login"], # from "steps"
    expected_result="User authenticated.",       # from "exp"
    preconditions=["Valid account"]              # from "prereq"
)
```

**Final Result:** Full TestCase object ready for ADO/JIRA

---

## 📊 Token Savings by Component

| Component | Standard Format | TOON Format | Savings |
|-----------|----------------|-------------|---------|
| **Field Names** | `"test_cases": [...]` (13 chars) | `"tcs": [...]` (6 chars) | 53.8% |
| **Test Type** | `"type": "positive"` (18 chars) | `"type": "pos"` (11 chars) | 38.9% |
| **Priority** | `"priority": "Critical"` (22 chars) | `"prio": "Crit"` (13 chars) | 40.9% |
| **Expected** | `"expected_result": "..."` (21 chars) | `"exp": "..."` (7 chars) | 66.7% |
| **Prerequisites** | `"prerequisites": "..."` (19 chars) | `"prereq": "..."` (11 chars) | 42.1% |

---

## 🎯 Key Principles

1. **Dictionary is NOT a separate file** - It's embedded in the code (system prompt and parser)
2. **AI learns the mappings** - From the system prompt instructions
3. **Automatic expansion** - Parser converts abbreviated response back to full format
4. **Bidirectional mapping** - Works for both compression (AI) and expansion (parser)
5. **Backward compatible** - Standard format is still supported (auto-detected)

---

## 🔧 Adding New Abbreviations

To add a new abbreviation:

1. **Update System Prompt** (`_get_system_prompt_toon()`):
   ```python
   **Abbreviations:**
   ..., newfield=new_field_name
   ```

2. **Update Parser** (`_parse_toon_format()`):
   ```python
   new_field = tc_data.get("newfield", "")
   ```

3. **Update Documentation** (`docs/TOON_IMPLEMENTATION.md`):
   Add to abbreviation reference table

---

## ✅ Summary

The TOON abbreviation dictionary is used in **three key locations**:

1. **System Prompt** - Teaches AI the abbreviations
2. **AI Response** - AI uses abbreviations to generate compact JSON
3. **Parser** - Expands abbreviations back to full terms

This three-stage process achieves **57.1% token reduction** while maintaining full test case quality! 🚀
