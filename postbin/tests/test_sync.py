from postbin import postSync

def test_sync():
    try:
        result = postSync("TestSync on repo https://github.com/dragdev-studios/postbin - Please ignore",
                          url="http://51.195.138.2:8888")
    except Exception as e:
        raise AssertionError from e  #
    assert result.startswith("http")

def test_sync_failure():
    class NonStringable(str):
        def __str__(self):
            raise NotImplementedError

        def __repr__(self):
            raise NotImplementedError
    try:
        result = postSync(NonStringable(), url="http://51.195.138.2:8888")
    except:
        return True
    else:
        assert not result.startswith("http")
