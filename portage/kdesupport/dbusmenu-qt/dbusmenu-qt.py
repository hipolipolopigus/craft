import info

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.dependencies['virtual/base'] = 'default'
        self.buildDependencies['dev-util/doxygen'] = 'default'
        self.dependencies['libs/qtbase'] = 'default'
        # self.dependencies['kdesupport/qjson'] = 'default'

    def setTargets( self ):
        # Dbusmenu-qt moved to bazaar in launchpad
        # check https://launchpad.net/libdbusmenu-qt for the trunk sources

        for ver in ['0.9.2','0.6.4']:
          self.targets[ver] = "https://launchpad.net/libdbusmenu-qt/trunk/" + ver +"/+download/libdbusmenu-qt-" +ver + ".tar.bz2"
          self.targetInstSrc[ver] = 'libdbusmenu-qt-' + ver
        self.targets[ "qt5" ] = "http://winkde.org/~pvonreth/other/tars/libdbusmenu-qt-qt5.tar.gz"
        self.targetInstSrc["qt5"] = 'libdbusmenu-qt-qt5'
        self.shortDescription = "a Qt implementation of the DBusMenu spec"

        self.patchToApply['0.9.2'] = [('dbusmenu-qt-0.9.2.diff', 1)]
        self.defaultTarget = 'qt5'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )

        self.subinfo.options.configure.defines = "-DBUILD_TESTS=OFF "

