
class DmmException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class DMM(object):

    rpc_public_api = ['set_sampling_rate', 'get_sampling_rate', 'single_voltage_measure', 'set_measure_path',
                      'get_measure_path', 'single_current_measure', 'continuous_voltage_measure',
                      'continuous_current_measure', 'start_continuous_measure', 'stop_continuous_measure']

    def __init__(self, adc=None, config_gpio=None,
                 meter_sel_bit=None, range_sel_bit=None, eeprom=None,
                 nct75=None, board_config=None, sample_res=1, gain=1,
                 offset=0):

        self.adc = adc
        self.config_gpio = config_gpio
        self.meter_sel_bit = meter_sel_bit
        self.range_sel_bit = range_sel_bit
        self.eeprom = eeprom
        self.nct75 = nct75
        self.board_config = board_config
        self.measure_path = {}
        self.sample_res = sample_res
        self.gain = gain
        self.offset = offset

    def set_sampling_rate(self, channel=None, sampling_rate=None):

        try:
            self.adc.set_sampling_rate(channel, sampling_rate)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)

    def get_sampling_rate(self, channel=None):
        try:
            return self.adc.get_sampling_rate(channel)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)

    def single_voltage_measure(self, channel=None):
        volt = 0
        try:
            volt = self.adc.read_volt()
        except Exception as e:
            raise DmmException("Dmm: %s" + e)
        return (volt, 'mV')

    def set_measure_path(self, channel, scope):
        self.measure_path["channel"] = channel
        self.measure_path["range"] = scope

    def get_measure_path(self):
        return self.measure_path

    def single_current_measure(self, channel=None):
        volt = 0
        try:
            volt = self.adc.measure_voltage(channel)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)
        return (volt / self.sample_res, "mA")

    def continuous_voltage_measure(self, channel):
        try:
            return self.adc.continuous_voltage_measure(channel)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)

    def continuous_current_measure(self, count):
        try:
            return self.adc.continuous_current_measure(count)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)

    def start_continuous_measure(self, channel):
        try:
            return self.adc.start_continuous_measure(channel)
        except Exception as e:
            raise DmmException("Dmm: %s" + e)

    def stop_continuous_measure(self):
        try:
            return self.adc.stop_continuous_measure()
        except Exception as e:
            raise DmmException("Dmm: %s" + e)
