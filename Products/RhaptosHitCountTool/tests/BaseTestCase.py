# BaseTestCase
from Testing import ZopeTestCase

#ZopeTestCase.installProduct('PageTemplates', quiet=1)
#ZopeTestCase.installProduct('PythonScripts', quiet=1)
#ZopeTestCase.installProduct('ExternalMethod', quiet=1)

import transaction
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from Acquisition import aq_base
import time

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('RhaptosHitCountTool')
ZopeTestCase.installProduct('MailHost')

portal_name  = 'portal'
portal_owner = 'portal_owner'
#default_user = ZopeTestCase._user_name


class BaseTestCase(ZopeTestCase.PortalTestCase):

    def afterSetUp(self):
        self.portal.manage_addProduct['RhaptosHitCountTool'].manage_addTool('HitCount Tool')
        self.hitcount = self.portal.portal_hitcount

def setupCMFSite(app=None, id=portal_name, quiet=0):
    '''Creates a CMF site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding CMF Site ... ')
        # Add user and log in
        app.acl_users._doAddUser(portal_owner, '', ['Manager'], [])
        user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
        newSecurityManager(None, user)
        # Add CMF Site
        factory = app.manage_addProduct['CMFDefault']
        factory.manage_addCMFSite(id, '', create_userfolder=1)
        # Log out
        noSecurityManager()
        transaction.commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

# Create a CMF site in the test (demo-) storage
app = ZopeTestCase.app()
setupCMFSite(app)
ZopeTestCase.close(app)
