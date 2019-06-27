from setuptools import setup, find_packages

setup(
    name="async_pool",
    version="0.1.4",
    keywords=("async", "multiprocessing", "producer-consumer"),
    description="A simple wrapper of library asyncio providing a multiprocessing-library-like coroutine worker pool.",
    license="MIT Licence",

    url="https://github.com/gwy15/async_pool",
    author="gwy15",
    author_email="gwy15thu@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    platforms="any"
)
