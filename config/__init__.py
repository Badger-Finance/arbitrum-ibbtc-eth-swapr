## Ideally, they have one file with the settings for the strat and deployment
## This file would allow them to configure so they can test, deploy and interact with the strategy

BADGER_DEV_MULTISIG = "0x468A0FF843BC5D185D7B07e4619119259b03619f"

WANT = "0x6a060a569e04a41794d6b1308865a13F27D27E53"  ## IBBTC/ETH swaprLP
# TODO/NOTE: CHANGE BEFORE FINAL DEPLOYMENT
LP_COMPONENT = (
    "0x70005b38b13E8978bb573562681F39fd142Fe121"  ## IBBTC/ETH Staking Contract
)
REWARD_TOKEN = "0xde903e2712288a1da82942dddf2c20529565ac30" ## SWPR

PROTECTED_TOKENS = [WANT, LP_COMPONENT, REWARD_TOKEN]
## Fees in Basis Points
DEFAULT_GOV_PERFORMANCE_FEE = 1000
DEFAULT_PERFORMANCE_FEE = 1000
DEFAULT_WITHDRAWAL_FEE = 10

FEES = [DEFAULT_GOV_PERFORMANCE_FEE, DEFAULT_PERFORMANCE_FEE, DEFAULT_WITHDRAWAL_FEE]

REGISTRY = "0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f"  # Multichain BadgerRegistry
