#!/bin/bash

MIX_ROOT_FOLDER_PATH="/mix"
APP_SCRIPT_FOLDER_PATH=$MIX_ROOT_FOLDER_PATH/lynx/script

FW_UPDATE_BASE_FOLDER=/var/fw_update
FW_UPLOAD_PACKAGE_FOLDER_PATH=$FW_UPDATE_BASE_FOLDER/upload
FW_UPDATE_TEMP_FOLDER_PATH=$FW_UPDATE_BASE_FOLDER/temp
FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH=$FW_UPDATE_TEMP_FOLDER_PATH/script
FW_BACKUP_TEMP_FOLDER_PATH=$FW_UPDATE_BASE_FOLDER/backup
FW_UPDATE_SEQUENCE_SCRIPTS=$FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH/sequence

#FW package tgz
FW_UPDATE_PACKAGE_NAME_RULE="MIX_FW_*.tgz"
FW_UPDATE_PACKAGE_FILE_NAME=

FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME="scripts.tgz"

FW_UPDATE_DEB_FILE_NAME_RULE="*.deb"
MD5SUM_FILE_NAME='md5.txt'
VERSION_FILE_NAME='version.json'

#get package path
echo "Firwmare upload folder path: $FW_UPLOAD_PACKAGE_FOLDER_PATH"

#get package name

echo "Firware package name rule: $FW_UPDATE_PACKAGE_NAME_RULE"

#check Firmware package is exist? and equal one count.
package_file_count=`ls $FW_UPLOAD_PACKAGE_FOLDER_PATH/$FW_UPDATE_PACKAGE_NAME_RULE | wc -l 2>/dev/null`
if [ $package_file_count -eq 0 ];then
    if [ -d $FW_UPDATE_TEMP_FOLDER_PATH ]; then
        deb_file_count=`ls $FW_UPDATE_TEMP_FOLDER_PATH/$FW_UPDATE_DEB_FILE_NAME_RULE | wc -l 2>/dev/null`
        if [ $deb_file_count -gt 0 ];then
            echo "-- Found deb packages, start to install..."
            FW_UPDATE_PACKAGE_FILE_NAME="DEB"
        else
            echo "- Warning - There is no valid FW package file"
            echo "Not Applicable" >> /tmp/update_skip
            exit 1
        fi
    else
        echo "- Warning - There is no valid FW package file"
        echo "Not Applicable" >> /tmp/update_skip
        exit 1
    fi
elif [ $package_file_count -gt 1 ];then
    echo "- Error - There are multiple($package_file_count) FW package files found in $FW_UPLOAD_PACKAGE_FOLDER_PATH"
    echo "-- Clean up now and please re-upload correctly"
    rm -rf $FW_UPLOAD_PACKAGE_FOLDER_PATH/$FW_UPDATE_PACKAGE_DEFAULT_NAME_RULE
    exit 2
else
    echo '-- Found valid FW package'
    cd $FW_UPLOAD_PACKAGE_FOLDER_PATH
    FW_UPDATE_PACKAGE_FILE_NAME=`ls $FW_UPDATE_PACKAGE_NAME_RULE`
    rm -rf $FW_UPDATE_TEMP_FOLDER_PATH
    mkdir -p $FW_UPDATE_TEMP_FOLDER_PATH

    echo ""
    echo "-- Update firmware package: $FW_UPDATE_PACKAGE_FILE_NAME"
fi

# Extract fw components from tgz
FW_Decompression(){

    if [ $FW_UPDATE_PACKAGE_FILE_NAME = "DEB" ]; then
        echo "[Install DEB] decompress fw package is Skipped"
        return 0
    fi

    if [ ! -f "$FW_UPLOAD_PACKAGE_FOLDER_PATH/$FW_UPDATE_PACKAGE_FILE_NAME" ]; then
        echo "Application update package file '$FW_UPDATE_PACKAGE_FILE_NAME' is not exist."
        return 1
    fi

    echo ""
    echo "Extract $FW_UPLOAD_PACKAGE_FOLDER_PATH/$FW_UPDATE_PACKAGE_FILE_NAME files -> $FW_UPDATE_TEMP_FOLDER_PATH"
    cd $FW_UPLOAD_PACKAGE_FOLDER_PATH
    tar -mzxvf $FW_UPDATE_PACKAGE_FILE_NAME -C $FW_UPDATE_TEMP_FOLDER_PATH
    if [ $? -ne 0 ]; then
        echo "- Error - 'failed to decompress $FW_UPDATE_PACKAGE_FILE_NAME"
        return 2
    fi
    echo "-- $FW_UPDATE_PACKAGE_FILE_NAME Decompression successful"
    return 0
}

FW_ExtractScripts()
{
    if [ $FW_UPDATE_PACKAGE_FILE_NAME = "DEB" ]; then
        echo "[Install DEB] Extract scripts is Skipped"
        return 0
    fi

    #scripts prepare
    mkdir -p $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH

    cd $FW_UPDATE_TEMP_FOLDER_PATH
    if [ -f $FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME ]; then
        echo "Extract '$FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME' -> '$FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH'. "
        tar -mzxvf $FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME -C $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH
        if [ $? -ne 0 ]; then
            echo "$FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME decompression failure."
            return 1
        fi
        echo "'$FW_UPDATE_SCRIPTS_PACKAGE_FILE_NAME' decompression successed."
    else
        echo "Failover to use present update scripts"
        cp -af $APP_SCRIPT_FOLDER_PATH/* $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH
    fi
    return 0
}

FW_MD5_Verify(){

    if [ $FW_UPDATE_PACKAGE_FILE_NAME = "DEB" ]; then
        echo "[Install DEB] md5 check is Skipped"
        return 0
    fi

    #MD5 verification
    set +e
    echo ""
    echo "MD5SUM verification"
    cd $FW_UPDATE_TEMP_FOLDER_PATH
    if [ ! -s $MD5SUM_FILE_NAME ];then
        echo "- Error - '$MD5SUM_FILE_NAME' file is not exist or it is empty"
        return 1
    fi
    echo "'$MD5SUM_FILE_NAME' file  is exist and not empty."


    echo "Checking '$MD5SUM_FILE_NAME' file integrity ..."
    cd $FW_UPDATE_TEMP_FOLDER_PATH
    file_name_list=`ls`
    echo "update firmware file list:"
    for file_name in $file_name_list
    do
        echo " $file_name"
    done

    for file_name in $file_name_list
    do
        echo "check '$file_name'"
        if [ $file_name = $MD5SUM_FILE_NAME ]; then
            continue
        fi

        exist_msg=`grep $file_name $MD5SUM_FILE_NAME -w`
        if [[ -n "$exist_msg" ]];then
            echo "'$file_name' is in '$MD5SUM_FILE_NAME' file"
            continue
        else
            echo "- Error -'$file_name' not in '$MD5SUM_FILE_NAME' file"
            return 2
        fi

    done
    echo "'$MD5SUM_FILE_NAME' file is complete."


    #check md5
    echo ""
    echo "Checking the firmware file integrity......"

    ERROR_MESSAGE=`md5sum -c $MD5SUM_FILE_NAME | grep -w 'FAILED'`
    WARNING_MESSAGE=`md5sum -c $MD5SUM_FILE_NAME | grep -w 'WARNING'`

    if [ -n "$ERROR_MESSAGE" ] || [ -n "$WARNING_MESSAGE" ];then
        echo "- Error - $ERROR_MESSAGE"
        echo "- Error - $WARNING_MESSAGE"
        echo "- Error - Firmware update files is not complete."
        return 3
    fi
    echo "Firmware update files is complete."
    return 0
}

CleanUp(){
    echo ""
    echo "Clean update object files..."
    #---------------------------------------
    rm -rf $FW_UPDATE_TEMP_FOLDER_PATH
    rm -rf $FW_BACKUP_TEMP_FOLDER_PATH
    rm -rf $FW_UPLOAD_PACKAGE_FOLDER_PATH/$FW_UPDATE_PACKAGE_FILE_NAME
    sync
    echo "Clean update object files finished"
    return 0
}

#-----------------------------
#Execution process
FW_Decompression
if [ $? -ne 0 ]; then
    CleanUp
    exit 2
fi

#MD5 Check
FW_MD5_Verify
if [ $? -ne 0 ]; then
    CleanUp
    exit 3
fi

#Extract Scripts
FW_ExtractScripts
if [ $? -ne 0 ]; then
    CleanUp
    echo "- Error - Firmware extract update scripts failed."
    exit 4
fi

echo ""
set +e
cd $FW_UPDATE_SEQUENCE_SCRIPTS
script_files_list=`ls *.sh`
for script_file in $script_files_list
do
    echo ""
    echo "-------------Enter script $script_file------------------"
    bash $script_file $FW_UPDATE_PACKAGE_FILE_NAME $FW_UPDATE_BASE_FOLDER
    errno=$?
    echo "-------------Leaving script $script_file----------------"
    echo ""

    if [ $errno -ne 0 ]; then
        echo "- Error - $script_file failed with return code $errno"
        echo "terminating..."
        CleanUp
        exit 5
    fi
done

# update scripts to APP folder
cp -af $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH/* $APP_SCRIPT_FOLDER_PATH/
CleanUp

echo "done" >> /tmp/update_success
echo " - Success - '$FW_UPDATE_PACKAGE_FILE_NAME' Firmware Update finished."
echo ""

exit 0
