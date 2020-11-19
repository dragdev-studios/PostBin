## Note to editors and future/current contributors:  ##
# this file is very messy.                            #
# Any contributions to tidying it up would be greatly #
# appriciated.                                        #
#                                                     #
# - eek                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # #

import typing

try:
    import requests
    RR = requests.Response
except ImportError:
    requests = None
    RR = None

try:
    import aiohttp
    CR = aiohttp.ClientResponse
except ImportError:
    aiohttp = None
    CR = None
import time
import asyncio
__import__("logging").info("PostBin v2 is now in development. If you would prefer a more OOP style postbin, consider using"
                           " \"postbin.v2\".")

_FALLBACKS = [
    "https://haste.clicksminuteper.net",
    "https://hastebin.com",
    "https://paste.pythondiscord.com",
    "https://haste.unbelievaboat.com",
    "https://mystb.in",
    "https://hst.sh"
]
#_HASTE_URLS_FOR_REGEX = '|'.join(_FALLBACKS[8:]).replace(".", "\\.")
# _HASTE_URLS_RAW = "(https://|http://)?({})/(raw/)?(?P<key>.+)".format(_HASTE_URLS_FOR_REGEX)
# _HASTE_REGEX = re.compile(_HASTE_URLS_RAW)

# we don't need the above anymore - Will be removed in the future.


class ResponseError(Exception):
    """Generic class raised when contacting the server failed."""
    def __init__(self, response: typing.Union[RR,CR]):
        self.raw_response = response
        if isinstance(response, requests.Response):
            self.status = response.status_code
        else:
            self.status = response.status

class NoFallbacks(Exception):
    """Raised when no fallback could be contacted."""

class NoMoreRetries(NoFallbacks):
    """Raised when we ran out of attempts to post."""


def findFallBackSync(verbose: bool = True):
    """Tries to find a fallback URL, if hastebin.com isn't working."""
    if not requests:
        raise RuntimeError("You need to install requests to be able to use findFallBackSync.")
    with requests.Session() as session:
        n = 0
        for n, url in enumerate(_FALLBACKS, 1):
            if verbose:
                print(f"Trying service {n}/{len(_FALLBACKS)}",end="\r")
            try:
                response = session.post(url+"/documents", data="")
            except:
                if verbose:
                    print(f"Service {n}/{len(_FALLBACKS)} failed. Waiting {n*1.25}s before trying again.", end="\r")
                time.sleep(n*1.25)
                continue
            if response.status_code != 200:
                continue
            else:
                if verbose:
                    print(f"{url} ({n}) worked. Using that.")
                break
        else:
            if verbose:
                print("No functional URLs could be found. Are you sure you're online?")
            raise NoFallbacks()
    return url

async def findFallBackAsync(verbose: bool = True):
    """Same as findFallBackSync, but just async."""
    if not aiohttp:
        raise RuntimeError("You need to install aiohttp to be able to use findFallBackAsync.")
    async with aiohttp.ClientSession() as session:
        n = 0
        for n, url in enumerate(_FALLBACKS, 1):
            if verbose:
                print(f"Trying service {n}/{len(_FALLBACKS)}",end="\r")
            try:
                async with session.post(url+"/documents", data="") as response:
                    if response.status != 200:
                        continue
                    else:
                        if verbose:
                            print(f"{url} ({n}) worked. Using that.")
                        break
            except:
                if verbose:
                    print(f"Service {n}/{len(_FALLBACKS)} failed. Waiting {n * 1.25}s before trying again.", end="\r")
                await asyncio.sleep(n*1.25)
                continue
        else:
            if verbose:
                print("No functional URLs could be found. Are you sure you're online?")
            raise NoFallbacks()
    return url


