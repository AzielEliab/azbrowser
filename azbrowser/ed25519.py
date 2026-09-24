"""Ed25519 (RFC 8032) for mesh handle-key checks.

AZBrowser navigation calls ``verify`` only. ``node_sign`` exists so a test
or the local node stand-in can produce a signature. Navigate, resolve, and
the capability sandbox never call it and never accept a secret key.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = (-121665 * pow(121666, P - 2, P)) % P
I = pow(2, (P - 1) // 4, P)


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _inv(x: int) -> int:
    return pow(x, P - 2, P)


def _xrecover(y: int) -> int | None:
    y %= P
    xx = ((y * y - 1) * _inv((D * y * y + 1) % P)) % P
    x = pow(xx, (P + 3) // 8, P)
    if (x * x - xx) % P != 0:
        x = (x * I) % P
    if (x * x - xx) % P != 0:
        return None
    if x % 2 != 0:
        x = P - x
    return x


def _on_curve(x: int, y: int) -> bool:
    return (-x * x + y * y - 1 - D * x * x * y * y) % P == 0


def _add(pt: tuple[int, int, int, int], qt: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, z1, t1 = pt
    x2, y2, z2, t2 = qt
    a = ((y1 - x1) * (y2 - x2)) % P
    b = ((y1 + x1) * (y2 + x2)) % P
    c = (2 * t1 * t2 * D) % P
    d = (2 * z1 * z2) % P
    e = (b - a) % P
    f = (d - c) % P
    g = (d + c) % P
    h = (b + a) % P
    return (e * f % P, h * g % P, f * g % P, e * h % P)


def _scalarmult(pt: tuple[int, int, int, int], e: int) -> tuple[int, int, int, int]:
    q: tuple[int, int, int, int] = (0, 1, 1, 0)
    while e > 0:
        if e & 1:
            q = _add(q, pt)
        pt = _add(pt, pt)
        e >>= 1
    return q


def _encode(pt: tuple[int, int, int, int]) -> bytes:
    x, y, z, _t = pt
    zi = _inv(z)
    x = (x * zi) % P
    y = (y * zi) % P
    out = bytearray(y.to_bytes(32, "little"))
    if x & 1:
        out[31] |= 0x80
    return bytes(out)


def _decode(raw: bytes) -> tuple[int, int, int, int] | None:
    if len(raw) != 32:
        return None
    y_full = int.from_bytes(raw, "little")
    sign = (y_full >> 255) & 1
    y = y_full & ((1 << 255) - 1)
    if y >= P:
        return None
    x = _xrecover(y)
    if x is None:
        return None
    if (x & 1) != sign:
        x = P - x
    if not _on_curve(x, y):
        return None
    return (x, y, 1, (x * y) % P)


_BY = (4 * _inv(5)) % P
_BX = _xrecover(_BY)
if _BX is None:
    raise RuntimeError("ed25519 base point")
_B = (_BX, _BY, 1, (_BX * _BY) % P)


def _clamp_scalar(h0: bytes) -> int:
    a = int.from_bytes(h0, "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a


def public_from_seed(seed: bytes) -> bytes:
    """Public key for a 32-byte seed. Does not return the seed."""
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    a = _clamp_scalar(_sha512(seed)[:32])
    return _encode(_scalarmult(_B, a))


def node_sign(seed: bytes, message: bytes) -> bytes:
    """Sign as the local node. AZBrowser navigate/resolve must not call this."""
    if len(seed) != 32:
        raise ValueError("ed25519 seed must be 32 bytes")
    digest = _sha512(seed)
    a = _clamp_scalar(digest[:32])
    prefix = digest[32:]
    r = int.from_bytes(_sha512(prefix + message), "little")
    R = _encode(_scalarmult(_B, r))
    A = _encode(_scalarmult(_B, a))
    k = int.from_bytes(_sha512(R + A + message), "little")
    S = (r + k * a) % L
    return R + S.to_bytes(32, "little")


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """True when ``signature`` is an Ed25519 signature by ``public_key``."""
    if len(public_key) != 32 or len(signature) != 64:
        return False
    R = _decode(signature[:32])
    A = _decode(public_key)
    if R is None or A is None:
        return False
    S = int.from_bytes(signature[32:], "little")
    if S >= L:
        return False
    k = int.from_bytes(_sha512(signature[:32] + public_key + message), "little")
    left = _encode(_scalarmult(_B, S))
    right = _encode(_add(R, _scalarmult(A, k)))
    return left == right
