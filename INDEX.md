# Documentation Navigation Guide

Welcome to the Myanmar-English Bilingual RAG Pipeline documentation!

## 📍 Where to Start?

### For First-Time Users (College Edition)

1. **Start here** → `README_COLLEGE.md`
   - Project overview
   - Key features
   - Quick start guide

2. **Then read** → `QUICK_START.md`
   - 5-minute setup
   - Step-by-step instructions
   - Prerequisites

3. **If you get stuck** → `SETUP.md`
   - Detailed installation
   - Troubleshooting guide
   - Common issues

### For Using the Pipeline

1. **Running queries** → `QUERY_GUIDE.md`
   - Interactive mode
   - Example queries
   - Language support

2. **Adding documents** → `SAMPLE_DATA.md`
   - Document requirements
   - Finding good documents
   - Testing your documents

### For Development

1. **Architecture overview** → `plan.md`
   - System design
   - Technical details
   - Component interactions

2. **Contributing code** → `CONTRIBUTING.md`
   - Setup for developers
   - Code guidelines
   - PR process

## 📚 Complete Documentation Map

### Core Documentation (You Should Read)

```
START HERE
    ↓
README_COLLEGE.md ←── Project overview & features
    ↓
QUICK_START.md ←──── 5-minute setup
    ↓
SETUP.md ←────────── Detailed installation
    ↓
EXECUTION_GUIDE.md ← Step-by-step usage
    ↓
QUERY_GUIDE.md ←────  Interactive querying
    ↓
SAMPLE_DATA.md ←───── Adding documents
```

### Advanced Documentation (As Needed)

```
plan.md ←─────────── Architecture & design
CONTRIBUTING.md ←── Development guide
INDEX.md ←────────── Documentation index
```

## 🎯 Documentation by Topic

### Getting Started

| Document            | Purpose             | Time   |
| ------------------- | ------------------- | ------ |
| `README_COLLEGE.md` | Overview & features | 10 min |
| `QUICK_START.md`    | Fast setup          | 5 min  |
| `SETUP.md`          | Detailed install    | 15 min |

### Using the Pipeline

| Document             | Purpose            | Time   |
| -------------------- | ------------------ | ------ |
| `EXECUTION_GUIDE.md` | Step-by-step usage | 20 min |
| `QUERY_GUIDE.md`     | Interactive mode   | 10 min |
| `SAMPLE_DATA.md`     | Add documents      | 15 min |

### Understanding the System

| Document            | Purpose          | Time   |
| ------------------- | ---------------- | ------ |
| `plan.md`           | Architecture     | 30 min |
| `CONTRIBUTING.md`   | Development      | 20 min |

## 🔍 Find Information By Topic

### Installation & Setup

- **Quick setup** → `QUICK_START.md`
- **Detailed setup** → `SETUP.md`
- **Troubleshooting** → `SETUP.md` (Troubleshooting section)
- **Dependencies** → `QUICK_START.md` (Prerequisites)
- **Configuration** → `.env.example` file

### Running the Pipeline

- **First run** → `EXECUTION_GUIDE.md`
- **Interactive querying** → `QUERY_GUIDE.md`
- **Step-by-step** → `EXECUTION_GUIDE.md`
- **Example commands** → `QUICK_START.md`

### Adding Documents

- **Where to place** → `SAMPLE_DATA.md`
- **What type to use** → `SAMPLE_DATA.md` (Document Quality section)
- **Finding documents** → `SAMPLE_DATA.md` (Recommended Documents)
- **Testing quality** → `SAMPLE_DATA.md` (Testing section)

### Document Management

- **Where to place** → `SAMPLE_DATA.md`
- **What type to use** → `SAMPLE_DATA.md` (Document Quality section)
- **Finding documents** → `SAMPLE_DATA.md` (Recommended Documents)
- **Testing quality** → `SAMPLE_DATA.md` (Testing section)

- **System overview** → `plan.md`
- **Components** → `plan.md` (System Architecture)
- **Bilingual support** → `plan.md` (Design Principles)
- **Data flow** → `README_COLLEGE.md` (Architecture diagram)

### Contributing & Development

- **Development setup** → `CONTRIBUTING.md`
- **Code style** → `CONTRIBUTING.md` (Code Style section)
- **Testing** → `CONTRIBUTING.md` (Testing section)
- **PR process** → `CONTRIBUTING.md` (Pull Request section)

### Troubleshooting

- **Installation issues** → `SETUP.md`
- **API key problems** → `SETUP.md` & `QUERY_GUIDE.md`
- **Connection errors** → `QUERY_GUIDE.md` (Troubleshooting)
- **Unicode/encoding** → `SAMPLE_DATA.md` (Troubleshooting)

## 💡 Common Questions

### "How do I get started?"

→ Read `QUICK_START.md` (5 minutes)

### "I need detailed setup help"

→ Read `SETUP.md` (includes troubleshooting)

### "How do I use the pipeline?"

