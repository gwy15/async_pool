import asyncio
from asyncio import Queue

def _cancel_all_tasks(loop):
    to_cancel = asyncio.all_tasks(loop)
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'unhandled exception during asyncio.run() shutdown',
                'exception': task.exception(),
                'task': task,
            })

def _run(main, *, debug=False):
    "For python 3.6 there's no asyncio.run"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(debug)
    try:
        return loop.run_until_complete(main)
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

try:
    from asyncio import run
except:
    run = _run


class EndSignal():
    pass


class Consumer():
    async def run(self, iQueue: Queue, oQueue: Queue, afunc):
        while True:
            arg = await iQueue.get()
            if isinstance(arg, EndSignal):
                await oQueue.put(arg)
                return  # end
            result = await afunc(arg)
            await oQueue.put(result)


class Producer():
    def getArg(self, args):
        for arg in args:
            yield arg
        while True:
            yield EndSignal()

    async def run(self, iQueue: Queue, oQueue: Queue, workers, args):
        argGenerator = self.getArg(args)
        for _ in range(workers):
            arg = next(argGenerator)
            await iQueue.put(arg)

        finishedWorkers = 0
        results = []
        while True:
            result = await oQueue.get()
            if isinstance(result, EndSignal):
                finishedWorkers += 1
                if finishedWorkers == workers:
                    break  # end
            else:
                results.append(result)
                arg = next(argGenerator)
                await iQueue.put(arg)
        return results


class Pool():
    def __init__(self, workers=0):
        if (workers < 0):
            raise ValueError('Number of workers must be at least 1')
        self.workers = workers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

    async def map_async_unlimited(self, afunc, args):
        aws = [
            afunc(arg) for arg in args
        ]
        task = asyncio.gather(*aws)
        try:
            results = await task
            return results
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            task.cancel()
            raise

    async def map_async(self, afunc, args):
        if self.workers == 0:
            return await self.map_async_unlimited(afunc, args)

        iQueue = Queue()
        oQueue = Queue()
        consumers = [Consumer()
                     for _ in range(self.workers)]
        producer = Producer()

        aws = [producer.run(iQueue, oQueue, self.workers, args)] + [
            consumer.run(iQueue, oQueue, afunc)
            for consumer in consumers
        ]
        task = asyncio.gather(*aws)
        try:
            results = await task
            return results[0]
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            task.cancel()
            raise

    def map(self, afunc, args):
        return run(self.map_async(afunc, args))
