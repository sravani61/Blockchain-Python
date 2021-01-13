#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import libraries

import subprocess
import json
import os
from constants import *
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy


# In[3]:


# Loading environment variable

load_dotenv()


# In[4]:


# get the saved mnemonic

mnemonic = os.getenv('mnemonic')
print(mnemonic)


# In[5]:


# connect to local ETH/ geth

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.setGasPriceStrategy(medium_gas_price_strategy)


# In[6]:


# Define function to derive wallet addresses.
def derive_wallets(coin_name):
    
    command = 'php hd-wallet-derive/derive -g --mnemonic="duck wolf scissors inside gain squeeze scan tenant clip run improve pool" --numderive=3 --coin="{}" --cols=index,path,address,privkey,pubkey,pubkeyhash,xprv,xpub --format=json'.format(coin_name)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    return json.loads(output)
    


# In[17]:


# create list of coins to be derived using declarations from constants.py

coin_name = [ETH,BTCTEST]
coins={}
for coin in coin_name:
    coins[coin] = derive_wallets(coin)
coins


# In[18]:


#create a function that convert the privkey string in a child key to an account object

def priv_key_to_account(coin,priv_key):
    print(coin)
    print(priv_key)
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)


# In[19]:


# Function to create transactions

def create_tx(coin,account, recipient, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from":eth_acc.address, "to":recipient, "value": amount}
        )
        return { 
            "from": eth_acc.address,
            "to": recipient,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(eth_acc.address)
        }
    
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(btc_acc.address, [(recipient, amount, BTC)])


# In[20]:


#Function to send transactions
def send_txn(coin,account,recipient, amount):
    txn = create_tx(coin, account, recipient, amount)
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        tx_btctest = create_tx(coin, account, recipient, amount)
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)


# In[21]:


# Declaring variables to store private key

eth_acc = priv_key_to_account(ETH, coins[ETH][0]['privkey'])
btc_acc = priv_key_to_account(BTCTEST,coins[BTCTEST][0]['privkey'])


# In[23]:


#Creating transaction in ETH

create_tx(ETH,eth_acc,"0xf096a93fAaCD15848F3CF94ACc0bd3f7d8F5c808", 1)


# In[24]:


#Sending the transaction to designated network

send_txn(ETH, eth_acc,"0x3dA0F09EF6F833b179768a63AdD29061e0702e47", 1)


# In[25]:


#checking balance of the account

w3.eth.getBalance("0x3dA0F09EF6F833b179768a63AdD29061e0702e47")


# In[27]:


#Creating transaction in BTC

create_tx(BTCTEST,btc_acc,"mvLxU6Do3d5cHRm5r9yGhg9c1DtRvRww5j", 0.00000001)


# In[28]:


send_txn(BTCTEST,btc_acc,"mvLxU6Do3d5cHRm5r9yGhg9c1DtRvRww5j", 0.00000001)


# In[ ]:





# In[ ]:




