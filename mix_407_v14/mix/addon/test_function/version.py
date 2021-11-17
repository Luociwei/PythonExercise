import re
import json

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class VERSION(object):

    rpc_public_api = ['version']
    def __init__(self, xobjects):
        self.xobject = xobjects
    
    def version(self):
    	try:
            with open('/mix/version.json', 'rU') as fp:
                ver = json.load(fp)
                return ver
        except Exception as e:
            return FAIL_MASK
    

   
