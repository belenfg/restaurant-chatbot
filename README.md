# Restaurant Chatbot

A Python-based restaurant chatbot system for managing reservations, answering FAQs, and maintaining contextual conversations using OpenAI or Anthropic (Claude).

## 🔧 Features

- Natural conversation for bookings, menu, and info.
- OpenAI and Anthropic AI integration.
- Graceful fallback to rule-based logic.
- Persistent storage of customer and reservation data.

## 🚀 Getting Started

### 1. Clone and Install

```bash
git clone https://github.com/belenfg/restaurant-chatbot
cd restaurant-chatbot
pip install -r requirements.txt
```

### 2. Set Up Environment

Rename `.env.example` to `.env` and fill your API keys:

```bash
cp .env.example .env
```

### 3. Run the Chatbot

```bash
python main.py
```

## 🧪 Running Tests

Tests are written with `pytest`. To run them:

```bash
pytest tests/
```

## 🗂️ Project Structure

The project follows a modular structure with separate files for entry point, chatbot logic, AI integration, and tests.

- `main.py`: Entry point
- `.env`: Configuration for API keys (excluded via `.gitignore`)
- `tests/`: Unit tests using `pytest`

For a full list of files and responsibilities, refer to the inline comments in each module.

## 📝 Notes

- The chatbot supports AI responses but works without them.
