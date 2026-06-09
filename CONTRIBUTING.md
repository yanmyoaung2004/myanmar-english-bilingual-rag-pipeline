# Contributing Guidelines

Thank you for your interest in contributing to the Myanmar-English Bilingual RAG Pipeline!

## Development Setup

### 1. Fork & Clone
```bash
git clone https://github.com/your-fork/rag.git
cd rag
```

### 2. Create Virtual Environment
```bash
# Using uv (recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 3. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

## Code Style

### Python Standards
- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and small

### Naming Conventions
```python
# Functions: snake_case
def calculate_token_count(text: str) -> int:

# Classes: PascalCase
class RAGAccuracyTester:

# Constants: UPPER_SNAKE_CASE
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
```

### Docstring Format
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Detailed explanation if needed, including any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When input is invalid
    """
    pass
```

## Testing

### Run Accuracy Tests
```bash
uv run python test_accuracy.py
```

### Expected Output
```
======================================================================
RAG PIPELINE ACCURACY TEST SUITE
======================================================================

Total Tests Run: 4
Average Precision: [XX]%
[OK/WARN] Overall Accuracy Rating: [RATING]
```

### Manual Testing
```bash
uv run python main.py
# Test with various queries:
# > What is the main topic?
# > Tell me about the content
# > Summarize the documents
```

## Commit Guidelines

### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (no logic change)
- **refactor**: Code refactoring
- **test**: Test additions/modifications
- **chore**: Build, dependencies, etc.

### Examples
```
feat: Add support for DOCX files

- Implement DOCX loader
- Update document processor
- Add tests for new format

Resolves #42
```

```
fix: Handle Unicode errors in Myanmar text

- Fix charmap encoding issue
- Add UTF-8 encoding verification
- Improve error messages

Fixes #38
```

## Types of Contributions

### 🐛 Bug Fixes
1. Create issue describing the bug
2. Fork repository
3. Create branch: `fix/description`
4. Make changes
5. Run tests: `python test_accuracy.py`
6. Submit PR with clear description

### ✨ New Features
1. Discuss in issues first (for major features)
2. Create branch: `feature/description`
3. Implement with tests
4. Update documentation
5. Run accuracy tests
6. Submit PR

### 📚 Documentation
1. Create branch: `docs/description`
2. Update relevant `.md` files
3. Add examples if applicable
4. Verify formatting
5. Submit PR

### 🧪 Tests & Optimization
1. Create branch: `test/description`
2. Add or improve test cases
3. Ensure tests pass
4. Document test coverage
5. Submit PR

## Areas for Contribution

### High Priority
- [ ] Add DOCX/DOCM document support
- [ ] Implement Myanmar text preprocessing
- [ ] Add web UI (Streamlit/FastAPI)
- [ ] Improve accuracy testing suite

### Medium Priority
- [ ] Add support for more languages
- [ ] Implement caching layer
- [ ] Add document metadata extraction
- [ ] Create CLI interface

### Low Priority
- [ ] Performance optimizations
- [ ] Code refactoring
- [ ] Additional documentation
- [ ] Configuration presets

## Pull Request Process

### Before Submitting
1. ✅ Fork the repository
2. ✅ Create feature branch
3. ✅ Make your changes
4. ✅ Add/update tests
5. ✅ Update documentation
6. ✅ Run accuracy tests: `python test_accuracy.py`
7. ✅ Verify no hardcoded secrets in code

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
- [ ] Accuracy tests pass
- [ ] Manual testing done
- [ ] New tests added

## Documentation
- [ ] README updated
- [ ] Docstrings added
- [ ] Changes documented

## Checklist
- [ ] My code follows PEP 8
- [ ] I've tested the changes
- [ ] No hardcoded secrets
- [ ] Comments added for complex logic
```

### Review Process
1. Code review (maintainers)
2. Accuracy test verification
3. Approval from 1-2 maintainers
4. Merge to main

## Code Review Checklist

When reviewing submissions:
- ✅ Code follows style guide
- ✅ Functionality works correctly
- ✅ Tests included and passing
- ✅ Documentation updated
- ✅ No performance degradation
- ✅ No security issues
- ✅ No hardcoded credentials

## Development Workflow

### File Organization
```
rag/
├── main.py                 # Core RAG pipeline
├── test_accuracy.py        # Testing suite
├── [feature].py            # New feature (optional)
├── docs/                   # Documentation
│   ├── CONTRIBUTING.md
│   └── [other docs].md
└── data/                   # Sample documents
```

### Feature Implementation Example

**Feature: Add DOCX Support**

1. Create branch:
   ```bash
   git checkout -b feature/docx-support
   ```

2. Implement loader:
   ```python
   # In main.py, add:
   from langchain_community.document_loaders import Docx2txtLoader
   
   def load_docx_files(directory: str) -> List[Document]:
       """Load DOCX files from directory."""
       # Implementation...
   ```

3. Update main loader:
   ```python
   def load_documents(directory: str) -> List[Document]:
       docs = []
       docs.extend(load_pdf_files(directory))
       docs.extend(load_docx_files(directory))  # Add this
       return docs
   ```

4. Add tests:
   ```python
   def test_docx_loading():
       # Test implementation...
   ```

5. Run tests:
   ```bash
   uv run python test_accuracy.py
   ```

6. Create PR with clear description

## Performance Guidelines

### Optimization Tips
- Use efficient data structures
- Minimize API calls
- Cache when possible
- Profile before optimizing

### Benchmarking
```python
import time

start = time.time()
# Code to benchmark
elapsed = time.time() - start
print(f"Execution time: {elapsed:.2f}s")
```

## Documentation Guidelines

### Update These Files
1. **README_COLLEGE.md** - User overview
2. **QUICK_START.md** - Quick setup
3. **EXECUTION_GUIDE.md** - Detailed steps
4. **plan.md** - Architecture details
5. **Code comments** - Inline documentation

### Writing Style
- Clear and concise
- Use examples
- Target college/student audience
- Avoid jargon when possible

## Version Control

### Branching Strategy
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches
- `docs/*` - Documentation branches

### Keeping Fork Updated
```bash
git remote add upstream https://github.com/original/rag.git
git fetch upstream
git rebase upstream/main
git push origin main
```

## Issues & Feature Requests

### Creating Issues
Use clear titles:
- ❌ "Bug" → ✅ "Unicode error in Myanmar text processing"
- ❌ "New feature" → ✅ "Add DOCX file support"

Include:
- Description of issue/request
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Screenshots if applicable

### Labeling
- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Docs improvement
- `good first issue` - Good for newcomers
- `help wanted` - Needs assistance

## Community

### Communication
- GitHub Issues - Bug reports & features
- Pull Requests - Code contributions
- Discussions - General questions

### Code of Conduct
- Be respectful and inclusive
- No harassment or discrimination
- Constructive feedback only
- Help newer contributors

## Getting Help

- 📖 Check documentation first
- 🔍 Search existing issues
- 💬 Ask in GitHub Discussions
- 📧 Contact maintainers if needed

## Recognition

Contributors will be recognized:
- Listed in README
- Mentioned in release notes
- Added to Contributors section

## Questions?

- See `README_COLLEGE.md` for overview
- Check `QUICK_START.md` for setup
- Review `plan.md` for architecture
- Consult existing issues for Q&A

---

**Thank you for contributing! 🚀**

We appreciate your help in making this project better for the college community.
