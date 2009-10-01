#
# FSImportTool tests
#

import os, sys
from DateTime import DateTime

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import BaseTestCase

class TestHitCountTool(BaseTestCase.BaseTestCase):
    """Test the portal_hitcount tool"""

    def testInterface(self):
        from Products.RhaptosHitCountTool.interfaces.portal_hitcount import portal_hitcount
        self.assertEqual(portal_hitcount.isImplementedBy(self.hitcount), 1)
        
    def testReset(self):
    	"""Make sure that Reset() works.  Should clear all stored dictionaries to an empty dictionary"""
        self.hitcount._hits = {'m11015':'some random stuff'}

        beforetime = DateTime()
        self.hitcount.resetHitCounts()
        aftertime = DateTime()

        self.assertEqual(self.hitcount._hits, {})
        self.assert_(beforetime <= self.hitcount.getStartDate() <= aftertime)

    def testRegisterObject(self):
        """Test registerObject initializes the object counts to 0"""
        objectId = 'm10000'
        self.hitcount.registerObject(objectId, DateTime())
        self.assertEqual(self.hitcount.getHitCountForObject(objectId), 0)
        self.assertEqual(self.hitcount.getHitCountForObject(objectId, True), 0)


    def testListRegisteredObjectsEmpty(self):
        self.hitcount.resetHitCounts()
        self.assertEqual(self.hitcount.listRegisteredObjects(), [])

    def testListRegisteredObjects(self):
        objectId = 'm10000'
        self.hitcount.resetHitCounts()
        self.hitcount.registerObject(objectId, DateTime())
        self.assertEqual(self.hitcount.listRegisteredObjects(), [objectId])


    def testIncrementBadObject(self):
        """IncrementCounts() should raise ValueError if one of the objects was not previously registered"""
        self.assertRaises(ValueError, self.hitcount.incrementCounts, {'m0000':10})
        
        
    def testIncrementNoDates(self):
    	"""IncrementCounts() shoulds work with no dates given.  It should make the end date the equal to the current timestamp"""

        oldenddate = self.hitcount.getIncrementDateRange()[1]
        beforetime = DateTime()
        self.hitcount.incrementCounts({})
        aftertime = DateTime()

        self.assertEqual(self.hitcount.getIncrementDateRange()[0], oldenddate)
        self.assert_(beforetime <= self.hitcount.getIncrementDateRange()[1] <= aftertime)

    def testIncrementBeginDate(self):
    	"""Increment should work when a begin date is given.  The end date should be equal to the current timestamp""" 

        newbegindate = 'sampletime'
        beforetime = DateTime()
        self.hitcount.incrementCounts({}, begin_date=newbegindate)
        aftertime = DateTime()

        self.assertEqual(self.hitcount.getIncrementDateRange()[0], newbegindate)
        self.assert_(beforetime <= self.hitcount.getIncrementDateRange()[1] <= aftertime)

    def testIncrementEndDate(self):
    	"""Increment should work with an enddate given.  It should know the begin date"""

        newenddate = 'sampletime'
        oldenddate = self.hitcount.getIncrementDateRange()[1]
        self.hitcount.incrementCounts({}, end_date=newenddate)

        self.assertEqual(self.hitcount.getIncrementDateRange()[1], newenddate)
        self.assertEqual(self.hitcount.getIncrementDateRange()[0], oldenddate)

    def testIncrementBothDates(self):
    	"""Increment should work with both dates given"""

        newbegindate = 'sampletime'
        newenddate = 'samepletime2'
        self.hitcount.incrementCounts({}, begin_date=newbegindate, end_date = newenddate)

        self.assertEqual(self.hitcount.getIncrementDateRange()[0], newbegindate)
        self.assertEqual(self.hitcount.getIncrementDateRange()[1], newenddate)


    def testIncrementSetsStartDate(self):
        """Setting an increment beginning before the start date should change the start date"""

        self.hitcount.resetHitCounts()
        newbegindate = DateTime() - 7

        self.hitcount.incrementCounts({}, begin_date=newbegindate)
        self.assertEqual(self.hitcount.getStartDate(), newbegindate)

    def testIncrementDoesNotSetStartDate(self):
        """Setting an increment beginning after the start date should not change the start date"""

        self.hitcount.resetHitCounts()
        newbegindate = DateTime() + 7

        start = self.hitcount.getStartDate()
        self.hitcount.incrementCounts({}, begin_date=newbegindate)
        self.assertEqual(self.hitcount.getStartDate(), start)

    def testNoIncrementDoesNotSetStartDate(self):
        """Setting an increment with no beginning time should not change the start date"""

        self.hitcount.resetHitCounts()

        start = self.hitcount.getStartDate()
        self.hitcount.incrementCounts({})
        self.assertEqual(self.hitcount.getStartDate(), start)

    def testIncrementSingle(self):
        """IncrementCounts should work with a single object"""
        objectId = 'm10000'
        counts = 17
        self.hitcount.resetHitCounts()
        self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts({objectId:counts})

        self.assertEqual(self.hitcount.getHitCountForObject(objectId), counts)
        self.assertEqual(self.hitcount.getHitCountForObject(objectId, True), counts)


    def testIncrementMultiple(self):
        """IncrementCounts should work with multiple object"""
        obj1 = 'm10000'
        obj2 = 'm10001'
        count1 = 17
        count2 = 23
        self.hitcount.resetHitCounts()
        self.hitcount.registerObject(obj1, DateTime())
        self.hitcount.registerObject(obj2, DateTime())
        self.hitcount.incrementCounts({obj1:count1, obj2:count2})

        self.assertEqual(self.hitcount.getHitCountForObject(obj1), count1)
        self.assertEqual(self.hitcount.getHitCountForObject(obj1, True), count1)
        self.assertEqual(self.hitcount.getHitCountForObject(obj2), count2)
        self.assertEqual(self.hitcount.getHitCountForObject(obj2, True), count2)


    def testRecentIncrement(self):
        """IncrementCounts should correct return recent and total counts"""
        objectId = 'm10000'
        count1 = 17
        count2 = 48
        self.hitcount.resetHitCounts()
        self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts({objectId:count1})
        self.hitcount.incrementCounts({objectId:count2})

        self.assertEqual(self.hitcount.getHitCountForObject(objectId), count1+count2)
        self.assertEqual(self.hitcount.getHitCountForObject(objectId, True), count2)

    def testIncrementBadMapping(self):
        """Verify that incrementing fails if a dictionary is not given"""
        self.assertRaises(TypeError, self.hitcount.incrementCounts, 'This is not a Valid Mapping!')

    def testGetHitCount(self):
    	"""Verify that GetHitCounts() returns the correct values"""
        data = [('m11016',1005), ('m11015',1001), ('m11017',900), ('m11018',200)]

        self.hitcount.resetHitCounts()
        for objectId, count in data:
            self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts(dict(data))

        self.assertEqual(self.hitcount.getHitCounts(True),data)
        self.assertEqual(self.hitcount.getHitCounts(),data)

    def testGetHitCountsRecent(self):
    	"""Verify that GetHitCounts(recent=True) returns correct values"""
        data1 = [('m11016',1005), ('m11015',1001), ('m11017',900), ('m11018',200)]
        data2 = [('m11016',120), ('m11015',100), ('m11017',90), ('m11018',25)]

        self.hitcount.resetHitCounts()
        for objectId, count in data1:
            self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts(dict(data1))
        self.hitcount.incrementCounts(dict(data2))
        
        self.assertEqual(self.hitcount.getHitCounts(True), data2)
        self.assertEqual(self.hitcount.getHitCounts(), map(lambda x, y: (x[0], x[1]+y[1]), data1, data2))

    def testGetHitCountForObjectTotal(self):
    	"""Verify that GetHitCountForObject returns the correct total tuple"""
        data = [('m11016',1005), ('m11015',1001), ('m11017',900), ('m11018',200)]

        self.hitcount.resetHitCounts()
        for objectId, count in data:
            self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts(dict(data))

        self.assertEqual(self.hitcount.getHitCountForObject('m11016', True), 1005)
        self.assertEqual(self.hitcount.getHitCountForObject('m11016'), 1005)

    def testGetHitCountForObjectRecent(self):
    	"""Verify that GetHitCountForObject returns the correct recent tuple"""
        data1 = [('m11016',1005), ('m11015',1001), ('m11017',900), ('m11018',200)]
        data2 = [('m11016',120), ('m11015',100), ('m11017',90), ('m11018',25)]

        self.hitcount.resetHitCounts()
        for objectId, count in data1:
            self.hitcount.registerObject(objectId, DateTime())
        self.hitcount.incrementCounts(dict(data1))
        self.hitcount.incrementCounts(dict(data2))

        self.assertEqual(self.hitcount.getHitCountForObject('m11016', True), 120)
        self.assertEqual(self.hitcount.getHitCountForObject('m11016'), 1005+120)

    def testGetHitCountForUnregistered(self):
        """Verify that unregistered objects return 0 for hit counts"""
        self.assertEqual(0, self.hitcount.getHitCountForObject('m0000', True))
        self.assertEqual(0, self.hitcount.getHitCountForObject('m0000'))
        
    def testAverageWithZeroCounts(self):
        """getDailyAverageForObject() should return an average of 0 if there 0 counts"""
        published = DateTime('2005/01/01')
        inc_start = published + 7
        inc_end = inc_start + 7

        objId = 'm0000'
        self.hitcount.registerObject(objId, published)
        self.hitcount.incrementCounts({}, inc_start, inc_end)

        self.assertEqual(self.hitcount.getDailyAverageForObject(objId), 0)
        
    def testAverageWithZeroIncrement(self):
        """getDailyAverageForObject() should return the number of counts if there is no range"""
        published = DateTime('2005/01/01')
        inc_start = published + 7
        inc_end = inc_start

        objId = 'm0000'
        count = 157
        
        self.hitcount.registerObject(objId, published)
        self.hitcount.incrementCounts({objId:count}, inc_start, inc_end)

        self.assertEqual(self.hitcount.getDailyAverageForObject(objId), count)

    def testAvgPublishedBeforeStart(self):
        """Verify that getDailyAverageForObject() returns correct values for objects published before hit count start date"""
        published = DateTime('2005/01/01')
        start = published + 7
        inc_start = start + 7
        inc_end = inc_start + 7

        objId = 'm0000'
        count = 100
        self.hitcount.resetHitCounts()
        self.hitcount.setStartDate(start)
        self.hitcount.registerObject(objId, published)
        self.hitcount.incrementCounts({objId:count}, inc_start, inc_end)

        self.assertEqual(self.hitcount.getDailyAverageForObject(objId), count/(inc_end-start))
        self.assertEqual(self.hitcount.getDailyAverageForObject(objId, True), count/(inc_end-inc_start))

    def testAvgPublishedBeforeIncrement(self):
        """Verify that getDailyAverageForObject() returns correct values for objects published before recent increment"""
        start = DateTime('2005/01/01')
        published = start + 7
        inc_start = published + 7
        inc_end = inc_start + 7

        objId = 'm0000'
        count = 100
        self.hitcount.resetHitCounts()
        self.hitcount.setStartDate(start)
        self.hitcount.registerObject(objId, published)
        self.hitcount.incrementCounts({objId:count}, inc_start, inc_end)

        self.assertEqual(self.hitcount.getDailyAverageForObject(objId), count/(inc_end-published))
        self.assertEqual(self.hitcount.getDailyAverageForObject(objId, True), count/(inc_end-inc_start))

    def testAvgPublishedBeforeIncrement(self):
        """Verify that getDailyAverageForObject() returns correct values for objects published during recent increment"""
        start = DateTime('2005/01/01')
        inc_start = start + 7
        published = inc_start + 7
        inc_end = published + 7

        objId = 'm0000'
        count = 100
        self.hitcount.resetHitCounts()
        self.hitcount.setStartDate(start)
        self.hitcount.registerObject(objId, published)
        self.hitcount.incrementCounts({objId:count}, inc_start, inc_end)

        self.assertEqual(self.hitcount.getDailyAverageForObject(objId), count/(inc_end-published))
        self.assertEqual(self.hitcount.getDailyAverageForObject(objId, True), count/(inc_end-published))

    def testSetStartDate(self):
    	"""Verify that setting the startdate works correctly"""
        teststartdate = DateTime()
        self.hitcount.setStartDate(teststartdate)
        self.assertEqual(teststartdate, self.hitcount.getStartDate())
        
    def testGetStartDate(self):
    	"""Verify that the startdate is returned correctly"""
        teststartdate = DateTime()
        self.hitcount._startdate = teststartdate
        self.assertEqual(self.hitcount.getStartDate(), teststartdate)

    def testGetIncrementRange(self):
    	"""Verify that the range of the increment is return correctly"""
        
        teststartdate = DateTime()
        testenddate = teststartdate + 7
        
        self.hitcount._inc_begin = teststartdate
        self.hitcount._inc_end = testenddate
       
        self.assertEqual(self.hitcount.getIncrementDateRange(), (teststartdate,testenddate))     
        
	
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestHitCountTool))
        return suite
