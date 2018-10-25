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
import os

from docopt import docopt

def open_udb (udb_path):
    try:
        db = understand.open(udb_path)
    except understand.UnderstandError as exc:
        print ("Error '%s' opening input file '%s'" % (exc, udb_path))
        sys.exit(-2)
    return db

def compare_udbs (udb_before, udb_after, metric_names):
    before_after_by_file = {}
    populate_file_metrics(udb_before, "before", metric_names, before_after_by_file)
    populate_file_metrics(udb_after, "after", metric_names, before_after_by_file)
    populate_diffs(before_after_by_file, "before", "after", "diff")
    only_changed = prune_unchanged (before_after_by_file, "diff")
    return only_changed

def prune_unchanged (before_after_by_file, diff_tag):
    return {file:metrics_by_before_after_tag for file, metrics_by_before_after_tag in before_after_by_file.items() if diff_tag in metrics_by_before_after_tag}

def _compute_dict_diff (dict_a, dict_b):
    result = {}
    for key_a, value_a in dict_a.items():
        value_b = dict_b.get(key_a, 0)
        result[key_a] = value_b - value_a
    for key_b, value_b in dict_b.items():
        if key_b not in dict_a: # new metric, was not present in the file
            result[key_b] = value_b
    return result

def populate_diffs(before_after_by_file, tag_before, tag_after, tag_diff):
    for file_path, dict_before_after in before_after_by_file.items():
        metrics_before = dict_before_after[tag_before]
        metrics_after = dict_before_after[tag_after]
        if metrics_before == metrics_after:
            continue
        dict_before_after[tag_diff] = _compute_dict_diff(metrics_before, metrics_after)

def populate_file_metrics(udb, tag, metric_names, result):
    # result: dict {key: <file-path>, value: dict {key: tag, value : dict (key: metric-name, value: metric-value} } }
    file_entities = udb.ents("file ~Unresolved ~Unknown ~Unparsed")
    for file_entity in file_entities:
        if file_entity.library() is not "": # skip files that belong to external libraries
            continue
        file_path = file_entity.relname()
        file_attribs = {}
        if file_path not in result:
           result[file_path] = file_attribs
        else:
            file_attribs = result[file_path]

        metric_dict = file_entity.metric(metric_names)
        unsupported_metrics_names = []
        for k, v in metric_dict.items():
            if metric_dict[k] is None:
                unsupported_metrics_names.append(k)
        if len(unsupported_metrics_names) > 0:
            for k in unsupported_metrics_names:
                del metric_dict[k]
                sys.stderr.write("WARNING '%s' not supported by file '%s' \n" % (unsupported_metrics_names, file_path))

        file_attribs[tag] = metric_dict

if __name__ == '__main__':
    arguments = docopt(__doc__, version='0.1')
    verbose = arguments["--verbose"]

    dllDir = arguments["--dllDir"]
    sys.path.insert(0,dllDir) # add the dir with the DLLs - Qt etc
    os.environ["PATH"] = dllDir + os.pathsep + os.environ["PATH"] # prepend
    sys.path.insert(0,os.path.join(dllDir,"Python")) # also needed, For interop
    sys.path.insert(0,os.path.join(dllDir,"python")) # also needed, For interop with older versions of Understand (which used lowercase)
    #hangs!!!!! os.environ["PYTHONPATH"] = os.path.join(dllDir,"python") + os.pathsep + os.environ.get("PYTHONPATH", "") # prepend


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


