from brownie import (
    accounts,
    chain,
    interface,
    Controller,
    SettV4,
    MyStrategy,
)
from config import (
    BADGER_DEV_MULTISIG,
    WANT,
    LP_COMPONENT,
    REWARD_TOKEN,
    PROTECTED_TOKENS,
    FEES,
)
from dotmap import DotMap
import pytest


@pytest.fixture
def deployed():
    """
    Deploys, vault, controller and strats and wires them up for you to test
    """
    deployer = accounts[1]

    strategist = deployer
    keeper = deployer
    guardian = deployer

    governance = accounts.at(BADGER_DEV_MULTISIG, force=True)

    controller = Controller.deploy({"from": deployer})
    controller.initialize(BADGER_DEV_MULTISIG, strategist, keeper, BADGER_DEV_MULTISIG)

    sett = SettV4.deploy({"from": deployer})
    sett.initialize(
        WANT,
        controller,
        BADGER_DEV_MULTISIG,
        keeper,
        guardian,
        False,
        "prefix",
        "PREFIX",
    )

    sett.unpause({"from": governance})
    controller.setVault(WANT, sett)

    ## TODO: Add guest list once we find compatible, tested, contract
    # guestList = VipCappedGuestListWrapperUpgradeable.deploy({"from": deployer})
    # guestList.initialize(sett, {"from": deployer})
    # guestList.setGuests([deployer], [True])
    # guestList.setUserDepositCap(100000000)
    # sett.setGuestList(guestList, {"from": governance})

    ## Start up Strategy
    strategy = MyStrategy.deploy({"from": deployer})
    strategy.initialize(
        BADGER_DEV_MULTISIG,
        strategist,
        controller,
        keeper,
        guardian,
        PROTECTED_TOKENS,
        FEES,
    )

    ## Tool that verifies bytecode (run independently) <- Webapp for anyone to verify

    ## Set up tokens
    want = interface.IERC20(WANT)
    lpComponent = interface.IERC20(LP_COMPONENT)
    rewardToken = interface.IERC20(REWARD_TOKEN)

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(WANT, strategy, {"from": governance})
    controller.setStrategy(WANT, strategy, {"from": deployer})

    ## Get some WETH
    WETH = interface.IERC20(strategy.WETH())
    WETH_DEP = interface.IWETH(strategy.WETH())
    WETH_DEP.deposit({"from": deployer, "value": 5000000000000000000})

    ## Get some IBBTC
    IBBTC = interface.IERC20(strategy.IBBTC())
    ibbtc_whale = "0x7c1D678685B9d2F65F1909b9f2E544786807d46C"
    IBBTC.transfer(deployer, 0.0005e18, {"from": ibbtc_whale})

    router = interface.IUniswapRouterV2(strategy.DX_SWAP_ROUTER())
    # router.swapExactETHForTokens(
    #     0,  ## Mint out
    #     [WETH, IBBTC],
    #     deployer,
    #     9999999999999999,
    #     {"from": deployer, "value": 5000000000000000000},
    # )

    # Get want - IBBTC/ETH LP
    WETH.approve(router, WETH.balanceOf(deployer), {"from": deployer})
    IBBTC.approve(router, IBBTC.balanceOf(deployer), {"from": deployer})
    router.addLiquidity(
        WETH,
        IBBTC,
        WETH.balanceOf(deployer),
        IBBTC.balanceOf(deployer),
        0,
        0,
        deployer,
        9999999999999999,
        {"from": deployer},
    )

    ## Set up necessary for this vault to work
    helper_vault = SettV4.at(strategy.HELPER_VAULT())
    gov = accounts.at(helper_vault.governance(), force=True)
    helper_vault.approveContractAccess(strategy, {"from": gov})

    # Sleep till staking starts
    staking_contract = interface.IERC20StakingRewardsDistribution(
        strategy.stakingContract()
    )
    time_left = max(0, staking_contract.startingTimestamp() - chain.time())
    chain.sleep(time_left)

    return DotMap(
        deployer=deployer,
        controller=controller,
        vault=sett,
        sett=sett,
        strategy=strategy,
        # guestList=guestList,
        want=want,
        lpComponent=lpComponent,
        rewardToken=rewardToken,
    )


## Contracts ##


@pytest.fixture
def vault(deployed):
    return deployed.vault


@pytest.fixture
def sett(deployed):
    return deployed.sett


@pytest.fixture
def controller(deployed):
    return deployed.controller


@pytest.fixture
def strategy(deployed):
    return deployed.strategy


## Tokens ##


@pytest.fixture
def want(deployed):
    return deployed.want


@pytest.fixture
def tokens():
    return [WANT, LP_COMPONENT, REWARD_TOKEN]


## Accounts ##


@pytest.fixture
def deployer(deployed):
    return deployed.deployer


@pytest.fixture
def strategist(strategy):
    return accounts.at(strategy.strategist(), force=True)


@pytest.fixture
def settKeeper(vault):
    return accounts.at(vault.keeper(), force=True)


@pytest.fixture
def strategyKeeper(strategy):
    return accounts.at(strategy.keeper(), force=True)


## Forces reset before each test
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass
