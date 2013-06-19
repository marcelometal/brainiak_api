import md5
import traceback
from email.utils import formatdate

import redis
import ujson

from brainiak import settings
from brainiak import log


class CacheError(redis.exceptions.RedisError):
    pass


exceptions = (CacheError, redis.connection.ConnectionError)


def connect():
    return redis.StrictRedis(host=settings.REDIS_ENDPOINT, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=0)


redis_client = connect()


def current_time():
    """
    Return current time in RFC 1123, according to:
    http://tools.ietf.org/html/rfc2822.html#section-3.3
    """
    return formatdate(timeval=None, localtime=True)


def fresh_retrieve(function, params):
    body = function(params)
    fresh_json = {
        "body": body,
        "meta": {
            "last_modified": current_time(),
            "cache": "MISS"
        }
    }
    return fresh_json


def memoize(function, params):
    if settings.ENABLE_CACHE:
        url = params['request'].uri
        cached_json = retrieve(url)
        if (cached_json is None) or (params.get('purge') == '1'):
            fresh_json = fresh_retrieve(function, params)
            create(url, ujson.dumps(fresh_json))
            return fresh_json
        else:
            cached_json["meta"]["cache"] = "HIT"
            return cached_json
    else:
        return fresh_retrieve(function, params)


def safe_redis(function):

    def wrapper(*params):
        try:
            response = function(*params)
        except exceptions as e:
            log.logger.error("CacheError: First try returned {0}".format(traceback.format_exc()))
            try:
                global redis_client
                redis_client = connect()
                response = function(*params)
            except exceptions as e:
                log.logger.error("CacheError: Second try returned {0}".format(traceback.format_exc()))
                response = None
        return response

    return wrapper


def purge(pattern):
    keys_with_pattern = keys(pattern) or []
    log.logger.debug("Cache: key(s) to be deleted: {0}".format(keys_with_pattern))
    log_details = "{0} key(s), matching the pattern: {1}".format(len(keys_with_pattern), pattern)
    response = 1
    for key in keys_with_pattern:
        response *= delete(key)

    if response and keys_with_pattern:
        log.logger.info("Cache: purged with success {0}".format(log_details))
    elif not keys_with_pattern:
        log.logger.info("Cache: {0}".format(log_details))
    else:
        log.logger.info("Cache: failed purging {0}".format(log_details))


@safe_redis
def create(key, value):
    return redis_client.set(key, value)


@safe_redis
def retrieve(key):
    response = redis_client.get(key)
    if response:
        response = ujson.loads(response)
    return response


@safe_redis
def delete(keys):
    return redis_client.delete(keys)


@safe_redis
def keys(pattern):
    pattern = "{0}*".format(pattern)
    return redis_client.keys(pattern)


def ping():
    return redis_client.ping()


def status():
    params = {
        "password": md5.new(str(settings.REDIS_PASSWORD)).digest(),
        "endpoint": "{0}:{1}".format(settings.REDIS_ENDPOINT, settings.REDIS_PORT),
    }
    failure_msg = "Redis connection authenticated [:%(password)s] | FAILED | %(endpoint)s | %(error)s"
    success_msg = "Redis connection authenticated [:%(password)s] | SUCCEED | %(endpoint)s"

    try:
        response = ping()
    except exceptions as e:
        params["error"] = traceback.format_exc()
        msg = failure_msg
    else:
        if not response:
            params["error"] = "Ping failed"
            msg = failure_msg
        else:
            msg = success_msg

    return msg % params
