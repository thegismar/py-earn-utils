from yclient import ChainClient
import os
from tqdm import tqdm
import pymongo
import pandas as pd


def get_hist(v_data):
    archive_node = os.getenv('ARCHIVENODE_API')
    mongo = os.getenv('MONGO')
    monclient = pymongo.MongoClient(mongo)

    mondb = monclient['yvault']
    moncol = mondb['histdata']

    cc = ChainClient(archive_node)
    df = v_data
    vault_data = df.to_dict('index')

    blocks = pd.read_csv('blocks.csv')
    blocks.drop(columns=['Unnamed: 0'], inplace=True)
    for v in vault_data:
        cc.setup(vault_data[v]['address'])
        pbar = tqdm(len(blocks(columns=['address'].index)))
        for b in blocks.iterrows():
            block = int(b[1]['block'])
            ts = int(b[1]['ts'])
            data = {}
            data['vault'] = v
            data['block'] = block
            data['ts'] = ts
            if block > vault_data[v]['first_block']:
                try:
                    data['price'] = float(cc.get_share_price_at(block)) / 10 ** 18
                except:
                    data['price'] = None
                try:
                    data['vault_holdings'] = float(cc.get_vault_holdings_at(block) / 10 ** 18)
                    free = float(cc.get_free(block)) / 10 ** 18
                    data['strat_holding'] = data['vault_holdings'] - free
                except:
                    data['vault_holdings'] = None
                    data['strat_holding'] = None
            else:
                data['price'] = None
                data['vault_holdings'] = None
                data['strat_holding'] = None

            x = moncol.insert_one(data)
            pbar.update(1)
