"""UDB Compare.

Usage:
  udbcmp       --before=<inputUDB> --after=<inputUDB> \r\n \
                [--metrics=inlineCSVofNames]
                [--dllDir=<dllDir>]\r\n \
                [--verbose]

Options:
  --before=<inputUDB>                           File path to a UDB with the "before" state of your sources
  --after=<inputUDB>                            File path to a UDB with the "after" state of your sources
  --metrics=inlineCSVofNames                    Inline string which is a CSV of names of metrics to compare, from a total listed at https://scitools.com/support/metrics_list/ [default: AvgCyclomaticModified,AvgLineCode]
  --dllDir=<dllDir>                             Path to the dir with the DLL to the Understand Python SDK.[default: C:/Program Files/SciTools/bin/pc-win32/python]
  --verbose                                     If you want lots of messages printed. [default: false]

Errors:
  DBAlreadyOpen        - only one database may be open at once
  DBCorrupt            - bad database file
  DBOldVersion         - database needs to be rebuilt
  DBUnknownVersion     - database needs to be rebuilt
  DBUnableOpen         - database is unreadable or does not exist
  NoApiLicense         - Understand license required

Author:
  Marcio Marchini (marcio@BetterDeveloper.net)

"""

import sys
import re
import datetime
import json

from docopt import docopt

def open_udb (udb_path):
    try:
        db = understand.open(udb_path)
    except understand.UnderstandError as exc:
        print ("Error '%s' opening input file '%s'" % (exc, udb_path))
        sys.exit(-2)
    return db

def compare_udbs (udb_before, udb_after, metric_names):
    result = {}
    populate_file_metrics(udb_before, "before", metric_names, result)
    populate_file_metrics(udb_after, "after", metric_names, result)
    return result


def populate_file_metrics(udb, tag, metric_names, result):
    # result: dict {key: <file-path>, value: dict {key: tag, value : dict (key: metric-name, value: metric-value} } }
    file_entities = udb.ents("file ~Unresolved ~Unknown ~Unparsed")
    for file_entity in file_entities:
        library_name = file_entity.library()
        if file_entity.library() is not "": # skip files that belong to external libraries
            continue
        file_path = file_entity.relname()
        file_attribs = {}
        if file_path not in result:
           result[file_path] = file_attribs
        else:
            file_attribs = result[file_path]
        file_metrics_by_tag = {}
        if tag not in file_attribs:
           file_attribs[tag] = file_metrics_by_tag
        else:
            file_metrics_by_tag = file_attribs[tag]
        for metric_name in metric_names:
            metric_dict = file_entity.metric((metric_name,))
            metric_value = metric_dict.get(metric_name, 0)  # the call returns a dict
            if metric_value is None:
                metric_value = 0
            file_metrics_by_tag[metric_name]=metric_value

if __name__ == '__main__':
    arguments = docopt(__doc__, version='UDB Compare')
    verbose = arguments["--verbose"]
    sys.path.append(arguments["--dllDir"]) # add the dir with the DLL to interop with understand
    if verbose:
        print ("\r\n====== udbcmp by Marcio Marchini: marcio@BetterDeveloper.net ==========")
        print(arguments)
    try:
        import understand
    except:
        print ("Can' find the Understand DLL. Use --dllDir=...")
        print ("Please set PYTHONPATH to point to Understand's C:/Program Files/SciTools/bin/pc-win64/python or equivalent")
        sys.exit(-1)
    if verbose:
        print ("\r\n...opening input udb %s" % arguments["--before"])
    udb_before = open_udb(arguments["--before"])
    if verbose:
        print ("\r\n...opening output udb %s" % arguments["--before"])
    udb_after = open_udb(arguments["--after"])
    metric_names = arguments["--metrics"].split(",")
    comparison = compare_udbs (udb_before, udb_after, metric_names)
    print (json.dumps(comparison))


