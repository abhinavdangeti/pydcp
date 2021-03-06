
import time

from constants import *
from lib.mc_bin_client import MemcachedClient as McdClient

class Stats():
    @staticmethod
    def get_stat(client, stat, type=''):
        response = client.stats(type)
        return response[stat]

    @staticmethod
    def check(client, stat, exp, type=''):
        op = client.stats(type)
        response = op.next_response()
        assert response['status'] == SUCCESS
        assert response['value'][stat] == exp

    @staticmethod
    def exists(client, stat, type=''):
        op = client.stats(type)
        response = op.next_response()
        assert response['status'] == SUCCESS
        return stat in response['value']

    @staticmethod
    def wait_for_persistence(client):
        while int(Stats.get_stat(client, 'ep_queue_size')) > 0:
            time.sleep(1)
        while int(Stats.get_stat(client, 'ep_commit_num')) == 0:
            time.sleep(1)

    @staticmethod
    def wait_for_stat(client, stat, val, type=''):
        for i in range(60):
            resp = client.stats(type)
            assert stat in resp
            if resp[stat] == str(val):
                return True
            time.sleep(1)
        return False

    @staticmethod
    def wait_for_warmup(host, port):
        while True:
            client = McdClient(host, port)
            try:
                response = client.stats()
                if response['ep_degraded_mode'] == '0':
                    break
            except:
                pass
            time.sleep(1)
