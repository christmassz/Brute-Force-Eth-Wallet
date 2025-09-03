# BIP-39 Ethereum Wallet Recovery Tool

A Python-based tool for recovering Ethereum wallets using partial BIP-39 mnemonic phrases. This tool is specifically designed to help recover wallets when you have a portion of the mnemonic phrase fixed and need to determine the remaining words.

## Features

- BIP-39 mnemonic validation with checksum verification
- Support for partial mnemonic recovery (fixed words in specific positions)
- Efficient permutation generation for missing words
- Standard Ethereum derivation path support (m/44'/60'/0'/0/0)
- CSV output for both valid and invalid attempts
- Progress tracking with detailed logging

## Requirements

- Python 3.8+
- bip_utils
- eth-account
- tqdm

## Installation

1. Clone the repository:
```bash
git clone https://github.com/christmassz/Brute-Force-Eth-Wallet.git
cd Brute-Force-Eth-Wallet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a wallet configuration in `data/wallets/wallet_config.yaml`:

```yaml
wallet_1:
  target_address: "0x28712bcf646ffe836288be6694bc708b24d03a32"
  fixed_words:
    positions: [10-24]  # Fixed words positions
    words:
      - "half"
      - "orphan"
      # ... other fixed words
  permutable_words:
    positions: [1-9]  # Positions to try different combinations
```

## Usage

Run the main script:
```bash
python main.py
```

The tool will:
1. Load the wallet configuration
2. Generate permutations of words for the specified positions
3. Validate each permutation's checksum
4. Derive Ethereum addresses for valid mnemonics
5. Output results to CSV files:
   - `output/1_mnemonic.csv`: All attempted mnemonics with checksum status
   - `output/2_derivations.csv`: Valid mnemonics with derived addresses

## Output Files

- `1_mnemonic.csv`: Contains all permutations attempted with their checksum validation status
- `2_derivations.csv`: Contains only valid mnemonics that passed checksum validation, along with their derived addresses

## Project Structure

```
├── data/
│   └── wallets/
│       └── wallet_config.yaml
├── src/
│   ├── validator.py
│   ├── wallet.py
│   └── recovery.py
├── tests/
├── main.py
└── requirements.txt
```

## Licensing

This software is a proprietary tool developed by **JL Capital**. All rights are reserved. Unauthorized copying, distribution, or modification of any part of this repository is strictly prohibited without prior written consent from JL Capital.

For approved internal or partner use, please refer to the `LICENSE` file for the full licensing terms and conditions.