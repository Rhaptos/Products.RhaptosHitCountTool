#!/usr/bin/env python
import gzip
import re
import time
from DateTime import DateTime

# FIXME: don't hardcode this
MODULE_PATTERN = re.compile('^/content/(m|col)([0-9]+)/([0-9.]+|latest/)$')

def parseZ2Log(name):
    f = gzip.open(name)
    try:
        f.readline()
        f.seek(0)
    except IOError: # Handle 'Not a gzipped file' case
        f.close()
        f=open(name)
    counts = {}
    start_time = None
    for line in f:
        data = line.split()
        if not start_time:
            start_time = DateTime(' '.join(data[3:5])[1:-1])
        if len(data) > 6:
            match = MODULE_PATTERN.match(data[6])
            if match:
                objectId = ''.join(match.groups()[0:2])
                if objectId:
                    counts[objectId] = counts.get(objectId, 0) + 1
    else:
        end_time = DateTime(' '.join(data[3:5])[1:-1])

    f.close()
    return counts, start_time, end_time

if __name__ == '__main__':
    import sys
    import transaction
    portal = app.objectValues('Plone Site')[0]

    for fname in sys.argv[1:]:

        increment, s_time, e_time = parseZ2Log(fname)

        # Filter out hits for objects that don't actually exist
        for objectId in increment.keys():
            if not portal.content.hasRhaptosObject(objectId):
                del increment[objectId]
        objids=portal.content.objectIds(['Version Folder','Module Version Folder'])
        for objid in objids:
            if not increment.has_key(objid):
                increment[objid]=0
                
        portal.portal_hitcount.incrementCounts(increment, DateTime(s_time), DateTime(e_time))
        transaction.commit()
        print "Updated logs for %s - %s" % (s_time, e_time)
