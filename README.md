# Python Project Template

This is a template Python project that provides a basic structure for building Python applications.

## Project Structure

```
.
├── README.md
├── requirements.txt
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Lint code: `flake8`

## License

MIT License 