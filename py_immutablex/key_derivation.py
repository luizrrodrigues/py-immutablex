''' Key derivation functions for Immutable X accounts. '''
import hashlib
from bip32 import BIP32
from eth_account import Account
from eth_account.messages import encode_defunct
from starkware.crypto.signature.signature import private_to_stark_key, \
    grind_key, EC_ORDER


def _get_int_from_bits(hex_str: str, start: int, end: int = None) -> int:
    num = int(hex_str, 16)
    if end is None:
        shift = abs(start)
        mask = (1 << shift) - 1
        return num & mask

    shift = abs(end)
    mask = (1 << (abs(start) - abs(end))) - 1
    return (num >> shift) & mask


def _get_account_path(eth_public_key: str, config: dict) -> str:
    layer = config['ACCOUNT_LAYER']
    application = config['ACCOUNT_APPLICATION']
    index = config['ACCOUNT_INDEX']

    layer_hash = hashlib.sha256(layer.encode('utf-8')).hexdigest()
    application_hash = hashlib.sha256(application.encode('utf-8')).hexdigest()

    ly = _get_int_from_bits(layer_hash, -31)
    app = _get_int_from_bits(application_hash, -31)
    eth1 = _get_int_from_bits(eth_public_key, -31)
    eth2 = _get_int_from_bits(eth_public_key, -62, -31)

    return f"m/2645'/{ly}'/{app}'/{eth1}'/{eth2}'/{index}"


def _get_private_key_from_path(seed: str, path: str) -> int:
    seed_bytes = bytes.fromhex(seed[2:] if seed.startswith('0x') else seed)
    bip32 = BIP32.from_seed(seed_bytes)
    derived_key = bip32.get_privkey_from_path(path)
    private_key_int = int.from_bytes(derived_key, 'big')
    return grind_key(private_key_int, EC_ORDER)


def derive_stark_keys(eth_signer: Account, config: dict) -> tuple[str, str]:
    '''Derive Stark private and public keys from an Ethereum signer.

    Args:
        eth_signer: An eth_account.Account object with the Ethereum private
            key.
        config: Configuration dictionary with STARK_SIGNATURE_MESSAGE,
            ACCOUNT_LAYER, etc.

    Returns:
        A tuple of (stark_private_key, stark_public_key) as hex strings.
    '''
    eth_public_key = eth_signer.address
    message_encoded = encode_defunct(text=config['STARK_SIGNATURE_MESSAGE'])
    signed_msg = eth_signer.sign_message(message_encoded)
    seed = hex(signed_msg.s)

    path = _get_account_path(eth_public_key, config)
    stark_private_key_int = _get_private_key_from_path(seed, path)
    stark_public_key_int = private_to_stark_key(stark_private_key_int)

    stark_private_key = f'0x{stark_private_key_int:064x}'
    stark_public_key = f'0x{stark_public_key_int:064x}'

    return stark_private_key, stark_public_key
