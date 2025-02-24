'''
This module provides the main client for interacting with Immutable X.
'''

from typing import Optional, Dict, Any
from eth_account import Account
from .api_client import APIClient
from .signing import sign_message, StarkSigner


class IMXClient:
    '''A client for interacting with the Immutable X API.

    Attributes:
        eth_signer (Account): The Ethereum signer object.
        eth_public_key (str): The Ethereum public key (address) of the user.
        stark_signer (StarkSigner): The Stark signer object.
        stark_public_key (str): The Stark public key of the user.
        api_client (APIClient): The API client for Immutable X requests.
        config (dict): Configuration settings for Stark key derivation.
    '''

    DEFAULT_CONFIG = {
        'STARK_SIGNATURE_MESSAGE':
            'Only sign this request if you’ve initiated an action ' +
            'with Immutable X.',
        'ACCOUNT_LAYER': 'starkex',
        'ACCOUNT_APPLICATION': 'immutablex',
        'ACCOUNT_INDEX': '1'
    }

    def __init__(
        self,
        eth_private_key: str,
        base_url: str = 'https://api.x.immutable.com'
    ):
        '''Initialize the IMX client with an Ethereum private key.

        Args:
            eth_private_key (str): The Ethereum private key in hex format
                (e.g., '0x...').
            base_url (str, optional): The base URL for the Immutable X API.
                Defaults to 'https://api.x.immutable.com'.

        Raises:
            RuntimeError: If initialization or registration fails.
        '''
        self.eth_signer = Account.from_key(  # pylint: disable=E1120
            private_key=eth_private_key
        )
        self.eth_public_key = self.eth_signer.address
        self.api_client = APIClient(base_url)
        self.config = self.DEFAULT_CONFIG

        try:
            self.stark_signer = StarkSigner.from_eth_key(
                self.eth_signer, self.config
            )
            self.stark_public_key = self.stark_signer.address
            self._register()
        except Exception as e:
            raise RuntimeError(f"Initialization failed: {e}") from e

    def _register(self):
        '''Register the user with Immutable X.

        This method is called automatically during initialization.

        Raises:
            RuntimeError: If registration fails or the API response is invalid.
        '''
        try:
            sign_data = self.api_client.sign_registration(
                self.eth_public_key, self.stark_public_key
            )
            payload_hash = sign_data['payload_hash']
            signable_message = sign_data['signable_message']
            stark_signature = self.stark_signer.sign(payload_hash)
            eth_signature = sign_message(
                self.eth_signer, signable_message
            )
            register = self.api_client.register_user(
                self.eth_public_key,
                self.stark_public_key,
                eth_signature,
                stark_signature
            )
            if not register:
                raise RuntimeError("User registration failed")
        except Exception as e:
            raise RuntimeError(f"Registration failed: {e}") from e

    def transfer(self, transfer_to: str, token: str, amount: str) -> str:
        '''Initiate a transfer on Immutable X.

        Args:
            transfer_to (str): The Ethereum address of the recipient.
            token (str): The token type (e.g., 'ETH').
            amount (str): The amount to transfer as a string
                (e.g., wei for ETH).

        Returns:
            str: The transfer ID if successful.

        Raises:
            RuntimeError: If the transfer fails or the API response is invalid.
        '''
        try:
            transfer_details = self.api_client.get_signable_transfer(
                self.eth_public_key, transfer_to, token, amount
            )
            eth_signature = sign_message(
                self.eth_signer,
                transfer_details['signable_message']
            )
            stark_signature = self.stark_signer.sign(
                transfer_details['payload_hash']
            )
            transfer_response = self.api_client.create_transfer(
                transfer_details,
                eth_signature,
                stark_signature,
                self.eth_public_key
            )
            if not transfer_response:
                raise RuntimeError("Transfer ID not returned")
            return transfer_response
        except Exception as e:
            raise RuntimeError(f"Transfer failed: {e}") from e

    def trade(
        self,
        order_id: int,
        fees: Optional[Dict[str, Any]] = None
    ) -> str:
        '''Execute a trade on Immutable X.

        Args:
            order_id (int): The ID of the order to trade.
            fees (dict, optional): Fee details
                (e.g., [{'address': '0x...', 'fee_percentage': '1'}]).

        Returns:
            str: The trade ID if successful.

        Raises:
            RuntimeError: If the trade fails or the API response is invalid.
        '''
        try:
            trade_details = self.api_client.get_signable_trade(
                order_id, self.eth_public_key, fees
            )
            eth_signature = sign_message(
                self.eth_signer, trade_details['signable_message']
            )
            stark_signature = self.stark_signer.sign(
                trade_details['payload_hash']
            )
            trade_response = self.api_client.create_trade(
                order_id,
                trade_details,
                eth_signature,
                stark_signature,
                self.eth_public_key,
                fees
            )
            if not trade_response:
                raise RuntimeError("Trade ID not returned")
            return trade_response
        except Exception as e:
            raise RuntimeError(f"Trade failed: {e}") from e
