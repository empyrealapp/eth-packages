from binascii import hexlify, unhexlify
from functools import partial
from typing import Callable, cast

from eth_rpc import get_selected_wallet
from eth_rpc._transport import _force_get_global_rpc
from eth_rpc.contract.function import EthCallArgs
from eth_rpc.rpc import RPCMethod
from eth_rpc.types import CallWithBlockArgs, RawTransaction
from eth_rpc.utils.dual_async import run
from eth_typing import HexStr
from pydantic import BaseModel, PrivateAttr

from .data_pack import SignedArgs, make_response
from .envelope import TransactionCipher

# Should transactions which deploy contracts be encrypted?
ENCRYPT_DEPLOYS = False

# Number of epochs to keep public keys for
EPOCH_LIMIT = 5


class CalldataPublicKey(BaseModel):
    epoch: int
    checksum: HexStr
    signature: HexStr
    key: HexStr


class CalldataPublicKeyManager(BaseModel):
    _keys: list[CalldataPublicKey] = PrivateAttr(default_factory=list)

    def _trim_and_sort(self, newest_epoch: int):
        self._keys = sorted(
            [v for v in self._keys if v.epoch >= newest_epoch - EPOCH_LIMIT],
            key=lambda o: o.epoch,
        )[-EPOCH_LIMIT:]

    @property
    def newest(self):
        if self._keys:
            return self._keys[-1]
        return None

    def add(self, pk: CalldataPublicKey):
        if self._keys:
            if self.newest.epoch < pk.epoch:
                self._keys.append(pk)
            self._trim_and_sort(pk.epoch)
        else:
            self._keys.append(pk)


def _should_intercept(method: RPCMethod, params: tuple):
    if not ENCRYPT_DEPLOYS:
        if method.name in ("eth_sendRawTransaction", "eth_estimateGas"):
            # When 'to' flag is missing, we assume it's a deployment
            if hasattr(params[0], "params"):
                if not params[0].params.to:
                    return False
    return method.name in ("eth_estimateGas", "eth_sendRawTransaction", "eth_call")


def _make_envelope(pk, data):
    c = TransactionCipher(peer_pubkey=pk.key, peer_epoch=pk.epoch)
    if isinstance(data, bytes):
        data_bytes = data
    elif isinstance(data, str):
        if len(data) < 2 or data[:2] != "0x":
            raise ValueError("Data is not hex encoded!", data)
        data_bytes = unhexlify(data[2:])
    else:
        raise TypeError("Invalid 'data' type", type(data))
    envelope = c.make_envelope(data_bytes)
    return c, envelope


def _encrypt_tx_params(
    pk: CalldataPublicKey, data: bytes | str | HexStr | RawTransaction
):
    c = TransactionCipher(peer_pubkey=pk.key, peer_epoch=pk.epoch)
    if isinstance(data, RawTransaction):
        data_bytes = data.signed_tx
        return c, [data.signed_tx]
    elif isinstance(data, bytes):
        data_bytes = data
    elif isinstance(data, str):
        if len(data) < 2 or data[:2] != "0x":
            raise ValueError("Data is not hex encoded!", data)
        data_bytes = unhexlify(data[2:])
    else:
        raise TypeError("Invalid 'data' type", type(data))

    encrypted_data = c.encrypt(data_bytes)
    return c, HexStr("0x" + hexlify(encrypted_data).decode("ascii"))


def sapphire_middleware(
    method: RPCMethod, make_request: Callable, is_async: bool = False
):  # noqa: C901
    """
    Transparently encrypt the calldata for:

     - eth_estimateGas
     - eth_sendTransaction
     - eth_call

    The calldata public key, which used to derive a shared secret with an
    ephemeral key, is retrieved upon the first request. This key is rotated by
    Sapphire every epoch, and only transactions encrypted with keys from the
    last 5 epochs are considered valid.

    Deployment transactions will not be encrypted, unless the global
    ENCRYPT_DEPLOYS flag is set. Encrypting deployments will prevent contracts
    from being verified.

    Pre-signed transactions can't be encrypted if submitted via this instance.
    """
    manager = CalldataPublicKeyManager()

    async def middleware(*params, sync: bool = False):
        if _should_intercept(method, params):
            if params:
                params = params[0]

            do_fetch = True
            pk = manager.newest
            while do_fetch:
                if not pk:
                    # If no calldata public key exists, fetch one
                    rpc = _force_get_global_rpc()
                    pk = rpc.oasis_calldata_public_key.sync()
                    if pk:
                        manager.add(pk)
                if not pk:
                    raise RuntimeError("Could not retrieve callDataPublicKey!")
                do_fetch = False

                if method.name == "eth_call":
                    _params = cast(EthCallArgs, params)
                    if not _params.params.from_ and _params.params.data:
                        c, data = _encrypt_tx_params(pk, _params.params.data)
                        _params.params.data = data
                        params = _params  # type: ignore
                    else:
                        c, envelope = _make_envelope(pk, _params.params.data)
                        wallet = get_selected_wallet()
                        if not wallet:
                            raise ValueError("Can not mock view call without a signer")
                        response = make_response(
                            _params.params.from_,
                            _params.params.to,
                            _params.params.data,
                            envelope,
                            wallet,
                        )
                        params = SignedArgs(req=response)  # type: ignore
                elif method.name == "eth_sendRawTransaction":
                    c, params = _encrypt_tx_params(pk, params)  # type: ignore
                elif method.name == "estimate_gas":
                    _params = cast(CallWithBlockArgs, params)  # type: ignore
                    if _params.params.data:
                        c, data = _encrypt_tx_params(pk, _params.params.data)
                        _params.params.data = data
                        params = _params  # type: ignore

                # We may encounter three errors here:
                #  'core: invalid call format: epoch too far in the past'
                #  'core: invalid call format: Tag verification failed'
                #  'core: invalid call format: epoch in the future'
                # We can only do something meaningful with the first!
                try:
                    if not is_async and sync:
                        result = make_request(params)
                    else:
                        result = await make_request(params)
                except ValueError as exc:
                    if (
                        "core: invalid call format: epoch too far in the past"
                        in exc.args[0]
                    ):
                        # force the re-fetch, and encrypt with new key
                        do_fetch = True
                        pk = None
                        continue
                    else:
                        raise exc

            # Only eth_call is decrypted
            if method.name == "eth_call" and result != "0x":
                decrypted = c.decrypt(unhexlify(result[2:]))
                result = HexStr("0x" + hexlify(decrypted).decode("ascii"))

            return result
        return make_request(*params)

    def sync_middleware(*params):
        return run(middleware, *params, sync=True)

    if is_async:
        return partial(middleware, sync=False)
    return sync_middleware
