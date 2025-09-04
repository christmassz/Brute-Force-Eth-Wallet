#!/usr/bin/env python3
"""
Brute-force the 5th word (index 4) of a 24-word BIP-39 mnemonic.

The script loads a YAML wallet configuration (data/wallets/wallet_word5.yaml)
where all 24 mnemonic words are specified except the 5th one, which is left
blank ("").  For every word in the official BIP-39 English word-list we
substitute it into the 5th position, verify the checksum of the resulting
mnemonic, and derive the Ethereum address using the same derivation logic as
in the main application.  If the derived address matches the configured
`target_address`, we output the working mnemonic and stop.

Usage:
    python test2.py  # runs against default YAML config path

Exit status:
    0 – matching mnemonic found
    1 – completed search with no match

This script is intentionally simple and single-purpose for ad-hoc recovery
scenarios rather than being part of the production pipeline.
"""

from pathlib import Path
import logging
import sys
import yaml

from src.validator import MnemonicHandler
from src.wallet import WalletDeriver

# Configure basic logging – can be overridden by parent application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def load_config(config_path: Path):
    """Load YAML configuration from *config_path*."""
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # We currently support a single wallet entry – extend as needed.
        wallet_data = next(iter(data.values()))
        known_words = wallet_data["known_words"]
        if len(known_words) != 24:
            raise ValueError("Expected 24 words (one of them blank), got {}".format(len(known_words)))
        target_address = wallet_data["target_address"].lower()
        derivation_path = wallet_data.get("derivation_path")
        return known_words, target_address, derivation_path
    except Exception:
        logger.exception("Failed loading YAML config %s", config_path)
        sys.exit(1)

def main():
    # Default config file lives next to data folder
    config_path = Path(__file__).parent / "data/wallets/wallet_word5.yaml"
    if not config_path.exists():
        logger.error("Config file %s not found", config_path)
        sys.exit(1)

    known_words, target_address, derivation_path = load_config(config_path)

    # In this scenario we know the 5th word (index 4) is the unknown, so enforce it
    blank_index = 4

    # Split into the two parts expected by MnemonicHandler
    fixed_words = known_words[10:]

    validator = MnemonicHandler()
    wallet = WalletDeriver(target_address, custom_path=derivation_path)

    logger.info("Starting brute-force over %d candidate words for position %d", len(validator.wordlist), blank_index + 1)

    for candidate in validator.wordlist:
        permuted = known_words[:10]  # copy first 10
        permuted[blank_index] = candidate  # substitute candidate

        # Fast path: validate words quickly before checksum to avoid heavy ops
        if not validator.validate_word_list(permuted + fixed_words):
            continue  # Should not happen – candidate is valid but precaution

        # Validate full mnemonic (checksum etc.)
        if not validator.validate_complete_mnemonic(permuted, fixed_words):
            continue

        mnemonic = " ".join(permuted + fixed_words)

        # First, try the specific derivation path if provided
        if derivation_path:
            derived_specific = wallet.derive_address(mnemonic, derivation_path)
            if derived_specific and derived_specific.lower() == target_address:
                logger.info(
                    "FOUND MATCHING MNEMONIC!\nMnemonic: %s\nDerivation Path: %s",
                    mnemonic,
                    derivation_path,
                )
                print(mnemonic)
                sys.exit(0)

        # Otherwise (or if no match), exhaustively try all common paths
        path, derived_address = wallet.try_all_derivation_paths(mnemonic)
        if derived_address and derived_address.lower() == target_address:
            logger.info("FOUND MATCHING MNEMONIC!\nMnemonic: %s\nDerivation Path: %s", mnemonic, path)
            print(mnemonic)
            sys.exit(0)

    logger.info("Completed search – no matching mnemonic found")
    sys.exit(1)


if __name__ == "__main__":
    main()
