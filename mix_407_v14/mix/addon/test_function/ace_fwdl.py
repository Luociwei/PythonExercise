import re
import time
import json

from mix.driver.smartgiant.smartgiant_fwdl.smartgiant_fwdl_def import SmartGiantFWDLDef

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"



class ACE_FWDL(object):

    rpc_public_api = ['programmer_erase','programmer_only','program_readverify','programmer_id']
    def __init__(self, xobjects):
        self.fwdl = xobjects['fwdl1']
        self.spi_flash_info = self.load_spi_Flash_info()
        print self.spi_flash_info

    def load_spi_Flash_info(self):
        spi_info = {}
        with open(SmartGiantFWDLDef.CHIP_CONFIG_FULL_NAME, 'r') as f:
            info = json.load(f)['spi_flash']
            for item in info:
                chip_id = '%s,%s,%s'%(item['id']["POWER_ID"],item['id']["MANUFACTOR_ID"],item['id']["DEVICE_ID"])
                chip_name = item['chip_name']
                spi_info[chip_id.lower()] = chip_name
        
        return spi_info

    def programmer_id(self,chip):
        '''
        erase ace programer function
        Args:
            ch1:         channel number, reserve
            chip:        ic chip module,such as: w25q128
        Examples:
            programmer_id(w25q128):

        '''       
        ret = self.fwdl.program_id(chip)
        match_group = re.findall("id:(0x\w+,0x\w+,0x\w+)",ret)
        chip_name = 'Unknown'
        if match_group :
            chip_id = match_group[0]
            chip_name = self.spi_flash_info.get(chip_id.lower())

        ret += '\nchip_name:%s'%chip_name
            
        return ret

    def programmer_erase(self,ch1,chip):
        '''
        erase ace programer function
        Args:
            ch1:         channel number, reserve
            chip:        ic chip module,such as: w25q128
        Examples:
            programmer_erase(ch1,w25q128):

        '''
        ret = self.fwdl.program_erase(chip)
        return ret

    def programmer_only(self,ch1,chip,binfile):
        '''
        program ace function
        Args: 
            ch1:        channel number, reserve
            chip:       ic chip module,such as: w25q128
            binfile:    program bin file name
        
        Examples:
		programmer_only(ch1,w25q128,binfileName)
        '''
        ret = self.fwdl.program_only(chip,binfile,0)
        return ret

    def program_readverify(self,ch1,chip,name,addr,filesize):
        '''
        check program correct or not
        Args:
            ch1:        channel number, reserve
            chip:       ic chip module,such as: w25q128
            name:       readback file name
            addr:       address for read back
            filesize:   size for read back
        example:
        program_readverify(ch1,w25q128,0,100)

        '''

        addr = int(addr,16)
        filesize = int(filesize,16)
        ret = self.fwdl.program_readverify(chip,name,addr,filesize)
        return ret



