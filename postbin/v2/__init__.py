import asyncio
import logging

import aiohttp

from postbin.v2 import errors
from postbin.v2.errors import FailedTest, HTTPException

__version__ = "2.0.2a"
logging.warning("Postbin v2 has not yet been tested. Proceed with caution.")

_HEADERS = {"User-Agent": f"PostBin (https://github.com/dragdev-studios/postbin)/{__version__})"}
_FALLBACKS = [
    "https://haste.clicksminuteper.net",
    "https://hastebin.com",
    "https://mystb.in",
    "https://paste.pythondiscord.com",
    "https://haste.unbelievaboat.com",
    "https://hst.sh",
    "https://hasteb.in"
]


class ConfigOptions:
    """Class similar to **kwargs except takes up less room."""
    def __init__(self, **kwargs):
        self.test_urls_first = kwargs.pop("test_urls_first", False)
        self.return_full_url = kwargs.pop("return_full_url", True)
        self.ignore_http_errors = kwargs.pop("ignore_http_errors", False)


class AsyncHaste:
    """
    Haste operations, centralised.

    All methods of this class, that need to be, are async.
    """
    def __init__(self, t: str = None, session: aiohttp.ClientSession = None):
        """Creates the class. You shouldn't provide arguments (other than [t]ext)"""
        self.text = t
        self.session = session

    async def find_working_fallback(self, retries_per_url: int = 3):
        for url in _FALLBACKS:
            try:
                working = await self._head(url)
            except aiohttp.ClientResponseError:
                continue
            else:
                return url
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
                            async with session.get(url) as embedded_response:
                                last_response = embedded_response
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
        if not hasattr(self, "session") or not self.session or self.session.closed:
            return
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop.create_task(self.session.close(), name="PostBin cleanup task")
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
                    if response.status == 400:
                        data = await response.json()
                        if data["message"].lower() == "document exceeds maximum length.":
                            raise errors.TextTooLarge(response, message=data["message"] + "\nText: " + text)
                    elif response.status == 413:
                        raise errors.TextTooLarge(response, message="Text: " + text)
                    if response.status not in [200, 201]:  # removed 202: That is processing, not complete.
                        raise HTTPException(response)
                    return (await response.json())["key"]
        except (aiohttp.ServerDisconnectedError, aiohttp.ClientConnectorError, aiohttp.ClientOSError) as e:
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
            response = await self._head(url, retries)
            if not response:
                raise FailedTest(response)
        elif url == "auto":
            url = await self.find_working_fallback(retries)
        try:
            res = await asyncio.wait_for(self._post(url + "/documents", text or self.text, headers=_HEADERS),
                                         timeout=timeout)
        except Exception as e:
            if config.ignore_http_errors:
                return ""
            raise e
        return res if not config.return_full_url else url + "/" + res

    async def raw(self, key: str, *, url: str = "auto", timeout: float = 30.0, retries_per_url: int = 3,
                  encoding: str = "utf-8"):
        """
        Gets the raw text of a haste.

        Note that the parameters are different from post, in that they apply per URL fetched (if url is auto)

        :param key: the key (after .tld/, e.g hastebin.com/{key})
        :param url: the URL to find the haste from. if "auto" (default), will search all fallbacks for it.
        :param timeout: The timeout to request a document from the servers. If this is hit, instead of raising timeout error, just skips to the next one.
        :param retries_per_url: how may times to retry a URL (unless it returned 404). set to 0 to disable.
        :param encoding: The encoding to encode the text in. Defaults to utf-8. | Version added: 2.0.2a
        :return: the found text, __or None if not found__.
        """
        async def get(URL):
            async with session.get(URL + "/raw/" + key) as response:
                if response.status == 404:
                    return None
                if response.status == 200:
                    return await response.text(encoding=encoding or "utf-8", errors="replace")

        session = await self._get_session()
        if url.lower() == "auto":
            for _URL in _FALLBACKS:
                res = await get(_URL)
                if res:
                    return res
            return None
        return await get(url + "/raw/" + key)


async def postAsync(text: str, *, url: str = "auto", config: ConfigOptions = ConfigOptions(), timeout: float = 30.0,
                    retries: int = 3):
    """Alias function for AsyncHaste().post(...)"""
    return await AsyncHaste().post(text, url=url, config=config, timeout=timeout, retries=retries)


def postSync(text: str, *, url: str = "auto", config: ConfigOptions = ConfigOptions(), timeout: float = 30.0,
             retries: int = 3):
    """
    Alias function for SyncHaste().post(...).

    WARNING! This relies on the asyncio event loop NOT being in use. If it is, this returns an asyncio.Task
    """
    paster = AsyncHaste(text)
    f = paster.post(None, config, timeout=timeout, retries=retries, url=url)
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.create_task(f, name="Paste-" + str(id(paster)))
    return loop.run_until_complete(f)

# this DOES NOT WORK?! WHY?!
# def set_fallbacks(new: list):
#     """
#     Sets your fallbacks to the provided list.
#     Note that this overwrites the active fallback selection system.
#
#     Some validation is performed, like ensuring there's at least 3 fallbacks, and one known one.
#
#     :param new: The new list of fallback URLs.
#     :raises ValueError: Insufficient count of fallbacks
#     :raises LookupError: No verified fallback was in the list.
#     :return: None
#     """
#     # global _FALLBACKS  # I HATE globals but this seems like the only way for this scope.
#     if len(new) < 3:
#         raise ValueError("New fallback list must have at least 3 entries")
#     if len(new) > 10:
#         logging.warning("There's a lot of fallbacks here. Note that you only really ever need 4 or 5 in total.")
#     cleaned = []
#     for url in new:
#         if url.endswith("/"):
#             url = url[:-1]
#         if not url.startswith("https"):
#             logging.warning("Provided fallback URL \"{}\" is not HTTPS secured.".format(url))
#         cleaned.append(url)
#     global _FALLBACKS
#     _FALLBACKS = new
#     return
