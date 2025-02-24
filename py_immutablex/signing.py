'''
    This module provides functions to sign messages and payloads with
    Ethereum and Stark private keys.
'''
from eth_account import Account
from eth_account.messages import encode_defunct
from starkware.crypto.signature.signature import sign

from .key_derivation import derive_stark_keys


class StarkSigner:
    '''A class to sign payloads with Stark private keys.'''
    def __init__(self, stark_private_key: str, stark_public_key: str):
        '''Initialize the StarkSigner with private and public keys.'''
        self._private_key = int(stark_private_key, 16)
        self.address = stark_public_key

    def sign(self, payload: str) -> str:
        '''Sign a payload with the Stark private key.

        Args:
            payload: The hex string payload to sign.

        Returns:
            The signature as a hex string.
        '''
        payload_int = int(payload, 16)
        signature = sign(payload_int, self._private_key)
        return f"0x{signature[0]:064x}{signature[1]:064x}"

    @classmethod
    def from_eth_key(cls, eth_signer: Account, config: dict) -> 'StarkSigner':
        '''Create a StarkSigner from an Ethereum signer.

        Args:
            eth_signer: An eth_account.Account object with the Ethereum
                private key.
            config: Configuration dictionary with STARK_SIGNATURE_MESSAGE,
                ACCOUNT_LAYER, etc.

        Returns:
            A new StarkSigner instance.
        '''
        stark_private_key, stark_public_key = derive_stark_keys(
            eth_signer, config
        )
        return cls(stark_private_key, stark_public_key)


def sign_message(signer: Account, message: str) -> str:
    '''Sign a message with an Ethereum signer.

    Args:
        signer: An eth_account.Account object with the Ethereum private key.
        message: The message to sign.

    Returns:
        The signature as a hex string.
    '''
    message_encoded = encode_defunct(text=message)
    signed_msg = signer.sign_message(message_encoded)
    v_fixed = signed_msg.v - 27
    return f"0x{signed_msg.r:064x}{signed_msg.s:064x}{v_fixed:02x}"
