import json

import httpx
from eth_typing import HexAddress


def get_abi(
    address: HexAddress, api_key: str, api_url: str = "https://api.etherscan.io/api"
):
    response = httpx.get(
        f"{api_url}?module=contract&action=getabi&address={address}&apikey={api_key}"
    )
    return json.loads(response.json()["result"])
