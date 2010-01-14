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
        self.loginAsPortalOwner()
        self.hit_count_tool = getToolByName(self.portal, 'portal_hitcount')

        # PloneTestCase already gives us a folder, so within that folder,
        # create a document and a collection to version.
        self.folder.invokeFactory('Document', 'doc')
        self.doc = self.folder.doc

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

    def test_hit_count_tool_register_and_list_objects(self):
        # Register an object.
        self.hit_count_tool.registerObject(self.folder.getId(), DateTime.DateTime())
        self.assertEqual(len(self.hit_count_tool.listRegisteredObjects()), 1)
        registered_object = self.hit_count_tool.listRegisteredObjects()[0]
        self.assertEqual(registered_object, self.folder.getId())

        # Register another object.
        self.hit_count_tool.registerObject(self.doc.getId(), DateTime.DateTime())
        self.assertEqual(len(self.hit_count_tool.listRegisteredObjects()), 2)
        registered_object = self.hit_count_tool.listRegisteredObjects()[0]
        self.assertEqual(registered_object, self.doc.getId())

        # Re-register the first object.
        self.hit_count_tool.registerObject(self.folder.getId(), DateTime.DateTime())
        self.assertEqual(len(self.hit_count_tool.listRegisteredObjects()), 2)
        registered_object = self.hit_count_tool.listRegisteredObjects()[1]
        self.assertEqual(registered_object, self.folder.getId())

    def test_hit_count_tool_start_date(self):
        # Make sure that we can get and set the start date from which to gather
        # analytics data.
        now = DateTime.DateTime()
        self.assertNotEqual(self.hit_count_tool.getStartDate(), now)
        self.hit_count_tool.setStartDate(now)
        self.assertEqual(self.hit_count_tool.getStartDate(), now)

    def test_hit_count_tool_increment_and_get_counts(self):
        # Make sure that there are no registered objects.
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 0)

        # Register an object.
        self.hit_count_tool.registerObject(self.folder.getId(), DateTime.DateTime())

        # Make sure that incrementCounts raises a TypeError when supplied with
        # a mapping that isn't a dict.
        mapping = None
        self.assertRaises(TypeError, self.hit_count_tool.incrementCounts, mapping)

        # Make sure that incrementCounts succeeds when supplied with an empty
        # mapping.
        mapping = {}
        self.hit_count_tool.incrementCounts(mapping)

        # Make sure that the newly registered object has a hit count of 0.
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 1)
        self.assertEqual(hit_counts[0], (self.folder.getId(), 0))

        # Increment the hit count for the registered object, and make sure that
        # it gets updated.
        mapping = {self.folder.getId(): 1}
        self.hit_count_tool.incrementCounts(mapping)
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 1)
        self.assertEqual(hit_counts[0], (self.folder.getId(), 1))

        # Register another object.
        self.hit_count_tool.registerObject(self.doc.getId(), DateTime.DateTime())
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 2)

        # Increment the hit count for the first registered object.
        mapping = {self.folder.getId(): 1}
        self.hit_count_tool.incrementCounts(mapping)
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(hit_counts[0], (self.folder.getId(), 2))

        # Make sure that the second registered object still has a hit count of 0.
        self.assertEqual(hit_counts[1], (self.doc.getId(), 0))

        # Make sure that we can get hit counts by object ID:
        self.assertEqual(self.hit_count_tool.getHitCountForObject(self.folder.getId()), 2)
        self.assertEqual(self.hit_count_tool.getHitCountForObject(self.doc.getId()), 0)

    def test_hit_count_tool_averages_and_percentiles(self):
        # Make sure that there are no registered objects.
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 0)

        # Register an object.
        self.hit_count_tool.registerObject(self.folder.getId(), DateTime.DateTime())
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 1)

        # Register another object.
        self.hit_count_tool.registerObject(self.doc.getId(), DateTime.DateTime())
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 2)

        # Increment the hit count for the first registered object.
        mapping = {self.folder.getId(): 2}
        self.hit_count_tool.incrementCounts(mapping)
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(hit_counts[0], (self.folder.getId(), 2))

        # Test the daily average hit counts.
        daily_averages = self.hit_count_tool.getDailyAverages()
# FIXME : there is something fishy about this test
# http://buildbot.rhaptos.org/builders/rhaptos-dist-debian/builds/377/steps/test_17/logs/stdio
##        self.assertEqual(daily_averages[0], (self.folder.getId(), 2))
        self.assertEqual(daily_averages[1], (self.doc.getId(), 0))
        self.assertEqual(self.hit_count_tool.getDailyAverageForObject(self.folder.getId()), 2)
        self.assertEqual(self.hit_count_tool.getDailyAverageForObject(self.doc.getId()), 0)

        # Test the percentiles.
        self.assertEqual(self.hit_count_tool.getPercentileForObject(self.folder.getId()), 50.0)
        self.assertEqual(self.hit_count_tool.getPercentileForObject(self.doc.getId()), 0.0)

    def test_hit_count_tool_reset_counts(self):
        # Make sure that there are no registered objects.
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 0)

        # Register an object.
        self.hit_count_tool.registerObject(self.folder.getId(), DateTime.DateTime())
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 1)

        # Reset the hit counts.
        self.hit_count_tool.resetHitCounts()
        hit_counts = self.hit_count_tool.getHitCounts()
        self.assertEqual(len(hit_counts), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRhaptosHitCountTool))
    return suite
