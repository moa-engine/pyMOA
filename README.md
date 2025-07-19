# pyMOA 🌐

**pyMOA** is a free and open source Python library that implements the MOA metasearch engine as a clean and easy-to-use client for Python. It allows you to seamlessly integrate web search into your Python programs.

The project is currently in alpha development, so there is no pre-built package.



## 🔍 Key Features

- **Privacy First**  
  No user data is stored or tracked during searches.

- **Metasearch Support**  
  Utilizes MOA under the hood to fetch and combine results from multiple search engines simultaneously.

- **Ad-free Search Results**  
  Clean, clutter-free search responses.

- **Open-source under GPL‑3.0 License**  
  Use, modify, and distribute freely under GPL‑3.0 terms.


## Install from pypi

```bash
pip install moa-engine
```
**⚠️ The package name is different in pypi. They will be the same in the next version. Use the name moa-engine in the following examples.**

### 🛠️ Build & Install from Source

1. Clone the repository:

```bash
git clone https://github.com/moa-engine/pyMOA.git
cd pyMOA
```

2. (Optional but recommended) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Build the package:

```bash
python -m build
```

5. Install the wheel package:

```bash
pip install dist/pyMOA-0.1.0-py3-none-any.whl
```

> Replace the filename if the version changes.

---

### ✅ Usage Example

```python
from pyMOA import search

results = search(
    q="privacy search engine",
    lang="en",
    country="us",
    engine=None,         # Optional: specify engines like ["google", "duckduckgo"]
    page=1,
    safesearch=1,        # 0: off, 1: moderate, 2: strict
    time_range=None,     # One of ["day", "week", "month", "year"]
    size=5               # Max number of results per engine
)

print(results)
```



Let me know if you also want to add error handling or CLI usage examples.


## 🤝 Contributing

- Open an Issue to report bugs or request new features  
- Submit a Pull Request to add functionality, improve tests, or update documentation



## 📄 License

Distributed under the **GPL‑3.0** License. You are free to use, modify, and redistribute this library, provided modified source is also shared.
