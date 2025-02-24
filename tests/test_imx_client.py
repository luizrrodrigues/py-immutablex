'''
    IMXClient class tests.
'''
import pytest
import requests_mock
from py_immutablex.imx_client import IMXClient


# Testing keys
# CAUTION: Never change this to real keys! These are testnet-only,
#          generated for testing.
TEST_ETH_PRIVATE_KEY = (
    '0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b'
)
TEST_STARK_PUBLIC_KEY = (
    '0x04ffbbee4a76255360197d36ea99ee9285cde259d16345fee186f673355f138b'
)


@pytest.fixture(name='imx_client')
def imx_client_fixture():
    '''Fixture for an IMXClient instance with mocked registration.'''
    base_url = 'https://api.sandbox.x.immutable.com'  # Testnet URL
    with requests_mock.Mocker() as m:
        # Mock registration API calls
        m.post(
            f"{base_url}/v1/signable-registration-offchain",
            json={"payload_hash": "0x1234", "signable_message": "Sign this"}
        )
        m.post(
            f"{base_url}/v1/users",
            json={"tx_hash": "0xTransactionHash"}
        )

        client = IMXClient(TEST_ETH_PRIVATE_KEY, base_url=base_url)
        yield client


def test_init_and_register_success(imx_client):
    '''Test IMXClient initialization and registration (mocked).'''
    assert imx_client.stark_public_key == TEST_STARK_PUBLIC_KEY


def test_transfer_success(imx_client):
    '''Test transfer with a successful response.'''
    with requests_mock.Mocker() as m:
        m.post(
            imx_client.api_client.url['SIGN_TRANSFER'],
            json={
                'payload_hash': '0x5678',
                'signable_message': 'Sign this transfer',
                'amount': '1000000000000000000',
                'asset_id': '0xAssetId',
                'expiration_timestamp': 1234567890,
                'nonce': 1,
                'receiver_stark_key': '0xReceiverStark',
                'receiver_vault_id': 2,
                'sender_stark_key': '0xSenderStark',
                'sender_vault_id': 1
            }
        )
        m.post(
            imx_client.api_client.url['TRANSFER'],
            json={'transfer_id': '123'}
        )

        transfer_id = imx_client.transfer(
            '0xReceiver', 'ETH', '1000000000000000000'
        )
        assert transfer_id == '123'


def test_trade_success_with_fees(imx_client):
    '''Test trade with fees and a successful response.'''
    fees = [{'address': '0xFeeAddress', 'fee_percentage': '1'}]
    with requests_mock.Mocker() as m:
        m.post(
            imx_client.api_client.url['SIGN_TRADE'],
            json={
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
        )
        m.post(
            imx_client.api_client.url['TRADE'],
            json={'trade_id': '456'}
        )

        trade_id = imx_client.trade(12345, fees=fees)
        assert trade_id == '456'


def test_trade_failure_no_id(imx_client):
    '''Test trade when no trade_id is returned.'''
    with requests_mock.Mocker() as m:
        m.post(
            imx_client.api_client.url['SIGN_TRADE'],
            json={
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
                'vault_id_sell': 4
            }
        )
        m.post(
            imx_client.api_client.url['TRADE'],
            json={}  # No trade_id
        )

        with pytest.raises(RuntimeError, match='Trade ID not returned'):
            imx_client.trade(12345)


def test_stark_key_generation():
    '''Integration test: Verify Stark key generation with real testnet API.'''
    client = IMXClient(
        TEST_ETH_PRIVATE_KEY,
        base_url='https://api.sandbox.x.immutable.com'
    )
    assert client.stark_public_key == TEST_STARK_PUBLIC_KEY
