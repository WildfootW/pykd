""" breakpoints """

import unittest
import pykd
import target
import testutils

class callCounter(object):
    def __init__(self,func):
        self.count = 0
        self.func = func
    def __call__(self,val):
        self.count = self.count+1
        return self.func(val)


class breakpoint(object):
    def __init__(self, offset, callback):
        self.id = pykd.setBp(offset,callback)
    def __del__(self):
        pykd.removeBp(self.id)


def stopOnBreak(id):
    return pykd.eventResult.Break

def continueOnBreak(id):
    return pykd.eventResult.Proceed


class BreakpointTest( unittest.TestCase ):

    def testNoBreakpoint(self):
        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :
            pykd.go()
            self.assertEqual( pykd.NoDebuggee, pykd.go() )

    def testSetBp(self):
        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        targetModule = pykd.module( target.moduleName )
        targetModule.reload()
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :
            pykd.go()
            pykd.setBp( targetModule.CdeclFunc )
            self.assertEqual( pykd.Break, pykd.go() )


    def testRemoveBp(self):
        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        targetModule = pykd.module( target.moduleName )
        targetModule.reload()
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :
            pykd.go()
            bpid = pykd.setBp(  targetModule.CdeclFunc )
            pykd.removeBp( bpid )
            self.assertEqual( pykd.NoDebuggee, pykd.go() )

    def testBreakCallback(self):
        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        targetModule = pykd.module( target.moduleName )
        targetModule.reload()
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :
            pykd.go()

            breakCount = callCounter(stopOnBreak)

            bp = breakpoint( targetModule.CdeclFunc, breakCount )

            self.assertEqual( pykd.Break, pykd.go() )

            self.assertEqual( 1, breakCount.count )

    def testNoBreakCallback(self):
        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        targetModule = pykd.module( target.moduleName )
        targetModule.reload()
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :
            pykd.go()

            breakCount = callCounter(continueOnBreak)

            bp = breakpoint( targetModule.CdeclFunc, breakCount )

            self.assertEqual( pykd.NoDebuggee, pykd.go() )

            self.assertEqual( 1, breakCount.count )

    def testBreakpointHandler(self):

        class BreakpointHandler( pykd.eventHandler ):

            def __init__(self):
                super(BreakpointHandler, self).__init__()
                self.count = 0

            def onBreakpoint( self, bpid_):
                self.count = self.count + 1

        processId = pykd.startProcess( target.appPath + " breakhandlertest" )
        targetModule = pykd.module( target.moduleName )
        targetModule.reload()
        with testutils.ContextCallIt( testutils.KillProcess(processId) ) as killStartedProcess :

            pykd.go()

            handler = BreakpointHandler()

            pykd.setBp( targetModule.CdeclFunc )

            self.assertEqual( pykd.Break, pykd.go() )

            self.assertEqual( 1, handler.count )
        



 


