from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def moveHitCountComputations(self):
    """Move all the hit count computations to the incrementHitCounts
    method instead of computing the numbers on the fly every time that
    one is asked for.  This will make the increment take much much longer,
    but should make page loads much faster."""

    hc_tool = getToolByName(self, 'portal_hitcount')
        
    dateRange = hc_tool.getIncrementDateRange()
    end = dateRange[1]
    inc_start = dateRange[0]
    tool_start = hc_tool.getStartDate()
        
    for objectId, hits in hc_tool._hits.items():
                
        count = hits.recent
        if not hasattr(hits,'_daily_average'):
            hits._daily_average = (0,0)
            
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

    rec_items = [(id, hits.recent) for (id, hits) in hc_tool._hits.items()]
    rec_items.sort(lambda a,b: cmp(b[1],a[1]))
    hc_tool._recent_hit_counts = rec_items
        
    items = [(id, hits.total) for (id, hits) in hc_tool._hits.items()]
    items.sort(lambda a,b: cmp(b[1],a[1]))
    hc_tool._hit_counts = items
        
    rec_items = [(id, hits.avgPerDay(True)) for (id, hits) in hc_tool._hits.items()]
    rec_items.sort(lambda a,b: cmp(b[1],a[1]))
    hc_tool._recent_daily_averages = rec_items
        
    items = [(id, hits.avgPerDay(False)) for (id, hits) in hc_tool._hits.items()]
    items.sort(lambda a,b: cmp(b[1],a[1]))
    hc_tool._daily_averages = items

    total_objects = len(hc_tool.listRegisteredObjects())
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

    for o_id,o_hits in hc_tool._hits.items():
        if not hasattr(o_hits,'_percentile'):
            o_hits._percentile = (0,0)
            
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
        
    hc_tool._p_changed=1
