## Script (Python) "getHitCountRanking"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objectId, recent=False
##title= Given an objectId, return its rank in terms of hit-count popularity
##

daily_avg_hits = context.portal_hitcount.getDailyAverages(recent)
objects, counts = zip(*daily_avg_hits)
objects = list(objects)
try:
    return objects.index(objectId) + 1
except ValueError:
    # ID not in list, return rank after all counted objects
    return len(objects) + 1
