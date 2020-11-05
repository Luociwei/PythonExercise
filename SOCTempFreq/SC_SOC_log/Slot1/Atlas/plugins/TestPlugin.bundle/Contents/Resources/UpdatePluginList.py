#!/usr/bin/env python

import os
import sys
import re
import argparse
import fileinput
import fnmatch
import plistlib

gVERSION = 1.0
gUNKNOWN = 'UNKNOWN'
gCoreTestPluginName = 'kCoreTestPluginName_'
gCTPluginProtocol = 'CTPluginProtocol'
gCTTestPluginProtocol = 'CTTestPluginProtocol'
gCommonTestPlatformPlistName = 'CommonTestPlatform.plist'

#find files recursively
def recursivelyFindFilesAtPath(pathToDirectory,fileName):
	print 'recursivelyFindFilesAtPath -> ' + pathToDirectory
	print 'fileName -> ' + fileName
	foundFiles = []
	for root, dirs, files in os.walk(pathToDirectory):
		for file in files:
		#for file in fnmatch.fnmatch(file,fileName):
			#print 'file ' + file
			#if fileName in file:
			if fnmatch.fnmatch(file, fileName):
				foundFiles.append(os.path.join(root, file))
				#print 'found file ' + fileName
	#print foundFiles
	return foundFiles


# find all .h files
def recursivelyFindPluginsAtPath(pathToSourceDirectory):
	print 'recursivelyFindPluginsAtPath -> ' + pathToSourceDirectory
	hfiles = []
	pluginNameDict = {}	
	hfiles = recursivelyFindFilesAtPath(pathToSourceDirectory,'*.h')
	print hfiles
	for file in hfiles:
		print 'reading [' + file +']'
		actualPluginName=gUNKNOWN
		actualClassName=gUNKNOWN
		for line in fileinput.input([file]):
			classNameDict = {}
			p = re.findall(gCoreTestPluginName, line, 0)
			if p:
				#print line
				pluginName = re.split('@',line)
				pluginNameParts = re.split('\"',pluginName[1])
				actualPluginName = pluginNameParts[1]
				#print 'pluginName -> ' + pluginName[1]
				print 'actualPluginName -> ' + actualPluginName
			c = re.findall("(@interface)", line, 0)
			if c:
				protocolNames = [gCTPluginProtocol,gCTTestPluginProtocol]
				if any(x in line for x in protocolNames):
					#print line
					className = re.split(':',line)
					classNameParts = re.split('@interface',className[0])
					actualClassName = re.sub(r"\s+", '', classNameParts[1])
					#print 'className -> ' + className[0]
					print 'actualClassName -> ' + actualClassName
			if (actualPluginName != gUNKNOWN) and (actualClassName != gUNKNOWN):
				classNameDict['ClassName'] = actualClassName
				print classNameDict
				pluginNameDict[actualPluginName] = classNameDict
				actualPluginName=gUNKNOWN
				actualClassName=gUNKNOWN
	return pluginNameDict

def findPathToCommonTestPlatformPlist(pathToDirectory):
	pathToCommonTestPlatformArray = recursivelyFindFilesAtPath(pathToDirectory,gCommonTestPlatformPlistName)
	print pathToCommonTestPlatformArray
	pathToCommonTestPlatformFile=''
	if len(pathToCommonTestPlatformArray)>1:
		print '*** ERROR: multipleCommonTestPlatformPlistFound'
		sys.exit(multipleCommonTestPlatformPlistFound)
	elif len(pathToCommonTestPlatformArray)==0:
		pathToCommonTestPlatformFile = pathToDirectory + '/' + gCommonTestPlatformPlistName
	else:
		pathToCommonTestPlatformFile = pathToCommonTestPlatformArray[0]
	print 'pathToCommonTestPlatformFile -> ' + pathToCommonTestPlatformFile
	return pathToCommonTestPlatformFile

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


#error
multipleCommonTestPlatformPlistFound = -1

# Main
parser = argparse.ArgumentParser(description='updates CommonTestPlugin.plist')
parser.add_argument("-p", "--path", help="path to source files", action=readable_dir ,required=True)
parser.add_argument("-v", "--version", action="version", version="%(prog)s " + str(gVERSION))
args = parser.parse_args()
print (args)
pluginList=recursivelyFindPluginsAtPath(args.path)
print pluginList
commonTestPlatformDict = {'Plugins':pluginList}
print commonTestPlatformDict
pathToCommonTestPlatformFile = findPathToCommonTestPlatformPlist(args.path)
plistlib.writePlist(commonTestPlatformDict,pathToCommonTestPlatformFile)
