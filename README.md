# PostBin
A simple package that allows you to post to haste services.

![Python package](https://github.com/dragdev-studios/PostBin/workflows/Python%20package/badge.svg)
![Version](https://img.shields.io/pypi/v/postbin)
[![CodeFactor](https://www.codefactor.io/repository/github/dragdev-studios/postbin/badge)](https://www.codefactor.io/repository/github/dragdev-studios/postbin)

## Features:
* "fallback" system, meaning your pastes always succeed
* async and sync functionality
* literally instant setup - see [execution](#Execution)

## Why this exists
There's no real need for a full-fledged module for simply creating pastes. So, I think a quick 2 function module
does the trick far easier.

*Note: v2 would like to disagree*

## [backwards] Compatibility
While postbin tries to support all versions, nothing is guaranteed.
So far, we actively support python 3.6 through to 3.9, however always check the below table and find your version. if its a check mark, it is supported and will work.

1.x:

| Version |     Supported     | EOL |
| ------- | ----------------- | --- |
| 3.9     | :white_check_mark:| N/A |
| 3.8     | :white_check_mark:| N/A |
| 3.7     | :white_check_mark:| N/A |
| 3.6     | :white_check_mark:| N/A |
| 3.5     | :x:               | N/A |

2.0.1a:

| Version |     Supported     | EOL |
| ------- | ----------------- | --- |
| 3.9     | :white_check_mark:| N/A |
| 3.8     | :white_check_mark:| N/A |
| 3.7     | :white_check_mark:| N/A |
| 3.6     | :white_check_mark:| N/A |
| 3.5     | :x:               | N/A |

Alternatively, install through pip (below) - pip releases are always guaranteed to be stable on 3.8-3.9.

## Installing
from pip: 
```shell script
$ [python3 -m] pip install postbin
```
or from git:
```shell script
$ [python3 -m] pip install git+https://github.com/dragdev-studios/PostBin.git
# OR
$ git clone https://github.com/dragdev-studios/PostBin.git
$ cd postbin
$ python[3] setup.py build && python[3] setup.py install
```

## Execution
from within a script:
```python
import postbin
# Async app
async def main():
    url = await postbin.postAsync(f"FooBar Bazz")
    print(f"Your paste is located at {url}")


# Sync app
def mainSync(): 
    url = postbin.postSync(f"FooBar Bazz 2")
    print(f"Your paste is located at {url}")
```

## Want your haste service to be a fallback?
Make sure all of the following are true:

1.  `POST /documents` with a text/plain body returns JSON `{"key": "url_part"}` or `{"url": "new_url"}`
2. Ratelimit is greater than or equal to 5/5s
3. Ratelimit response is JSON (html is only allowed in extreme circumstances, like if cloudflare responds instead.). 
`x-ratelimit-reset-after` response headers can be used in replacement of body if required.
4. `GET /raw/:key` returns the text/plain content of the key
5. `HEAD /:key` or `HEAD /:raw/key` or `HEAD /documents[/:key]` returns a 200 response, or other information 
response regarding the status of the service, rather than 404 for not found/

If those are all met, open a PR modifying `_FALLBACKS` to add your site __to the end of the list__.
