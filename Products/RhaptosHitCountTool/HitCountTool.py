"""
Rhaptos HitCount Product

Author: Brent Hendricks and Kyle Clarkson
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import zLOG
import AccessControl
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import View, ManagePortal
from interfaces.portal_hitcount import portal_hitcount as IHitCountTool
import DateTime, operator
from types import DictType
import pickle, StringIO


class HitCountTool(UniqueObject, SimpleItem):

    __implements__ = (IHitCountTool)

    id = 'portal_hitcount'
    meta_type = 'HitCount Tool'
    security = AccessControl.ClassSecurityInfo()

    manage_options=(( {'label':'Overview', 'action':'manage_overview'},
                      )
                    + SimpleItem.manage_options
                    )

    def __init__(self):
        self._hits={}
        self._recent_hit_counts = []
        self._hit_counts = []
        self._recent_daily_averages = []
        self._daily_averages = []
        self._startdate = self._inc_begin = self._inc_end = DateTime.DateTime()

    ##   ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/explainHitCountTool', globals() )

    # IHitCountTool Interface fulfillment 
        
    def resetHitCounts(self):
        """
        Reset all hit counts to 0 and set the start date to the current date and time
        """
        if hasattr(self,'_hits'):
            self._hits.clear()
        else:
            self._hits={}
        self._recent_hit_counts = []
        self._hit_counts = []
        self._recent_daily_averages = []
        self._daily_averages = []
        self._startdate = self._inc_begin = self._inc_end = DateTime.DateTime()
        try:
            objs = self.content.objectValues(['Version Folder','Module Version Folder'])
            for ob in objs:
                self.registerObject(ob.id,ob.created())
        except AttributeError:
            pass

    def registerObject(self, objectId, published_date):
        """Register an object with the HitCountTool"""

        self._hits[objectId] = Hits(published_date, self)
        self._recent_hit_counts.append((objectId,0))
        self._hit_counts.append((objectId,0))
        self._recent_daily_averages.append((objectId,0))
        self._daily_averages.append((objectId,0))
        self._p_changed = 1
        
    def listRegisteredObjects(self):
        """Return a list of identifiers for registered objects"""
        return self._hits.keys()

    def incrementCounts(self, mapping, begin_date=None, end_date=None):
        """
        Increment the hit counter for content objects.  mapping must
        be a mapping from objectID to an integer number of hit counts.
        begin_date and end_date specify the range of time covered by
        this increment.  If end_date is None, the current timestamp
        will be used.
        """
        if not type(mapping) is DictType:
            raise TypeError

        self.recentHits = mapping
        self._inc_begin = begin_date or self._inc_end
        self._inc_end = end_date or DateTime.DateTime()

        #If the increment begin date is earlier than the start date, update it
        if begin_date and (begin_date < self._startdate):
            self._startdate = begin_date

        dateRange = self.getIncrementDateRange()
        end = dateRange[1]
        inc_start = dateRange[0]
        tool_start = self.getStartDate()
        
        for objectId, count in mapping.items():
            try:
                hits = self._hits[objectId]
            except KeyError:
                raise ValueError, "Object %s not registered" % objectId
                
            hits.recent = count
            hits.total += count
            
            recent_age = end - (hits.published > inc_start and hits.published or inc_start)
            # If there is no age, just use the count as the average
            if recent_age:
                recent_avg = count*1.0/recent_age
            else:
                recent_avg = count
                
            full_age = end - (hits.published > tool_start and hits.published or tool_start)
            # If there is no age, just use the count as the average
            if full_age:
                avg = hits.total*1.0/full_age
            else:
                avg = hits.total
            
            hits._daily_average = (avg, recent_avg)

        rec_items = [(id, hits.recent) for (id, hits) in self._hits.items()]
        rec_items.sort(lambda a,b: cmp(b[1],a[1]))
        self._recent_hit_counts = rec_items
        
        items = [(id, hits.total) for (id, hits) in self._hits.items()]
        items.sort(lambda a,b: cmp(b[1],a[1]))
        self._hit_counts = items
        
        rec_items = [(id, hits.avgPerDay(True)) for (id, hits) in self._hits.items()]
        rec_items.sort(lambda a,b: cmp(b[1],a[1]))
        self._recent_daily_averages = rec_items
        
        items = [(id, hits.avgPerDay(False)) for (id, hits) in self._hits.items()]
        items.sort(lambda a,b: cmp(b[1],a[1]))
        self._daily_averages = items

        total_objects = len(self.listRegisteredObjects())
        if total_objects:
            object_ranks, counts = zip(*items)
            object_ranks = list(object_ranks)
            recent_object_ranks, recent_counts = zip(*rec_items)
            recent_object_ranks = list(recent_object_ranks)
        else:
            object_ranks = []
            counts = []
            recent_object_ranks = []
            recent_counts = []

        for o_id,o_hits in self._hits.items():
            try:
                index = object_ranks.index(o_id) + 1
            except ValueError:
                # Object not ranked, place after ranked objects
                index = total_objects
            try:
                recent_index = recent_object_ranks.index(o_id) + 1
            except ValueError:
                # Object not ranked, place after ranked objects
                recent_index = total_objects
            o_hits._percentile = ((total_objects - index)*100.0/total_objects,(total_objects - recent_index)*100.0/total_objects)

        self._p_changed=1
        

    def getHitCounts(self, recent=False):
        """
        Return hit counts for all content objects.  If recent is True,
        return the count for the previous increment, otherwise returns
        counts for all time

        The return value will be a list of (objectId, count) tuples in
        descending hit count order.
        """
        
        if recent:
            return self._recent_hit_counts
        else:
            return self._hit_counts

    def getHitCountForObject(self, objectId, recent=False):
        """
        Return the hit counts for the specified object ID.  If recent
        is True, return the count for the previous increment,
        otherwise returns counts for all time
        """
        try:
            hits = self._hits[objectId]
        except KeyError:
            return 0

        if recent:
            return hits.recent
        else:
            return hits.total

    def getDailyAverages(self, recent=False):
        """
        Return the average daily hit count for all registered objects.
        If recent=True, return the average for the previous increment,
        otherwise returns averages for all time.
        """

        if recent:
            return self._recent_daily_averages
        else:
            return self._daily_averages

    def getDailyAverageForObject(self, objectId, recent=False):
        """
        Return the average daily hit count for the specified object
        from its date of publication to the present (for the date
        range statistics are available).  If recent=True, return the
        average for the previous increment, otherwise returns averge
        for all time.
        """
        try:
            return self._hits[objectId].avgPerDay(recent)
        except KeyError:
            return 0

    def getPercentileForObject(self, objectId, recent=False):
        """
        Return the average daily hit count for the specified object
        from its date of publication to the present (for the date
        range statistics are available).  If recent=True, return the
        average for the previous increment, otherwise returns averge
        for all time.
        """
        try:
            return self._hits[objectId].getPercentile(recent)
        except KeyError:
            return 0

    
    def setStartDate(self, date):
        """
        Set the initial date from which hits are counted
        """
        self._startdate = date

    def getStartDate(self):
        """
        Get the initial date from which hits are counted
        """
        return self._startdate

    def getIncrementDateRange(self):
        """
        Return the date range covered by the most recent increment as
        a tuple (begin_date, end_date)
        """
        return (self._inc_begin, self._inc_end)

    def dumpHitCounts(self):
        """Returns a transferable string object of all the hit count data. 
        For use with restoreHitCounts"""
        pstr = StringIO.StringIO()
        kosher = pickle.Pickler(pstr)
        for attr in (self._hits, self._recent_hit_counts, self._hit_counts,
                self._recent_daily_averages, self._daily_averages,
                self._startdate, self._inc_begin, self._inc_end ):
            kosher.dump(attr)
        pdata=pstr.getvalue()
        pstr.close()
        return pdata

    def restoreHitCounts(self,dumpstr):
        """Destructively overrides the hit count data with that provided 
        in the dump string, which was previously generated by dumpHitCounts"""
        pstr = StringIO.StringIO(dumpstr)
        dill = pickle.Unpickler(pstr)
        self.resetHitCounts()
        self._hits.update(dill.load())
        self._recent_hit_counts.extend(dill.load())
        self._hit_counts.extend(dill.load())
        self._recent_daily_averages.extend(dill.load())
        self._daily_averages.extend(dill.load())
        self._startdate= dill.load()
        self._inc_begin= dill.load()
        self._inc_end= dill.load()


class Hits:

    meta_type = 'Hit Count'
    
    def __init__(self, published, tool, recent=0, total=0):
        self.published = published
        self.recent = recent
        self.total = total
        self._tool = tool
        self._daily_average = (0,0)
        self._percentile = (0,0)

    def avgPerDay(self, recent=False):

        if recent:
            return self._daily_average[1]
        else:
            return self._daily_average[0]

    def getPercentile(self, recent=False):

        if recent:
            return self._percentile[1]
        else:
            return self._percentile[0]

InitializeClass(HitCountTool)


# Convenience functions

   
