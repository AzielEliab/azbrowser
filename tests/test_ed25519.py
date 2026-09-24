"""RFC 8032 Ed25519 vector. Navigation uses verify only."""

from azbrowser.ed25519 import node_sign, public_from_seed, verify

SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
PUBLIC = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
SIG = bytes.fromhex(
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
    "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
)


def test_rfc8032_empty_message():
    assert public_from_seed(SEED) == PUBLIC
    assert node_sign(SEED, b"") == SIG
    assert verify(PUBLIC, b"", SIG) is True
    assert verify(PUBLIC, b"x", SIG) is False


def test_verify_rejects_short_key():
    assert verify(b"\x00" * 31, b"m", b"\x00" * 64) is False
