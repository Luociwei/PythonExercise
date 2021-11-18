# -*- coding:utf-8 -*-

import re
import os
import subprocess
import threading
from time import sleep
from argparse import ArgumentParser





def ssh_command_execute(host_name, user_name, password, command):
    ssh_cmd = r"""
        expect -c "
        set timeout 10;
        spawn ssh {user}@{host} {command}
        expect {{
            \"*(yes/no)*\" {{ send "yes"\n; exp_continue }}
            \"*assword*\" {{ send {password}\n }}
        }} ;
        expect *\n;
        expect eof
        "
    """.format(user=user_name, host=host_name, password=password, command=command)

    p = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    print "output -- >",output
    print "err -->" , err
    print 
    return output


def get_xavier_fw_version(hostname, user_username, passwd):
    versoion_file = '/mix/version.json'
    stdout = ssh_command_execute(hostname, user_username, passwd, "cat " + versoion_file)
    if "No such file or directory" in stdout:
        raise Exception("%s is not exit" % versoion_file)
    version_info = eval(stdout[stdout.find('{'):stdout.find('}') + 1])
    # return version_info['Addon_J617_FCT_SC']
    print(version_info)
    for k in version_info:
        if 'Addon' in k:
            # print(k)
            result = re.match(r"Addon_J\d+_(\w+)_(\w+)",k)
            if result is None:
                raise Exception("match not fail")
            else:
                # print(result.group(1),result.group(2))
                return result.group(1),result.group(2)





if __name__ == '__main__':
    # /usr/bin/python /Users/gdlocal/Library/Atlas2/supportFiles/create_shortcut.py >> /Users/gdlocal/Desktop/create_shortcut.log
    ret = get_xavier_fw_version('169.254.1.32','root','123456')
    print(ret[1])
    if ret[1] =='SC':
       os.system('ln -s /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture_SC.dylib /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture.dylib')
       # os.system('rm /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture_PRM.dylib')
    elif ret[1] =='PRM':
       os.system('ln -s /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture_PRM.dylib /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture.dylib')
       # os.system('rm /Users/gdlocal/Library/Atlas2/supportFiles/libFCTFixture_SC.dylib')



