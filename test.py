import unittest
import asyncio

from async_pool import Pool


class AsyncPoolTest(unittest.TestCase):
    def testWorkersCheck(self):
        with self.assertRaises(ValueError):
            Pool(0)
        with self.assertRaises(ValueError):
            Pool(-1)

    def testNoExcept(self):
        async def afunc(i):
            return i + 1

        for workers in (1, 2, 3, 4, 6, 7, 100, 1000):
            with Pool(workers) as pool:
                results = pool.map(afunc, (1, 2, 3))
            self.assertEqual({2, 3, 4}, set(results))

    def testWithExcept(self):
        class TestExcept(Exception):
            pass

        async def afunc(i):
            if i == 2:
                raise TestExcept()
            return i + 1

        for workers in (1, 2, 3, 4, 6, 7, 100, 1000):
            with self.assertRaises(TestExcept):
                with Pool(workers) as pool:
                    results = pool.map(afunc, (1, 2, 3))

    def testNoExceptAsync(self):
        async def afunc(i):
            return i + 1

        async def main():
            for workers in (1, 2, 3, 4, 6, 7, 100, 1000):
                with Pool(workers) as pool:
                    results = await pool.map_async(afunc, (1, 2, 3))
                self.assertEqual({2, 3, 4}, set(results))

        asyncio.run(main())

    def testWithExceptAsync(self):
        class TestExcept(Exception):
            pass

        async def afunc(i):
            if i == 2:
                raise TestExcept()
            return i + 1

        async def main():
            for workers in (1, 2, 3, 4, 6, 7, 100, 1000):
                with self.assertRaises(TestExcept):
                    with Pool(workers) as pool:
                        results = await pool.map_async(afunc, (1, 2, 3))

        asyncio.run(main())


if __name__ == "__main__":
    unittest.main()
