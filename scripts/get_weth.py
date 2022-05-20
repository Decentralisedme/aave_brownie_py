from brownie import network, config, interface
from scripts.helpful_scripts import get_account
import time


def get_weth():
    """
    Mints WETH by depositing ETH
    """
    #  To deposit eth we need:
    # -- ABI
    # -- WETH Address
    # -- WE NEED THE INTERFACE
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Got 0.1 WETH")
    return tx


def main():
    get_weth()
