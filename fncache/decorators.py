import copy
import logging
import os
import shelve
from inspect import signature

import memcache


logger = logging.getLogger(__name__)


def _join(*args):
    return '_'.join(args)


def get_signature(fn, args, prefix):
    _args = list(copy.deepcopy(args))
    sig = signature(fn)

    # remove first arg if instance
    if sig.parameters['self']:
        _args.pop(0)

    sig_key = prefix

    args_part = _join(*[str(x) for x in _args])
    if args_part:
        sig_key = _join(prefix, args_part)

    # remove whitespace from cache key
    return sig_key.replace(' ', '')


def fncache_read(key, ttl=3600):

    def _decorator(fn):

        def wrapper(*args, **kwargs):
            cache_key = get_signature(fn, args, key)

            localstore = shelve.open(os.environ['FNCACHE_FILE'], 'c')
            try:
                return localstore[cache_key]
            except KeyError:
                pass

            cache = memcache.Client([os.environ['FNCACHE_SERVERS']])
            result = cache.get(cache_key)
            if not result:
                result = fn(*args, **kwargs)

                # cache to memcached
                cache.add(cache_key, result, ttl)

            # cache to local cache
            localstore[cache_key] = result

            cache.disconnect_all()
            localstore.close()
            return result
        return wrapper
    return _decorator


def fncache_revoke(fn_str, fn_args=[]):

    def _decorator(fn):

        def wrapper(*args, **kwargs):
            _args = list(copy.deepcopy(args))
            sig = signature(fn)

            key_part = []
            # remove first arg if instance
            for arg in sig.parameters:
                if arg in fn_args:
                    key_part.append(str(_args.pop(0)))
                else:
                    _args.pop(0)

            cache_key = _join(*[fn_str] + key_part)

            with shelve.open(os.environ['FNCACHE_FILE']) as localstore:
                try:
                    del localstore[cache_key]
                except KeyError:
                    pass

            cache = memcache.Client([os.environ['FNCACHE_SERVERS']], debug=0)
            cache.delete(cache_key)
            cache.disconnect_all()

            return fn(*args, **kwargs)
        return wrapper
    return _decorator
