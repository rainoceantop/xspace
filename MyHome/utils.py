import time
from django_redis import get_redis_connection
import uuid
from base64 import urlsafe_b64encode


class ConvertTime:
    _MINUTE = 60
    _HOUR = _MINUTE * 60
    _DAY = _HOUR * 24
    _MONTH = _DAY * 30
    _HALFYEAR = _MONTH * 6
    _YEAR = _DAY * 365

    def convertDatetime(self, t):
        beginTime = t.timestamp()
        nowTime = time.time()

        betweenTime = int(nowTime - beginTime)

        if betweenTime < self._MINUTE:
            return '刚刚'
        elif betweenTime < self._HOUR:
            return '{}分钟'.format(betweenTime//self._MINUTE)
        elif betweenTime < self._DAY:
            return '{}小时'.format(betweenTime//self._HOUR)
        elif betweenTime < self._MONTH:
            return '{}天'.format(betweenTime//self._DAY)
        elif betweenTime < self._HALFYEAR:
            return '{}个月'.format(betweenTime//self._MONTH)
        elif betweenTime < self._YEAR:
            return '{}'.format(t.strftime('%m-%d'))
        else:
            return '{}'.format(t.date())


def get_redis():
    return get_redis_connection('default')


def get_uuid_base64():
    u = uuid.uuid4()
    b = urlsafe_b64encode(u.bytes).decode().replace('=', '')
    return b
