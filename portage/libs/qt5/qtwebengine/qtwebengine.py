# -*- coding: utf-8 -*-
import info


class subinfo(info.infoclass):
    def setTargets( self ):       
        self.versionInfo.setDefaultValues( )

    def setDependencies( self ):
        self.dependencies['libs/qtbase'] = 'default'


from Package.Qt5CorePackageBase import *

class Package( Qt5CorePackageBase ):
    def __init__( self, **args ):
        Qt5CorePackageBase.__init__( self )
        
    def compile(self):
        if not ("Paths","Python27") in emergeSettings:
            utils.die("Please make sure Paths/Python27 is set in your kdesettings.ini")
        utils.prependPath(emergeSettings.get("Paths","PYTHON27",""))
        return Qt5CorePackageBase.compile(self)
       

        
