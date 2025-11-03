"""
Ethereum wallet derivation module.
"""
from typing import Optional, List, Tuple
import logging
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from eth_account import Account

logger = logging.getLogger(__name__)

class WalletDeriver:
    """Handles Ethereum wallet derivation from mnemonics"""
    
    DERIVATION_PATHS = [
        "m/44'/60'/0'/0/0",
        "m/44'/60'/0'",
        "m/44'/60'/0'/0",
        "m/44'/60'/0/0",
        "m/44'/60'/0/0/0",
        "m/44'/60'/0",
        "m/44'/60'",
        "m/0'/0'/0'",
        "m/0/0/0",
    ]
    
    def __init__(self, target_address: str, custom_path: Optional[str] = None):
        self.target_address = target_address.lower()
        if custom_path and custom_path not in self.DERIVATION_PATHS:
            logger.info(f"Adding custom derivation path: {custom_path}")
            self.DERIVATION_PATHS.insert(0, custom_path)
            
    def _derive_key_from_path(self, bip44_mst_ctx: Bip44, path: str) -> Optional[bytes]:
        """Helper to derive private key from path"""
        try:
            if path == "m/44'/60'/0'/0/0":
                return (
                    bip44_mst_ctx
                    .Purpose()
                    .Coin()
                    .Account(0)
                    .Change(Bip44Changes.CHAIN_EXT)
                    .AddressIndex(0)
                    .PrivateKey()
                    .Raw()
                    .ToBytes()
                )
            elif path == "m/44'/60'/0'":
                return (
                    bip44_mst_ctx
                    .Purpose()
                    .Coin()
                    .Account(0)
                    .PrivateKey()
                    .Raw()
                    .ToBytes()
                )
                
            path_parts = path.lstrip('m/').split('/')
            current_ctx = bip44_mst_ctx
            
            for part in path_parts:
                index = int(part.replace("'", ""))
                hardened = "'" in part
                
                if part.startswith("44"):
                    current_ctx = current_ctx.Purpose()
                elif part.startswith("60"):
                    current_ctx = current_ctx.Coin()
                elif len(current_ctx.PrivateKey().Raw().ToBytes()) > 0:
                    break
                else:
                    if hardened:
                        current_ctx = current_ctx.Account(index)
                    else:
                        if hasattr(current_ctx, 'Change'):
                            current_ctx = current_ctx.Change(index)
                        else:
                            current_ctx = current_ctx.AddressIndex(index)
                            
            return current_ctx.PrivateKey().Raw().ToBytes()
            
        except Exception as e:
            logger.debug(f"Error deriving key for path {path}: {str(e)}")
            return None
            
    def derive_address(self, mnemonic: str, path: Optional[str] = None) -> str:
        """
        Derives Ethereum address from mnemonic using specified path
        
        Args:
            mnemonic (str): Valid 24-word mnemonic
            path (str, optional): BIP-44 derivation path
            
        Returns:
            str: Derived Ethereum address
        """
        try:
            seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
            
            bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
            
            if path is None:
                path = self.DERIVATION_PATHS[0]

            private_key_bytes = self._derive_key_from_path(bip44_mst_ctx, path)
            if not private_key_bytes:
                logger.debug(f"Could not derive private key for path: {path}")
                return ""
                
            account = Account.from_key(private_key_bytes)
            derived = account.address.lower()
            logger.debug(f"Derived address {derived} using path {path}")
            return derived
            
        except Exception as e:
            logger.debug(f"Error deriving address with path {path}: {str(e)}")
            return ""
            
    def try_all_derivation_paths(self, mnemonic: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Try all derivation paths for a given mnemonic, prioritizing the most common path
        
        Args:
            mnemonic (str): Valid 24-word mnemonic
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (working_path, derived_address) if found, (None, None) otherwise
        """
        logger.info("Trying most common derivation path: m/44'/60'/0'/0/0")
        derived_address = self.derive_address(mnemonic, self.DERIVATION_PATHS[0])
        if derived_address:
            if derived_address == self.target_address:
                logger.info("Found match with most common derivation path!")
                return self.DERIVATION_PATHS[0], derived_address
            logger.debug(f"Most common path produced non-matching address: {derived_address}")
        
        logger.info("Trying alternative derivation paths...")
        for path in self.DERIVATION_PATHS[1:]:
            try:
                logger.debug(f"Trying path: {path}")
                derived_address = self.derive_address(mnemonic, path)
                if not derived_address:
                    continue
                    
                logger.debug(f"Testing {derived_address} against target {self.target_address}")
                if derived_address == self.target_address:
                    logger.info(f"Found matching address with alternative path {path}")
                    return path, derived_address
                    
            except Exception as e:
                logger.debug(f"Error with path {path}: {str(e)}")
                continue
                
        logger.info("No matching address found with any derivation path")
        return None, None

    def verify_address(self, derived_address: str) -> bool:
        """
        Verify if derived address matches target
        
        Args:
            derived_address (str): Address to verify
            
        Returns:
            bool: True if addresses match
        """
        return derived_address.lower() == self.target_address