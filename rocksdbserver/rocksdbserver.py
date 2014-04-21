import os
import uuid
import resource
import random
import string

from decorator import decorator
import msgpack
import rocksdb
from funcserver import RPCServer, RPCClient, BaseHandler

MAX_OPEN_FILES = 500000
ALPHANUM = set(string.letters + string.digits)

def gen_random_seq(length=10):
    return ''.join([random.choice(ALPHANUM) for i in xrange(length)])

@decorator
def ensuretable(fn):
    def wfn(self, table, *args, **kwargs):
        if table not in self.tables:
            raise Exception('Table "%s" does not exist' % table)
        return fn(self, self.tables[table], *args, **kwargs)
    return wfn

@decorator
def ensurenewiter(fn):
    def wfn(self, *args, **kwargs):
        name = kwargs['name'] or gen_random_seq()
        if name in self.iters:
            raise Exception('iter "%s" exists already!' % name)

        return fn(*args, **kwargs)
    return wfn

class Iterator(object):
    NUM_RECORDS = 1000

    def __init__(self, table, prefix=None, type='items', reverse=False):
        '''
        @type: str; can be items/keys/values
        '''
        self.table = table
        self.type = type
        self.prefix = prefix
        self.reverse = reverse

        iterfn = getattr(self.table.rdb,
            {'keys': 'iterkeys', 'values': 'itervalues'}\
            .get(type, 'iteritems'))

        self._iter = iterfn(prefix=prefix)

        if reverse:
            self._iter = reversed(self._iter)

    def get(self, num=NUM_RECORDS):
        records = []

        for record in self._iter:
            if self.type == 'items':
                key, item = record
                item = self.table.unpackfn(item)
                record = (key, item)
            elif self.type == 'values':
                record = self.table.unpackfn(record)

            records.append(record)
            if len(records) >= num: break

        return records

    def seek(self, key):
        self._iter.seek(key)

class Table(object):
    NAME = 'noname'
    ITER = Iterator

    KEYFN = lambda item: uuid.uuid1().hex
    PACKFN = lambda item: msgpack.packb
    UNPACKFN = lambda value: msgpack.unpackb

    def __init__(self, data_dir, db):
        self.data_dir = os.path.join(data_dir, self.NAME)
        self.rdb = self.open()
        self.db = db
        self.iters = {}

        self.keyfn = self.KEYFN
        self.packfn = self.PACKFN
        self.unpackfn = self.UNPACKFN
        self.iter_klass = self.ITER

    def __str__(self):
        return '<Table: %s>' % self.NAME

    def __unicode__(self):
        return str(self)

    def open(self):
        opts = self.define_options()
        opts.create_if_missing = True
        return rocksdb.DB(self.data_dir, opts)

    def define_options(self):
        opts = rocksdb.Options()
        return opts

    def put(self, key, item, batch=None,
            keyfn=None, packfn=None):

        packfn = packfn or self.packfn
        keyfn = keyfn or self.keyfn

        db = batch or self.rdb

        key = key or item.get('_id', None) or keyfn(item)
        item['_id'] = key

        value = packfn(item)
        db.put(key, value)

        return key

    def get(self, key, unpackfn=None):
        unpackfn = unpackfn or self.unpackfn

        value = self.rdb.get(key)
        if value is None: return None

        item = unpackfn(value)
        return item

    def delete(self, key, batch=None):
        db = batch or self.rdb
        db.delete(key)

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

    def delete_many(self, keys):
        batch = rocksdb.WriteBatch()
        for key in keys:
            self.delete(key, batch=batch)
        self.rdb.write(batch)

    @ensurenewiter
    def iter_keys(self, prefix=None, name=None, reverse=False):
        self.iters[name] = self.iter_klass(self, prefix,
            type='keys', reverse=reverse)

    @ensurenewiter
    def iter_values(self, prefix=None, name=None, reverse=False):
        self.iters[name] = self.iter_klass(self, prefix,
            type='values', reverse=reverse)

    @ensurenewiter
    def iter_items(self, prefix=None, name=None, reverse=False):
        self.iters[name] = self.iter_klass(self, prefix,
            type='items', reverse=reverse)

    def list_iters(self):
        return self.iters.keys()

    def close_iter(self, name):
        del self.iters[name]

    def iter_get(self, name, num=Iterator.NUM_RECORDS):
        self.iters[name].get(num)

class RocksDBAPI(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.tables = self.define_tables()

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
    def delete(self, table, key):
        return table.delete(key)

    @ensuretable
    def put_many(self, table, data):
        return table.put_many(data)

    @ensuretable
    def get_many(self, table, keys):
        return table.get_many(keys)

    @ensuretable
    def delete_many(self, table, keys):
        return table.delete_many(keys)

class RocksDBServer(RPCServer):
    NAME = 'RocksDBServer'
    DESC = 'RocksDB Server'

    def __init__(self, *args, **kwargs):
        super(RocksDBServer, self).__init__(*args, **kwargs)

        # make data dir if not already present
        self.data_dir = os.path.abspath(self.args.data_dir)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def set_file_limits(self):
        try:
            # ulimit -n unlimited
            resource.setrlimit(resource.RLIMIT_NOFILE,
                (MAX_OPEN_FILES, MAX_OPEN_FILES))
        except ValueError:
            self.log.warning('unable to increase num files limit. run as root?')

    def pre_start(self):
        super(RocksDBServer, self).pre_start()
        self.set_file_limits()

    def prepare_api(self):
        return RocksDBAPI(self.args.data_dir)

    def define_args(self, parser):
        parser.add_argument('data_dir', type=str, metavar='data-dir',
            help='Directory path where data is stored')

class RocksDBClient(RPCClient):
    pass

if __name__ == '__main__':
    RocksDBServer().start()
