import csv
from datetime import datetime


CSV_FILEPATH = 'OGUTS_CSV.csv'
PY_FILEPATH = 'script_from_csv.py'

# CSV Column Headers
CMD = 'Command'
TN = 'TestName'
MATCH = 'Prompt'
TO = 'Timeout'
KNOWN_VAL = 'Known'
REGEX = 'Regex'
PASS_CB = 'Pass_CallBack'
TO_CB = 'Timeout_CallBack'
F_CB = 'Fail_CallBack'

ABORT_FUNC = 'raise AbortTest'

def write_ta_from_csv():
    """
    Generates send/expect code from csv file    
    """
    print 'hello'
    script = open(PY_FILEPATH, 'w')
    # write header
    script.write('"""\nAuto-Generated TA Script from %s.\nGenerated on %s\n"""\n' % (CSV_FILEPATH, datetime.now()))
    # write any imports required
    script.write('\nimport re\n')
    script.write('\n')

    # parse CSV
    with open(CSV_FILEPATH) as csvfile:
        reader = csv.DictReader(csvfile)
        test = ''
        cmd = ''
        indent = ''
        for t in reader:
            # sticky testname
            if t[TN]:
                indent = ''
                test = t[TN].lower()
                script.write('\n%sdef %s():\n' % (indent, test))
                indent += '\t'

            if t[CMD]:
                cmd = t[CMD]

            # if both send and expect
            if t[CMD] and t[MATCH]:
                script.write("%scmd = '%s'\n" % (indent, t[CMD]))
                script.write("%sresult = session.sendexpect(cmd, '%s', %s)\n" % (indent, t[MATCH], t[TO]))
                script.write("%sif result['timeout']\n" % indent)
                indent += '\t'
                msg = 'Script timed out during \'%s\' command.'
                script.write("%s%s(\"%s\" %% cmd)\n\n" % (indent, ABORT_FUNC, msg))
                indent = indent[:-1]
            # if just send
            elif t[CMD]:
                script.write("%scmd = '%s'\n" % (indent, t[CMD]))
                script.write("%ssession.send(cmd)\n" % indent)
            # if just expect
            elif t[MATCH]:
                script.write("%sresult = expect('%s', %s)\n" % (indent, t[MATCH], t[TO]))
                script.write("%sif result['timeout']\n" % indent)
                indent += '\t'
                msg = "Script timed out during '%s' command."
                script.write("%s%s(\"%s\") %% cmd\n\n" % (indent, ABORT_FUNC, msg))
                indent = indent[:-1]

            if t[REGEX]:
                script.write("%sbuf = result['buffer']\n" % indent)
                script.write("%sregex = re.compile('%s')\n" % (indent, t[REGEX]))
                script.write("%sregexresult = re.search(regex, buf)\n" % indent)
                script.write("%sif not regexresult:\n" % indent)
                indent += '\t'
                msg = "Unable to extract regex [%s] from command '%%s' buffer." % (t[REGEX])
                script.write("%s%s(\"%s\" %% cmd)\n" % (indent, ABORT_FUNC, msg))
                indent = indent[:-1]
                # compare with known value
                if t[KNOWN_VAL]:
                    script.write("%selse:\n" % indent)
                    indent += '\t'
                    script.write("%sknown_val = '%s'\n" % (indent, t[KNOWN_VAL]))
                    script.write("%sextracted_val = regexresult.group(1)\n" % indent)
                    script.write("%sif extracted_val != known_val:\n" % indent)
                    indent += '\t'
                    msg = "Mismatched extracted/known values! Got: [%s], Expected: [%s]"
                    script.write("%s%s(\"%s\" %% (extracted_val, known_val))\n\n" % (indent, ABORT_FUNC, msg))
                    indent = indent[:-2]
                # just validate regex was in previous buf
                else:
                    pass

if __name__ == "__main__":
    write_ta_from_csv()
