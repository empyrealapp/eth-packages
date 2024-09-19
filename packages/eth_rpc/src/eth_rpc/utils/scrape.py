import httpx

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
}


async def get_contract():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://etherscan.io/address/0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b#code',
            headers=headers,
        )
    return response.text


async def load():
    from bs4 import BeautifulSoup

    html = get_contract()
    soup = BeautifulSoup(html)
    index = soup.text.find('Contract Name:')
    contract_name = soup.text[index: index + 200].split('\n')[2]
