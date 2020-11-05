import re
import os
import logging
import time
import platform
from logging.handlers import RotatingFileHandler
from logging import INFO, DEBUG, ERROR, CRITICAL, FATAL

'''
logging
Using 60MB as total max log file size;
Splited into 2 files, 30MB each at max.
Cannot use a single file because logging module need at least 1 backup count
to do rotate and finally control total file size.

60MB is a supported upper limit that will not cause memory issue on xavier
when getting log file with such size from xavier to station.
Because we don't use compression, actual log file size will be RPC response
payload size.
70MB will fail with the following memory error:

root@ubuntu-arm:~# Exception in thread Thread-4:
Traceback (most recent call last):
  File "/usr/lib/python2.7/threading.py", line 810, in __bootstrap_inner
    self.run()
  File "/mix/rpc/tinyrpcx/tinyrpc/server/__init__.py", line 189, in run
    self.transport.send_reply(task['context'], response.serialize())
  File "/mix/rpc/tinyrpcx/tinyrpc/protocols/jsonrpc.py", line 162, in serialize
    return json.dumps(self._to_dict())
OverflowError: Could not reserve memory block

json.dump() use much memory; that's why reducing payload size could make it work.
On MBP with large memory, 70MB could pass but in Activity Monitor we can observe
large memory usage by python.

On xavier ultra lite with 512MB memory, the log file size that will crash server
is 42MB, so choose 40MB (20 * 2) as max log size.

'''
MAX_LOG_FILE_SIZE_MB_512 = 20
MAX_LOG_FILE_SIZE_MB_DEFAULT = 30
# default
MAX_LOG_FILE_SIZE = MAX_LOG_FILE_SIZE_MB_DEFAULT * 1024 * 1024
MAX_LOG_FILE_NUM = 2

# determine max log size based on xavier DIMM size
os_str = platform.platform().lower()
if 'linux' in os_str:
    # Xavier: Linux-4.0.0.02-xilinx-armv7l-with-Ubuntu-14.04-trusty
    # MemTotal:        1029332 kB
    # MemTotal:         509516 kB
    pattern = 'MemTotal:\s+(?P<mem_size>\d+) kB'
    with open('/proc/meminfo', 'rb') as f:
        for line in f.readlines():
            ret = re.search(pattern, line)
            if ret:
                size = int(ret.group('mem_size'))
                if size < 512 * 1024:
                    # 512M DIMM
                    MAX_LOG_FILE_SIZE = MAX_LOG_FILE_SIZE_MB_512 * 1024 * 1024
                break

DEFAULT_LOG_LEVEL = INFO
SERVER_LOG_FORMAT = '%(asctime)s:%(created)f:%(levelname)s:%(module)s:%(message)s'


class RPCLogger(logging.Logger):
    '''
    Logger class to support logging to screen and file.
    '''
    def __init__(self, name, level=DEFAULT_LOG_LEVEL, log_format='', log_folder_path=None):
        super(RPCLogger, self).__init__(name, level)
        self.name = name
        format_str = log_format if log_format else SERVER_LOG_FORMAT
        self.formatter = logging.Formatter(format_str)
        self.init_file_handler(log_folder_path)

    def init_file_handler(self, log_path):
        '''
        Creat log handler for logging into file.
        '''
        # log file name
        now = time.time()
        ts = time.strftime('%Y%m%d_%H%M%S', time.localtime(now))
        if log_path:
            # use expanduser() to support '~' in log_path
            self.log_folder = os.path.abspath(os.path.expanduser(log_path))
        else:
            self.log_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log'))
        # mkdir folder if not exists
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        self.file_name = 'rpc_server_{}_{}.log'.format(self.name, ts)
        self.file_path = os.path.join(self.log_folder, self.file_name)

        # add handler for writing to file.
        # create RotatingFileHandler to limit total log file size to max file size.
        rotating_file_handler = RotatingFileHandler(self.file_path,
                                                    maxBytes=MAX_LOG_FILE_SIZE,
                                                    backupCount=MAX_LOG_FILE_NUM - 1)

        rotating_file_handler.setFormatter(self.formatter)
        self.addHandler(rotating_file_handler)

    def init_console_handler(self):
        '''
        create handler for logging to console
        '''
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.addHandler(console_handler)

    def reset(self):
        '''
        clean up existing log file content, and start logging again.
        Log file before server reset will be removed to clean up storage space.
        This is mainly for start a new test and avoid logging to include previous test records.
        '''
        for handler in self.handlers:
            self.removeHandler(handler)
            handler.close()

        # remove previous log files of this server
        for f in self.files():
            os.remove(os.path.join(self.log_folder, f))
        self.init_file_handler(self.log_folder)

    def files(self):
        '''
        return log file list, like rpc_server_xxx.log.1, rpc_server_xxx.log.2
        It returns all log files with same self.name.
        '''
        ret = []
        file_to_search = 'rpc_server_{}_[0-9]+_[0-9]+\.log'.format(self.name)
        for f in os.listdir(self.log_folder):
            if re.match(file_to_search, f):
                ret.append(os.path.join(self.log_folder, f))
        return ret
