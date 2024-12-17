from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
from base58 import b58decode, b58encode
from .core.keypair import Keypair
from .core.publickey import PublicKey
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from .core.instructions import Instruction, AccountMeta
from .core.message import (
    Message,
    MessageHeader,
    CompiledInstruction,
    encode_length,
    decode_length
)

PACKET_DATA_SIZE = 1232
DEFAULT_SIGNATURE = bytes([0] * 64)


@dataclass
class PKSigPair:
    public_key: PublicKey
    signature: bytes | None = None


class Transaction:
    def __init__(self, **config):
        self.fee_payer: PublicKey = config.get("fee_payer")
        self.nonce_info = config.get("nonce_info")
        self.recent_blockhash = config.get("recent_blockhash")
        self.signers: list[PublicKey] | list[Keypair] = config.get("signers")
        self.instructions: list[Instruction] = []
        self.signatures: list[PKSigPair] = config.get("signatures", [])
        if "instructions" in config:
            instructions: Instruction = config.get("instructions")
            if (
                type(instructions) is list and
                isinstance(instructions[0], Instruction)
            ):
                self.instructions.extend(config["instructions"])
            else:
                raise TypeError((
                                "instructions keyword argument"
                                "must be a list of Instruction objects"
                                ))
            
        def to_public_key(signer: PublicKey | Keypair) -> PublicKey:
            if isinstance(signer, Keypair):
                return signer.public_key
            elif isinstance(signer, PublicKey):
                return signer
            else:
                raise TypeError(("The argument must be either "
                                "PublicKey or Keypair object."))

        pk_sig_pairs: List[PKSigPair] = [PKSigPair(
            public_key=to_public_key(signer)
        ) for signer in self.signers]

        if not self.signatures:
            self.signatures = pk_sig_pairs

        self._message: Message = None
        self.json = None

    def _to_json(self):
        return {
            "recentBlockhash": self.recent_blockhash if hasattr(self, 'recent_blockhash') else None,
            "feePayer": self.fee_payer.base58_encode() if hasattr(self, 'fee_payer') else None,
            "nonceInfo": {
                "nonce": self.nonce_info.nonce,
                "nonceInstruction": self.nonce_info.nonce_instruction._to_json()
            } if self.nonce_info else None,
            "instructions": [instruction._to_json() for instruction in self.instructions],
            "signers": [signature.public_key.base58_encode() for signature in self.signatures]
        }
    
    def compile_transaction(self) -> bytes:
        # Reference: https://github.com/solana-labs/solana-web3.js/blob/a1fafee/packages/library-legacy/src/transaction/legacy.ts#L367
        if self._message and self._to_json() == self.json:
            return self._message.serialize()

        if self.nonce_info:
            self.recent_blockhash = self.nonce_info.nonce

        if not self.instructions:
            raise AttributeError("No instructions provided.")

        if not self.recent_blockhash:
            raise AttributeError("Recent blockhash not provided.")

        if not self.signatures:
            raise AttributeError("No signatures found in the transaction.")

        if not self.fee_payer:
            self.fee_payer = self.signatures[0].public_key

        account_metas: List[AccountMeta] = []
        program_ids: List[str] = []

        for instruction in self.instructions:
            if not instruction.program_id:
                raise AttributeError(
                    "Invalid instruction (no program ID found): ",
                    instruction
                )
            account_metas.extend(instruction.keys)
            if str(instruction.program_id) not in program_ids:
                program_ids.append(str(instruction.program_id))

        for program_id in program_ids:
            account_metas.append(AccountMeta(
                public_key=PublicKey(program_id),
                is_signer=False,
                is_writable=False
            ))

        account_metas.sort(key=lambda account: (
            not account.is_signer, not account.is_writable))

        fee_payer_idx = 0
        seen: Dict[str, int] = {}
        uniq_metas: List[AccountMeta] = []

        for sig in self.signatures:
            public_key = str(sig.public_key)
            if public_key in seen:
                uniq_metas[seen[public_key]].is_signer = True
            else:
                uniq_metas.append(AccountMeta(sig.public_key, True, True))
                seen[public_key] = len(uniq_metas) - 1
                if sig.public_key == self.fee_payer:
                    fee_payer_idx = min(fee_payer_idx, seen[public_key])

        for a_m in account_metas:
            public_key = str(a_m.public_key)
            if public_key in seen:
                idx = seen[public_key]
                uniq_metas[idx].is_writable = uniq_metas[idx].is_writable or a_m.is_writable
            else:
                uniq_metas.append(a_m)
                seen[public_key] = len(uniq_metas) - 1
                if a_m.public_key == self.fee_payer:
                    fee_payer_idx = min(fee_payer_idx, seen[public_key])

        if fee_payer_idx == 1:
            uniq_metas = [AccountMeta(self.fee_payer, True, True)] + uniq_metas
        else:
            uniq_metas = (
                [uniq_metas[fee_payer_idx]] + uniq_metas[:fee_payer_idx] +
                uniq_metas[fee_payer_idx + 1:]
            )

        signed_keys: List[str] = []
        unsigned_keys: List[str] = []
        num_required_signatures = num_readonly_signed_accounts = num_readonly_unsigned_accounts = 0
        for a_m in uniq_metas:
            if a_m.is_signer:
                signed_keys.append(str(a_m.public_key))
                num_required_signatures += 1
                num_readonly_signed_accounts += int(not a_m.is_writable)
            else:
                num_readonly_unsigned_accounts += int(not a_m.is_writable)
                unsigned_keys.append(str(a_m.public_key))
        if not self.signatures:
            self.signatures = [PKSigPair(public_key=PublicKey(
                key), signature=None) for key in signed_keys]

        account_keys: List[str] = signed_keys + unsigned_keys
        account_indices: Dict[str, int] = {
            str(key): i for i, key in enumerate(account_keys)}
        compiled_instructions: List[CompiledInstruction] = [
            CompiledInstruction(
                accounts=[account_indices[str(a_m.public_key)]
                          for a_m in instr.keys],
                program_id_index=account_indices[str(instr.program_id)],
                data=b58encode(instr.data),
            )
            for instr in self.instructions
        ]
        message: Message = Message(
            MessageHeader(
                num_required_signatures=num_required_signatures,
                num_readonly_signed_accounts=num_readonly_signed_accounts,
                num_readonly_unsigned_accounts=num_readonly_unsigned_accounts,
            ),
            account_keys,
            compiled_instructions,
            self.recent_blockhash,
        )
        serialized_message: bytes = message.serialize()
        return serialized_message

    def sign(self, signatures: List[bytes] = None) -> None:
        sign_data: bytes = self.compile_transaction()
        if signatures:
            if len(signatures) != len(self.signers):
                raise ValueError(
                    "Number of signatures does not match number of signers."
                )
            for idx, signature in enumerate(signatures):
                if len(signature) != 64:
                    raise RuntimeError(
                        "Signature has invalid length: ",
                        signature
                    )
                self.signatures[idx].signature = signature
        else:
            for idx, signer in enumerate(self.signers):
                signature = signer.sign(sign_data).signature
                if len(signature) != 64:
                    raise RuntimeError(
                        "Signature has invalid length: ",
                        signature
                    )
                self.signatures[idx].signature = signature

    def verify_signatures(self, signed_data: bytes | None = None) -> bool:
        if signed_data is None:
            signed_data: bytes = self.compile_transaction()
        for sig_pair in self.signatures:
            if not sig_pair.signature:
                return False
            try:
                VerifyKey(bytes(sig_pair.public_key)).verify(
                    signed_data, sig_pair.signature)
            except BadSignatureError:
                return False
        return True

    def serialize(self) -> bytes:
        if not self.signatures:
            raise AttributeError("Transaction has not been signed.")

        sign_data: bytes = self.compile_transaction()
        if not self.verify_signatures(sign_data):
            raise AttributeError("Transaction has not been signed correctly.")

        if len(self.signatures) >= 64 * 4:
            raise AttributeError("Too many signatures to encode.")

        wire_transaction = bytearray()
        signature_count = encode_length(len(self.signatures))
        wire_transaction.extend(signature_count)
        for sig_pair in self.signatures:
            if sig_pair.signature and len(sig_pair.signature) != 64:
                raise RuntimeError(
                    "Signature has invalid length: ", sig_pair.signature
                )

            if not sig_pair.signature:
                wire_transaction.extend(bytearray(64))
            else:
                wire_transaction.extend(sig_pair.signature)

        wire_transaction.extend(bytearray(sign_data))

        if len(wire_transaction) > PACKET_DATA_SIZE:
            raise RuntimeError(
                "Transaction too large: ",
                len(wire_transaction)
            )
        return bytes(wire_transaction)

    def add_instructions(self, *instructions: Instruction) -> None:
        for instr in instructions:
            if not isinstance(instr, Instruction):
                raise ValueError(
                    "Argument not an instruction object: ",
                    instr
                )
            self.instructions.append(instr)

    @classmethod
    def populate(self, message: Message, signatures: List[bytes], signers: List[Keypair]) -> Transaction:
        decoded_signatures = list(map(lambda x: PKSigPair(
            public_key=message.account_keys[x[0]],
            signature=None if x[1] == b58encode(
                DEFAULT_SIGNATURE) else b58decode(x[1])
        ), enumerate(signatures)))

        instructions: List[Instruction] = []
        for instruction in message.instructions:

            acc_metas: List[AccountMeta] = []
            for account in instruction.accounts:
                pubkey = message.account_keys[account]
                acc_metas.append(AccountMeta(
                    public_key=pubkey,
                    is_signer=message.is_account_signer(account) or pubkey in [
                        x.public_key for x in decoded_signatures],
                    is_writable=message.is_account_writable(account)
                ))

            instructions.append(Instruction(
                program_id=message.account_keys[instruction.program_id_index],
                keys=acc_metas,
                data=b58decode(instruction.data)
            ))

        fee_payer = message.account_keys[0] if message.header.num_required_signatures > 0 else None
        transaction =  Transaction(
            fee_payer=fee_payer,
            recent_blockhash=message.recent_blockhash,
            signatures=decoded_signatures,
            instructions=instructions,
            signers = signers
        )
        transaction._message = message
        transaction.json = transaction._to_json()
        return transaction

    @classmethod
    def from_buffer(self, buffer: bytes, signers: List[Keypair]) -> Transaction:
        # Reference: https://github.com/solana-labs/solana-web3.js/blob/a1fafee/packages/library-legacy/src/transaction/legacy.ts#L878
        if not isinstance(buffer, bytes):
            raise TypeError("Buffer must be a bytes object.")

        buffer_array: List[int] = list(buffer)
        signature_length = decode_length(buffer_array)

        signatures: List[bytes] = []
        for _ in range(signature_length):
            signature = bytes(buffer_array[:64])
            buffer_array = buffer_array[64:]
            signatures.append(b58encode(signature))

        message: Message = Message.from_buffer(bytes(buffer_array))
        return Transaction.populate(message, signatures, signers)
