"""
Orbiter has a unique technique for bridging.  An account can transfer
funds directly to the Orbiter address for the asset, and the trailing
4 digits of the transaction is used to identify the target network.

For example, transferring 100009001 ETH to 0x80c67432656d59144ceff962e8faf8926599bcf8
on any supported chain will bridge the funds (minus a fee) to Mainnet.
"""


class OrbiterRelays:
    USDC_ADDRESS = "0x41d3D33156aE7c62c094AAe2995003aE63f587B3"
    ETH_ADDRESS = "0x80c67432656d59144ceff962e8faf8926599bcf8"
    USDT_ADDRESS = "0x80c67432656d59144ceff962e8faf8926599bcf8"


class OrbiterChainIds:
    MAINNET: int = 9001
    ARBITRUM: int = 9002
    BASE: int = 9021
    LINEA: int = 9023