→ Read `EXECUTION_GUIDE.md` or `QUERY_GUIDE.md`

### "How do I add documents?"

→ Read `SAMPLE_DATA.md`

### "How does the system work?"

→ Read `plan.md`

### "How do I contribute?"

→ Read `CONTRIBUTING.md`

### "Where can I find troubleshooting help?"

→ Check `SETUP.md` or `QUERY_GUIDE.md`

## 📋 File Quick Reference

### Quick Links

```
.env.example        ← Copy to .env and add API keys
main.py             ← Core RAG pipeline (don't modify without understanding)
pyproject.toml      ← Dependencies list
data/               ← Place your PDF files here
```

### Documentation Files

```
README_COLLEGE.md   ← Start here for college edition
QUICK_START.md      ← 5-minute setup
SETUP.md            ← Detailed setup + troubleshooting
EXECUTION_GUIDE.md  ← How to use step-by-step
QUERY_GUIDE.md      ← How to query the system
SAMPLE_DATA.md      ← How to add documents
plan.md             ← Technical architecture
CONTRIBUTING.md     ← Development guide
INDEX.md            ← This file
.gitignore          ← Git ignore rules
AGENTS.md           ← From project root
```

## 🚀 Quick Start Paths

### Path 1: Get Running in 5 Minutes

1. `QUICK_START.md` - Follow prerequisites & setup
2. Add PDFs to `data/`
3. Run: `uv run python main.py`
4. Start querying!

### Path 2: Full Understanding (30 Minutes)

1. `README_COLLEGE.md` - Understand what this is
2. `SETUP.md` - Detailed setup
3. `plan.md` - Understand architecture
4. `EXECUTION_GUIDE.md` - Learn to use
5. Ready to customize!

### Path 3: Add Good Documents (15 Minutes)

1. `SAMPLE_DATA.md` - Learn what makes good docs
2. Find documents from suggested sources
3. Place in `data/` folder
4. `QUERY_GUIDE.md` - Test your documents
5. Refine document selection

### Path 4: Contribute Code (1 Hour)

1. `CONTRIBUTING.md` - Development guidelines
2. `QUICK_START.md` - Setup dev environment
3. `plan.md` - Understand architecture
4. Make your changes
5. Submit PR!

## 📞 Need Help?

### Documentation Search

- Use Ctrl+F to search within docs
- Check this INDEX for topic keywords
- Review Troubleshooting sections

### Common Issues

**Can't find API key?**
→ See `SETUP.md` → Prerequisites section

**Connection refused?**
→ See `QUERY_GUIDE.md` → Troubleshooting section

**Unsure what to do?**
→ Start with `QUICK_START.md` or `README_COLLEGE.md`

## 🎓 For College Instructors

### Teaching with This Project

1. **Setup** - Have students follow `QUICK_START.md`
2. **Understanding** - Discuss `plan.md` architecture
3. **Experiment** - Have students test accuracy with different documents
4. **Contribute** - Invite students to enhance features via `CONTRIBUTING.md`

### Assessment Ideas

- Document selection quality (see `SAMPLE_DATA.md`)
- Code contributions (follow `CONTRIBUTING.md`)
- System understanding and deployment
- Presentation of findings

## 📊 Document Statistics

| Document           | Length    | Read Time | Difficulty |
| ------------------ | --------- | --------- | ---------- |
| README_COLLEGE.md  | Long      | 10 min    | Easy       |
| QUICK_START.md     | Short     | 5 min     | Easy       |
| SETUP.md           | Long      | 15 min    | Easy       |
| EXECUTION_GUIDE.md | Long      | 20 min    | Medium     |
| QUERY_GUIDE.md     | Medium    | 10 min    | Medium     |
| SAMPLE_DATA.md     | Long      | 15 min    | Medium     |
| plan.md            | Very Long | 30 min    | Hard       |
| CLEANUP_REPORT.md  | Medium    | 10 min    | Easy       |
| CONTRIBUTING.md    | Long      | 20 min    | Medium     |

## ✅ Recommended Reading Order

### Absolute Minimum (15 min)

1. `README_COLLEGE.md` (5 min) - What is this?
2. `QUICK_START.md` (5 min) - How to setup?
3. `QUERY_GUIDE.md` (5 min) - How to use?

### Recommended (45 min)

1. `README_COLLEGE.md` (5 min)
2. `QUICK_START.md` (5 min)
3. `SETUP.md` (15 min)
4. `EXECUTION_GUIDE.md` (10 min)
5. `QUERY_GUIDE.md` (5 min)
6. `SAMPLE_DATA.md` (5 min)

### Complete (2+ hours)

Read all documentation plus:

- Review `main.py` code
- Review `test_accuracy.py` code
- Run the system end-to-end
- Try accuracy tests
- Experiment with documents

---

**Happy learning! 🚀**

Start with `README_COLLEGE.md` or `QUICK_START.md` depending on how much time you have.
