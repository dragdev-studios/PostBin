from postbin import postAsync
from asyncio import get_event_loop

def test_async():
    loop = get_event_loop()
    try:
        assert loop.run_until_complete(
            postAsync("TestSync on repo https://github.com/dragdev-studios/postbin - Please ignore")
        ).startswith("https://")
    except Exception as e:
        raise AssertionError from e

# def test_sync_failure():
#     loop = get_event_loop()
#     try:
#         result = loop.run_until_complete(
#             postAsync("TestAsync on repo https://github.com/dragdev-studios/postbin - Please ignore")
#         )
#     except:
#         assert True
#     else:
#         assert not result.startswith("http")
