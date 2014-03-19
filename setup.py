from setuptools import setup, find_packages

setup(
    name="rocksdbserver",
    version='0.1',
    description="RocksDB Server",
    keywords='rocksdbserver rocksdb',
    author='Prashanth Ellina',
    author_email="Use the github issues",
    url="https://github.com/prashanthellina/rocksdbserver",
    license='MIT License',
    install_requires=[
        'tornado',
        'msgpack-python',
    ],
    package_dir={'rocksdbserver': 'rocksdbserver'},
    packages=find_packages('.'),
    include_package_data=True
)
