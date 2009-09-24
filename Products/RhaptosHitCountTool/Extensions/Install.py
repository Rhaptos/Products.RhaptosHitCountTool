from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.RhaptosHitCountTool import product_globals as GLOBALS
from StringIO import StringIO
import string

def install(self):
    """Add the tool"""
    out = StringIO()

    # Add the tool
    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject();
    try:
        portal.manage_delObjects('portal_hitcount')
        out.write("Removed old portal_hitcount tool\n")
    except:
        pass  # we don't care if it fails
    portal.manage_addProduct['RhaptosHitCountTool'].manage_addTool('HitCount Tool', None)

    # Register skins
    install_subskin(self, out, GLOBALS)
    
    out.write("Adding HitCount Tool\n")

    return out.getvalue()
