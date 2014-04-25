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
        'gevent',
        'decorator',
        'tornado',
        'msgpack-python',
        'funcserver',
    ],
    dependency_links=[
        'http://github.com/prashanthellina/funcserver/tarball/master#egg=funcserver'
    ],
    package_dir={'rocksdbserver': 'rocksdbserver'},
    packages=find_packages('.'),
    include_package_data=True
)
