from brownie import config, network, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3
import time

# eth =0.1
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # to deposit we need to use LendingPool contract so we need its:
    # -ABI
    # -Address  >>> to get this address we need address provider - interface
    lending_pool = get_lending_pool()
    print(lending_pool)
    # APPROVE ERC-20 token from IERC-20
    approve_erc20(amount, lending_pool, erc20_address, account)
    # DEPOSIT: from LendingPool
    # deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    print("Depositing ....")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Deposit Done!!!")
    #  we want to borrow now, but how much?
    # we need to get info about our deposit
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow DAI")
    # we need to know asset price
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable eth >> borrowable day * 95% (tobe safe)
    print(f"We are going to borrow: {amount_dai_to_borrow} DAI")
    # BORROW
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("borrowed some DAI from AAVE Protocol")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    print(
        "This contract just DEPOSITED, BORROWED, REPAYED with Aave, Brownie and Chainlink"
    )


def repay_all(amount, lending_pool, account):
    # APPROVE: the DAI first
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    #  REPAY: funct
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed the DEBT to the Pool")


def get_asset_price(price_feed_address):
    # ABI >> we need interface
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"DAI/ETH: {converted_latest_price}")
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    # we get info and put it in a tuple
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"Your Tot Collateral in eth is: {total_collateral_eth}")
    print(f"Your have borrowed (Tot Debt) in eth is: {total_debt_eth}")
    print(f"Your still can borrow: {available_borrow_eth}")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    # As always we need
    # ABI
    # address
    #  As usual we can build our interface or copy it and use approve function
    print("Approving ERC-20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!!!!")
    return tx


def get_lending_pool():
    #  we do interface ourself in interfaces
    #  ABI: from Interface
    #  address : this is the address of this contract (LPAdressProv) and we get it from docs
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    #  Lending Pool Address
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    #  Lending Pool ABI >> via interfaces
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

