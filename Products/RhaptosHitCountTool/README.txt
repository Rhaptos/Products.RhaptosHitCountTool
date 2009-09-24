RhaptosHitCountTool

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  RhaptosHitCountTool provides a CMF tool that stores and provides
  access to browser hit counts and statistics for content objects.

  NOTE: RhaptosHitCountTool does *not* detect browser hits.  It relies on
  external scripts to parse server logs and input data.

Future plans

  - BTreeFolder2 storage?

  - An SQL backend?

  - Store percentile information so it does not have to be
    recalculated

  - Provide a graph of hits over time