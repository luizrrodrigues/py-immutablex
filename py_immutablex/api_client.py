'''
This module contains the APIClient class for interacting with
the Immutable X API.
'''

from typing import Dict, Any
import requests


class APIClient:
    '''A class to interact with the Immutable X API.

    Attributes:
        base_url (str): The base URL for the Immutable X API.
        url (dict): A mapping of API endpoints.
        headers (dict): Default HTTP headers for API requests.
    '''
    def __init__(self, base_url: str = 'https://api.x.immutable.com'):
        '''Initialize the APIClient with a base URL.

        Args:
            base_url (str, optional): The base URL for the Immutable X API.
                Defaults to 'https://api.x.immutable.com'.
        '''
        self.base_url = base_url
        self.url = {
            'SIGN_REGISTRATION':
                f'{base_url}/v1/signable-registration-offchain',
            'REGISTRATION': f'{base_url}/v1/users',
            'SIGN_TRADE': f'{base_url}/v3/signable-trade-details',
            'TRADE': f'{base_url}/v3/trades',
            'SIGN_TRANSFER': f'{base_url}/v1/signable-transfer-details',
            'TRANSFER': f'{base_url}/v1/transfers'
        }
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def sign_registration(
            self, eth_public_key: str, stark_public_key: str
    ) -> Dict[str, str]:
        '''Request signable registration details from Immutable X.

        Args:
            eth_public_key (str): The Ethereum public key of the user.
            stark_public_key (str): The Stark public key of the user.

        Returns:
            dict: A dictionary containing 'payload_hash' and
                'signable_message'.

        Raises:
            requests.HTTPError: If the API request fails.
        '''
        payload = {'ether_key': eth_public_key, 'stark_key': stark_public_key}
        response = requests.post(
            self.url['SIGN_REGISTRATION'],
            headers=self.headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def register_user(
            self,
            eth_public_key: str,
            stark_public_key: str,
            eth_signature: str,
            stark_signature: str
    ) -> bool:
        '''Register a user with Immutable X.

        Args:
            eth_public_key (str): The Ethereum public key of the user.
            stark_public_key (str): The Stark public key of the user.
            eth_signature (str): The Ethereum signature of the
                signable message.
            stark_signature (str): The Stark signature of the payload hash.

        Returns:
            bool: True if registration succeeds (tx_hash present),
                False otherwise.

        Raises:
            requests.HTTPError: If the API request fails.
        '''
        payload = {
            'ether_key': eth_public_key,
            'stark_key': stark_public_key,
            'eth_signature': eth_signature,
            'stark_signature': stark_signature
        }
        response = requests.post(
            self.url['REGISTRATION'],
            headers=self.headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        response_json = response.json()
        return 'tx_hash' in response_json

    def get_signable_transfer(
            self, sender: str, receiver: str, token: str, amount: str
    ) -> Dict[str, Any]:
        '''Retrieve signable details for a transfer between two
            Immutable X users.

        Args:
            sender (str): The Ethereum address of the sender.
            receiver (str): The Ethereum address of the recipient.
            token (str): The token type (e.g., 'ETH').
            amount (str): The amount to transfer as a string (e.g., in
                wei for ETH).

        Returns:
            dict: Signable transfer details including 'payload_hash' and
                'signable_message'.

        Raises:
            requests.HTTPError: If the API request fails.
        '''
        token_data = {}
        if token == 'ETH':
            token_data = {'type': 'ETH', 'data': {'decimals': 18}}
        payload = {
            'amount': amount,
            'receiver': receiver,
            'sender': sender,
            'token': token_data
        }
        response = requests.post(
            self.url['SIGN_TRANSFER'],
            headers=self.headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_transfer(
        self,
        data: Dict[str, Any],
        eth_signature: str,
        stark_signature: str,
        eth_public_key: str
    ) -> str:
        '''Execute a transfer between two Immutable X users.

        Args:
            data (dict): Signable transfer details from get_signable_transfer,
                containing 'amount', 'asset_id', 'expiration_timestamp', etc.
            eth_signature (str): The Ethereum signature of the
                signable message.
            stark_signature (str): The Stark signature of the payload hash.
            eth_public_key (str): The Ethereum public key of the sender
                (e.g., '0x...').

        Returns:
            str: The transfer ID if successful, False if not present.

        Raises:
            requests.HTTPError: If the API request fails.
            KeyError: If required fields are missing from the signable data.
        '''
        payload = {
            'amount': data['amount'],
            'asset_id': data['asset_id'],
            'expiration_timestamp': data['expiration_timestamp'],
            'nonce': data['nonce'],
            'receiver_stark_key': data['receiver_stark_key'],
            'receiver_vault_id': data['receiver_vault_id'],
            'sender_stark_key': data['sender_stark_key'],
            'sender_vault_id': data['sender_vault_id'],
            'stark_signature': stark_signature
        }
        headers = self.headers.copy()
        headers.update({
            'x-imx-eth-address': eth_public_key,
            'x-imx-eth-signature': eth_signature
        })
        response = requests.post(
            self.url['TRANSFER'],
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('transfer_id', False)

    def get_signable_trade(
        self, order_id: int, user_address: str, fees: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        '''Retrieve signable details for a trade on Immutable X.

        Args:
            order_id (int): The ID of the order to sign.
            user_address (str): The Ethereum address of the user
                (e.g., '0x...').
            fees (dict, optional): Fee details
                (e.g., [{'address': '0x...', 'fee_percentage': '1'}]).

        Returns:
            dict: Signable trade details including 'payload_hash',
                'signable_message', 'amount_buy', 'amount_sell',
                'fees' (if provided), etc.

        Raises:
            requests.HTTPError: If the API request fails.
        '''
        payload = {
            'order_id': order_id,
            'user': user_address,
        }
        if fees:
            payload.update({'fees': fees})
        response = requests.post(
            self.url['SIGN_TRADE'],
            headers=self.headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_trade(
        self,
        order_id: int,
        data: Dict[str, Any],
        eth_signature: str,
        stark_signature: str,
        eth_public_key: str,
        fees: Dict[str, Any] = None
    ) -> str:
        '''Execute a trade for an Immutable X user.

        Args:
            order_id (int): The ID of the order to trade.
            data (dict): Signable trade details from get_signable_trade,
                containing 'amount_buy', 'amount_sell', 'asset_id_buy', etc.
            eth_signature (str): The Ethereum signature of the
                signable message.
            stark_signature (str): The Stark signature of the payload hash.
            eth_public_key (str): The Ethereum public key of the user
                (e.g., '0x...').
            fees (dict, optional): Fee details
                (e.g., [{'address': '0x...', 'fee_percentage': '1'}]).

        Returns:
            str: The trade ID if successful, False if not present.

        Raises:
            requests.HTTPError: If the API request fails.
            KeyError: If required fields are missing from the signable data.
        '''
        payload = {
            'amount_buy': data['amount_buy'],
            'amount_sell': data['amount_sell'],
            'asset_id_buy': data['asset_id_buy'],
            'asset_id_sell': data['asset_id_sell'],
            'expiration_timestamp': data['expiration_timestamp'],
            'fee_info': data['fee_info'],
            'nonce': data['nonce'],
            'order_id': order_id,
            'stark_key': data['stark_key'],
            'stark_signature': stark_signature,
            'vault_id_buy': data['vault_id_buy'],
            'vault_id_sell': data['vault_id_sell']
        }
        if fees:
            payload.update({'fees': fees})
        headers = self.headers.copy()
        headers.update({
            'x-imx-eth-address': eth_public_key,
            'x-imx-eth-signature': eth_signature
        })
        response = requests.post(
            self.url['TRADE'],
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('trade_id', False)
