"""
Initialize RhaptosHitCount Product

Author: Brent Hendricks and Kyle Clarkson
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import sys
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import HitCountTool

this_module = sys.modules[ __name__ ]
product_globals = globals()
tools = ( HitCountTool.HitCountTool,)

# Make the skins available as DirectoryViews
registerDirectory('skins', globals())

def initialize(context):
    utils.ToolInit('HitCount Tool',
                    tools = tools,
                    icon='tool.gif' 
                    ).initialize( context )
