import serial
import time
import sys
import os


if __name__ == '__main__':
    try:
	    serial_path = 's'
	    t = serial.Serial(serial_path,115200)
	    # t = serial.Serial('/dev/cu.SLAB_USBtoUART',115200)
	    #print t
	    os.system('clear')
	    print '= '*5 + 'iPort FW Update ' + '= '*5 +'\n'
	    file_path = sys.argv[2]
    
	    f = open(file_path, 'rb')
	    print file_path
	    f_list = f.readlines()
	    f_len = len(f_list)
	    f.seek(0)
	    while t.isOpen() != True:
		    0 == 0

	    t.timeout = 2	#50ms

	    #print 'Serial port is opened successfully.\n'

	    t.write('update mcu')
	    output = t.read(5)
	    #print output

	    i=1
	    if output == 'next\n' :
		    print '\n' + ' '*3 + '-'*5+'Upadate start'+ '-'*5 + '\n'
		    t0 = time.time()
		    for line in f_list:
			    n = t.write(line[:-2])
			    output = ''
			    while output != 'next\n':
				    output = t.read(5)
			    #print i,'send: ',line, 'Return: ',output
                
			    sys.stdout.write("\rTime: %d s\tPercent: %.2f %%" %(time.time()-t0, i*100.0/f_len))

			    if i % 100 == 0 :
			    	sys.stdout.flush()

			    if i == f_len :
			    	sys.stdout.flush()
	
		
			    i = i + 1
		    t.write('update end')
		    #print 'Update end'
		    output = ''
		    while output != 'next\n':
			    output = t.read(5)
		    #sys.stdout.write('\rPercent: 100.00 %\n')
		    #sys.stdout.flush()
		    #print 'Return: '+ output
		    # print '\n\n' + ' '*3 + '*'*5 + 'Update success' + '*'*5 +'\n'


    finally:
        if f:
        
            f.close()
        if t:
           	t.close()
	    #if t.isOpen() != True:
		#print 'Serial port close.\n'
	sys.stdout.flush()	
	print 'Quit.\n'
