import uuid

import rocksdb
from funcserver import RPCServer, BaseHandler

def ensuretable(fn):
    def wfn(self, table, *args, **kwargs):
        if not table not in self.tables:
            raise Exception('Table "%s" does not exist' % table)
        return fn(self.tables[table], *args, **kwargs)
    return wfn

class Table(object):
    NAME = 'noname'

    def __init__(self, data_dir, db):
        self.data_dir = os.path.join(data_dir, self.NAME)
        self.rdb = self.open()
        self.db = db

    def __str__(self):
        return '<Table: %s>' % self.NAME

    def __unicode__(self):
        return str(self)

    def open(self):
        opts = self.define_options()
        return rocksdb.DB(self.data_dir, opts)

    def define_options(self):
        opts = rocksdb.Options()
        return opts

    def put(self, key, item, batch=None):
        db = batch or self.rdb

        key = key or item.get('_id', None) or uuid.uuid1()
        item['_id'] = key

        value = msgpack.packb(item)
        db.put(key, value)

        return key

    def get(self, key):
        value = self.rdb.get(key)
        if value is None: return None

        item = msgpack.unpackb(value)
        return item

    def put_many(self, data):
        batch = rocksdb.WriteBatch()
        for key, item in data:
            self.put(key, item, batch=batch)
        self.rdb.write(batch)

    def get_many(self, keys):
        data = self.rdb.multi_get(keys)
        for key, value in data.iteritems():
            data[key] = None if value is None else msgpack.unpackb(value)
        return data

class RocksDBAPI(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.tables = {}

    def define_tables(self):
        return {}

    def list_tables(self):
        return self.tables.keys()

    @ensuretable
    def put(self, table, key, item):
        return table.put(key, item)

    @ensuretable
    def get(self, table, key):
        return table.get(key)

    @ensuretable
    def put_many(self, table, data):
        return table.put_many(data)

    @ensuretable
    def get_many(self, table, keys):
        return table.get_many(keys)

class RocksDBServer(RPCServer):
    NAME = 'RocksDBServer'
    DESC = 'RocksDB Server'

    def __init__(self, *args, **kwargs):
        super(RocksDBServer, self).__init__(*args, **kwargs)

        # make data dir if not already present
        self.data_dir = os.path.abspath(self.args.data_dir)
        if not os.path.exists(self.data_dir):
            os.path.makedirs(self.data_dir)

    def prepare_api(self):
        return RocksDBAPI(args.data_dir)

    def define_args(self, parser):
        parser.add_argument('data-dir', type=str, help='Directory path where data is stored')

if __name__ == '__main__':
    RocksDBServer().start()
