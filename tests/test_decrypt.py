import base64
import json

from Crypto.Cipher import AES

from tvbox_config.decrypt import (
    decode,
    extract_base64,
    is_json_obj,
    pad_end,
    try_aes_cbc,
    try_base64,
)

_VALID_JSON = '{"spider": "s", "sites": [{"key": "k", "name": "n", "type": 3}]}'
_COMMENT_JSON = "// comment\n{\"spider\": \"s\", \"sites\": [{\"key\": \"k\", \"name\": \"n\", \"type\": 3}]}"


class TestIsJsonObj:
    def test_valid_json(self) -> None:
        assert is_json_obj(_VALID_JSON) is True

    def test_json_with_comments(self) -> None:
        assert is_json_obj(_COMMENT_JSON) is True

    def test_encrypted_hex_string(self) -> None:
        assert is_json_obj("2423313233343536") is False

    def test_random_text(self) -> None:
        assert is_json_obj("hello world") is False

    def test_empty_string(self) -> None:
        assert is_json_obj("") is False

    def test_invalid_partial_json(self) -> None:
        assert is_json_obj('{"spider": "s"') is False


class TestExtractBase64:
    def test_with_pattern(self) -> None:
        data = "prefix12345678**" + base64.b64encode(b"hello").decode()
        assert extract_base64(data) == base64.b64encode(b"hello").decode()

    def test_without_pattern(self) -> None:
        assert extract_base64("no pattern here") == ""

    def test_empty_string(self) -> None:
        assert extract_base64("") == ""


class TestTryBase64:
    def test_valid_base64(self) -> None:
        encoded = base64.b64encode(b'{"spider":"s","sites":[]}').decode()
        data = f"12345678**{encoded}"
        result = try_base64(data)
        assert is_json_obj(result) is True

    def test_invalid_base64(self) -> None:
        data = "12345678**!!!not-valid-base64!!"
        assert try_base64(data) == data

    def test_no_pattern_returns_original(self) -> None:
        data = "plain text"
        assert try_base64(data) == data


class TestPadEnd:
    def test_short_key(self) -> None:
        assert pad_end("abc") == b"abc0000000000000"

    def test_exact_16(self) -> None:
        assert pad_end("a" * 16) == b"a" * 16

    def test_empty_key(self) -> None:
        assert pad_end("") == b"0000000000000000"


class TestTryAesCbc:
    def _encrypt_for_test(self, plaintext: str, key_str: str, iv_str: str) -> str:
        key = pad_end(key_str)
        iv = pad_end(iv_str)

        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext.encode() + bytes([pad_len] * pad_len)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(padded)

        key_hex = key_str.encode().hex()
        ct_hex = ct.hex()
        iv_hex = iv_str.encode().hex()

        return f"2423{key_hex}2324{ct_hex}{iv_hex}"

    def test_decrypt_valid(self) -> None:
        plaintext = _VALID_JSON
        data = self._encrypt_for_test(plaintext, "a", "aaaaaaaaaaaaa")
        result = try_aes_cbc(data)
        assert result == plaintext

    def test_decrypt_with_different_key(self) -> None:
        plaintext = _VALID_JSON
        data = self._encrypt_for_test(plaintext, "testkey", "bbbbbbbbbbbbb")
        result = try_aes_cbc(data)
        assert result == plaintext

    def test_decrypt_result_is_valid_json(self) -> None:
        plaintext = _VALID_JSON
        data = self._encrypt_for_test(plaintext, "k", "ccccccccccccc")
        result = try_aes_cbc(data)
        data = json.loads(result)
        assert data["spider"]
        assert data["sites"]


class TestDecode:
    def test_plain_json(self) -> None:
        assert decode(_VALID_JSON) == _VALID_JSON

    def test_json_with_comments(self) -> None:
        assert decode(_COMMENT_JSON) == _COMMENT_JSON

    def test_empty_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="empty response"):
            decode("")

    def test_aes_cbc_decryption(self) -> None:
        key_str = "m"
        iv_str = "ddddddddddddd"
        plaintext = _VALID_JSON

        key = pad_end(key_str)
        iv = pad_end(iv_str)
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext.encode() + bytes([pad_len] * pad_len)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(padded)

        data = f"2423{key_str.encode().hex()}2324{ct.hex()}{iv_str.encode().hex()}"
        result = decode(data)
        assert result == plaintext

    def test_base64_decryption(self) -> None:
        encoded = base64.b64encode(_VALID_JSON.encode()).decode()
        data = f"12345678**{encoded}"
        result = decode(data)
        assert result == _VALID_JSON

    def test_aes_only_no_false_base64(self) -> None:
        """Data has ** pattern AND starts with 2423. ** is inside the AES region
        so try_base64 does not extract it (no 8-char prefix before **)."""
        plaintext = _VALID_JSON
        key_str = "n"
        iv_str = "eeeeeeeeeeeee"

        key = pad_end(key_str)
        iv = pad_end(iv_str)
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext.encode() + bytes([pad_len] * pad_len)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(padded)

        data = f"2423{key_str.encode().hex()}2324{ct.hex()}{iv_str.encode().hex()}"
        result = decode(data)
        assert result == plaintext

    def test_base64_only_no_aes(self) -> None:
        """No 2423 prefix → only base64 decode applied."""
        encoded = base64.b64encode(_VALID_JSON.encode()).decode()
        data = f"12345678**{encoded}"
        result = decode(data)
        assert result == _VALID_JSON
