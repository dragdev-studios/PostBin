import asyncio
import logging

import aiohttp

from postbin.v2 import errors
from postbin.v2.errors import FailedTest, HTTPException

__version__ = "2.0.1a"
logging.warning("Postbin v2 has not yet been tested. Proceed with caution.")

_HEADERS = {"User-Agent": f"PostBin(https://github.com/dragdev-studios/postbin)/{__version__}"}
_FALLBACKS = [
    "https://hastebin.com",
    "https://mystb.in",
    "https://paste.pythondiscord.com",
    "https://haste.unbelievaboat.com",
    "https://hst.sh"
]
# _HASTE_URLS_FOR_REGEX = '|'.join(_FALLBACKS[8:]).replace(".", "\\.")
# _HASTE_URLS_RAW = "(https://|http://)?({})/(raw/)?(?P<key>.+)".format(_HASTE_URLS_FOR_REGEX)
# _HASTE_REGEX = re.compile(_HASTE_URLS_RAW)

class ConfigOptions:
    """Class similar to **kwargs except takes up less room."""
    def __init__(self, **kwargs):
        self.test_urls_first      = kwargs.pop("test_urls_first", False)
        self.return_full_url      = kwargs.pop("return_full_url", True)


class AsyncHaste:
    """
    Haste operations, centralised.

    All methods of this class, that need to be, are async.
    """
    def __init__(self, t: str=None, s: int=None, url: str=None, *, verbose: int = 1, session: aiohttp.ClientSession = None):
        """Creates the class. You shouldn't provide arguments (other than [t]ext)"""
        self.url = url
        self.text = t
        self.status = s
        self.verbose = verbose
        self.session = session

    async def find_working_fallback(self, retries_per_url: int = 3):
        for url in _FALLBACKS:
            try:
                working = await self._head(url)
            except:
                continue
            else:
                return url
        else:
            raise ConnectionError("Unable to connect anywhere. Are you sure you're online?")

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _head(self, url, retries=3):
        last_response = None
        for i in range(retries+1):
            try:
                async with await self._get_session() as session:
                    async with session.head(url) as response:
                        # some services may not support HEAD requests,so we can just GET if not.
                        # We never download the content anyway, its more saving the server's bandwidth.
                        # Because we're not assholes.
                        if response.status == 405:
                            async with session.get(url) as response:
                                last_response = response
                                response.raise_for_status()
                                return True
                        else:
                            last_response = response
                            response.raise_for_status()
                            return True
            except:
                await asyncio.sleep(2.5*i)
                continue
        return response

    def __del__(self):
        self.close_session()

    def close_session(self):
        """
        Simple method that performs cleanup of the class.

        This is called automatically by garbage collection (__del__)

        :return: Optional[asyncio.Task] - if task is provided, it is closing the aiohttp session.
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.create_task(self.session.close(), name="PostBin cleanup task")
        else:
            loop.run_until_complete(self.session.close())  # this could cause issues with other async apps
                                                           # if the edge-case where it tries to do the same as us
                                                           # but we got the loop first
            return

    async def _post(self, url, text, **kwargs):
        try:
            async with await self._get_session() as session:
                async with session.post(url,data=text, **kwargs) as response:
                    retry_after = response.headers.get("retry_after") or response.headers.get("x-retry-after")
                    if response.status == 429 and retry_after:
                        await asyncio.sleep(float(retry_after))
                        return await self._post(url, text, **kwargs)
                    if response.status not in [200, 201]:  # removed 202: That is processing, not complete.
                        raise HTTPException(response)
                    return (await response.json())["key"]
        except (aiohttp.ServerDisconnectedError, aiohttp.ClientConnectorError) as e:
            raise errors.OfflineServer(None, message="Exception while connecting - assuming dead host.") from e

    async def post(self, text: str = None, config: ConfigOptions = ConfigOptions(), *, timeout: float = 30.0,
                   retries: int = 3, url: str = "auto"):
        """
        Creates a haste URL, returning the URL of the new haste.

        :param text: The text to post. Defaults to the text provided/set in self.__init__.
        :param config: The configuration.
        :param timeout: After how long to stop trying to post to a certain URL, and find a fallback.
        :param retries: How many times to attempt to post to the current URL before finding a fallback.
        :param url: The BASE url to post to. If "auto" (default), this will try each url until it works.
        :return: the completed URL or just the key if specified in Config.
        """
        session = await self._get_session()
        if url != "auto" and config.test_urls_first:
            response=await self._head(url, retries)
            if not response:
                raise FailedTest(response)
        elif url == "auto":
            url = await self.find_working_fallback(retries)
        res = await asyncio.wait_for(self._post(url+"/documents", text or self.text, headers=_HEADERS), timeout=timeout)
        return res if not config.return_full_url else url+"/"+res

    async def raw(self, key: str, *, url: str = "auto", timeout: float = 30.0, retries_per_url: int = 3):
        """
        Gets the raw text of a haste.

        Note that the parameters are different from post, in that they apply per URL fetched (if url is auto)

        :param key: the key (after .tld/, e.g hastebin.com/{key})
        :param url: the URL to find the haste from. if "auto" (default), will search all fallbacks for it.
        :param timeout: The timeout to request a document from the servers. If this is hit, instead of raising timeout error, just skips to the next one.
        :param retries_per_url: how may times to retry a URL (unless it returned 404). set to 0 to disable.
        :return: the found text, __or None if not found__.
        """
        async def get(URL):
            async with session.get(URL + "/raw/" + key) as response:
                if response.status == 404:
                    return None
                elif response.status == 200:
                    return await response.text(encoding="utf-8", errors="replace")
        session = await self._get_session()
        if url.lower() == "auto":
            for url in _FALLBACKS:
                res = await get(url)
                if res: return res
            return None
        else:
            return await get(url+"/raw/"+key)
#
