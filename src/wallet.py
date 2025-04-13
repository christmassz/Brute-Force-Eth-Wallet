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
    
    # Common Ethereum derivation paths
    DERIVATION_PATHS = [
        "m/44'/60'/0'/0/0",     # Most common (MetaMask, MEW, etc)
        "m/44'/60'/0'",         # Alternative
        "m/44'/60'/0'/0",       # Alternative
        "m/44'/60'/0/0",        # Alternative without hardened derivation
        "m/44'/60'/0/0/0",      # Alternative without hardened derivation
        "m/44'/60'/0",          # Base path
        "m/44'/60'",            # Minimum path
        "m/0'/0'/0'",           # Legacy
        "m/0/0/0",              # Legacy without hardening
    ]
    
    def __init__(self, target_address: str, custom_path: Optional[str] = None):
        self.target_address = target_address.lower()
        if custom_path and custom_path not in self.DERIVATION_PATHS:
            logger.info(f"Adding custom derivation path: {custom_path}")
            self.DERIVATION_PATHS.insert(0, custom_path)  # Add custom path at the beginning
            
    def _derive_key_from_path(self, bip44_mst_ctx: Bip44, path: str) -> Optional[bytes]:
        """Helper to derive private key from path"""
        try:
            # For simple paths, use direct derivation
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
            
            # For other paths, parse each component
            path_parts = path.lstrip('m/').split('/')
            current_ctx = bip44_mst_ctx
            
            for part in path_parts:
                index = int(part.replace("'", ""))
                hardened = "'" in part
                
                if part.startswith("44"):
                    current_ctx = current_ctx.Purpose()
                elif part.startswith("60"):
                    current_ctx = current_ctx.Coin()
                elif len(current_ctx.PrivateKey().Raw().ToBytes()) > 0:  # Check if we can already get a key
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
            # Generate seed from mnemonic
            seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
            
            # Create BIP44 wallet
            bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
            
            if path is None:
                path = self.DERIVATION_PATHS[0]

            # Get private key based on path
            private_key_bytes = self._derive_key_from_path(bip44_mst_ctx, path)
            if not private_key_bytes:
                logger.debug(f"Could not derive private key for path: {path}")
                return ""
                
            # Generate Ethereum address
            account = Account.from_key(private_key_bytes)
            derived = account.address.lower()
            logger.debug(f"Derived address {derived} using path {path}")
            return derived
            
        except Exception as e:
            logger.debug(f"Error deriving address with path {path}: {str(e)}")
            return ""
            
    def try_all_derivation_paths(self, mnemonic: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Try all derivation paths for a given mnemonic
        
        Args:
            mnemonic (str): Valid 24-word mnemonic
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (working_path, derived_address) if found, (None, None) otherwise
        """
        logger.debug(f"Trying {len(self.DERIVATION_PATHS)} derivation paths")
        
        # First try the default/custom path
        derived_address = self.derive_address(mnemonic, self.DERIVATION_PATHS[0])
        if derived_address:
            if derived_address == self.target_address:
                return self.DERIVATION_PATHS[0], derived_address
            logger.debug(f"Default path produced address: {derived_address}")
        
        # Then try other paths
        for path in self.DERIVATION_PATHS[1:]:
            try:
                derived_address = self.derive_address(mnemonic, path)
                if not derived_address:
                    continue
                    
                logger.debug(f"Testing {derived_address} against target {self.target_address}")
                if derived_address == self.target_address:
                    logger.info(f"Found matching address with path {path}")
                    return path, derived_address
                    
            except Exception as e:
                logger.debug(f"Error with path {path}: {str(e)}")
                continue
                
        return None, derived_address  # Return the last derived address even if no match

    def verify_address(self, derived_address: str) -> bool:
        """
        Verify if derived address matches target
        
        Args:
            derived_address (str): Address to verify
            
        Returns:
            bool: True if addresses match
        """
        return derived_address.lower() == self.target_address