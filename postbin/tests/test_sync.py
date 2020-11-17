from postbin import postSync

def test_sync():
    try:
        result = postSync("TestSync on repo https://github.com/dragdev-studios/postbin - Please ignore")
    except Exception as e:
        raise AssertionError from e
    assert result.startswith("https://")

# def test_sync_failure():
#     try:
#         result = postSync("", url="http://example.com")  # sorry example.com
#     except:
#         return True
#     else:
#         assert not result.startswith("http")
