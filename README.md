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

## Usage

Consider this simple usage example from the examples/ directory.

``` python
from rocksdbserver import RocksDBServer, RocksDBAPI, Table

class NamesTable(Table):
    NAME = 'names'

class SimpleDBAPI(RocksDBAPI):
    def define_tables(self):
        names = NamesTable(self.data_dir, self)
        return {names.NAME: names}

class SimpleDBServer(RocksDBServer):
    NAME = 'SimpleDBServer'
    DESC = 'Simple DB Server based on RockDB Server'

    def prepare_api(self):
        return SimpleDBAPI(self.args.data_dir)

if __name__ == '__main__':
    SimpleDBServer().start()
```

The above code represents a database with just one table called 'names'. Run this server by doing

``` bash
python examples/simple_db.py /tmp/data
```

The argument /tmp/data points to the data directory where the db files are stored. You can pick an alternate location too.

Now visit http://locahost:8889 to use the web based console and try out the following

![Image](./simpledb.png?raw=true)
