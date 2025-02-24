'''
    API Client Tests
'''
import pytest
import requests_mock
from py_immutablex.api_client import APIClient


@pytest.fixture(name='api_client')
def api_client_fixure():
    '''Fixture to create an APIClient instance.'''
    return APIClient(base_url='https://api.sandbox.x.immutable.com')


def test_sign_registration_success(api_client):
    '''Test sign_registration with a successful response.'''
    eth_key = '0xEthPublicKey'
    stark_key = '0xStarkPublicKey'
    mock_response = {
        'payload_hash': '0x1234',
        'signable_message': 'Sign this'
    }

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['SIGN_REGISTRATION'],
            json=mock_response
        )
        result = api_client.sign_registration(eth_key, stark_key)
        assert result == mock_response


def test_register_user_success(api_client):
    '''Test register_user with a successful response.'''
    eth_key = '0xEthPublicKey'
    stark_key = '0xStarkPublicKey'
    eth_sig = '0xEthSignature'
    stark_sig = '0xStarkSignature'
    mock_response = {'tx_hash': '0xTransactionHash'}

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['REGISTRATION'],
            json=mock_response
        )
        result = api_client.register_user(
            eth_key, stark_key, eth_sig, stark_sig
        )
        assert result is True


def test_get_signable_transfer_success(api_client):
    '''Test get_signable_transfer with a successful response.'''
    sender = '0xSender'
    receiver = '0xReceiver'
    token = 'ETH'
    amount = '1000000000000000000'
    mock_response = {
        'payload_hash': '0x5678',
        'signable_message': 'Sign this transfer',
        'amount': amount,
        'asset_id': '0xAssetId',
        'expiration_timestamp': 1234567890,
        'nonce': 1,
        'receiver_stark_key': '0xReceiverStark',
        'receiver_vault_id': 2,
        'sender_stark_key': '0xSenderStark',
        'sender_vault_id': 1
    }

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['SIGN_TRANSFER'],
            json=mock_response
        )
        result = api_client.get_signable_transfer(
            sender, receiver, token, amount
        )
        assert result == mock_response


def test_create_transfer_success(api_client):
    '''Test create_transfer with a successful response.'''
    data = {
        'amount': '1000000000000000000',
        'asset_id': '0xAssetId',
        'expiration_timestamp': 1234567890,
        'nonce': 1,
        'receiver_stark_key': '0xReceiverStark',
        'receiver_vault_id': 2,
        'sender_stark_key': '0xSenderStark',
        'sender_vault_id': 1
    }
    eth_sig = '0xEthSignature'
    stark_sig = '0xStarkSignature'
    eth_key = '0xEthPublicKey'
    mock_response = {'transfer_id': '123'}

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['TRANSFER'],
            json=mock_response
        )
        result = api_client.create_transfer(
            data, eth_sig, stark_sig, eth_key
        )
        assert result == '123'


def test_get_signable_trade_success_with_fees(api_client):
    '''Test get_signable_trade with fees and a successful response.'''
    order_id = 12345
    user = '0xUserAddress'
    fees = [{'address': '0xFeeAddress', 'fee_percentage': '1'}]
    mock_response = {
        'payload_hash': '0x9012',
        'signable_message': 'Sign this trade',
        'amount_buy': '100',
        'amount_sell': '1',
        'asset_id_buy': '0xBuyAsset',
        'asset_id_sell': '0xSellAsset',
        'expiration_timestamp': 1234567890,
        'fee_info': [],
        'nonce': 2,
        'order_id': 12345,
        'stark_key': '0xStarkKey',
        'vault_id_buy': 3,
        'vault_id_sell': 4,
        'fees': fees
    }

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['SIGN_TRADE'],
            json=mock_response
        )
        result = api_client.get_signable_trade(
            order_id, user, fees=fees
        )
        assert result == mock_response


def test_create_trade_success_with_fees(api_client):
    '''Test create_trade with fees and a successful response.'''
    order_id = 12345
    data = {
        'amount_buy': '100',
        'amount_sell': '1',
        'asset_id_buy': '0xBuyAsset',
        'asset_id_sell': '0xSellAsset',
        'expiration_timestamp': 1234567890,
        'fee_info': [],
        'nonce': 2,
        'stark_key': '0xStarkKey',
        'vault_id_buy': 3,
        'vault_id_sell': 4,
        'fees': [{'address': '0xFeeAddress', 'fee_percentage': '1'}]
    }
    eth_sig = '0xEthSignature'
    stark_sig = '0xStarkSignature'
    eth_key = '0xEthPublicKey'
    fees = [{'address': '0xFeeAddress', 'fee_percentage': '1'}]
    mock_response = {'trade_id': '456'}

    with requests_mock.Mocker() as m:
        m.post(
            api_client.url['TRADE'],
            json=mock_response
        )
        result = api_client.create_trade(
            order_id, data, eth_sig, stark_sig, eth_key, fees=fees
        )
        assert result == '456'
