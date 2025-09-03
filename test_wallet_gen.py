from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins
from eth_account import Account
import json

# Generate a new random mnemonic
mnemonic = Bip39MnemonicGenerator().FromWordsNumber(24)
print(f"\nMnemonic:\n{mnemonic}")

# Generate seed
seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

# Use alternative path m/44'/60'/0'
path = "m/44'/60'/0'"
bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
private_key_bytes = (
    bip44_mst_ctx
    .Purpose()
    .Coin()
    .Account(0)
    .PrivateKey()
    .Raw()
    .ToBytes()
)

# Generate Ethereum address
account = Account.from_key(private_key_bytes)
address = account.address.lower()

print(f"\nDerivation Path: {path}")
print(f"Address: {address}")

# Save to wallet config
config = {
    "wallet_1": {
        "target_address": address,
        "fixed_words": str(mnemonic).split()[10:24],  # Words 11-24 are fixed (14 words)
        "permutable_words": str(mnemonic).split()[:10],  # Words 1-10 are permutable
        "derivation_path": path
    }
}

with open('data/wallets/wallet_config.yaml', 'w') as f:
    import yaml
    yaml.dump(config, f) 