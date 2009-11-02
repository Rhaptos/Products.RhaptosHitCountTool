#------------------------------------------------------------------------------#
#   test_rhaptos_hit_count_tool.py                                             #
#                                                                              #
#       Authors:                                                               #
#       Rajiv Bakulesh Shah <raj@enfoldsystems.com>                            #
#                                                                              #
#           Copyright (c) 2009, Enfold Systems, Inc.                           #
#           All rights reserved.                                               #
#                                                                              #
#               This software is licensed under the Terms and Conditions       #
#               contained within the "LICENSE.txt" file that accompanied       #
#               this software.  Any inquiries concerning the scope or          #
#               enforceability of the license should be addressed to:          #
#                                                                              #
#                   Enfold Systems, Inc.                                       #
#                   4617 Montrose Blvd., Suite C215                            #
#                   Houston, Texas 77006 USA                                   #
#                   p. +1 713.942.2377 | f. +1 832.201.8856                    #
#                   www.enfoldsystems.com                                      #
#                   info@enfoldsystems.com                                     #
#------------------------------------------------------------------------------#
"""Unit tests.
$Id: $
"""


from Products.RhaptosTest import config
import Products.RhaptosHitCountTool
config.products_to_load_zcml = [('configure.zcml', Products.RhaptosHitCountTool),]
config.products_to_install = ['RhaptosHitCountTool']
config.extension_profiles = ['Products.RhaptosHitCountTool:default']

import DateTime

from Products.CMFCore.utils import getToolByName
from Products.RhaptosHitCountTool.interfaces.portal_hitcount import portal_hitcount as IHitCountTool
from Products.RhaptosTest import base


class TestRhaptosHitCountTool(base.RhaptosTestCase):

    def afterSetUp(self):
        self.hit_count_tool = getToolByName(self.portal, 'portal_hitcount')

    def beforeTearDown(self):
        pass

    def test_hit_count_tool_interface(self):
        # Make sure that the hit count tool implements the expected interface.
        self.failUnless(IHitCountTool.isImplementedBy(self.hit_count_tool))

    def test_hit_count_tool_init_values(self):
        # Make sure that the initial values are sane.
        self.assertEqual(self.hit_count_tool._hits, {})
        self.assertEqual(self.hit_count_tool._recent_hit_counts, [])
        self.assertEqual(self.hit_count_tool._hit_counts, [])
        self.assertEqual(self.hit_count_tool._recent_daily_averages, [])
        self.assertEqual(self.hit_count_tool._daily_averages, [])
        self.assertEqual(self.hit_count_tool._inc_begin, self.hit_count_tool._startdate)
        self.assertEqual(self.hit_count_tool._inc_end, self.hit_count_tool._startdate)
        self.assertEqual(len(self.hit_count_tool.listRegisteredObjects()), 0)

    def test_hit_count_tool_register_object(self):
        # Register an object.
        self.hit_count_tool.registerObject(self.folder, DateTime.DateTime())
        self.assertEqual(len(self.hit_count_tool.listRegisteredObjects()), 1)
        registered_object = self.hit_count_tool.listRegisteredObjects()[0]
        self.assertEqual(registered_object.getId(), self.folder.getId())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosHitCountTool))
    return suite
