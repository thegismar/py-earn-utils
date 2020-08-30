import os
from tqdm import tqdm
import pymongo
import requests
import time

archive_node = os.getenv('ARCHIVENODE_API')
mongo = os.getenv('MONGO')
monclient = pymongo.MongoClient(mongo)
mondb = monclient['yvault']
moncol = mondb['histdata']


def get_blocks(ts):
    blocks_ = []
    current_time = time.time()
    max_ = int((current_time - ts) / 3600)

    pbar = tqdm(total=max_)
    while ts < int(current_time):
        while True:
            try:
                response = requests.get(
                    f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={ts}&closest=before&apikey=7PFFRTS264XV42KD3GMP8Z7X9WA5QVHJBX')
            except:
                time.sleep(0.1)
            else:
                break
        block_ = int(response.json()['result'])
        bdict = {}
        bdict['ts'] = ts
        bdict['block'] = block_
        blocks_.append(bdict)
        ts = ts + 3600
        pbar.update(1)
        if ts > current_time:
            break

    return blocks_



