from brownie import accounts, network, config


LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development",
    "ganache",
    "ganache-local",
    "hardhat",
    "mainnet-fork",
    "mainnet-fork-dev",
]


def get_account(index=None, id=None):
    if index:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    return None

