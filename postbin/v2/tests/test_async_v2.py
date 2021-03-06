from asyncio import get_event_loop

import pytest

from .. import AsyncHaste, ConfigOptions
from ..errors import OfflineServer, TextTooLarge

loop = get_event_loop()


def post_test():
    from random import shuffle
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffle(chars)

    try:
        cls = AsyncHaste(''.join(chars))
    except:
        raise AssertionError
    else:
        result = loop.run_until_complete(cls.post())
        assert result.startswith("http")

def get_test():
    from random import shuffle
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffle(chars)

    try:
        cls = AsyncHaste(''.join(chars))
    except:
        raise AssertionError
    else:
        result = loop.run_until_complete(cls.post(config=ConfigOptions(return_full_url=False)))
        assert result.startswith("http")
        result2 = loop.run_until_complete(cls.raw(result))
        assert result is not None and result == chars


def test_with_fake_url():  #
    from random import shuffle
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    shuffle(chars)
    chars = ''.join(chars)

    try:
        cls = AsyncHaste(chars)
    except:
        raise AssertionError
    else:
        with pytest.raises(OfflineServer) as exec_info:
            result = loop.run_until_complete(cls.post(url=f"http://{chars}.com"))
        try:
            assert not result.startswith("http")
        except UnboundLocalError:
            assert exec_info.errisinstance(OfflineServer)


def test_large_payload():
    text = "." * 100_000_000
    try:
        cls = AsyncHaste(text)
    except:
        raise AssertionError
    else:
        with pytest.raises(TextTooLarge) as exec_info:
            result = loop.run_until_complete(cls.post())
        try:
            assert not result.startswith("http")
        except UnboundLocalError:
            assert exec_info.errisinstance(TextTooLarge)
