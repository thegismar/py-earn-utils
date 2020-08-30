from yclient import ChainClient
import pymongo
import os
from pathlib import Path
import time
from tqdm import tqdm
from get_hist_blocks import get_blocks
import pandas as pd
from get_hist_data import get_hist
from data_miner import getdata


def get_block_data():
    getdata(mongodb=get_mongo(), cc=get_archive_client(), vault_data=get_vault_data())


def get_hist_data():
    get_hist(get_vault_data())


def blocks():
    first_ts = 1595746408
    b = get_blocks(first_ts)
    df = pd.DataFrame(b)
    df.to_csv('blocks.csv')


def get_archive_node():
    return 'https://api.archivenode.io/73w07ccm19lzdnx9gp01ctp173w07ccm'


def get_project_root():
    return str(Path(__file__).parent.parent.parent)


def get_mongo():
    return 'mongodb://thegismar:maugan00@cluster0-shard-00-00.mr9b8.mongodb.net:27017,cluster0-shard-00-01.mr9b8.mongodb.net:27017,cluster0-shard-00-02.mr9b8.mongodb.net:27017/yVault?ssl=true&replicaSet=atlas-ciekb2-shard-0&authSource=admin&retryWrites=true&w=majority'


def get_archive_client():
    return ChainClient(get_archive_node())


def get_mongo_client():
    return pymongo.MongoClient(get_mongo())


def get_yvault_db():
    return get_mongo_client()['yvault']


def get_hist_db():
    return get_yvault_db()['hist']


def get_roi_collection():
    return get_yvault_db()['roi']


def get_info_collection():
    return get_yvault_db()['info']


def get_prices_collection():
    return get_yvault_db()['prices']


def get_vault_data():
    db = get_info_collection()
    cursor = db.find({}, {'_id': 0})
    for i in cursor:
        return i


def pull_roi() -> list:
    coll = []
    vault = []
    for d in get_roi_collection().find({}, {'_id': 0}).limit(14).sort([('ts', -1), ('vault', 1)]):
        if d['vault'] not in vault:
            coll.append(d)
            vault.append(d['vault'])

    return coll


def push_roi():
    vault_data = get_vault_data()

    cc = get_archive_client()

    blocks = {'Historic average daily': cc.get_block_at_time(60 * 60 * 24),
              'Historic average weekly': cc.get_block_at_time(60 * 60 * 24 * 7)}
    i = 0
    for v in vault_data:
        cc.setup(vault_data[v]['address'])
        roi = {'vault': v}
        a = vault_data[v]['address']
        roi['address'] = a

        for b in blocks:
            mbar = tqdm(desc='Processing blocks for ' + v)
            if blocks[b] > vault_data[v]['first_block']:
                roi[b] = cc.get_roi_set(blocks[b])
                mbar.update()
        sb = vault_data[v]['first_strategy_block']
        roi['Historic average since strategy change'] = cc.get_roi_set(sb)
        fb = vault_data[v]['first_block']
        roi['Historic average since inception'] = cc.get_roi_set(fb)
        roi['ts'] = int(time.time())
        try:
            get_roi_collection().insert_one(roi)
        except:
            None
