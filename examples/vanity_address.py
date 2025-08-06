"""
Vanity Address Generator Example

This example demonstrates how to:
1. Generate Ethereum addresses with specific prefixes
2. Use eth-rpc's wallet functionality for key generation
3. Implement efficient address searching with performance considerations

Key concepts:
- Private key generation and address derivation
- Hexadecimal address matching
- Performance optimization for address mining

WARNING: This is for educational purposes. In production:
- Use secure random number generation
- Consider the computational cost of longer prefixes
- Store private keys securely
"""

import time
from eth_rpc.wallet import PrivateKeyWallet


def find_wallet_with_prefix(prefix_hex: int, max_attempts: int = 1000000):
    """
    Generate a wallet with an address starting with the specified hex prefix.
    
    This function repeatedly generates new wallets until it finds one whose
    address starts with the desired prefix. The difficulty increases exponentially
    with prefix length.
    
    Args:
        prefix_hex: Hexadecimal number to match at start of address (e.g., 0xBEEF)
        max_attempts: Maximum number of attempts before giving up
        
    Returns:
        PrivateKeyWallet with matching address prefix
        
    Raises:
        ValueError: If no matching address found within max_attempts
        
    Note:
        - Each additional hex character increases difficulty by ~16x
        - 0xBEEF (4 chars) takes ~65,536 attempts on average
        - 0xDEADBEEF (8 chars) would take ~4.3 billion attempts on average
    """
    prefix_str = hex(prefix_hex).lower()
    attempts = 0
    start_time = time.time()
    
    print(f"Searching for address starting with {prefix_str}...")
    print(f"Expected attempts: ~{16 ** (len(prefix_str) - 2):,}")
    
    while attempts < max_attempts:
        wallet = PrivateKeyWallet.create_new()
        attempts += 1
        
        if wallet.address.lower().startswith(prefix_str):
            elapsed = time.time() - start_time
            print(f"Found matching address after {attempts:,} attempts in {elapsed:.2f}s")
            print(f"Rate: {attempts / elapsed:.0f} addresses/second")
            return wallet
        
        if attempts % 10000 == 0:
            elapsed = time.time() - start_time
            rate = attempts / elapsed if elapsed > 0 else 0
            print(f"Attempt {attempts:,} - Rate: {rate:.0f} addr/sec")
    
    raise ValueError(f"No matching address found after {max_attempts:,} attempts")


def estimate_difficulty(prefix_hex: int):
    """
    Estimate the computational difficulty of finding a vanity address.
    
    Args:
        prefix_hex: Hexadecimal prefix to analyze
        
    Returns:
        Dictionary with difficulty metrics
    """
    prefix_str = hex(prefix_hex).lower()
    hex_chars = len(prefix_str) - 2  # Subtract '0x'
    
    expected_attempts = 16 ** hex_chars
    estimated_seconds = expected_attempts / 10000  # Assume 10k addr/sec
    estimated_hours = estimated_seconds / 3600
    
    return {
        "prefix": prefix_str,
        "hex_characters": hex_chars,
        "expected_attempts": expected_attempts,
        "estimated_seconds": estimated_seconds,
        "estimated_hours": estimated_hours,
    }


if __name__ == "__main__":
    examples = [
        ("BEEF", 0xBEEF),
        ("DEAD", 0xDEAD),
        ("CAFE", 0xCAFE),
        ("1337", 0x1337),
    ]
    
    print("VANITY ADDRESS GENERATOR")
    print("=" * 50)
    
    print("\nDifficulty estimates:")
    for name, prefix in examples:
        stats = estimate_difficulty(prefix)
        print(f"{name:>6}: ~{stats['expected_attempts']:>10,} attempts "
              f"(~{stats['estimated_hours']:.1f} hours)")
    
    print("\n" + "=" * 50)
    
    BEEF = 0xBEEF
    
    try:
        wallet = find_wallet_with_prefix(BEEF, max_attempts=100000)
        
        print("\n" + "=" * 50)
        print("SUCCESS!")
        print("=" * 50)
        print(f"Address: {wallet.address}")
        print(f"Private Key: {wallet.private_key}")
        print("\nIMPORTANT: Store this private key securely!")
        print("Anyone with the private key can control this address.")
        
    except ValueError as e:
        print(f"\n{e}")
        print("Try running again or increase max_attempts for better chances.")
        
    print("\nTips for vanity address generation:")
    print("- Shorter prefixes are much faster to find")
    print("- Use mixed case for easier prefixes (addresses are case-insensitive)")
    print("- Consider using dedicated vanity address tools for long prefixes")
    print("- Always verify the generated address matches your expectations")
