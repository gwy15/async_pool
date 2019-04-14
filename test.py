import unittest
import asyncio

from async_pool import Pool


async def afunc(i):
    return i+1


async def afunc_except(i):
    if i == 2:
        raise TestExcept()
    return i + 1


class TestExcept(Exception):
    pass


WORKERS_CASES = (1, 2, 3, 4, 6, 7, 100, 1000, 0)
ARGS_CASES = (1, 2, 3)
RESULTS_EXPECTED = {2, 3, 4}  # set


class AsyncPoolTest(unittest.TestCase):
    def testWorkersCheck(self):
        with self.assertRaises(ValueError):
            Pool(-1)

    def testNoExcept(self):
        for workers in WORKERS_CASES:
            with Pool(workers) as pool:
                results = pool.map(afunc, ARGS_CASES)
            self.assertEqual(RESULTS_EXPECTED, set(results))

    def testWithExcept(self):
        for workers in WORKERS_CASES:
            with self.assertRaises(TestExcept):
                with Pool(workers) as pool:
                    results = pool.map(afunc_except, ARGS_CASES)

    def testNoExceptAsync(self):
        async def main():
            for workers in WORKERS_CASES:
                with Pool(workers) as pool:
                    results = await pool.map_async(afunc, ARGS_CASES)
                self.assertEqual(RESULTS_EXPECTED, set(results))

        asyncio.run(main())

    def testWithExceptAsync(self):
        async def main():
            for workers in WORKERS_CASES:
                with self.assertRaises(TestExcept):
                    with Pool(workers) as pool:
                        results = await pool.map_async(afunc_except, ARGS_CASES)

        asyncio.run(main())


if __name__ == "__main__":
    unittest.main()
