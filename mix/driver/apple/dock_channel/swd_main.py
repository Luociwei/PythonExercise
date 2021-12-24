import sys
import os
import time
import argparse
from dock_channel import daemon
from dock_channel.dc_manager import start_dc_manager, check_slot

class DCDaemon(daemon.Daemon):
    def __init__(self, *args, **kwargs):
        super(DCDaemon, self).__init__(*args, **kwargs)
        for arg in args:
            self.slot_id = int(arg[-1])
            break

    def run(self):
        start_dc_manager(self.slot_id, self.tps_pin, self.iic_pin)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--ident', help='logical dc identifier (e.g. 0 -> /dev/axiswd0', type=int, action='store',
                        default=0)
    parser.add_argument('-tps_pin', '--tps', help='pin for tps irq', type=int, action='store', default=946)
    parser.add_argument('-iic_pin', '--iic', help='pin for iic/alert_n irq', type=int, action='store', default=918)
    args = parser.parse_args()

    print args.ident
    print args.tps
    print args.iic

    # set daemon
    slot_id = int(args.ident)
    if check_slot(slot_id):
        swd_name = "swd" + str(slot_id)
        log_file = '/var/log/'+swd_name
        dc_daemon = DCDaemon(swd_name, stdout=log_file, stderr=log_file)
        dc_daemon.tps_pin = int(args.tps)
        dc_daemon.iic_pin = int(args.iic)
        dc_daemon.start()
