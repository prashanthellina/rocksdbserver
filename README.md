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

The above exercise demonstrates how to interact with the database via a web based shell. Now let us try to interact with the database from a Pythons script using the client API.

Consider this sample client code from examples/simple_db_client.py

``` python
from rocksdbserver import RocksDBClient

if __name__ == '__main__':
    db = RocksDBClient('http://localhost:8889')
    print db.put('names', 'prashanth', {'last_name': 'ellina', 'days': 10})
    key = db.put('names', None, {'last_name': 'doe', 'days': 12})
    print key

    print db.get('names', 'prashanth')
    print db.get('names', key)
```

Run this by doing

``` bash
python examples/simple_db_client.py
```

The output will look something like this

``` bash
$ python simple_db_client.py 
prashanth
238b74b0af8d11e3bcd3d43d7e99b40b
{'last_name': 'ellina', 'days': 10, '_id': 'prashanth'}
{'last_name': 'doe', 'days': 12, '_id': '238b74b0af8d11e3bcd3d43d7e99b40b'}
```
