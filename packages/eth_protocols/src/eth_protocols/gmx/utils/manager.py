from typing import Literal

import httpx


async def get_tokens_address_dict(chain: Literal["arbitrum", "avalanche"] = "arbitrum"):
    """
    Query the GMX infra api for to generate dictionary of tokens available on v2

    Parameters
    ----------
    chain : avalanche | arbitrum

    Returns
    -------
    token_address_dict : dict
        dictionary containing available tokens to trade on GMX.

    """
    url = {
        "arbitrum": "https://arbitrum-api.gmxinfra.io/tokens",
        "avalanche": "https://avalanche-api.gmxinfra.io/tokens"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url[chain])

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            token_infos = response.json()['tokens']
        else:
            print(f"Error: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error: {e}")

    token_address_dict = {}

    for token_info in token_infos:
        token_address_dict[token_info['address']] = token_info

    return token_address_dict


def find_dictionary_by_key_value(outer_dict: dict, key: str, value: str):
    """
    For a given dictionary, find a value which matches a set of keys

    Parameters
    ----------
    outer_dict : dict
        dictionary to filter through.
    key : str
        keys to search for.
    value : str
        required key to match.

    """
    for inner_dict in outer_dict.values():
        if key in inner_dict and inner_dict[key] == value:
            return inner_dict
    return None


def apply_factor(value, factor):
    return value * factor / 10**30


def get_funding_factor_per_period(
    market_info: dict, is_long: bool, period_in_seconds: int,
    long_interest_usd: int, short_interest_usd: int
):
    """
    For a given market, calculate the funding factor for a given period

    Parameters
    ----------
    market_info : dict
        market parameters returned from the reader contract.
    is_long : bool
        direction of the position.
    period_in_seconds : int
        Want percentage rate we want to output to be in.
    long_interest_usd : int
        expanded decimal long interest.
    short_interest_usd : int
        expanded decimal short interest.

    """

    funding_factor_per_second = (
        market_info['funding_factor_per_second'] * 10**-28
    )

    long_pays_shorts = market_info['is_long_pays_short']

    if is_long:
        is_larger_side = long_pays_shorts
    else:
        is_larger_side = not long_pays_shorts

    if is_larger_side:
        factor_per_second = funding_factor_per_second * -1
    else:
        if long_pays_shorts:
            larger_interest_usd = long_interest_usd
            smaller_interest_usd = short_interest_usd

        else:
            larger_interest_usd = short_interest_usd
            smaller_interest_usd = long_interest_usd

        if smaller_interest_usd > 0:
            ratio = larger_interest_usd * 10**30 / smaller_interest_usd

        else:
            ratio = 0

        factor_per_second = apply_factor(ratio, funding_factor_per_second)

    return factor_per_second * period_in_seconds


def determine_swap_route(markets: dict, in_token: str, out_token: str):
    """
    Using the available markets, find the list of GMX markets required
    to swap from token in to token out

    Parameters
    ----------
    markets : dict
        dictionary of markets output by getMarketInfo.
    in_token : str
        contract address of in token.
    out_token : str
        contract address of out token.

    Returns
    -------
    list
        list of GMX markets to swap through.
    is_requires_multi_swap : TYPE
        requires more than one market to pass thru.

    """

    if in_token == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
        in_token = "0x47904963fc8b2340414262125aF798B9655E58Cd"

    if out_token == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
        out_token = "0x47904963fc8b2340414262125aF798B9655E58Cd"

    if in_token == "0xaf88d065e77c8cC2239327C5EDb3A432268e5831":
        gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            out_token
        )['gmx_market_address']
    else:
        gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            in_token
        )['gmx_market_address']

    is_requires_multi_swap = False

    if out_token != "0xaf88d065e77c8cC2239327C5EDb3A432268e5831" and \
            in_token != "0xaf88d065e77c8cC2239327C5EDb3A432268e5831":
        is_requires_multi_swap = True
        second_gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            out_token
        )['gmx_market_address']

        return [gmx_market_address, second_gmx_market_address], is_requires_multi_swap

    return [gmx_market_address], is_requires_multi_swap
