#
# copyright (c) 2009 Ralf Habacker <ralf.habacker@freenet.de>
#
import inspect
import os
import sys
import datetime
from ctypes import *

import functools

from CraftDebug import craftDebug
import portage
from compiler import craftCompiler
from CraftConfig import *
import utils


## @todo complete a release and binary merge dir below rootdir
# 1.  enable build type related otDmerge install settings
# 2a. use different install databases for debug and release
# 3. binary packages which are build type independent should be
# marked in both databases or should have a separate install database
# question: How to detect reliable this case ?


class InitGuard(object):
    _initialized = {}
    _verbose = False

    @staticmethod
    def _dummy_init(key, *args, **kwargs):
        if InitGuard._verbose:
            print("dummy_init", key)
        args[0].__dict__ = InitGuard._initialized[key].__dict__

    @staticmethod
    def init_once(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            if fun.__name__ != "__init__":
                raise Exception("InitGuard can only handle __init__ calls")
            key = (args[0].__class__, fun.__code__)
            if key not in InitGuard._initialized:
                if InitGuard._verbose:
                    print("init", key)
                InitGuard._initialized[key] = args[0]
                return fun(*args, **kwargs)
            else:
                return InitGuard._dummy_init(key, *args, **kwargs)
        return inner

class CraftBase(object):
    """base class for craft system - holds attributes and methods required by base classes"""

    @InitGuard.init_once
    def __init__( self):
        # TODO: some __init__  of subclasses need to already have been
        # called here. That is really the wrong way round.
        object.__init__(self)
        craftDebug.log.debug("CraftBase.__init__ called")

        self.filename, self.category, self.subpackage, self.package, mod = portage.PortageInstance._CURRENT_MODULE  # ugly workaround we need to replace the constructor
        self.subinfo = mod.subinfo(self, portage.PortageInstance.options)

        self.buildSystemType = None

        self.versioned              = False
        self.CustomDefines       = ""
        self.createCombinedPackage  = False

        self.isoDateToday           = str( datetime.date.today() ).replace('-', '')

    def __str__(self):
        if self.subpackage:
            return "%s/%s/%s" % (self.category,self.subpackage,self.package)
        else:
            return "%s/%s" % (self.category,self.package)

    @property
    def noFetch(self):
        return craftSettings.getboolean("General", "WorkOffline", False)

    @property
    def noFast(self):
        return craftSettings.getboolean("General", "EMERGE_NOFAST", True )

    @property
    def noClean(self):
        return craftSettings.getboolean("General", "EMERGE_NOCLEAN", False )

    @property
    def forced(self):
        return craftSettings.getboolean("General", "EMERGE_FORCED", False )

    @property
    def buildTests(self):
        return craftSettings.getboolean("Compile", "BuildTests")

    def buildType(self):
        """return currently selected build type"""
        return craftSettings.get("Compile","BuildType")

    def buildArchitecture(self):
        """return the target CPU architecture"""
        craftCompiler.architecture()

    def workDirPattern(self):
        """return base directory name for package related work directory"""
        directory = ""
        if self.subinfo.options.useCompilerType == True:
            directory += "%s-" % craftCompiler.getCompilerName()
        if self.subinfo.options.cmake.useIDE or self.subinfo.options.cmake.openIDE:
            directory += "ide-"
        if self.subinfo.options.useBuildType == False:
            directory += "%s" % (self.buildTarget)
        elif( self.buildType() == None ):
            directory += "%s-%s" % ("default", self.buildTarget)
        else:
            directory += "%s-%s" % (self.buildType(), self.buildTarget)
        return directory

    def imageDirPattern(self):
        """return base directory name for package related image directory"""
        directory = "image"

        if self.subinfo.options.useCompilerType == True:
            directory += '-' + craftCompiler.getCompilerName()
        if self.subinfo.options.useBuildType == True:
            directory += '-' + self.buildType()
        directory += '-' + self.buildTarget
        return directory

    def sourceDir(self, dummyIndex=0):
        utils.abstract()

    def packageDir(self):
        """ add documentation """
        return portage.getDirname( self.category, self.package )

    def buildRoot(self):
        """return absolute path to the root directory of the currently active package"""
        return os.path.join( CraftStandardDirs.craftRoot(), "build", self.category, self.package )

    def workDir(self):
        """return absolute path to the 'work' subdirectory of the currently active package"""
        return os.path.join( self.buildRoot(), "work" )

    def buildDir(self):
        craftDebug.log.debug("CraftBase.buildDir() called")
        builddir = os.path.join(self.workDir(), self.workDirPattern())
        if self.subinfo.options.unpack.unpackIntoBuildDir and self.subinfo.hasTargetSourcePath():
            builddir = os.path.join(builddir, self.subinfo.targetSourcePath())
        craftDebug.log.debug("package builddir is: %s" % builddir)
        return builddir

    def imageDir(self):
        """return absolute path to the install root directory of the currently active package
        """
        return os.path.join( self.buildRoot(), self.imageDirPattern() )

    def installDir(self):
        """return absolute path to the install directory of the currently active package.
        This path may point to a subdir of imageDir() in case @ref info.targetInstallPath is used
        """
        if self.subinfo.hasInstallPath():
            installDir = os.path.join( self.imageDir(), self.subinfo.installPath())
        else:
            installDir = self.imageDir()
        return installDir

    def mergeSourceDir(self):
        """return absolute path to the merge source directory of the currently active package.
        This path may point to a subdir of imageDir() in case @ref info.targetInstallPath for a
        specific target or @ref self.subinfo.options.merge.sourcePath is used
        """
        if not self.subinfo.options.merge.sourcePath == None:
            directory = os.path.join( self.imageDir(), self.subinfo.options.merge.sourcePath )
        else:
            directory = self.imageDir()
        return directory

    def mergeDestinationDir(self):
        """return absolute path to the merge destination directory of the currently active package.
        """
        return CraftStandardDirs.craftRoot()

    def packageDestinationDir( self, withBuildType=True ):
        """return absolute path to the directory where binary packages are placed into.
        Default is to optionally append build type subdirectory"""

        craftDebug.log.debug("CraftBase.packageDestinationDir called")
        dstpath = craftSettings.get("General","EMERGE_PKGDSTDIR", os.path.join( CraftStandardDirs.craftRoot(), "tmp" ) )

        if not os.path.exists(dstpath):
            utils.createDir(dstpath)
        return dstpath

    @property
    def buildTarget(self):
        return self.subinfo.buildTarget

    @property
    def version(self):
        return self.subinfo.defaultTarget

    @property
    def rootdir(self):
        return CraftStandardDirs.craftRoot()

    def enterBuildDir(self):
        craftDebug.trace("CraftBase.enterBuildDir called")

        if ( not os.path.exists( self.buildDir() ) ):
            os.makedirs( self.buildDir() )
            craftDebug.log.debug("creating: %s" % self.buildDir())

        os.chdir( self.buildDir() )
        craftDebug.log.debug("entering: %s" % self.buildDir())

    def enterSourceDir(self):
        if ( not os.path.exists( self.sourceDir() ) ):
            return False
        craftDebug.log.warning("entering the source directory!")
        os.chdir( self.sourceDir() )
        craftDebug.log.debug("entering: %s" % self.sourceDir())

    def system( self, command, errorMessage="", debuglevel=1, **kw):
        """convencience function for running system commands.
        This method prints a debug message and then runs a system command.
        If the system command returns with errors the method prints an error
        message and exits if @ref self.subinfo.options.exitOnErrors  is true"""

        if utils.system( command, **kw):
            return True
        craftDebug.log.critical(f"Craft encountered an error: {errorMessage} cmd: {command}")
        return False

    def proxySettings(self):
        host = craftSettings.get("General", 'EMERGE_PROXY_HOST', "")
        port = craftSettings.get("General", 'EMERGE_PROXY_PORT', "")
        username = craftSettings.get("General", 'EMERGE_PROXY_USERNAME', "")
        password = craftSettings.get("General", 'EMERGE_PROXY_PASSWORD', "")
        return [host, port, username, password]


    def binaryArchiveName(self, pkgSuffix=None, fileType=craftSettings.get("Packager", "7ZipArchiveType", "7z")) -> str:
        if not pkgSuffix:
            pkgSuffix = ''
            if hasattr(self.subinfo.options.package, 'packageSuffix') and self.subinfo.options.package.packageSuffix:
                pkgSuffix = self.subinfo.options.package.packageSuffix

        if self.subinfo.hasSvnTarget():
            version = "latest"
        else:
            version = self.getPackageVersion()[0]
        if fileType:
            fileType = f".{fileType}"
        else:
            fileType = ""
        return f"{self.package}-{version}-{craftCompiler}{pkgSuffix}{fileType}"

    def cacheLocation(self) -> str:
        if craftSettings.getboolean("QtSDK", "Enabled", "False"):
            version = "QtSDK_%s" % craftSettings.get("QtSDK", "Version")
        else:
            version = portage.getPackageInstance("libs", "qtbase").subinfo.buildTarget
            version = "Qt_%s" % version
        cacheDir = craftSettings.get("Packager", "CacheDir", os.path.join(CraftStandardDirs.downloadDir(), "binary"))
        return os.path.join(cacheDir, version, *craftCompiler.signature, self.buildType())

    def cacheRepositoryUrls(self) -> [str]:
        if craftSettings.getboolean("QtSDK", "Enabled", "False"):
            version = "QtSDK_%s" % craftSettings.get("QtSDK", "Version")
        else:
            version = portage.getPackageInstance("libs", "qtbase").subinfo.buildTarget
            version = "Qt_%s" % version
        return ["/".join([url, version, *craftCompiler.signature, self.buildType()]) for url in craftSettings.get("Packager", "RepositoryUrl").split(";")]

