#!/usr/bin/env  python


#--- Purpose.
#
#   Manage a build process based on compiling and linking a bunch of object files.
#   Specifically, compile a number of source code files, and link the resulting
# object files into an executable or dynamic link library.


#--- Note on directory location.
#
#   This script can be run from any working directory, and does not need to
# reside in that working directory.
#   The only requirement is that the file names passed to the script must
# include the correct path to the files.


#--- Note on compile and link batch files.
#
#   This script uses separate, system-dependent, batch files to compile and
# link source code.  For more information, see fcns printCompileBatchInfo()
# and printLinkBatchInfo() below.


#--- Running this script.
#
#   To call this script from the Python interpreter, or from another Python script:
# >>> import <this-file-base-name>
# >>> <this-file-base-name>.manageCompileLink(arguments)


#--- Runtime help.
#
def printCompileBatchInfo(compileBatchFileName):
  #
  print 'Require a batch file {' +compileBatchFileName +'}'
  print '-- The batch file should compile the source code files of interest'
  print '-- The batch file should accept one argument, the name (including path) of the source code file to compile'
  print '-- The batch file should leave the resulting object file in the working directory'
  #
  # End fcn printCompileBatchInfo().


def printLinkBatchInfo(linkBatchFileName, compileBatchFileName):
  #
  print 'Require a batch file {' +linkBatchFileName +'}'
  print '-- The batch file should link object files compiled via ' +compileBatchFileName
  print '-- The batch file should produce a command-line executable or a library'
  print '-- The batch file should accept at least two arguments, in this order:'
  print '  ** the name of the output executable or library'
  print '  ** the name(s) of the object files to link'
  #
  # End fcn printLinkBatchInfo().


#--- Ensure access.
#
import os
import subprocess
import sys


#--- Fcn to print diagnostics.
#
def printDiagnostic(messageStr):
  #
  print '!', os.path.basename(__file__), '--', messageStr
  #
  # End fcn printDiagnostic().


#--- Fcn to quit due to an error.
#
def quitWithError(messageStr):
  #
  print 'ERROR from script file {' +os.path.basename(__file__) +'}'
  #
  if( messageStr is not None ):
    print messageStr
  #
  sys.exit(1)
  #
  # End fcn quitWithError().


#--- Fcn to verify a file exists.
#
#   If file exists, return its absolute path.  Otherwise, quit.
#
def findFileOrQuit(fileDesc, fileName):
  #
  if( not os.path.isfile(fileName) ):
    (dirName, fileName) = os.path.split(os.path.abspath(fileName))
    if( not os.path.isdir(dirName) ):
      quitWithError('Missing directory {' +dirName +'} for ' +fileDesc +' file {' +fileName +'}')
    quitWithError('Missing ' +fileDesc +' file {' +fileName +'} in directory {' +dirName +'}')
  #
  return( os.path.abspath(fileName) )
  #
  # End fcn findFileOrQuit().


#--- Fcn to delete a file.
#
#   OK if file does not exist.
#
def deleteFile(fileName):
  #
  if( os.path.isfile(fileName) ):
    try:
      os.remove(fileName)
    except:
      quitWithError('Unable to delete file {' +fileName +'}')
  elif( os.path.isdir(fileName) ):
    quitWithError('Expecting {' +fileName +'} to be a file; found a directory')
  #
  # End fcn deleteFile().


#--- Fcn to create a directory if necessary.
#
#   Return {True} if directory already exists.
#
def ensureDir(showDiagnostics, dirDesc, dirName):
  #
  if( os.path.isdir(dirName) ):
    return( True )
  #
  if( os.path.isfile(dirName) ):
    quitWithError('Expecting {' +dirName +'} to be a directory; found a file')
  #
  if( showDiagnostics ):
    printDiagnostic('Creating ' +dirDesc +' directory {' +dirName +'}')
  try:
    os.mkdir(dirName)
  except:
    quitWithError('Unable to create ' +dirDesc +' directory {' +dirName +'}')
  #
  return( False )
  #
  # End fcn ensureDir().


#--- Fcn to clean up an existing directory, or create it.
#
def cleanDir(showDiagnostics, dirDesc, dirName):
  #
  if( ensureDir(showDiagnostics, dirDesc, dirName) ):
    # Here, {dirName} already existed; need to clean it up.
    if( showDiagnostics ):
      printDiagnostic('Cleaning up existing ' +dirDesc +' directory {' +dirName +'}')
    for theEntryName in os.listdir(dirName):
      theEntryFullName = os.path.abspath(os.path.join(dirName, theEntryName))
      deleteFile(theEntryFullName)
  #
  # End fcn cleanDir().


#--- Fcn to remove an existing directory.
#
#   Assume the directory has no subdirectories.
#
def deleteDir(showDiagnostics, dirDesc, dirName):
  #
  if( showDiagnostics ):
    printDiagnostic('Removing ' +dirDesc +' directory {' +dirName +'}')
  #
  if( not os.path.isdir(dirName) ):
    quitWithError('Expecting a directory called {' +dirName +'}')
  #
  # Remove files.
  for theEntryName in os.listdir(dirName):
    theEntryFullName = os.path.abspath(os.path.join(dirName, theEntryName))
    deleteFile(theEntryFullName)
  #
  # Remove directory.
  try:
    os.rmdir(dirName)
  except:
    quitWithError('Unable to delete directory {' +dirName +'}')
  #
  # End fcn deleteDir().


