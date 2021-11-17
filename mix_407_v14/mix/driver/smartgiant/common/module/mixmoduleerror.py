class MIXModuleError(Exception):
    '''
    Generic error for all MIX modules
    '''
    def __init__(self, error_details=''):
        self.error_details = error_details

    def __str__(self):
        return self.error_details


class InvalidHardwareChannel(MIXModuleError):
    '''
    The specified hardware channel is invalid

    Could occur if a module supports channels 0 and 1, and a function is passed a channel of 2
    '''


class InvalidHardwareChannelType(MIXModuleError):
    '''
    The specified hardware channel type is invalid

    Could occur if a module supports "voltage" and "current" modes for a channel, but a function is passed
    a different channel type such as "volttage" (misspelling) or a completely unsupported type such as
    "resistance"
    '''


class InvalidRange(MIXModuleError):
    '''
    The specified range is invalid

    Could occur if a configuration function is passed an acquisition or generation range outside the supported
    ranges of that module
    '''


class InvalidSampleRate(MIXModuleError):
    '''
    The specified sample rate is invalid

    Could occur if an acquisition/generation is configured for a sample rate outside those supported by the module
    '''


class InvalidSampleCount(MIXModuleError):
    '''
    The specified sample count is invalid

    Could occur if an acquisition/generation is configured for a number of samples outside the supported range of
    the module
    '''


class InvalidTimeout(MIXModuleError):
    '''
    The specified timeout value is invalid

    Could occur if a module acquisiton or generation is passed an invlid timeout value, usually meaning <0 but
    could be specific to that module.
    '''


class InvalidCalibrationIndex(MIXModuleError):
    '''
    Thrown if the user attempts to configure a module with an invalid Calibration
    index.
    '''


class InvalidCalibrationCell(MIXModuleError):
    '''
    Thrown if the user attempts to read from a calibration cell that has an invalid
    MD5 checksum.
    '''


class ModuleDoesNotSupportCalibration(MIXModuleError):
    '''
    Thrown if the user attempts to read or write a calibration cell on a module
    which supports 0 calibration cells
    '''


class AllCalibrationCellsInvalid(MIXModuleError):
    '''
    Thrown if the user attempts to read the latest calibration index when all
    calibration cells are invalid (no date or incorrect checksum).
    '''


class InvalidCalibrationDataLength(MIXModuleError):
    '''
    Thrown if the user attempts to write a blob of cal data that does not match
    the expected length stored in the module nvmem.
    '''


class InvalidCalibrationDate(MIXModuleError):
    '''
    Thrown if the user attempts to read a calibration date cell that is either
    empty or corrupted and cannot be converted to a python datetime object.
    '''
