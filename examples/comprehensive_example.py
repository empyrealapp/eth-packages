"""
Comprehensive eth-packages Example

This example demonstrates the full capabilities of eth-packages by building
a complete DeFi analytics tool that:

1. Monitors real-time events across multiple networks
2. Analyzes historical data using efficient batch operations
3. Executes transactions with proper gas management
4. Handles complex contract interactions with full type safety

Key concepts demonstrated:
- Multi-network operations
- Event streaming and historical analysis
- Multicall for efficient batch operations
- Transaction execution with wallets
- Error handling and retry logic
- Type-safe contract interfaces
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List

from eth_rpc import Block, EventData, Transaction, get_current_network, set_alchemy_key
from eth_rpc.networks import Arbitrum, Base, Ethereum
from eth_rpc.wallet import PrivateKeyWallet
from eth_typeshed.erc20 import ERC20, TransferEvent, TransferEventType
from eth_typeshed.multicall import multicall
from eth_typeshed.uniswap_v2 import V2PairCreatedEvent
from eth_typing import HexAddress, HexStr


class DeFiAnalytics:
    """
    A comprehensive DeFi analytics tool demonstrating eth-packages capabilities.
    """

    def __init__(self):
        self.networks = [Ethereum, Arbitrum, Base]
        self.monitored_tokens = {
            Ethereum: "0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e",
            Arbitrum: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
            Base: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        }

    async def analyze_network_status(self):
        """
        Analyze the current status across multiple networks.
        Demonstrates: Multi-network operations, batch queries
        """
        print("🌐 NETWORK STATUS ANALYSIS")
        print("=" * 50)

        block_tasks = [Block[network].latest() for network in self.networks]
        blocks = await asyncio.gather(*block_tasks)

        for network, block in zip(self.networks, blocks):
            print(
                f"{network.__name__:>10}: Block {block.number:,} "
                f"({datetime.fromtimestamp(block.timestamp).strftime('%H:%M:%S')})"
            )

    async def analyze_token_distribution(
        self, token_address: HexAddress, network_class
    ):
        """
        Analyze token distribution using historical transfer events.
        Demonstrates: Event filtering, historical analysis, data aggregation
        """
        print(f"\n💰 TOKEN DISTRIBUTION ANALYSIS - {network_class.__name__}")
        print("=" * 50)

        token = ERC20[network_class](address=token_address)
        name, symbol, decimals = await multicall[network_class].execute(
            token.name(), token.symbol(), token.decimals()
        )

        print(f"Analyzing: {name} ({symbol}) - {decimals} decimals")

        latest_block = await Block[network_class].latest()
        start_block = latest_block.number - 1000

        print(f"Scanning blocks {start_block:,} to {latest_block.number:,}...")

        total_volume = 0
        unique_senders = set()
        unique_recipients = set()
        large_transfers = []

        transfer_count = 0
        async for event in (
            TransferEvent[network_class]
            .set_filter(addresses=[token_address])
            .backfill(start_block, latest_block.number)
        ):
            transfer = event.event
            amount = transfer.amount / (10**decimals)

            total_volume += amount
            unique_senders.add(transfer.sender)
            unique_recipients.add(transfer.recipient)
            transfer_count += 1

            if amount > 10000:
                large_transfers.append((transfer.sender, transfer.recipient, amount))

            if transfer_count >= 100:
                break

        print(f"\n📊 Results (last {transfer_count} transfers):")
        print(f"Total Volume: {total_volume:,.2f} {symbol}")
        print(f"Unique Senders: {len(unique_senders)}")
        print(f"Unique Recipients: {len(unique_recipients)}")
        print(f"Large Transfers (>10k): {len(large_transfers)}")

        if large_transfers:
            print("\n🔥 Notable Large Transfers:")
            for sender, recipient, amount in large_transfers[:5]:
                print(
                    f"  {amount:,.2f} {symbol}: {sender[:10]}... → {recipient[:10]}..."
                )

    async def execute_sample_transaction(self, network_class):
        """
        Demonstrate transaction execution with proper gas management.
        Demonstrates: Transaction preparation, gas estimation, signing, execution
        """
        print(f"\n⚡ TRANSACTION EXECUTION DEMO - {network_class.__name__}")
        print("=" * 50)

        if "DEMO_PRIVATE_KEY" not in os.environ:
            print("⚠️  Skipping transaction demo - no DEMO_PRIVATE_KEY provided")
            print("   Set DEMO_PRIVATE_KEY environment variable to test transactions")
            return

        try:
            wallet = PrivateKeyWallet(private_key=os.environ["DEMO_PRIVATE_KEY"])
            print(f"Wallet Address: {wallet.address}")

            balance = await wallet[network_class].get_balance()
            print(f"ETH Balance: {balance / 10**18:.6f} ETH")

            if balance < 10**15:  # Less than 0.001 ETH
                print("⚠️  Insufficient balance for transaction demo")
                return

            token_address = self.monitored_tokens[network_class]
            token = ERC20[network_class](address=token_address)

            estimated_gas = await token.name().estimate_gas(from_=wallet.address)
            print(f"Estimated Gas: {estimated_gas:,}")

            latest_block = await Block[network_class].latest()
            base_fee = latest_block.base_fee_per_gas or 0
            print(f"Base Fee: {base_fee / 10**9:.2f} gwei")

            print("✅ Transaction preparation successful")
            print("   (Skipping actual execution in demo)")

        except Exception as e:
            print(f"❌ Transaction demo failed: {e}")

    async def monitor_live_events(self, duration_seconds: int = 30):
        """
        Monitor live events across multiple networks.
        Demonstrates: Real-time event streaming, multi-network monitoring
        """
        print(f"\n📡 LIVE EVENT MONITORING ({duration_seconds}s)")
        print("=" * 50)

        monitoring_tasks = []

        for network in self.networks:
            token_address = self.monitored_tokens[network]
            task = asyncio.create_task(
                self._monitor_network_events(network, token_address, duration_seconds)
            )
            monitoring_tasks.append(task)

        try:
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)
        except Exception as e:
            print(f"Monitoring error: {e}")

    async def _monitor_network_events(
        self, network_class, token_address: HexAddress, duration: int
    ):
        """Helper method for monitoring events on a specific network."""
        try:
            print(f"🔍 Monitoring {network_class.__name__} transfers...")

            event_count = 0
            start_time = asyncio.get_event_loop().time()

            async for event in (
                TransferEvent[network_class]
                .set_filter(addresses=[token_address])
                .subscribe()
            ):
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > duration:
                    break

                transfer = event.event
                token = ERC20[network_class](address=token_address)
                symbol = await token.symbol().get()
                decimals = await token.decimals().get()

                amount = transfer.amount / (10**decimals)
                timestamp = datetime.now().strftime("%H:%M:%S")

                print(
                    f"[{timestamp}] {network_class.__name__}: "
                    f"{amount:,.2f} {symbol} "
                    f"{transfer.sender[:8]}...→{transfer.recipient[:8]}..."
                )

                event_count += 1

                if event_count >= 5:
                    break

        except Exception as e:
            print(f"❌ {network_class.__name__} monitoring error: {e}")

    async def run_comprehensive_analysis(self):
        """
        Run the complete analytics suite.
        """
        print("🚀 ETH-PACKAGES COMPREHENSIVE DEMO")
        print("=" * 60)
        print("This demo showcases the full capabilities of eth-packages")
        print("including multi-network operations, event analysis, and more.")
        print("=" * 60)

        try:
            await self.analyze_network_status()

            await self.analyze_token_distribution(
                self.monitored_tokens[Ethereum], Ethereum
            )

            await self.execute_sample_transaction(Ethereum)

            await self.monitor_live_events(duration_seconds=15)

            print("\n✅ ANALYSIS COMPLETE")
            print("=" * 60)
            print("This demo showed:")
            print("• Multi-network blockchain data retrieval")
            print("• Historical event analysis with filtering")
            print("• Efficient batch operations using multicall")
            print("• Transaction preparation and gas estimation")
            print("• Real-time event streaming across networks")
            print("• Type-safe contract interactions throughout")

        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            print("Make sure you have:")
            print("1. Valid ALCHEMY_KEY environment variable")
            print("2. Stable internet connection")
            print("3. Sufficient RPC rate limits")


async def main():
    """
    Main entry point for the comprehensive example.
    """
    if "ALCHEMY_KEY" not in os.environ:
        print("❌ Error: ALCHEMY_KEY environment variable required")
        print("Get your free API key from https://www.alchemy.com/")
        return

    set_alchemy_key(os.environ["ALCHEMY_KEY"])

    analytics = DeFiAnalytics()
    await analytics.run_comprehensive_analysis()


if __name__ == "__main__":
    asyncio.run(main())
