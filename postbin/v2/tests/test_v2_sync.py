import pytest

from .. import postSync
from ..errors import OfflineServer, TextTooLarge


def post_test():
    from random import shuffle
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffle(chars)
    result = postSync(''.join(chars))
    assert result.startswith("http")

# def get_test():
#     from random import shuffle
#     chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
#     shuffle(chars)
#     result = postSync(''.join(chars), config=ConfigOptions(return_full_url=False))
#     assert result.startswith("http")
#     result2 = loop.run_until_complete(cls.raw(result))
#     assert result is not None and result == chars
# Not yet possible with v2

def test_with_fake_url():  #
    from random import shuffle
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffle(chars)
    chars = ''.join(chars)
    with pytest.raises(OfflineServer) as exec_info:
        result = postSync(chars, url=f"http://{chars}.com")
    try:
        assert not result.startswith("http")
    except UnboundLocalError:
        assert exec_info.errisinstance(OfflineServer)


def test_large_payload():
    text = "." * 100_000_000
    with pytest.raises(TextTooLarge) as exec_info:
        result = postSync(text)
    try:
        assert not result.startswith("http")
    except UnboundLocalError:
        assert exec_info.errisinstance(TextTooLarge)

# def test_settable_fallbacks():
#     original = _FALLBACKS.copy()
#     srted = list(sorted(_FALLBACKS, key=lambda x: len(x)))
#     set_fallbacks(srted)
#     assert _FALLBACKS == srted
#     set_fallbacks(original)
#     assert _FALLBACKS == original