#--- Fcn to compile a source code file.
#
#   Return object file name.
#
def runCompiler(showDiagnostics, compileBatchFileName, srcFileName, objDirName):
  #
  if( showDiagnostics ):
    printDiagnostic('Compiling {' +os.path.basename(srcFileName) +'}')
  srcFileName = findFileOrQuit('source code', srcFileName)
  #
  try:
    subprocess.call([compileBatchFileName, srcFileName])
  except:
    # Check failure due to missing {compileBatchFileName} before complain about
    # unknown problem.
    compileBatchFileName = findFileOrQuit('compiler batch', compileBatchFileName)
    quitWithError('Failed to run compiler batch file {' +compileBatchFileName +
      '} on source code file {' +srcFileName +'}: reason unknown')
  #
  # Check made an object file.
  (objFileBaseName, ext) = os.path.splitext(os.path.basename(srcFileName))
  objFileName = objFileBaseName +'.obj'
  if( not os.path.isfile(objFileName) ):
    objFileName = objFileBaseName +'.o'
    if( not os.path.isfile(objFileName) ):
      quitWithError('Failed to create object file for source code file {' +srcFileName +'}')
  #
  # Move object file to directory {objDirName}.
  ensureDir(showDiagnostics, 'object', objDirName)
  destObjFileName = os.path.join(objDirName, objFileName)
  if( os.path.isfile(destObjFileName) ):
    quitWithError('Object file {' +objFileName +'} already exists in directory {' +objDirName +'}')
  try:
    os.rename(objFileName, destObjFileName)
  except:
    quitWithError('Unable to move object file {' +objFileName +'} to directory {' +objDirName +'}: reason unknown')
  #
  return( objFileName )
  #
  # End fcn runCompiler().


#--- Fcn to manage a compile-link build process.
#
#   Note this fcn doesn't escape characters, such as spaces, in directory and
# file names.  The caller must take care of these issues.
#
def manageCompileLink(showDiagnostics, litter, forceRebuild,
  compileBatchFileName, linkBatchFileName, srcFileNameList, outputFileName):
  #
  if( showDiagnostics ):
    printDiagnostic('Begin compile-link build of {' +outputFileName +'}')
  #
  # Short-circuit work if possible.
  # hoho  Consider being make-like, and only rebuilding object files that are old
  # compared to sources, and only rebuilding output that is old compared to
  # object files.
  if(  os.path.isfile(outputFileName) and (not forceRebuild) ):
    if( showDiagnostics ):
      printDiagnostic('Output file {' +outputFileName + '} already exists; doing nothing')
    return
  #
  # Delete expected outputs if they already exist.
  #   To prevent confusion in case of an error.
  deleteFile(outputFileName)
  #
  # Form names of system-specific scripts.
  findFileOrQuit('compiler batch', compileBatchFileName)
  findFileOrQuit('linker batch', linkBatchFileName)  # hoho Should figure out a way to dump the printLinkBatchInfo() information.
  #
  # Name the build directory.
  #   Put it in the working directory (which may differ from both the directory
  # for {outputFileName}, and the directory where this script file resides).
  objDirName = 'obj-' +os.path.basename(outputFileName).replace('.', '-')
  #
  # Create or clean the build directory.
  cleanDir(showDiagnostics, 'object', objDirName)
  #
  # Compile sources.
  if( showDiagnostics ):
    printDiagnostic('Compiling files using {' +compileBatchFileName +'}')
  objFileNameList = list()
  for srcFileName in srcFileNameList:
    objFileName = runCompiler(showDiagnostics, compileBatchFileName, srcFileName, objDirName)
    objFileNameList.append(objDirName +os.path.sep +objFileName)
  #
  # Link objects into {outputFileName}.
  if( showDiagnostics ):
    printDiagnostic('Linking object files using {' +linkBatchFileName +'}')
    printDiagnostic('Linking to create {' +outputFileName +'}')
  subprocess.call([linkBatchFileName, outputFileName] +objFileNameList)
  if( not os.path.isfile(outputFileName) ):
    quitWithError('Failed to link object files into {' +outputFileName +'}')
  #
  # Clean up intermediates.
  if( not litter ):
    if( showDiagnostics ):
      printDiagnostic('Cleaning up intermediate files')
    deleteDir(showDiagnostics, 'object', objDirName)
  #
  return( outputFileName )
  #
  # End fcn manageCompileLink().


#--- Run if called from command line.
#
#   If called from command line, {__name__} is "__main__".  Otherwise,
# {__name__} is base name of the script file, without ".py".
#
if __name__ == '__main__':
  #
  quitWithError('Do not run from command line: call fcn manageCompileLink() directly')
