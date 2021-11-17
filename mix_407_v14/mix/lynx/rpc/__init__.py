from rpc_server import RPCServerWrapper
from rpc_client import RPCClientWrapper
from publisher import *
from logger import RPCLogger

from functools import wraps


def var_params_list(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        import inspect
        useful_kwargs = {}
        args_info = inspect.getargspec(f)
        args_list = args_info.args
        for arg in args_list:
            if arg in kwargs:
                useful_kwargs[arg] = kwargs[arg]
        return f(*args, **useful_kwargs)
    return wrapper

