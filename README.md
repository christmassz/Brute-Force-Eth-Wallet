# Ethereum Wallet Recovery Tool

## Overview
A Python-based tool for recovering Ethereum wallet access using a partially known 24-word BIP-39 mnemonic phrase. Specifically designed for scenarios where:
- 15 words (positions 10-24) are known and fixed in their positions
- 9 words (positions 1-9) are known but their order is uncertain

## Features
- Parallel processing for efficient permutation testing
- Real-time progress tracking with detailed statistics
- Automatic progress saving and recovery
- Comprehensive BIP-39 mnemonic validation
- Support for multiple Ethereum derivation paths
- Test mode with simulated wallet recovery
- Detailed logging and error handling

## Requirements
- Python 3.8+
- Required packages (see `requirements.txt`)

## Installation
1. Clone the repository:
```bash
git clone [repository-url]
cd ethereum-wallet-recovery
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Prepare your input data:
   - 15 known words in positions 10-24
   - 9 known words for positions 1-9 (order unknown)
   - Target Ethereum address

2. Run the recovery tool:
```bash
python src/main.py --target-address 0x... --fixed-words "word10 ... word24" --permutable-words "word1 ... word9"
```

3. Monitor progress:
   - Real-time progress bar shows completion percentage
   - Detailed statistics including estimated time remaining
   - Progress automatically saved every 5 minutes

## Project Structure
```
wallet-recovery/
├── src/
│   ├── __init__.py
│   ├── main.py           # Entry point
│   ├── permutation.py    # Permutation generation
│   ├── validator.py      # Mnemonic validation
│   ├── wallet.py         # Ethereum wallet derivation
│   └── worker.py         # Worker process implementation
├── tests/
│   └── test_*.py         # Unit tests
├── docs/
│   ├── technical_spec.md # Detailed technical specification
│   └── architecture.md   # System architecture documentation
├── requirements.txt
└── README.md
```

## Safety and Security
- All sensitive operations are performed locally
- No data is transmitted over the network
- Progress files are encrypted at rest
- Memory is securely wiped after processing

## Development
- Run tests: `python -m pytest tests/`
- Generate documentation: `make docs`
- Run linting: `flake8 src/ tests/`

## License
MIT License - See LICENSE file for details

## Contributing
See CONTRIBUTING.md for guidelines

## Support
For issues and feature requests, please use the GitHub issue tracker. 