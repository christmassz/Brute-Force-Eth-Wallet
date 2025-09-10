"""Trial 3 brute-force recovery script.

Usage:
    python trial3.py [wallet_id] [config_path]

Defaults:
    wallet_id    = "wallet_trial3"
    config_path  = "data/wallets/wallet_trial3.yaml"

The script:
1. Loads YAML configuration.
2. Validates input lists.
3. Streams permutations using `generate_trial3_word_sets`.
4. For each checksum-valid mnemonic, derives addresses and checks target.
5. Writes CSV logs similar to original recovery.py.
"""
import sys
import itertools
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import yaml
from tqdm import tqdm
import csv
import os
import math

from src.validator import MnemonicHandler
from src.wallet import WalletDeriver
from src.trial3_generator import generate_trial3_word_sets

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_CONFIG = "data/wallets/wallet_trial3.yaml"
BLANK_TOKEN = ""

class Trial3Recovery:
    def __init__(self, config_path: str = DEFAULT_CONFIG, wallet_id: str = "wallet_trial3") -> None:
        self.config_path = Path(config_path)
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
        if wallet_id not in self.config:
            raise KeyError(f"Wallet id '{wallet_id}' not found in {config_path}")
        self.wallet = self.config[wallet_id]
        self.settings = self.config.get("settings", {})

        # Validate lists
        self.fixed_words: List[str] = self.wallet["fixed_words"]
        self.scrambled_words: List[str] = self.wallet["scrambled_words"]
        self.replacement_pool: List[str] = self.wallet["replacement_pool"]
        self.target_address: str = self.wallet["target_address"].lower().strip()
        self.custom_path: Optional[str] = self.wallet.get("derivation_path")

        if len(self.fixed_words) != 15:  # words10–24 inclusive is 15?
            # actually 10-24 is 15 positions (inclusive). earlier doc said 14 because counting 11-24.
            # adjust validation to 15.
            raise ValueError(f"fixed_words must have 15 words (positions 10-24), got {len(self.fixed_words)}")
        if len(self.scrambled_words) != 9:
            raise ValueError("scrambled_words must have 9 entries (one blank)")
        if self.scrambled_words.count(BLANK_TOKEN) != 1:
            raise ValueError("scrambled_words must contain exactly one blank token \"\"")
        if len(self.replacement_pool) != 30:
            raise ValueError("replacement_pool must have 30 candidate words")

        # Normalise word casing/whitespace
        self.fixed_words = [w.lower().strip() for w in self.fixed_words]
        self.scrambled_words = [w.lower().strip() for w in self.scrambled_words]
        self.replacement_pool = [w.lower().strip() for w in self.replacement_pool]

        # Handlers
        self.mnemonic_handler = MnemonicHandler()
        self.wallet_deriver = WalletDeriver(self.target_address, self.custom_path)

        # Output setup
        os.makedirs("output", exist_ok=True)
        self.mnemonic_file = open("output/1_mnemonic.csv", "w", newline="")
        self.mnemonic_writer = csv.writer(self.mnemonic_file)
        self.mnemonic_writer.writerow(["mnemonic", "checksum_valid"])
        self.derivation_file = open("output/2_derivations.csv", "w", newline="")
        self.derivation_writer = csv.writer(self.derivation_file)
        self.derivation_writer.writerow(["mnemonic", "derived_address"])

    def recover(self) -> Optional[Tuple[str, str]]:
        # Pre-compute total permutations for progress bar
        total_perms = 30 * math.factorial(9)
        logger.info(f"Processing up to {total_perms:,} permutations …")

        for perm in tqdm(generate_trial3_word_sets(self.scrambled_words, self.replacement_pool), total=total_perms, desc="Permutations"):
            mnemonic = " ".join([*perm, *self.fixed_words])
            if len(mnemonic.split()) != 24:
                raise ValueError("Constructed mnemonic does not have 24 words")
            is_valid = self.mnemonic_handler.validate_checksum(mnemonic)
            self.mnemonic_writer.writerow([mnemonic, is_valid])
            if not is_valid:
                continue
            # Derive address
            working_path, derived_addr = self.wallet_deriver.try_all_derivation_paths(mnemonic)
            if working_path:
                logger.info("Success! Found matching mnemonic.")
                self.derivation_writer.writerow([mnemonic, derived_addr])
                return mnemonic, working_path
        return None

    def __del__(self):
        try:
            self.mnemonic_file.close()
            self.derivation_file.close()
        except:  # noqa
            pass

def main():
    wallet_id = sys.argv[1] if len(sys.argv) > 1 else "wallet_trial3"
    config_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CONFIG
    recovery = Trial3Recovery(config_path, wallet_id)
    result = recovery.recover()
    if result:
        mnemonic, path = result
        print("\nSUCCESS — Mnemonic found:\n", mnemonic)
        print("Derivation path:", path)
    else:
        print("\nFinished search: no matching mnemonic found.")

if __name__ == "__main__":
    main()
