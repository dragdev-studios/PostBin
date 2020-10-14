# PostBin
A simple package that allows you to post to haste services.

## Features:
* "fallback" system, meaning your pastes always succeed
* async and sync functionality
* literally instant setup - see [execution](#Execution)

## Why this exists
There's no real need for a full-fledged module for simply creating pastes. So, I think a quick 2 function module
does the trick far easier.

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
Just open an issue, with the URL, and we'll add it!

## Changelog:
1.0.2:
* Fixed An AttributeError in the error class
* Added the retry keyword to post methods. Defaults to 5 retries