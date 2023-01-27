# from dis import Bytecode
import json
from subprocess import call
from solcx import compile_standard, install_solc
from web3 import Web3
import os 
from dotenv import load_dotenv
load_dotenv()

with open("./SimpleStorage.sol" , "r" ) as file :
    simple_storage_file = file.read()
_solc_version = "0.8.0"
install_solc(_solc_version)

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version=_solc_version,
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# # get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# print(abi)


w3 =  Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/739083bf64b24a998a9c740a93f609bb"))
chain_id = 5
my_address = "0x776C0222E36972035608D733EfaDF7248f473a6b"
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi , bytecode=bytecode) 

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction({"chainId":int(chain_id) , "from" :my_address , "nonce":nonce , "gas": 1728712, "gasPrice": w3.toWei('21', 'gwei') })  
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
tx_hash  = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_Storage = w3.eth.contract(address=tx_receipt.contractAddress , abi = abi)

print(simple_Storage.functions.retrive().call())
print(simple_Storage.functions.store(15).call())

store_transaction = simple_Storage.functions.store(25).buildTransaction({
    "chainId" : chain_id , 
    "from" : my_address , 
    "nonce" : nonce+1 ,
    "gas": 1728712 , 
    "gasPrice": w3.toWei('21', 'gwei')
    
})

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction , private_key = private_key
)

send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_txn)

print(simple_Storage.functions.retrive().call())




