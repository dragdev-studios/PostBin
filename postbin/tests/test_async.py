from asyncio import get_event_loop

from postbin import postAsync


def test_async():
    loop = get_event_loop()
    try:
        assert loop.run_until_complete(
            postAsync("TestSync on repo https://github.com/dragdev-studios/postbin - Please ignore",
                      url="http://51.195.138.2:8888")
        ).startswith("http")
    except Exception as e:  #
        raise AssertionError from e


# noinspection PyTypeChecker
def test_sync_failure():
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
