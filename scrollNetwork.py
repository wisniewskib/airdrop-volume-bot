import json
from web3.middleware import geth_poa_middleware
from web3 import Web3, Account
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# Addresses
USDT = Web3.to_checksum_address("0xf55BEC9cafDbE8730f096Aa55dad6D22d44099Df")
USDC = Web3.to_checksum_address("0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4")
scrollSushiSwap = Web3.to_checksum_address("0xca6fe749878841b96f620ec79638b13daad3d320")

# Connect
rpc_url = "https://rpc.scroll.io/"
web3 = Web3(Web3.HTTPProvider(rpc_url))

key = config["DEFAULT"]["KEY"]
account = Account.from_key(key)

# Load abi
scrollFile = open("./abis/sushiSwap.json")
scrollAbi = json.load(scrollFile)
tokenFile = open("./abis/erc20.json")
tokenAbi = json.load(tokenFile)


# # Set the contract address and ABI
swap_router_contract = web3.eth.contract(address=scrollSushiSwap, abi=scrollAbi)
usdc_contract = web3.eth.contract(address=USDC, abi=tokenAbi)
usdt_contract = web3.eth.contract(address=USDT, abi=tokenAbi)

web3.middleware_onion.inject(geth_poa_middleware, layer=0)


# Approve
def approve(tokenContract):
    try:
        approve_tx = tokenContract.functions.approve(
            scrollSushiSwap, 50000 * 10**18
        ).build_transaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 200000,  # Example, adjust based on method gas requirements
                "gasPrice": web3.to_wei(
                    "0.4", "gwei"
                ),  # Example, adjust to current conditions or preferences
            }
        )

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(approve_tx, account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Transaction output
        print(f"Transaction hash: {tx_hash.hex()}")

        # Check the transaction status
        if tx_receipt.status == 1:
            print("Approve transaction was successful.")
        else:
            print("Approve transaction failed.")

    except Exception as e:
        print(f"An error occurred: {e}")


# approve(usdt_contract)
# approve(usdc_contract)

amountIn = 900 * 10**6
amountOut = 895 * 10**6
dataUsdtToUsdc = "0x02f55bec9cafdbe8730f096aa55dad6d22d44099df01ffff01ae5aa896bb93f4c7c5660b7fc894b3892255d0150016900163e16188078b48548086a78f048da8805c"
dataUsdcToUsdt = "0x0206efdbff2a14a7c8e15944d1f4a48f9f95f663a401ffff01ae5aa896bb93f4c7c5660b7fc894b3892255d0150116900163e16188078b48548086a78f048da8805c"


def swap(swapFrom, swapTo, data):
    try:
        approve_tx = swap_router_contract.functions.processRoute(
            swapFrom,
            amountIn,
            swapTo,
            amountOut,
            account.address,
            data,
        ).build_transaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "gas": 321000,  # Example, adjust based on method gas requirements
                "gasPrice": web3.to_wei(
                    "0.4", "gwei"
                ),  # Example, adjust to current conditions or preferences
            }
        )

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(approve_tx, account.key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        ethLeft = web3.from_wei(web3.eth.get_balance(account.address), "ether")

        # Transaction output
        print(f"Transaction hash: {tx_hash.hex()}")

        # Check the transaction status
        if tx_receipt.status == 1:
            print(f"Swap transaction was successful. Eth left: {ethLeft}")
        else:
            print(f"Swap transaction failed. Eth left: {ethLeft}")
            exit()

    except Exception as e:
        print(f"An error occurred: {e}")


for _ in range(7):
    swap(USDT, USDC, dataUsdtToUsdc)
    swap(USDC, USDT, dataUsdcToUsdt)
