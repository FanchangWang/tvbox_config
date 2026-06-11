import base64
import re

import dirtyjson
from Crypto.Cipher import AES


def is_json_obj(text: str) -> bool:
    try:
        data = dirtyjson.loads(text)
    except dirtyjson.error.Error:
        return False
    return isinstance(data, dict) and "spider" in data and "sites" in data


def extract_base64(data: str) -> str:
    m = re.search(r"[A-Za-z0-9]{8}\*\*", data)
    if m:
        return data[data.index(m.group()) + 10 :]
    return ""


def try_base64(data: str) -> str:
    extracted = extract_base64(data)
    if not extracted:
        return data
    try:
        return base64.b64decode(extracted).decode("utf-8")
    except (ValueError, TypeError, UnicodeDecodeError):
        return data


def pad_end(key: str) -> bytes:
    return (key + "0000000000000000"[: 16 - len(key)]).encode("utf-8")


def try_aes_cbc(data: str) -> str:
    data = re.sub(r"\s+", "", data)
    raw = bytes.fromhex(data).decode("utf-8", errors="replace").lower()

    key_str = raw[raw.index("$#") + 2 : raw.index("#$")]
    iv_str = raw[-13:]

    key = pad_end(key_str)
    iv = pad_end(iv_str)

    ct_start = data.index("2324") + 4
    ct_end = len(data) - 26
    ct = bytes.fromhex(data[ct_start:ct_end])

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ct)

    pad_len = plaintext[-1]
    if 0 < pad_len <= 16:
        plaintext = plaintext[:-pad_len]

    return plaintext.decode("utf-8")


def decode(data: str) -> str:
    if not data:
        raise ValueError("empty response")

    if is_json_obj(data):
        return data

    if "**" in data:
        data = try_base64(data)

    if re.sub(r"\s+", "", data).startswith("2423"):
        data = try_aes_cbc(data)

    return data
