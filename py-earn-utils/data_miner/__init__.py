import pandas as pd
import tqdm as tqdm
import time


def getdata(mongodb, cc, vault_data):
    cc = cc
    mongodb = mongodb
    df = vault_data
    d = {}
    blocks = pd.read_csv('blocks.csv')
    blocks.drop(columns=['Unnamed: 0'], inplace=True)
    for v in df:
        pbar = tqdm.tqdm(desc='Processing ' + v, total=len(blocks['block']))
        for b in blocks['block']:
            if b > int(df[v]['first_block']):
                cc.setup(df[v]['address'])
                whitelist_functions = {
                    'available': cc.contract.functions.available().call(block_identifier=b) / 10 ** 18 if (
                                                                                                                  'available' in cc.abi) and v != 'yaLINK' else None,
                    'balance': cc.contract.functions.balance().call(
                        block_identifier=b) / 10 ** 18 if 'balance' in cc.abi else None,
                    'getPricePerFullShare': cc.contract.functions.getPricePerFullShare().call(
                        block_identifier=b) / 10 ** 18 if 'getPricePerFullShare' in cc.abi else None}
                d['Vault'] = v
                d['Address'] = df[v]['address']
                for f in whitelist_functions:
                    if f in cc.abi:
                        d[f] = whitelist_functions[f]
                pbar.update()
                mongodb.insert_one(d)
                time.sleep(1)
            d = {}
