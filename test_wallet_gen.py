from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins
from eth_account import Account
import json

mnemonic = Bip39MnemonicGenerator().FromWordsNumber(24)
print(f"\nMnemonic:\n{mnemonic}")

seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

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

account = Account.from_key(private_key_bytes)
address = account.address.lower()

print(f"\nDerivation Path: {path}")
print(f"Address: {address}")

config = {
    "wallet_1": {
        "target_address": address,
        "fixed_words": str(mnemonic).split()[10:24],
        "permutable_words": str(mnemonic).split()[:10],
        "derivation_path": path
    }
}

with open('data/wallets/wallet_config.yaml', 'w') as f:
    import yaml
    yaml.dump(config, f) 