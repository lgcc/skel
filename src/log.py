from __future__ import print_function

__slot__ = ['Log']


class Log(object):
    DEBUG, INFO, WARN, ERROR = 1, 2, 3, 4
    debug = info = None

    def __init__(self, level=None):
        if level == None:
            level = Log.INFO
        d = {False: lambda *arg: None, True: self._print}
        self.debug = d[level <= Log.DEBUG]
        self.info = d[level <= Log.INFO]
        self.warn = d[level <= Log.WARN]
        self.error = d[level <= Log.ERROR]

    def _print(self, *arg, **kw):
        print(*arg, **kw)
    # def _print(self, *arg, **kw):
    #     print ' '.join(['%s' % i for i in arg])


if __name__ == '__main__':
    log = Log(level=Log.INFO)
    log.debug('--- debug start ---')
    log.info('=== Info ===')
