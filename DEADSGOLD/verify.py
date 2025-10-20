import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

pubkey_b58    = "YourPublicKeyBase58Here"
signature_b58 = "SignatureBase58Here"
message_str   = "The exact message that was signed"

pubkey = base58.b58decode(pubkey_b58)     # bytes (32)
signature = base58.b58decode(signature_b58) # bytes (64)
message = message_str.encode('utf-8')

try:
    # VerifyKey.verify(msg, signature) will raise on bad sig
    vk = VerifyKey(pubkey)
    vk.verify(message, signature)   # raises BadSignatureError if invalid
    print("signature valid? True")
except BadSignatureError:
    print("signature valid? False")