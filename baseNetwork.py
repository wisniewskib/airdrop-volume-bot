import json
from web3.middleware import geth_poa_middleware
from web3 import Web3, Account
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# Addresses
DAI = Web3.to_checksum_address("0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb")
USDC = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
sushiswap = Web3.to_checksum_address("0x83ec81ae54dd8dca17c3dd4703141599090751d1")

# Connect
rpc_url = "https://mainnet.base.org"
web3 = Web3(Web3.HTTPProvider(rpc_url))

key = config["DEFAULT"]["KEY"]
account = Account.from_key(key)

# Load abi
scrollFile = open("./abis/sushiSwap.json")
scrollAbi = json.load(scrollFile)
tokenFile = open("./abis/erc20.json")
tokenAbi = json.load(tokenFile)


# # Set the contract address and ABI
swap_router_contract = web3.eth.contract(address=sushiswap, abi=scrollAbi)
usdc_contract = web3.eth.contract(address=USDC, abi=tokenAbi)
dai_contract = web3.eth.contract(address=DAI, abi=tokenAbi)

web3.middleware_onion.inject(geth_poa_middleware, layer=0)


# Approve
def approve(tokenContract):
    try:
        approve_tx = tokenContract.functions.approve(
            sushiswap, 50000 * 10**18
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


# approve(dai_contract)
# approve(usdc_contract)

usdcAmount = 950 * 10**6
daiAmount = 950 * 10**18

daiToUsdcDataRoute = "0x0250c5725949a6f0c72e6c4a641f24049a917db0cb02155501c18f50d6a832f12f6dcaaeee8d0c87a65b96787e0116900163e16188078b48548086a78f048da8805cffff0122f9623817f152148b4e080e98af66fbe9c5adf80183ec81ae54dd8dca17c3dd4703141599090751d101d9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca01ffff0106959273e9a65433de71f5a452d529544e07ddd00016900163e16188078b48548086a78f048da8805c"

usdcToDaiRoute = "0x02833589fcd6edb6e08f4c7c32d4f71b54bda0291302155501c18f50d6a832f12f6dcaaeee8d0c87a65b96787e0016900163e16188078b48548086a78f048da8805cffff0106959273e9a65433de71f5a452d529544e07ddd00183ec81ae54dd8dca17c3dd4703141599090751d101d9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca01ffff0122f9623817f152148b4e080e98af66fbe9c5adf80016900163e16188078b48548086a78f048da8805c"


def swap(swapFrom, swapTo, data, amountIn, amountOut):
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
                "gas": 500000,  # Example, adjust based on method gas requirements
                "maxFeePerGas": web3.to_wei("0.000000505", "gwei"),
                "maxPriorityFeePerGas": web3.to_wei("0.000000435", "gwei"),
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


for _ in range(13):
    swap(USDC, DAI, usdcToDaiRoute, usdcAmount, daiAmount - (5 * 10**18))
    swap(DAI, USDC, daiToUsdcDataRoute, daiAmount, usdcAmount - (5 * 10**6))
