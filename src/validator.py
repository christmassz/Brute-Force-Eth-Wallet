"""
Mnemonic validation and handling module.
"""
from typing import List
import logging
import importlib.resources
from bip_utils import Bip39SeedGenerator
import binascii

logger = logging.getLogger(__name__)

class MnemonicHandler:
    """Manages BIP-39 mnemonic operations and validation"""
    
    def __init__(self):
        # Load wordlist from a known good source
        with importlib.resources.open_text("bip_utils.bip.bip39.wordlist", "english.txt") as f:
            self.wordlist = set(word.strip() for word in f)
        logger.debug(f"Initialized with {len(self.wordlist)} BIP-39 words")
        
    def validate_word_list(self, words: List[str]) -> bool:
        """
        Validates if all words are in the BIP-39 wordlist
        
        Args:
            words (List[str]): List of words to validate
            
        Returns:
            bool: True if all words are valid
        """
        try:
            # Check each word individually for better debugging
            invalid_words = []
            for word in words:
                word = word.lower().strip()
                if word not in self.wordlist:
                    invalid_words.append(word)
            
            if invalid_words:
                logger.debug(f"Invalid words found: {invalid_words}")
                return False
            return True
        except Exception as e:
            logger.debug(f"Error validating words: {str(e)}")
            return False
        
    def construct_mnemonic(self, permuted_words: List[str], fixed_words: List[str]) -> str:
        """
        Combines permuted and fixed words into full mnemonic
        
        Args:
            permuted_words: First 10 words in current permutation (positions 1-10)
            fixed_words: Known words for positions 11-24
            
        Returns:
            str: Complete 24-word mnemonic phrase
        """
        if len(permuted_words) != 10:
            raise ValueError(f"Expected 10 permuted words, got {len(permuted_words)}: {permuted_words}")
            
        if len(fixed_words) != 14:
            raise ValueError(f"Expected 14 fixed words, got {len(fixed_words)}: {fixed_words}")
            
        # Clean and normalize all words
        permuted_clean = [str(w).lower().strip().strip('"\'') for w in permuted_words]
        fixed_clean = [str(w).lower().strip().strip('"\'') for w in fixed_words]
        
        # Verify lengths after cleaning
        if len(permuted_clean) != 10:
            raise ValueError(f"Invalid permuted words after cleaning: {permuted_clean}")
        if len(fixed_clean) != 14:
            raise ValueError(f"Invalid fixed words after cleaning: {fixed_clean}")
            
        # Combine words in correct positions (1-10 permuted, 11-24 fixed)
        all_words = permuted_clean + fixed_clean
        if len(all_words) != 24:
            raise ValueError(f"Invalid total words: {len(all_words)}")
            
        # Join with single spaces
        mnemonic = " ".join(all_words)
        
        # Debug output
        logger.debug("Constructed mnemonic details:")
        logger.debug(f"Permuted words (positions 1-10): {permuted_clean}")
        logger.debug(f"Fixed words (positions 11-24): {fixed_clean}")
        logger.debug(f"Full mnemonic: {mnemonic}")
        
        return mnemonic
        
    def validate_checksum(self, mnemonic: str) -> bool:
        """
        Validates BIP-39 checksum of complete mnemonic
        
        Args:
            mnemonic (str): Complete 24-word mnemonic
            
        Returns:
            bool: True if checksum is valid
        """
        try:
            # First verify we have exactly 24 words
            words = mnemonic.split()
            if len(words) != 24:
                logger.debug(f"Invalid word count: {len(words)}")
                return False
                
            # Verify each word is valid
            if not self.validate_word_list(words):
                return False
                
            # Try to generate a seed - this will fail if checksum is invalid
            try:
                Bip39SeedGenerator(mnemonic).Generate()
                return True
            except Exception as e:
                logger.debug(f"Invalid checksum: {str(e)}")
                return False
                
        except Exception as e:
            logger.debug(f"Error validating checksum: {str(e)}")
            return False
            
    def validate_complete_mnemonic(self, permuted_words: List[str], fixed_words: List[str]) -> bool:
        """
        Validates both word list and checksum for a complete mnemonic
        
        Args:
            permuted_words: First 10 words in current permutation
            fixed_words: Known words for positions 11-24
            
        Returns:
            bool: True if mnemonic is completely valid
        """
        try:
            # First validate all words are in wordlist
            all_words = permuted_words + fixed_words
            if not self.validate_word_list(all_words):
                logger.debug("Word list validation failed")
                return False
                
            # Then construct and validate checksum
            mnemonic = self.construct_mnemonic(permuted_words, fixed_words)
            if not self.validate_checksum(mnemonic):
                return False
                
            return True
            
        except Exception as e:
            logger.debug(f"Error in complete validation: {str(e)}")
            return False 