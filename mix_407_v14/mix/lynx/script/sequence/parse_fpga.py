'''
Python script to get information like xavier type from FPGA bitstream
Xilinx .git file header format:
    http://www.fpga-faq.com/FAQ_Pages/0026_Tell_me_about_bit_files.htm
    https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf
'''
import argparse
import json

def str_2_int(string, endian='be'):
    '''
    Convert string to int. le for little-endian, be for big-endian
    bit file defaults to have big-endian.
    '''
    ret = 0
    if endian == 'le':
        string = reversed(string)
    elif endian == 'be':
        pass
    else:
        raise Exception('Unexpected endian{}; either le or be.'.format(endian))
    for i in string:
        ret = ret << 8
        ret += ord(i)

    return ret

def parse_bit_file_header(bit_file):
    keys = ['0', 'a', 'b', 'c', 'd']
    headers = {}
    field_names = {
        '0': 'header',
        'a': 'design_name',
        'b': 'part_name',
        'c': 'build_date',
        'd': 'build_time',
    }
    with open(bit_file, 'rb') as f:
        # initially there is no key like 'a' or 'b' for 1st field
        # starting from reading 2 bytes for 1st field length
        rd_len = 2
        for key in keys:
            '''
            read field a, b, c, d
            a: string design name
            b: part name, like '7z007sclg400'
            c: build date
            d: build time
            e: rest of file; 32bit length bytes; do not read.
            '''
            if key != '0':
                key_read = f.read(1).decode()
                assert key == key_read
            data = bytearray(f.read(rd_len))
            field_len = str_2_int(data.decode())
            data = bytearray(f.read(field_len).lower())
            # 0xaa995566 is sync word that separate header and real bitstream data
            if key == '0':
                # additional 0x0001 before 1st key 'a'
                f.read(2)
            headers[field_names[key]] = data[:-1]  #ignore trailing \x00
    return headers


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file',
                        help='FPGA bitstream file; default fpga.bit',
                        default='fpga.bit')
    parser.add_argument('-o', '--output_file',
                        help='optional output file of parsed FPGA header; '
                             'default None means do not generate output file but only print to console',
                        default=None)
    parser.add_argument('-f', '--format',
                        help='output format; simple means each item in 1 line, '
                             'with header name and value separated by ":"; '
                             'json means json dictionary.',
                        default='simple')

    parser.add_argument('--field', help='single field value to print',
                        default=None)

    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    output_format = args.format
    field = args.field
    headers = parse_bit_file_header(input_file)
    if field:
        # print field value and exit.
        print(headers[field].decode())
        exit(0)
    dict_output_format = {
        'simple': lambda x: '\n'.join('{}: {}'.format(k, v) for k, v in x.items()),
        'json': lambda x: json.dumps(x, indent=4)
    }
    printing = dict_output_format[output_format](headers)
    print(printing)
