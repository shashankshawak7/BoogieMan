# 👹 The BoogieMan — The Mythic Reaper of Tech Debt

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Zero Bloat](https://img.shields.io/badge/Dependencies-Zero--Bloat_REST-10B981?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Offline Local AI](https://img.shields.io/badge/Local_AI-LM_Studio_%7C_Ollama-F59E0B?style=for-the-badge&logo=ollama&logoColor=white)](#)
[![PDF Generation](https://img.shields.io/badge/Exports-Binary_PDF_%26_Markdown-6366F1?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](#)

<br/>

**"Code is a liability, not an asset. Debts must be paid."**

*An ancient mythic phantom lurking in the shadows of over-engineering.*  
*Dismantling bloated architectures, resume-driven frameworks, speculative abstractions, and enterprise buzzwords.*

---

[🚀 Quickstart](#-quickstart--installation) • 
[🎯 Two Ways to Use](#-two-operational-modes) • 
[⚙️ AI Setup](#%EF%B8%8F-ai-engine-configuration) • 
[🔍 Features & Ingestion](#-target-contract-ingestion) • 
[👔 Dual Tone Modes](#-dual-delivery-modes) • 
[💬 Multi-Turn Chat & Synthesis](#-multi-turn-interrogation--discussion-synthesis) • 
[⬇️ PDF & Markdown Exports](#%EF%B8%8F-export--reporting-suite) • 
[📖 Example Roasts](#-real-world-examples)

</div>

---

## 📖 The Folkloric Persona & Philosophy

In modern software development, teams build colossal towers of complexity—twenty microservices to do what one SQLite database can do, distributed message brokers for three daily requests, and AI agent swarms inside trench coats.

**The BoogieMan** is the ancient folkloric reckoning hiding under the desks of resume-driven developers and buzzword architects. He is the hyper-pragmatic, battle-hardened Principal Architect who refuses to build things that do not need to exist.

### The Pre-Acceptance Gauntlet
Before evaluating any implementation, line of code, or architecture proposal, The BoogieMan runs it through five lethal tests:
1. **The Delete Test:** Can this system be deleted entirely without paying customers leaving?
2. **The Framework Test:** Does the framework, language standard library, or operating system already do this natively?
3. **The Database Test:** Can a single SQL query, index, constraint, or view replace 500 lines of application loops?
4. **The Cloud / OS Test:** Can a cron job, a shell command (`grep`, `curl`, `awk`), or a cloud primitive handle this?
5. **The 3:00 AM Test:** Will a sleep-deprived junior on-call engineer be able to debug this five years from now when the author has fled the company?

### The Mandatory 6-Part Evaluation Template
Every evaluation—whether delivered as a folkloric roast or a formal boardroom advisory memo—strictly adheres to this rigorous engineering template:
1. **Executive Summary & Reality Check:** Stripping away buzzwords to define the core proposal.
2. **Ruthless Elimination:** Specific components, endpoints, microservices, and layers to delete or merge immediately.
3. **Offloading & Delegation:** Offloading logic to SQL, standard libraries, or static configuration.
4. **Violation Analysis:** Auditing YAGNI, KISS, DRY, and Resume-Driven Development (RDD) sins.
5. **Financial & Operational Impact:** Estimating maintenance burden, technical debt accumulation, and on-call risk.
6. **Action Plan & Final Recommendation:** Ordered refactoring roadmap and definitive verdict (**REJECT**, **DESTRUCTIVE REFACTOR**, or **ACCEPT WITH CAVEATS**).

---

## 🎯 Two Operational Modes

You can run The BoogieMan in two distinct workflows:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        THE BOOGIEMAN ECOSYSTEM                         │
├───────────────────────────────────┬────────────────────────────────────┤
│   MODE 1: ZERO-UI IN-IDE AGENT    │    MODE 2: INTERACTIVE PLATFORM    │
│   • Cursor (.cursorrules)         │    • Full Streamlit Web Server     │
│   • GitHub Copilot (instructions) │    • Multi-Format File Extractor   │
│   • Claude Code / Antigravity     │    • Live PR Diff Ingestion        │
│   • 1-Click Copy-Paste Setup      │    • Multi-Turn Chat & PDF Exports │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Mode 1: Zero-UI In-IDE Agent (Cursor, Copilot, Antigravity)
Drop The BoogieMan's brain directly into your repository. Your AI coding assistants will immediately adopt his ruthless architectural discipline:

* **For Cursor:** Copy [boogieMan.md](boogieMan.md) to `.cursorrules` in your project root:
  ```bash
  cp boogieMan.md /path/to/your/project/.cursorrules
  ```
* **For GitHub Copilot:** Place it in `.github/copilot-instructions.md`:
  ```bash
  mkdir -p /path/to/your/project/.github
  cp boogieMan.md /path/to/your/project/.github/copilot-instructions.md
  ```
* **For Claude Code / Antigravity / Gemini:**
  Include [boogieMan.md](boogieMan.md) in your system prompt or workspace `GEMINI.md` / `CLAUDE.md`.

*(Tip: In the Streamlit UI, the **"BoogieMan Integration"** tab provides 1-click installer buttons!)*

---

### Mode 2: Interactive Web Server & CLI Platform

Run the dedicated web portal with live socket probing, document parsers, multi-turn interrogation chat, and PDF generation.

---

## 🚀 Quickstart & Installation

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/project_AI.git
cd project_AI

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install Zero-Bloat Dependencies
No heavy agent frameworks (LangChain, CrewAI, AutoGen) are used. Only lightweight, battle-tested utilities:
```bash
pip install -r requirements.txt
```
*Dependencies:* `streamlit`, `httpx`, `pypdf`, `python-docx`, `openpyxl`, `fpdf2`, `rich`, `python-dotenv`.

### 3. Launch the Web Server
```bash
python -m streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

### 4. Or Run the Headless Terminal CLI
```bash
# Roast a text idea
python boogie.py --idea "Building a distributed microservice for user signups"

# Interrogate an RFP or Roadmap file
python boogie.py --rfp path/to/proposal.pdf
python boogie.py --roadmap path/to/q3_roadmap.xlsx

# Roast uncommitted git changes
python boogie.py --git-diff

# Audit a public or private GitHub PR
python boogie.py --pr https://github.com/organization/repo/pull/42
```

---

## ⚙️ AI Engine Configuration

The BoogieMan platform features **isolated configuration** with zero state bleeding between providers. Each engine's settings are saved independently in `.boogie_config.json`.

| Engine | Type | Default Endpoint | API Key Required? |
| :--- | :--- | :--- | :--- |
| **LM Studio** | Local (Offline) | `http://127.0.0.1:1234/v1` | ❌ No (Optional) |
| **Ollama** | Local (Offline) | `http://127.0.0.1:11434` | ❌ No (Optional) |
| **Google Gemini** | Cloud API | Native REST | ✅ Yes (Gemini API Key) |
| **OpenAI** | Cloud API | `https://api.openai.com/v1` | ✅ Yes (OpenAI API Key) |
| **Groq** | Cloud Fast LPU | `https://api.groq.com/openai/v1` | ✅ Yes (Groq API Key) |
| **Anthropic Claude** | Cloud API | Native REST | ✅ Yes (Anthropic API Key) |
| **Azure OpenAI** | Enterprise Cloud | Custom Resource URL | ✅ Yes (Azure Key + Deployment) |

### Real-Time Socket Probing: "Lock Engine" & "Check Live"
* **Check Live (🔄):** Probes the underlying socket/endpoint (e.g. `/v1/models` for LM Studio, `/api/tags` for Ollama) and immediately reports latency and model availability with visual green/slate indicators in the sidebar.
* **Lock Engine (💾):** Saves the selected provider and credentials as your active default.
* **Zero UI Lag:** Probes are cached so navigating between tabs and document types occurs instantaneously with 0ms delay.

---

## 🔍 Target Contract Ingestion

The BoogieMan can interrogate virtually any technical artifact:

### 1. 💡 Architecture & Startup Pitches
Paste raw ideas, whiteboard designs, or buzzword-heavy concepts. Ideal for testing whether a project is a legitimate product or "three shell scripts stacked inside a Kubernetes cluster."

### 2. 📑 Enterprise RFPs (Request for Proposal)
Upload **PDF**, **Word (.docx)**, **Excel (.xlsx)**, or Markdown documents. Exposes:
* Hidden vendor lock-in traps
* Unmeasurable SLAs and compliance theatre
* Vaguely scoped deliverables designed for change-order extortion

### 3. 🗺️ Product & Tech Roadmaps
Upload **Excel (.xlsx)**, **CSV**, **Word (.docx)**, or **PDF** roadmap schedules. Exposes:
* Feature-factory delusion
* Complete lack of technical debt amortization
* Unrealistic timelines and speculative scaling

### 4. 📋 Business Analyst (BA) Requirements Specs (PRDs)
Upload user stories, acceptance criteria, and workflow specs. Strips:
* Circular business logic
* Vanity metrics
* Over-specified edge cases that will never execute in production

### 5. 📄 Architecture & Source Code Files
Inspect `.py`, `.ts`, `.js`, `.go`, `.rs`, `.java`, `.sql`, `.yaml`, `.json` files. Audits god-classes, leaky abstractions, and over-engineered inheritance trees.

### 6. 🔍 Git Diffs (Local & Remote PRs)
* **Local Workspace Diff:** Audits uncommitted staged or unstaged Git changes in your working tree.
* **Remote Pull Requests & Branches:** Paste any GitHub/GitLab PR or branch comparison link.
  * **Public PRs:** Ingested instantly with zero authentication.
  * **Private Repositories:** Prompts for Username and Personal Access Token (PAT) only when encountering HTTP 401/404 restrictions.

---

## 👔 Dual Delivery Modes

Toggle delivery tone effortlessly in the main dashboard:

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│     👹 THE BOOGIEMAN (FOLKLORIC)      │      👔 EXECUTIVE ADVISORY AUDIT      │
├───────────────────────────────────────┼───────────────────────────────────────┤
│ • Biting, cynical, satirical humor    │ • Polished, diplomatic C-suite prose  │
│ • Punctures hype balloons with wit    │ • Capital efficiency & TCO metrics    │
│ • Unfiltered, brutal engineering truth│ • Risk exposure & board presentation  │
│ • "Delete this before sunrise"        │ • "Recommend decommissioning phase 1" │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

### ⚡ 1-Click Transmutation
Generated a satirical roast and need to present it to your CTO, VP, or Board of Directors?  
Click **"👔 Transmute to Formal Boardroom Report"**. The system retains every single technical elimination and architectural finding while converting the prose into an objective, data-grounded C-suite advisory memo.

---

## 💬 Multi-Turn Interrogation & Discussion Synthesis

The review doesn't end with a single verdict. After summoning The BoogieMan:

1. **Continue the Conversation:** Use the interactive chat input at the bottom of the evaluation dossier to ask follow-up questions:
   * *"How can I replace Kafka with Postgres in this specific design?"*
   * *"What are the trade-offs if we keep the cache layer?"*
   * *"Give me the absolute simplest architecture that satisfies these 3 requirements."*
2. **Context-Aware Responses:** The agent maintains full conversational memory and stays in your chosen persona (satirical veteran or executive consultant).
3. **Synthesize Full Discussion:** Click **"👔 Transmute Full Discussion to Executive Report"** to consolidate the original target, initial verdict, and all subsequent Q&A into a unified, formal advisory report ready for stakeholders.

---

## ⬇️ Export & Reporting Suite

Never lose an architectural review. Built-in export tools include:

* **⬇️ Export as PDF Report:** Builds an executive-grade binary PDF using `fpdf2`, featuring custom running headers, page numbering (`Page X of Y`), clean typographic hierarchy, and sanitized character encoding.
* **⬇️ Export as Markdown (.md):** Downloads the raw markdown report for inclusion in documentation repos or PR summaries.
* **📁 Historical Records:** Past reviews are saved to the `roasts/` directory with timestamps and can be re-downloaded at any time from the sidebar.

---

## 📖 Real-World Examples

### Example 1: Buzzword Startup Pitch (Folkloric Mode)

**Input:**
> *"We are building an AI-powered resume screening platform. We use Kafka to stream incoming resumes, a vector database with 1536-dimensional embeddings, 8 autonomous AI agents using LangChain to debate each applicant, and deploy it on Kubernetes across 3 multi-cloud regions."*

**The BoogieMan's Verdict:**

#### 1. Executive Summary & Reality Check
> This is not an architecture; it is an involuntary cry for help disguised as an AWS invoice. You have built a 14-gear Rube Goldberg contraption to perform basic keyword filtering on PDF files that 99% of recruiters glance at for six seconds.

#### 2. Ruthless Elimination
* **Execute Immediately:** Delete Kafka. Delete 7 of the 8 "debating" agents. Delete multi-cloud Kubernetes.
* **Merge:** Merge the "agent debate" into a single deterministic prompt or standard regex parser.
* **Simplify:** Replace the vector database with PostgreSQL Full-Text Search (`tsvector`) and a `GIN` index.

#### 3. Offloading & Delegation
* **Database Offloading:** Postgres handles PDF text search in 4 milliseconds without external vector servers.
* **OS / Stdlib:** A single background worker (`asyncio` or `Celery`) reading from a Postgres queue replaces Kafka.

#### 4. Violation Analysis & Roast
* **YAGNI Violations:** Multi-cloud Kubernetes for a platform that currently has zero paying customers.
* **Resume-Driven Development (RDD):** LangChain "agent debates" designed to farm Twitter/LinkedIn engagement rather than deliver reliable parsing.

#### 5. Financial & Operational Horror Show
* **Monthly Token Burn:** ~$4,200/month just for agents to hallucinate arguments over candidate GPAs.
* **Maintenance Burden:** High. At least 3 distributed failures per week when Kafka consumer groups rebalance unexpectedly.

#### 6. Action Plan & Recommendation
* **Roadmap:**
  1. Drop Kubernetes. Deploy a single container on a managed PaaS (Fly.io, Render, AWS ECS).
  2. Replace Kafka with a Postgres table `status = 'PENDING' SKIP LOCKED`.
  3. Strip the 8 agents down to one deterministic evaluation call.
* **Final Verdict:** **DESTRUCTIVE REFACTOR**

---

### Example 2: Transmuted Executive Advisory Memo (Boardroom Mode)

**The Same Verdict After 1-Click Transmutation:**

#### 1. Strategic Summary & Capital Allocation
> The proposed technical roadmap reflects premature architectural complexity that disproportionality increases Total Cost of Ownership (TCO) prior to revenue validation. The infrastructure footprint can be reduced by 85% while meeting all customer throughput requirements.

#### 2. Infrastructure Rationalization
* **Decommission:** Distributed messaging queue (Kafka) and multi-region Kubernetes clusters.
* **Consolidation:** Standardize data storage and indexing on existing enterprise PostgreSQL instances.
* **Optimization:** Replace speculative multi-agent consensus logic with single-pass deterministic evaluation.

#### 3. Financial & Operational Risk
* **Cost Amortization:** Current architecture incurs unnecessary infrastructure overhead of ~$4,200/month in compute and API consumption.
* **SLA Risk:** High operational surface area with 5 distinct failure points across asynchronous pipelines.

#### 4. Strategic Recommendation
* **Final Verdict:** **RESTRUCTURE PRIOR TO CAPITAL EXPENDITURE**

---

## 🛡️ License & Principles

Released under the **MIT License**.  
Free for individual developers, enterprise engineering teams, and anyone who wants to prevent 3:00 AM on-call disasters.
