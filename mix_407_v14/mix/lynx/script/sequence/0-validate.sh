#!/bin/bash

PACKAGE_SOURCE_PATH=
FW_UPDATE_FOLDER_BASE=

set +e

Usage()
{
cat <<EOF
Usage:
$0 <fw_package_name> <fw_update_folder_base>
EOF
}

if [ "$#" -lt 2 ] ;then
    Usage
    exit 0
fi

PACKAGE_SOURCE_PATH=$1
FW_UPDATE_FOLDER_BASE=$2
FW_UPDATE_TEMP_FOLDER_PATH=$FW_UPDATE_FOLDER_BASE/temp
FW_UPDATE_SEQUENCE_TEMP_FOLDER=$FW_UPDATE_TEMP_FOLDER_PATH/script/sequence



fpga_validate(){
    # get zynq part name on xavier and zynq part name from given fpga.bit
    # block update if not-match.
    # flashing wrong uboot could corrupt xavier's filesystem;
    # flashing wrong fpga.bit could result in xavier boot stop in uboot.

    if [ $PACKAGE_SOURCE_PATH = "DEB" ]; then
        echo "[Install DEB] fpga check is Skipped"
        return 0
    fi
    set +e
    zynq_type_current=`python $FW_UPDATE_SEQUENCE_TEMP_FOLDER/get_current_zynq_type.py`
    ret=$?
    if [[ $ret -ne 0 ]]
    then
        echo "- Error - Failed to get current zynq SOC type by reading CLSR PSS_IDCODE; ret=$ret"
        return 1
    fi

    zynq_type_bitstream=`python $FW_UPDATE_SEQUENCE_TEMP_FOLDER/parse_fpga.py -i $FW_UPDATE_TEMP_FOLDER_PATH/fpga.bit --field part_name`
    ret=$?
    if [[ $ret -ne 0 ]]
    then
        echo "- Error - Failed to get zynq SOC type from fpga.bit header; ret=$ret"
        return 1
    fi

    if [[ $zynq_type_bitstream == *$zynq_type_current* ]]
    then
        # match; proceed with firmware update
        echo "Zyqn SOC type in system ("$zynq_type_current") and in bitstream ("$zynq_type_bitstream") matches. proceede with updating."
        return 0
    else
        echo "Zyqn SOC type in system ("$zynq_type_current") and in bitstream ("$zynq_type_bitstream") dose not match. Firmware update stopped."
        return 1
    fi
}


fpga_validate
if [ $? -ne 0 ]; then
    exit 1
fi

exit 0
