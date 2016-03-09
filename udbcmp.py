"""UDB Compare.

Usage:
  srccheck       --before=<inputUDB> --after=<inputUDB> --files=<fileWithListOfFiles> --metrics=inlineCSVofNames \r\n \
                [--dllDir=<dllDir>]\r\n \
                [--outputCSV=<outputCSV>] \r\n \
                [--verbose]

Options:
  --before=<inputUDB>                           File path to a UDB with the "before" state of your sources
  --after=<inputUDB>                            File path to a UDB with the "after" state of your sources
  --files=<fileWithListOfFiles>                 File path to a text file with a list of files to compare for metrics changes in the before/after
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

def compare_udbs (udb_before, udb_after, file_paths, metric_names):
    result = {}
    for file_path in file_paths:
        attributes = {}
        result [file_path] = attributes
        searchstr = re.compile(file_path,re.I)
        before_metrics = get_file_metrics(metric_names, searchstr, udb_before)
        after_metrics = get_file_metrics(metric_names, searchstr, udb_after)
        attributes ["before"] = before_metrics
        attributes ["after"] = after_metrics
    return result


def get_file_metrics(metric_names, searchstr, udb):
    result = {}
    file_entities = udb.lookup(searchstr, "File")
    if len(file_entities) != 1:
        print ("More than one file found with the same path %s. Contact support." % searchstr)
        sys.exit(-4)
    for file_entity in file_entities:
        for metric_name in metric_names:
            metric_dict = file_entity.metric((metric_name,))
            metric_value = metric_dict.get(metric_name, 0)  # the call returns a dict
            if metric_value is None:
                metric_value = 0
            result[metric_name]=metric_value
    return result

if __name__ == '__main__':
    start_time = datetime.datetime.now()
    arguments = docopt(__doc__, version='UDB Compare')
    verbose = arguments["--verbose"]
    sys.path.append(arguments["--dllDir"]) # add the dir with the DLL to interop with understand
    if verbose:
        print ("\r\n====== udbcmp by Marcio Marchini: marcio@BetterDeveloper.net ==========") if verbose
        print(arguments)
    try:
        import understand
    except:
        print ("Can' find the Understand DLL. Use --dllDir=...")
        print ("Please set PYTHONPATH to point an Understand's C:/Program Files/SciTools/bin/pc-win32/python or equivalent")
        sys.exit(-1)

    if verbose:
        print ("\r\n...opening input udb %s" % arguments["--before"])
    db_before = arguments["--before"]
    if verbose:
        print ("\r\n...opening input udb %s" % arguments["--before"])
    db_after = arguments["--after"]
    try:
        with open(arguments["--files"]) as f:
            file_paths = f.readlines()
    except:
        print ("Can' read the text file '%s' with a list a files" % arguments["--files"])
        sys.exit(-3)
    metric_names = arguments["--metrics"].split(",")
    comparison = compare_udbs (db_before, db_after, file_paths, metric_names)
    print (json.dumps(comparison))


