"""
Ethereum wallet recovery implementation.
"""
from typing import List, Optional, Iterator, Tuple
import itertools
import logging
from pathlib import Path
import yaml
from tqdm import tqdm
import csv
import os

from src.validator import MnemonicHandler
from src.wallet import WalletDeriver

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WalletRecovery:
    """Main wallet recovery implementation"""
    
    def __init__(self, config_path: str = "data/wallets/wallet_config.yaml"):
        self.config_path = Path(config_path)
        self.load_config()
        self.mnemonic_handler = MnemonicHandler()
        self.wallet_deriver = None  # Will be initialized with target address
        self.tried_permutations = set()  # Track permutations we've tried
        self.valid_checksums = 0  # Track how many valid checksums we find
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Initialize CSV writers
        self.mnemonic_file = open("output/1_mnemonic.csv", "w", newline="")
        self.mnemonic_writer = csv.writer(self.mnemonic_file)
        self.mnemonic_writer.writerow(["permutation_id", "mnemonic", "checksum_valid"])
        
        self.derivation_file = open("output/2_derivations.csv", "w", newline="")
        self.derivation_writer = csv.writer(self.derivation_file)
        self.derivation_writer.writerow(["permutation_id", "derived_address"])
        
    def load_config(self) -> None:
        """Load wallet configuration from YAML"""
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        # Load settings
        self.settings = self.config.get("settings", {})
        self.chunk_size = self.settings.get("chunk_size", 1000)
        self.debug = self.settings.get("logging_level", "INFO") == "DEBUG"
        
        # Normalize wallet configuration
        for wallet_id in self.config:
            if wallet_id == "settings":
                continue
                
            wallet = self.config[wallet_id]
            if "fixed_words" in wallet:
                # Clean and normalize fixed words
                wallet["fixed_words"] = [
                    str(word).lower().strip().strip('"\'') 
                    for word in wallet["fixed_words"]
                ]
                logger.debug(f"Normalized fixed words: {wallet['fixed_words']}")
                
            if "permutable_words" in wallet:
                # Clean and normalize permutable words
                wallet["permutable_words"] = [
                    str(word).lower().strip().strip('"\'')
                    for word in wallet["permutable_words"]
                ]
                logger.debug(f"Normalized permutable words: {wallet['permutable_words']}")
                
            if "target_address" in wallet:
                # Normalize address
                wallet["target_address"] = wallet["target_address"].lower().strip()
                logger.debug(f"Normalized target address: {wallet['target_address']}")
            
    def generate_permutations(self, words: List[str]) -> Iterator[List[str]]:
        """Generate permutations of words in memory-efficient chunks"""
        # Ensure all words are lowercase
        words = [word.lower() for word in words]
        
        # First validate all input words are in BIP-39 wordlist
        if not self.mnemonic_handler.validate_word_list(words):
            logger.error("Some input words are not valid BIP-39 words!")
            return
            
        # Generate permutations
        perm_id = 0
        for perm in itertools.permutations(words):
            perm_list = list(perm)
            perm_str = " ".join(perm_list)
            if perm_str in self.tried_permutations:
                logger.warning(f"Duplicate permutation detected: {perm_str}")
                continue
            self.tried_permutations.add(perm_str)
            yield perm_list, perm_id
            perm_id += 1
            
    def process_permutation(self, 
                          permuted_words: List[str],
                          perm_id: int,
                          fixed_words: List[str],
                          target_address: str) -> Optional[Tuple[str, str]]:
        """Process a single permutation of words"""
        try:
            # Ensure all words are lowercase
            permuted_words = [word.lower() for word in permuted_words]
            fixed_words = [word.lower() for word in fixed_words]
            
            # First validate all words are in wordlist
            if not self.mnemonic_handler.validate_word_list(permuted_words + fixed_words):
                if self.debug:
                    logger.debug("Invalid word in wordlist")
                return None
                
            # Construct mnemonic
            mnemonic = self.mnemonic_handler.construct_mnemonic(permuted_words, fixed_words)
            
            # Validate checksum and write to mnemonic CSV
            checksum_valid = self.mnemonic_handler.validate_checksum(mnemonic)
            self.mnemonic_writer.writerow([perm_id, mnemonic, checksum_valid])
            
            if not checksum_valid:
                if self.debug:
                    logger.debug(f"Invalid checksum for mnemonic: {mnemonic}")
                return None
                
            # If we get here, we found a valid checksum
            self.valid_checksums += 1
            logger.info(f"Found valid checksum ({self.valid_checksums} total)! Mnemonic: {mnemonic}")
            
            # Try all derivation paths
            working_path, derived_address = self.wallet_deriver.try_all_derivation_paths(mnemonic)
            
            # Write to derivation CSV - write the derived address for each valid checksum
            if derived_address:
                self.derivation_writer.writerow([perm_id, derived_address])
            else:
                # If we couldn't derive an address, try the default path directly
                try:
                    derived_address = self.wallet_deriver.derive_address(mnemonic)
                    if derived_address:
                        self.derivation_writer.writerow([perm_id, derived_address])
                except Exception as e:
                    logger.debug(f"Error deriving address: {str(e)}")
            
            if working_path:
                logger.info(f"Found match! Mnemonic: {mnemonic}")
                logger.info(f"Derivation path: {working_path}")
                logger.info(f"Derived address: {derived_address}")
                return mnemonic, working_path
                
            if self.debug:
                logger.debug(f"No matching address found for valid mnemonic: {mnemonic}")
                
        except Exception as e:
            if self.debug:
                logger.debug(f"Error processing permutation: {str(e)}")
            
        return None
        
    def recover_wallet(self, wallet_id: str = "wallet_1") -> Optional[Tuple[str, str]]:
        """Main recovery function"""
        wallet_config = self.config[wallet_id]
        target_address = wallet_config["target_address"].lower()  # Normalize address
        fixed_words = wallet_config["fixed_words"]
        permutable_words = wallet_config["permutable_words"]
        custom_path = wallet_config.get("derivation_path")  # Now optional
        
        # Validate inputs
        if len(fixed_words) != 15:
            logger.error(f"Expected 15 fixed words, got {len(fixed_words)}")
            return None
            
        if len(permutable_words) != 9:
            logger.error(f"Expected 9 permutable words, got {len(permutable_words)}")
            return None
            
        logger.info(f"Target address: {target_address}")
        logger.info(f"Fixed words: {fixed_words}")
        logger.info(f"Permutable words: {permutable_words}")
        if custom_path:
            logger.info(f"Custom derivation path: {custom_path}")
            
        # Validate all input words are in BIP-39 wordlist
        all_words = fixed_words + permutable_words
        if not self.mnemonic_handler.validate_word_list(all_words):
            logger.error("Some input words are not valid BIP-39 words!")
            return None
            
        # Initialize wallet deriver with target address and optional custom path
        self.wallet_deriver = WalletDeriver(target_address, custom_path)
        
        # Calculate total permutations for progress bar
        total_permutations = len(list(itertools.permutations(permutable_words)))
        logger.info(f"Processing {total_permutations} possible permutations...")
        logger.info("Trying multiple derivation paths for each permutation...")
        
        # Process all permutations with progress bar
        with tqdm(total=total_permutations, desc="Checking permutations") as pbar:
            for permutation, perm_id in self.generate_permutations(permutable_words):
                result = self.process_permutation(permutation, perm_id, fixed_words, target_address)
                if result:
                    mnemonic, path = result
                    logger.info(f"Found valid mnemonic with derivation path: {path}")
                    return result
                pbar.update(1)
                
        logger.info(f"No valid mnemonic found. Stats:")
        logger.info(f"Total permutations tried: {len(self.tried_permutations)}")
        logger.info(f"Valid checksums found: {self.valid_checksums}")
        return None

    def __del__(self):
        """Cleanup CSV files on object destruction"""
        try:
            self.mnemonic_file.close()
            self.derivation_file.close()
        except:
            pass

def main():
    """Main entry point"""
    recovery = WalletRecovery()
    result = recovery.recover_wallet()
    
    if result:
        mnemonic, path = result
        print("\nSuccess! Found valid mnemonic:")
        print(f"Mnemonic: {mnemonic}")
        print(f"Derivation path: {path}")
    else:
        print("\nNo valid mnemonic found with any derivation path")

if __name__ == "__main__":
    main() 