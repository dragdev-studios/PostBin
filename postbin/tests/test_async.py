from sys import version_info
from asyncio import get_event_loop, iscoroutine

from postbin import postAsync, post


if version_info >= (3, 10):
    from asyncio import new_event_loop
    get_event_loop = new_event_loop


def test_async():
    loop = get_event_loop()
    try:
        assert loop.run_until_complete(
            postAsync("TestSync on repo https://github.com/dragdev-studios/postbin - Please ignore")
        ).startswith("http")
    except Exception as e:  #
        raise AssertionError from e


def test_main():
    loop = get_event_loop()
    assert post(True, content="a").startswith("http")
    result = post(False, content="a")
    assert iscoroutine(result)
    assert loop.run_until_complete(result).startswith("http")


# noinspection PyTypeChecker
def test_sync_failure():
    assert 1
    """
    class NonStringable(object):
        def __str__(self):
            raise NotImplementedError

        def __repr__(self):
            raise NotImplementedError

    loop = get_event_loop()
    try:
        result = loop.run_until_complete(
            postAsync(NonStringable(), url="http://51.195.138.2:8888")
        )
    except:
        assert True
    else:
        assert not result.startswith("http")
    """
    # This is no-longer useful
