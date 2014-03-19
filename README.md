# rocksdbserver

A server exposing an RPC interface to RocksDB

## Installation

(original instructions from http://pyrocksdb.readthedocs.org/en/latest/installation.html)

### First install librocksdb.so

``` bash
$ sudo apt-get install build-essential
$ sudo apt-get install libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev
$ git clone https://github.com/facebook/rocksdb.git
$ cd rocksdb
$ # It is tested with this version
$ git checkout 2.7.fb
$ make librocksdb.so
$ sudo mv librocksdb.so /usr/lib/
$ sudo mv include/* /usr/include/
```

### Install pyrocksdb module

``` bash
$ sudo apt-get install python-virtualenv python-dev
$ sudo pip install cython (ensure cython version >=0.20)
$ sudo pip install git+git://github.com/stephan-hof/pyrocksdb.git
```

### Install FuncServer

``` bash
sudo pip install git+git://github.com/prashanthellina/funcserver.git
```

### Install RocksDBServer

``` bash
sudo pip install git+git://github.com/prashanthellina/rocksdbserver.git
```
