import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

    def setDependencies( self ):
        self.dependencies['virtual/base'] = 'default'
        self.buildDependencies['dev-util/png2ico'] = 'default'
        # needed for many kf5's
        self.buildDependencies['dev-util/winflexbison'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )

