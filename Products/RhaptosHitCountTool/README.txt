RhaptosHitCountTool

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  RhaptosHitCountTool provides a CMF tool that stores and provides
  access to browser hit counts and statistics for content objects.

  NOTE: RhaptosHitCountTool does *not* detect browser hits.  It relies on
  external scripts to parse server logs and input data. Example scripts 
  specific to Zope Z2.log or  cnx.org and custom Squid logs are present
  in the Extensions folder. 

  Run as: <path_to_zopectl> run <path_to_Z2.log>

Future plans

  - BTreeFolder2 storage?

  - An SQL backend?

  - Store percentile information so it does not have to be
    recalculated [DONE]

  - Provide a graph of hits over time
