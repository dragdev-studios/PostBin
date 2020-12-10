# Examples
These are simple examples displaying usage of most of the PostBin methods, **including betas**.

## FAQ
### Which do I need? Whats the difference between Async and Sync?
Mainly, if you `await` anything in your program, or you're in an `async def`ined function, you should use Async (since the function/program is async). Otherwise, use sync.

The main difference is that Sync **blocks your program's execution**, so if you're running background tasks, this will pause them, whereas async doesn't.

------------

## Importing
### v1
```python
import postbin
# v1 only has two (public) functions, so you can also do 
from postbin import postAsync, postSync
# Or just postSync/Async, whichever you need.
```

### v2
```python
from postbin.v2 import AsyncHaste
```
Sync support for v2 is not currently available.
You can, however, use the below sample to run it. Import asyncio, then `asyncio.get_event_loop().run_until_complete(awaitable)`. e.g: `asyncio.get_event_loop().run_until_complete(asyncio.sleep(5))`

## Usage
The below samples will post "Hello World" to the first available haste service.
### v1
```python
# async program
  url = await postAsync("Hello World")
# Sync
  url = postSync("Hello World")
```

### v2
```python
# Predefining a haste container (recommended)
paster = AsyncHaste()
# ... somewhere else
  url = await paster.post("Hello World")

# Or, if you want an inline solution
  url = await AsyncHaste("Hello World").post()
  # OR
  url = await AsyncHaste().post("Hello World")
```
v2's class-based system means that it is more efficient and uses slightly less resources than v1, and also allows for some funky tricks.

See the wiki for documentation.
