Async Pool
---
[![image](https://travis-ci.org/gwy15/async_pool.svg?branch=master)](https://travis-ci.org/gwy15/async_pool)
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)

A simple wrapper of library asyncio providing a multiprocessing-library-like coroutine worker pool.


## Requirements

Python >= 3.7

## Usage:

```Python
from async_pool import Pool

async def afunc(i):
    return i

args = (1,2,3)
with Pool(4) as pool:
    results = pool.map(afunc, args) # expects any combination of (1,2,3)

```
