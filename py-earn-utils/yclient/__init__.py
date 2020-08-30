from web3 import Web3
from pathlib import Path
from datetime import datetime
import time
import json

ROOT = str(Path(__file__).parent.parent.parent)


class ChainClient:

    def __init__(self, provider):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.blocks_in_year = 2425846
        self.blocks_in_week = 46523.073972606
        self.blocks_in_day = 6646.153424658
        self.blocks_in_hour = 276.923059361
        self.price_zero = 10 ** 18
        self.abi = None
        self.contract = None
        self.contract_address = None
        self.contract_chcks_address = None

    def setup(self, address):
        self.abi = self.get_abi(address)
        self.contract_address = address
        self.contract_chcks_address = self.get_address_checksum()
        self.contract = self.get_contract()

    # call
    def get_address_checksum(self):
        self.sleep()
        return Web3.toChecksumAddress(self.contract_address)

    # call
    def get_contract(self):
        self.sleep()
        return self.w3.eth.contract(address=self.contract_chcks_address, abi=self.abi)

    # call
    def get_latest_block(self):
        self.sleep()
        return int(self.w3.eth.getBlock('latest')['number'])

    def get_block_at_time(self, seconds):
        delta_blocks = int(seconds / 15)
        return self.get_latest_block() - delta_blocks

    # call
    def get_block_time(self, block_number):
        self.sleep()
        block_time = self.w3.eth.getBlock(block_number)['timestamp']
        time_object = datetime.fromtimestamp(block_time)
        return time_object.strftime('%Y-%m-%d %H:%M')

    # call
    def get_share_price_at(self, block):
        self.sleep()
        block = int(block)
        return int(
            self.contract.functions.getPricePerFullShare().call(block_identifier=block))

    # call
    def get_vault_holdings_at(self, block):
        self.sleep()
        block = int(block)
        return int(self.contract.functions.balance().call(block_identifier=block))

    # call
    def get_free(self, block):
        self.sleep()
        block = int(block)
        return int(self.contract.functions.available().call(block_identifier=block))

    @staticmethod
    def get_abi(address):
        with open(ROOT + '/assets/' + address + '.json') as f:
            info_json = json.load(f)
            return info_json['result']

    def get_delta_block(self, block):
        last_block = self.get_latest_block()
        first_block = block
        last_price = self.get_share_price_at(block=last_block)
        first_price = self.get_share_price_at(first_block)

        return ((last_price - first_price) / (last_block - first_block)) / 10 ** 18

    def get_roi_hour(self, block):
        return self.get_delta_block(block) * self.blocks_in_hour

    def get_roi_day(self, block):
        return self.get_delta_block(block) * self.blocks_in_day

    def get_roi_week(self, block):
        return self.get_delta_block(block) * self.blocks_in_week

    def get_roi_year(self, block):
        return self.get_delta_block(block) * self.blocks_in_year

    def get_roi_set(self, block):
        hour = self.get_roi_hour(block)
        day = self.get_roi_day(block)
        week = self.get_roi_week(block)
        year = self.get_roi_year(block)

        return {'Hour': f'{hour:.5%}', f'Day': f'{day:.5%}',
                f'Week': f'{week:.5%}',
                f'Year': f'{year:.5%}'}

    @staticmethod
    def sleep():
        time.sleep(3)
