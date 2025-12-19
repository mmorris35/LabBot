# LabBot

> **A case study in structured AI-assisted development**

![CI](https://github.com/USER/labbot/actions/workflows/ci.yml/badge.svg)

LabBot helps patients interpret their lab results in plain language. But this project is about more than the destination - it's about demonstrating how structured AI development planning transforms an idea into a working product.

---

## The Problem

Patients receive lab results with cryptic values like "Hemoglobin: 14.5 g/dL" and no context. They turn to Google, often finding alarming misinformation. Healthcare providers are overwhelmed and can't explain every result in detail.

**LabBot bridges this gap** by providing:
- Plain-language explanations of lab values
- Visual severity indicators (normal/borderline/abnormal)
- Citations to authoritative medical sources
- Built-in safeguards against PII exposure

---

## The Journey

This project was built using the **DevPlan methodology** - a structured approach to AI-assisted software development. Every step is documented, demonstrating how an idea becomes a product.

### 1. Requirements Capture → [PROJECT_BRIEF.md](PROJECT_BRIEF.md)
An AI-guided interview extracted:
- Core features and constraints
- Technical requirements
- Success criteria

### 2. Implementation Roadmap → [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)
The brief was transformed into:
- 5 phases, 17 subtasks
- Explicit deliverables and success criteria
- "Paint by numbers" instructions for implementation

### 3. Development Standards → [CLAUDE.md](CLAUDE.md)
Coding rules ensuring:
- Consistent code quality
- Complete test coverage
- Proper documentation

### 4. The Build → [DEVLOG.md](DEVLOG.md)
A timestamped journal capturing:
- Implementation decisions
- Challenges encountered
- Time invested per phase

### 5. The Result → This working application

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              index.html / app.js                     │   │
│  │         JSON Input → PII Warning → Results           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS API Gateway                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     AWS Lambda                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    FastAPI                           │   │
│  │                                                      │   │
│  │   POST /api/interpret                                │   │
│  │         │                                            │   │
│  │         ▼                                            │   │
│  │   ┌─────────────┐                                    │   │
│  │   │ PII Detector│──── PII Found? ──→ 400 Error      │   │
│  │   └─────────────┘                                    │   │
│  │         │ Clean                                      │   │
│  │         ▼                                            │   │
│  │   ┌─────────────┐     ┌──────────────┐              │   │
│  │   │ Interpreter │────▶│ Claude Haiku │              │   │
│  │   └─────────────┘     └──────────────┘              │   │
│  │         │                                            │   │
│  │         ▼                                            │   │
│  │   ┌─────────────┐                                    │   │
│  │   │  Citations  │                                    │   │
│  │   └─────────────┘                                    │   │
│  │         │                                            │   │
│  │         ▼                                            │   │
│  │   InterpretationResponse                             │   │
│  │   (explanations + severity + citations)              │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### ✅ MVP (Implemented)

| Feature | Description |
|---------|-------------|
| JSON Lab Input | Accept structured lab results via API or web form |
| PII Detection | Block requests containing SSN, DOB, email, phone, names |
| AI Interpretation | Claude Haiku explains values in plain language |
| Severity Indicators | Visual flags: normal (green), borderline (yellow), abnormal (red) |
| Medical Citations | Links to Mayo Clinic, NIH, MedlinePlus |
| Responsive UI | Works on desktop and mobile |
| Serverless Deploy | Auto-deploys to AWS Lambda via GitHub Actions |

### 🔮 Future (v2)

- PDF export of results
- Quest/LabCorp format parsing
- Historical comparison
- Mobile-native app

---

## Quick Start

### Local Development

```bash
# Clone and enter directory
git clone https://github.com/USER/labbot.git
cd labbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run locally
uvicorn labbot.main:app --reload
```

Visit `http://localhost:8000` to use the web interface.

### Deploy to AWS

1. Fork this repository
2. Add GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `ANTHROPIC_API_KEY`
3. Push to main - auto-deploys via GitHub Actions

---

## API Usage

### Interpret Lab Results

```bash
curl -X POST https://your-api-url/api/interpret \
  -H "Content-Type: application/json" \
  -d '{
    "lab_values": [
      {
        "name": "Hemoglobin",
        "value": 14.5,
        "unit": "g/dL",
        "reference_min": 12.0,
        "reference_max": 17.5
      },
      {
        "name": "Glucose",
        "value": 105,
        "unit": "mg/dL",
        "reference_min": 70,
        "reference_max": 100
      }
    ]
  }'
```

### Response

```json
{
  "results": [
    {
      "name": "Hemoglobin",
      "value": 14.5,
      "unit": "g/dL",
      "severity": "normal",
      "explanation": "Hemoglobin carries oxygen in your blood. Your level of 14.5 g/dL is within the healthy range, indicating good oxygen-carrying capacity.",
      "citation": "https://www.mayoclinic.org/tests-procedures/hemoglobin-test/about/pac-20385075"
    },
    {
      "name": "Glucose",
      "value": 105,
      "unit": "mg/dL",
      "severity": "borderline",
      "explanation": "Blood glucose measures sugar levels. Your fasting level of 105 mg/dL is slightly above normal (100 mg/dL). This may indicate prediabetes - discuss with your healthcare provider.",
      "citation": "https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis"
    }
  ],
  "disclaimer": "This information is educational only. Always consult a healthcare provider for medical advice.",
  "summary": "1 of 2 values require attention. Consider discussing the borderline glucose with your doctor."
}
```

---

## Development Metrics

| Metric | Value |
|--------|-------|
| Planning Time | ~15 minutes |
| Implementation Time | TBD |
| Lines of Python | TBD |
| Lines of Tests | TBD |
| Test Coverage | TBD% |
| Subtasks Completed | 0/17 |

---

## The DevPlan Methodology

This project demonstrates structured AI-assisted development:

1. **Brief First**: Capture requirements before writing code
2. **Plan in Detail**: Break work into explicit, testable subtasks
3. **Standards Matter**: Consistent code quality through defined rules
4. **Document the Journey**: Every decision captured for learning

The approach works because AI assistants (like Claude Code) excel at:
- Following explicit instructions
- Maintaining consistency across sessions
- Completing well-defined tasks

But struggle with:
- Ambiguous requirements
- Architectural decisions without context
- Maintaining coherence over long projects

DevPlan bridges this gap by front-loading the thinking, then letting AI execute methodically.

---

## License

GNU GPL v3 - See [LICENSE](LICENSE)

---

## Disclaimer

⚠️ **LabBot is for educational purposes only.** It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider about your lab results.

---

*Built with the DevPlan methodology - from idea to deployment in structured steps.*
