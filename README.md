# Simple Patent Search

A streamlined, modular patent search tool that combines OpenAI API patent discovery with title similarity verification. This project provides a simple alternative to complex LangGraph-based solutions while maintaining accuracy and reliability.

## Overview

This tool implements a two-step process:

1. **Patent Discovery**: Uses OpenAI GPT-4.1 with web search to find relevant patents for chemical compound synthesis
2. **Title Verification**: Scrapes actual patent titles from Google Patents and uses similarity matching to verify accuracy

## Features

- 🔍 **OpenAI-powered search**: Leverages GPT-4.1 with web search capabilities
- ✅ **Title verification**: 80% similarity threshold for accuracy
- 🌐 **Multi-language support**: Handles Chinese, Japanese, Korean patents with language notes
- 📊 **Comprehensive saving**: Saves ALL patents regardless of similarity score
- 📁 **Organized output**: Results saved in compound-specific directories
- 🚀 **Simple & modular**: Each file under 100 lines, easy to understand
- ⚡ **Real-time saving**: Patents saved immediately upon verification
- 🛡️ **Error handling**: Robust error handling and retry logic
- 🔍 **Title validation**: Prevents abstracts from being mistaken for titles

## Project Structure

```
simple_patent_search/
├── main.py                 # Entry point (< 100 lines)
├── patent_search.py        # OpenAI patent search (< 100 lines)
├── title_verification.py   # Title similarity verification (< 100 lines)
├── config.py              # Configuration settings (< 100 lines)
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

## Usage

### Command Line
```bash
python main.py "3-(trifluoromethyl)pyridine-4-carboxamide"
```

### Programmatic Usage
```python
from main import run_patent_search

results = run_patent_search("3-(trifluoromethyl)pyridine-4-carboxamide")
print(f"Found {results['patents_verified']} verified patents")
```

## Configuration

Edit `config.py` to customize:

- `OPENAI_MODEL`: OpenAI model to use (default: "gpt-4.1")
- `MAX_PATENTS`: Maximum patents to search for (default: 20)
- `SIMILARITY_THRESHOLD`: Title similarity threshold (default: 0.8)
- `REQUEST_DELAY`: Delay between web requests (default: 2 seconds)

## Output Format

Results are saved to `results/{compound_name}/verified_patents.json`:

```json
{
  "compound": "3-(trifluoromethyl)pyridine-4-carboxamide",
  "verified_patents": [
    {
      "patent_id": "WO2015051141A1",
      "title": "Methods for preparation of fluorinated sulfur-containing compounds",
      "relevancy": "High - Direct synthesis method described",
      "similarity_score": 0.95,
      "verified": true
    },
    {
      "patent_id": "CN101052619B",
      "title": "制备4-{4-[({[4-氯-3-(三氟甲基)苯基]氨基}羰基)氨基]苯氧基}-n-甲基吡啶-2-甲酰胺的方法",
      "relevancy": "High - Direct synthesis method",
      "similarity_score": 0.274,
      "verified": false,
      "language_note": "Non-English title - similarity may be affected by language"
    }
  ]
}
```

## Example Output

```
🚀==============================================================
🚀 SIMPLE PATENT SEARCH STARTING
🚀==============================================================
🧪 Compound: 3-(trifluoromethyl)pyridine-4-carboxamide
🎯 Max patents: 20
📊 Similarity threshold: 0.8
🤖 Model: gpt-4.1
======================================================================

==================================================
STEP 1: PATENT SEARCH
==================================================
🔍 Searching for patents related to: 3-(trifluoromethyl)pyridine-4-carboxamide
🤖 Calling OpenAI API...
✅ Received response (2847 characters)
📋 Found 8 patents

==================================================
STEP 2: TITLE VERIFICATION
==================================================
🔍 Verifying 8 patents...
📋 Verifying patent 1/8: WO2015051141A1
📊 Title similarity: 0.950
✅ Patent WO2015051141A1 verified (similarity: 0.950)
💾 Saved patent WO2015051141A1 to results/3-trifluoromethylpyridine-4-carboxamide/verified_patents.json

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
SEARCH COMPLETE
🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
📋 Patents found: 8
✅ Patents verified: 6
📊 Success rate: 75.0%
💾 Results saved to: results/3-trifluoromethylpyridine-4-carboxamide/verified_patents.json
```

## Architecture

The tool follows a simple, linear workflow:

```
Input Compound → OpenAI Search → Title Verification → Save Results
```

### Components

1. **PatentSearcher** (`patent_search.py`)
   - Uses OpenAI GPT-4.1 with web search tools
   - Builds structured prompts for patent discovery
   - Returns JSON-formatted patent data

2. **TitleVerifier** (`title_verification.py`)
   - Scrapes Google Patents for actual titles
   - Calculates similarity using SequenceMatcher
   - Saves verified patents immediately

3. **Config** (`config.py`)
   - Centralized configuration management
   - Environment variable handling
   - Output path generation

## Error Handling

- API failures are caught and logged
- Web scraping includes retry logic
- Invalid JSON responses are handled gracefully
- Missing environment variables are validated

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web scraping

## License

This project is provided as-is for educational and research purposes.
