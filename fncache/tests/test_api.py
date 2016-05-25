import os
import shelve

from fncache.decorators import fncache_read, fncache_revoke

import memcache


class Api(object):

    @fncache_read('get')
    def get_resource(self, resource, id, short=True):
        return 'foo'

    @fncache_revoke('get', fn_args=['resource', 'id'])
    def set_resource(self, resource, id, data):
        pass

    @fncache_read('token')
    def get_token(self):
        return 'bar'

    @fncache_revoke('token')
    def refresh_token(self):
        pass


class TestDecorator(object):

    def setup(self):
        memcached_servers = '127.0.0.1:11211'
        os.environ['FNCACHE_SERVERS'] = memcached_servers

        self.api = Api()

        self.mc = memcache.Client([memcached_servers])
        self.mc.flush_all()

        self.fncache_file = os.environ['FNCACHE_FILE']
        with shelve.open(self.fncache_file, 'c') as localstore:
            localstore.clear()

    def teardown(self):
        """ Clear all caches """
        self.mc.flush_all()

        with shelve.open(self.fncache_file, 'c') as localstore:
            localstore.clear()

    def test_get_resource_cold_caches(self):
        expected_key = 'get_foo_1'

        # test cold cache
        assert not self.mc.get(expected_key)
        with shelve.open(self.fncache_file, 'w') as localstore:
            expected_key not in localstore

        result = self.api.get_resource('foo', 1)
        assert result == 'foo'

        # test warm caches
        assert self.mc.get(expected_key) == 'foo'
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] == 'foo'

    def test_get_token_cold_caches(self):
        expected_key = 'token'

        # test cold cache
        assert not self.mc.get(expected_key)
        with shelve.open(self.fncache_file, 'w') as localstore:
            expected_key not in localstore

        result = self.api.get_token()
        assert result == 'bar'

        # test warm caches
        assert self.mc.get(expected_key) == 'bar'
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] == 'bar'

    def test_get_resource_warm_local(self):
        expected_key = 'get_foo_1'

        # warm up local
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] = 'foo'

        result = self.api.get_resource('foo', 1)
        assert result == 'foo'

        # test only local warm cache
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] == 'foo'
        assert not self.mc.get(expected_key) == 'foo'

    def test_get_resource_warm_memcached(self):
        expected_key = 'get_foo_1'

        # test cold local
        with shelve.open(self.fncache_file, 'w') as localstore:
            expected_key not in localstore

        # warm up memcached
        self.mc.set(expected_key, 'foo', 3600)
        assert self.mc.get(expected_key) == 'foo'

        result = self.api.get_resource('foo', 1)
        assert result == 'foo'

        # test warm local cache
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] == 'foo'

    def test_set_resource_revoke_existing_key(self):
        expected_key = 'get_foo_1'

        # warm up local and memcached
        self.mc.set(expected_key, 'foo', 3600)
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] = 'foo'

        self.api.set_resource('foo', 1, {'data': []})

        assert not self.mc.get(expected_key)
        with shelve.open(self.fncache_file, 'w') as localstore:
            assert expected_key not in localstore

    def test_refresh_token_revoke_existing_key(self):
        expected_key = 'token'

        # warm up local and memcached
        self.mc.set(expected_key, 'bar', 3600)
        with shelve.open(self.fncache_file, 'w') as localstore:
            localstore[expected_key] = 'bar'

        self.api.refresh_token()

        assert not self.mc.get(expected_key)
        with shelve.open(self.fncache_file, 'w') as localstore:
            assert expected_key not in localstore
