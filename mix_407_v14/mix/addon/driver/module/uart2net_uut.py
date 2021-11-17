import os
import re
import time
import select
import socket
import threading
import multiprocessing
import signal
from mix.driver.core.bus.uart import UART
# from threading import Thread


PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class UART2NET_UUT(object):

    rpc_public_api = ['read','read_hex','write','write_hex','config','open','close','start','stop']
    def __init__(self, dev_name,port):
        self._port = int(port)
        self._connect_socket = None
        self._uart_device = UART(dev_name)
        self._uart_device.open()
        self._inputs = []
        self._uart_stop = True
        self.uart_server_thread = None
    
    def start(self):
        self._uart_stop = False
        self.uart_server_thread = multiprocessing.Process(target=self.run)
        self.uart_server_thread.daemon = True
        self.uart_server_thread.start()

    def stop(self):
        self._uart_stop = True
        if self.uart_server_thread:
            self.uart_server_thread.close()
  
    def read(self, size = 1024, timeout_s=0):
    	'''
        uart read data
        Args:
            size:      int,     default 1024
            timeout_s  int,      default 0
		Example:
		    uart_read()
    	'''
        result = self._uart_device.read_hex(size, timeout_s)
        new_string = []
        for c in result:
            if c !=255:
                new_string.append(str(chr(c)))
        if new_string:
            s=''.join(new_string)
            return s
        else:
            return ''

    def read_hex(self, size = 1024, timeout_s=0):
    	'''
        uart read data hex
        Args:
            size:      int,     default 1024
            timeout_s  int,      default 0
        Example:
            read_hex()
    	'''
        return self._uart_device.read_hex(size, timeout_s)

    def write(self, datastring, timeout_s=None):
    	'''
        uart write string
        Args:
            datastring:      string,   any words
            timeout_s:       int,      none
        Example:
		  uart_write(datastring)
		  uart_write("hello world")
    	'''
    	data_list = []
        for c in datastring:
            data_list.append(int(str(ord(c))))
        return self._uart_device.write_hex(data_list)
    def write_hex(self, data, timeout_s=None):
    	'''
	    uart write hex
        Args:
            data:            int,   hex data
            timeout_s:       int,      none
        Example:
          uart_write_hex(0x13)
    	'''
        return self._uart_device.write_hex(data)

    def config(self, name, baudrate=115200, data_bits=8, stop_bits=1,parity='none',timestamp='OFF'):
    	'''
        uart config
        Args:
            name:   string,       uart device name or None. The port will open on object creation,
                                                when port given. The port will not be open when port not given.
                                                Default port is None.
            baudrate:              int,          uart baud rate such as 9600 or 115200 etc. Default baudrate is 115200.
            data_bits:              int,          number of data bits. Possible values: 5,6,7,8. Default data_bits is
                                                8bit.
            stop_bits:              float,        number of stop bits. Possible values: 1,1.5,2. Default stop_bits is 1.                                 
            parity:                string,       enable parity checking. Possible values: ('none'/'odd'/'even'/
                                                mark'/'space'). 'none' for no check 'odd' for odd check, 'even' for
                                                even check. Default no check parity, 'mark' for parity bit is always 1,
                                                'space' for parity bit is always 0.
            timestamp:              string,     reserve
 
    	Example:
		    uart_config(UUT,1000000,8,1,none,OFF)

    	'''
        self._uart_device.config(int(baudrate),int(data_bits),parity,int(stop_bits))
        return PASS_MASK

    def open(self):
        '''
        Open uart port and reset input/output buffer.
        Args:
            none
        Example:
            uart_open()
        '''
        return self._uart_device.open()
        
    def close(self):
        '''
        Uart close port immediately
        Args:
            none
        Example:
            uart_close()

        '''
    	return self._uart_device.close()

  #   def pin_contrl(self,uart,state):
  #   	'''
  #       set uart enbale or disable
  #       Args:
  #           uart:    string,   reserve
  #           state:   int,      0 or 1
		# Example:
		#     uart_pin_contrl("uart","enable")
		#     uart_pin_contrl("uart","disable")

  #   	'''
  #       if state == 'enable':
  #           self.gpio_995.set_dir('output')
  #           self.gpio_995.set_level(1)
  #       else:
  #           self.gpio_995.set_level(0)
  #       return PASS_MASK

    def _create_server_socket(self, port):
        try:
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            raise e

        try:
            serversocket.setblocking(False)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            addr = ("0.0.0.0", port)
            serversocket.bind(addr)
            serversocket.listen(5)
        except socket.error as e:
            serversocket.close()
            raise e

        return serversocket

    def _add_connect_socket(self, client):
        if self._connect_socket is not None:
            self._del_connect_socket()
        self._inputs.append(client)
        self._connect_socket = client
        print("add connected socket fd = %d"%(client.fileno()))

    def _del_connect_socket(self):
        if self._connect_socket is not None:
            self._inputs.remove(self._connect_socket)
            self._connect_socket.close()
            self._connect_socket = None

    def _net_to_uart(self):
        try:
            data = self._connect_socket.recv(2048)
        except socket.error as e:
            print("read %d socket error:%s"%(self._connect_socket.fileno(), repr(e)))
            self._del_connect_socket()
            return 0

        if len(data) == 0:
            self._del_connect_socket()
            return 0

        # self._total_net_size += len(data)
        # print("recev %s net byte size %d total recev :%d"%('self._uartname' ,len(data),\
        #             self._total_net_size))
        # print("net to uart data:%s"%(logger.print_list2hex(list(bytearray.fromhex(data.encode("hex"))))))

        try:
            # self._uart_device.write((data))
            # self._uart_device.write_hex((data))
            self.write(data)
        except Exception as e:
            print("write %s device error %s"%('self._uartname',repr(e)))
            return 0
        return 1

    def _uart_to_net(self):
        # uart_data = self._uart_device.read()
        # uart_data = self._uart_device.read_hex(size=1024, timeout_s=0)
        uart_data = self.read()
        if self._connect_socket is None:
            return 0

        if not uart_data:
            return 0
        else :
            # self._total_uart_size += len(uart_data)
            # print(" read %s data byte size :%d total read size : %d"%\
            #             ('self._uartname',len(uart_data),self._total_uart_size))

            try:
                self._connect_socket.send(bytes(uart_data))
                # print("client %d send  byte size : %d"%(self._connect_socket.fileno(),len(uart_data)))
            except socket.error as e:
                print("device %s net send error"%('self._uartname'))
                self._del_connect_socket()

        return 1

    def run(self):
        try:
            self._server_socket = self._create_server_socket(self._port)
        except socket.error as e:
            print("%s device create port %d server socket failed:%s" % ('self._uartname', self._port, repr(e)))
            return
        else:
            print("%s device create server socket fd=%s port=%d" %
                        ('self._uartname', self._server_socket.fileno(), self._port))

        self._inputs.append(self._server_socket)
        while not self._uart_stop:
            '''nonboclking mode to poll the socket'''
            read_able_list = select.select(self._inputs, [], [], 0)[0]

            if self._server_socket in read_able_list:
                client, addr = self._server_socket.accept()
                self._del_connect_socket()
                self._add_connect_socket(client)
                continue

            if self._connect_socket in read_able_list:
                try:
                    self._net_to_uart()
                except Exception as e:
                    print("%s net to uart error:%s" % ('self._uartname', repr(e)))
                    break

            # if self._uart_device in read_able_list:
            #     try:
            #         self._uart_to_net()
            #     except Exception as e:
            #         print("%s uart to net error:%s" % ('self._uartname', repr(e)))
            #         break


            try:
                ret_uart2net = self._uart_to_net()
            except Exception as e:
                print("%s uart to net error:%s"%('self._uartname', repr(e)))
                break

            if ret_uart2net == 0 and len(read_able_list) == 0:
                time.sleep(0.05)


        self._del_connect_socket()
        self._server_socket.close()



   