# noinspection PyIncorrectDocstring
def postSync(content: typing.Union[str, typing.Iterable], *, url: str = None, retry: int = 5, find_fallback_on_unavailable: bool = True,
             find_fallback_on_retry_runout: bool = False):
    """
    Creates a new haste

    :param content: Union[str, Iterable] - the content to post to hastebin. If this is a list, it will join with a newline.
    :keyword url: the custom URL to post to. Defaults to HasteBin.
    :keyword retry: the number of times to retry. Pass `0` to disable
    :keyword find_fallback_on_unavailable: Whether or not to find a fallback or give up if the url fails to return.
    :keyword find_fallback_on_retry_runout: if True, instead of raising NoMoreRetries(), find a fallback instead.
    :raise RuntimeError: requests is not installed or you provided a retry value above 1000 (which would raise recursion error)
    :raise TypeError: Either the provided `content` was not string/iterable, or you disabled find_..._unavailable.
    :return: the returned URL
    """
    if retry > 1000:
        raise RuntimeError("")
    if not requests:
        raise RuntimeError("requests must be installed if you want to be able to run postSync.")
    if isinstance(content,
                  (list, tuple, set, frozenset)):  # 1.0.6: Made all iterables supported (e.g generators or tuples)
        content = [str(item) for item in content]
        content = "\n".join(content)
    if not isinstance(content, str):
        raise TypeError("Content parameter should be list or string, not " + type(content).__name__)
    url = url or "https://haste.clicksminuteper.net"
    with requests.Session() as session:
        try:
            response = session.post(url+"/documents", data=content)
            if response.status_code == 503:
                print(url, "is unavailable. Finding a fallback...")
                return postSync(content, url=findFallBackSync(True), find_fallback_on_retry_runout=True)
            if response.status_code != 200:
                raise ResponseError(response)
            elif response.headers.get("Content-Type", "").lower() != "application/json":
                print(url, "is returning an invalid response. Finding a Fallback")
                return postSync(content, url=findFallBackSync(True), find_fallback_on_retry_runout=True)
            key = response.json()["key"]
        except (requests.ConnectionError, ConnectionError):
            print(url, "is unable. Finding a fallback...")
            return postSync(content, url=findFallBackSync(True), find_fallback_on_retry_runout=True)
        except Exception as e:
            print(f"Exception while POSTing to {url}/documents: {e}\nFinding a fallback...")
            if retry <= 0:
                if find_fallback_on_retry_runout:
                    print(url, "is unavailable. Finding a fallback...")
                    return postSync(content, url=findFallBackSync(True), find_fallback_on_retry_runout=True)
                raise NoMoreRetries()
            print(f"Error posting. {retry-1} retries left.")
            retry -= 1
            if find_fallback_on_unavailable:
                return postSync(content, url=url, retry=retry, find_fallback_on_unavailable=True,
                                find_fallback_on_retry_runout=True)
            else:
                raise TypeError("Unable to create a haste with the provided URL.")
    return url+"/"+key

async def postAsync(content: typing.Union[str, list], *, url: str = None, retry: int = 5, find_fallback_on_unavailable: bool = True,
                    find_fallback_on_retry_runout: bool = False):
    """The same as :func:postSync, but async."""
    if not aiohttp:
        raise RuntimeError("aiohttp must be installed if you want to be able to run postAsync.")
    if isinstance(content, (list, tuple, set, frozenset)):
        content = [str(item) for item in content]
        content = "\n".join(content)
    if not isinstance(content, str):
        raise TypeError("Content parameter should be list or string, not " + type(content).__name__)
    url = url or "https://haste.clicksminuteper.net"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url+"/documents", data=content) as response:
                if response.status == 503:
                    print(url, "is unavailable. Finding a fallback...")
                    return await postAsync(content, url=await findFallBackAsync(True), find_fallback_on_retry_runout=True)
                if response.status != 200:
                    raise ResponseError(response)
                elif response.headers.get("Content-Type", "").lower() != "application/json":
                    print(url, "is returning an invalid response. Finding a Fallback")
                    return await postAsync(content, url=await findFallBackAsync(True), find_fallback_on_retry_runout=True)
                key = (await response.json())["key"]
        except aiohttp.ClientConnectionError:
            if find_fallback_on_unavailable:
                print(url, "is unavailable. Finding a fallback...")
                return await postAsync(content, url=await findFallBackAsync(True), find_fallback_on_retry_runout=True)
            else:
                raise TypeError("Unable to create a haste with the provided URL")
        except Exception as e:
            print(e)
            if retry <= 0:
                if find_fallback_on_retry_runout:
                    print(url, "is unavailable. Finding a fallback...")
                    return await postAsync(content, url=await findFallBackAsync(True), find_fallback_on_retry_runout=True)
                raise NoMoreRetries()
            print(f"Error posting. {retry-1} retries left.")
            retry -= 1
            # return await postAsync(content, url=url, retry=retry, find_fallback_on_retry_runout=True)
            if find_fallback_on_unavailable:
                return await postAsync(content, url=url, retry=retry, find_fallback_on_unavailable=True,
                                find_fallback_on_retry_runout=True)
            else:
                raise TypeError("Unable to create a haste with the provided URL.")
    return url+"/"+key

