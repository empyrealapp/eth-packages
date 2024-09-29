import ast

from eth_rpc.codegen import codegen

UNISWAP_UNIVERAL_ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "permit2", "type": "address"},
                    {"internalType": "address", "name": "weth9", "type": "address"},
                    {"internalType": "address", "name": "seaport", "type": "address"},
                    {"internalType": "address", "name": "nftxZap", "type": "address"},
                    {"internalType": "address", "name": "x2y2", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "foundation",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "sudoswap", "type": "address"},
                    {"internalType": "address", "name": "nft20Zap", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "cryptopunks",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "looksRare", "type": "address"},
                    {
                        "internalType": "address",
                        "name": "routerRewardsDistributor",
                        "type": "address",
                    },
                    {
                        "internalType": "address",
                        "name": "looksRareRewardsDistributor",
                        "type": "address",
                    },
                    {
                        "internalType": "address",
                        "name": "looksRareToken",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "v2Factory", "type": "address"},
                    {"internalType": "address", "name": "v3Factory", "type": "address"},
                    {
                        "internalType": "bytes32",
                        "name": "pairInitCodeHash",
                        "type": "bytes32",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "poolInitCodeHash",
                        "type": "bytes32",
                    },
                ],
                "internalType": "struct RouterParameters",
                "name": "params",
                "type": "tuple",
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {"inputs": [], "name": "ContractLocked", "type": "error"},
    {"inputs": [], "name": "ETHNotAccepted", "type": "error"},
    {
        "inputs": [
            {"internalType": "uint256", "name": "commandIndex", "type": "uint256"},
            {"internalType": "bytes", "name": "message", "type": "bytes"},
        ],
        "name": "ExecutionFailed",
        "type": "error",
    },
    {"inputs": [], "name": "FromAddressIsNotOwner", "type": "error"},
    {"inputs": [], "name": "InsufficientETH", "type": "error"},
    {"inputs": [], "name": "InsufficientToken", "type": "error"},
    {"inputs": [], "name": "InvalidBips", "type": "error"},
    {
        "inputs": [
            {"internalType": "uint256", "name": "commandType", "type": "uint256"}
        ],
        "name": "InvalidCommandType",
        "type": "error",
    },
    {"inputs": [], "name": "InvalidOwnerERC1155", "type": "error"},
    {"inputs": [], "name": "InvalidOwnerERC721", "type": "error"},
    {"inputs": [], "name": "InvalidPath", "type": "error"},
    {"inputs": [], "name": "InvalidReserves", "type": "error"},
    {"inputs": [], "name": "LengthMismatch", "type": "error"},
    {"inputs": [], "name": "NoSlice", "type": "error"},
    {"inputs": [], "name": "SliceOutOfBounds", "type": "error"},
    {"inputs": [], "name": "SliceOverflow", "type": "error"},
    {"inputs": [], "name": "ToAddressOutOfBounds", "type": "error"},
    {"inputs": [], "name": "ToAddressOverflow", "type": "error"},
    {"inputs": [], "name": "ToUint24OutOfBounds", "type": "error"},
    {"inputs": [], "name": "ToUint24Overflow", "type": "error"},
    {"inputs": [], "name": "TransactionDeadlinePassed", "type": "error"},
    {"inputs": [], "name": "UnableToClaim", "type": "error"},
    {"inputs": [], "name": "UnsafeCast", "type": "error"},
    {"inputs": [], "name": "V2InvalidPath", "type": "error"},
    {"inputs": [], "name": "V2TooLittleReceived", "type": "error"},
    {"inputs": [], "name": "V2TooMuchRequested", "type": "error"},
    {"inputs": [], "name": "V3InvalidAmountOut", "type": "error"},
    {"inputs": [], "name": "V3InvalidCaller", "type": "error"},
    {"inputs": [], "name": "V3InvalidSwap", "type": "error"},
    {"inputs": [], "name": "V3TooLittleReceived", "type": "error"},
    {"inputs": [], "name": "V3TooMuchRequested", "type": "error"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256",
            }
        ],
        "name": "RewardsSent",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "bytes", "name": "looksRareClaim", "type": "bytes"}
        ],
        "name": "collectRewards",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes", "name": "commands", "type": "bytes"},
            {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"},
        ],
        "name": "execute",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes", "name": "commands", "type": "bytes"},
            {"internalType": "bytes[]", "name": "inputs", "type": "bytes[]"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
        ],
        "name": "execute",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC1155BatchReceived",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC1155Received",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC721Received",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "int256", "name": "amount0Delta", "type": "int256"},
            {"internalType": "int256", "name": "amount1Delta", "type": "int256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "uniswapV3SwapCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {"stateMutability": "payable", "type": "receive"},
]
UNISWAP_SWAP_ROUTER = [
    {
        "inputs": [
            {"internalType": "address", "name": "_factory", "type": "address"},
            {"internalType": "address", "name": "_WETH9", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "inputs": [],
        "name": "WETH9",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "bytes", "name": "path", "type": "bytes"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "amountOutMinimum",
                        "type": "uint256",
                    },
                ],
                "internalType": "struct ISwapRouter.ExactInputParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInput",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "amountOutMinimum",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint160",
                        "name": "sqrtPriceLimitX96",
                        "type": "uint160",
                    },
                ],
                "internalType": "struct ISwapRouter.ExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
        ],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "bytes", "name": "path", "type": "bytes"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "amountInMaximum",
                        "type": "uint256",
                    },
                ],
                "internalType": "struct ISwapRouter.ExactOutputParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactOutput",
        "outputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "amountInMaximum",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint160",
                        "name": "sqrtPriceLimitX96",
                        "type": "uint160",
                    },
                ],
                "internalType": "struct ISwapRouter.ExactOutputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "exactOutputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "factory",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes[]", "name": "data", "type": "bytes[]"}],
        "name": "multicall",
        "outputs": [{"internalType": "bytes[]", "name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "refundETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "uint8", "name": "v", "type": "uint8"},
            {"internalType": "bytes32", "name": "r", "type": "bytes32"},
            {"internalType": "bytes32", "name": "s", "type": "bytes32"},
        ],
        "name": "selfPermit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "nonce", "type": "uint256"},
            {"internalType": "uint256", "name": "expiry", "type": "uint256"},
            {"internalType": "uint8", "name": "v", "type": "uint8"},
            {"internalType": "bytes32", "name": "r", "type": "bytes32"},
            {"internalType": "bytes32", "name": "s", "type": "bytes32"},
        ],
        "name": "selfPermitAllowed",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "nonce", "type": "uint256"},
            {"internalType": "uint256", "name": "expiry", "type": "uint256"},
            {"internalType": "uint8", "name": "v", "type": "uint8"},
            {"internalType": "bytes32", "name": "r", "type": "bytes32"},
            {"internalType": "bytes32", "name": "s", "type": "bytes32"},
        ],
        "name": "selfPermitAllowedIfNecessary",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
            {"internalType": "uint8", "name": "v", "type": "uint8"},
            {"internalType": "bytes32", "name": "r", "type": "bytes32"},
            {"internalType": "bytes32", "name": "s", "type": "bytes32"},
        ],
        "name": "selfPermitIfNecessary",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amountMinimum", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"},
        ],
        "name": "sweepToken",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "token", "type": "address"},
            {"internalType": "uint256", "name": "amountMinimum", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "feeBips", "type": "uint256"},
            {"internalType": "address", "name": "feeRecipient", "type": "address"},
        ],
        "name": "sweepTokenWithFee",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "int256", "name": "amount0Delta", "type": "int256"},
            {"internalType": "int256", "name": "amount1Delta", "type": "int256"},
            {"internalType": "bytes", "name": "_data", "type": "bytes"},
        ],
        "name": "uniswapV3SwapCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountMinimum", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"},
        ],
        "name": "unwrapWETH9",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountMinimum", "type": "uint256"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "feeBips", "type": "uint256"},
            {"internalType": "address", "name": "feeRecipient", "type": "address"},
        ],
        "name": "unwrapWETH9WithFee",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
    {"stateMutability": "payable", "type": "receive"},
]


def test_codegen():
    result = codegen(UNISWAP_SWAP_ROUTER, "UniversalRouter")
    ast.parse(result)

    result = codegen(UNISWAP_UNIVERAL_ROUTER_ABI, "UniversalRouter")
    ast.parse(result)
