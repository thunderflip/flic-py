import bisect
import getopt
import logging
import os
import sys
from datetime import datetime, timedelta

from model.integrityentry import IntegrityEntry
from model.integrityfile import IntegrityFile
from flac.flacoperation import FlacOperation


DATE_FORMAT                 = "%Y-%m-%d %H:%M:%S"
DATE_UNDEFINED_VAL          = datetime(1900, 1, 1)

EXIT_CODE_OK                =  0
EXIT_CODE_ERR_OPTION        = -1
EXIT_CODE_ERR_VALIDATION    = -2

LOG                         = None
MODTIME_TOLERANCE           = 1000
MINUTES_BETWEEN_AUTO_SAVE   = 3


def init_logging():
    logging.root.setLevel(logging.INFO)

    # Add console handler
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] [%(filename)-20s%(lineno)-3s] %(message)s')
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)


def usage(argv_0, exit_val):

    print("FLAC Integrity Check\n")

    print("A python script for FLAC Integrity Check\n")
    print("Usage: %s [-h  || --help] --flac <flac-path> --folder <folder-path> --report <report-path> [--age <number-minutes>] [--min-percentage <number-percentage> || --max-percentage <number-percentage>]" % argv_0)

    print("\t-h / --help        : Shows this help")
    print("\t--flac             : Path to the flac executable")    
    print("\t--folder           : Root folder path to FLAC collection for recursive files search")
    print("\t--report           : Path to the report file")
    print("\t--age              : Age in minutes to identify files to check")
    print("\t--min-percentage   : Minimum percentage of collection to check")
    print("\t--max-percentage   : Maximum percentage of collection to check")

    sys.exit(exit_val)  
  

def main(argv):

    global LOG 

    flac_path = None
    folder = None
    report_file = None
    age = None
    percentage = None
    percentage_limit = None

    try:
        init_logging()        
        LOG = logging.getLogger('IntegrityCheck')

        opts, args = getopt.getopt(argv[1:], 'h', ['help', 'folder=', 'flac=', 'report=', 'age=', 'min-percentage=', 'max-percentage='])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage(argv[0], EXIT_CODE_OK)
            elif opt == "--folder":
                folder = arg
            elif opt == "--flac":
                flac_path = arg
            elif opt == "--report":
                report_file = arg
            elif opt == "--age":
                try:
                    age = int(arg)
                except:
                    LOG.warning("Option 'age' must be an integer")
                    LOG.warning("No value will be used for this option")
                    age = None
            elif opt == "--min-percentage":
                try:
                    if (percentage_limit is not None):
                        LOG.error("A 'xxx-percentage' argument has already been provided")
                        sys.exit(EXIT_CODE_ERR_OPTION)
                    percentage = int(arg)
                    percentage_limit = 'MIN'
                except:
                    LOG.warning("Option 'min-percentage' must be an integer")
                    LOG.warning("No value will be used for this option")
            elif opt == "--max-percentage":
                try:                
                    if (percentage_limit is not None):
                        LOG.error("A 'xxx-percentage' option has already been provided")
                        sys.exit(EXIT_CODE_ERR_OPTION)
                    percentage = int(arg)
                    percentage_limit = 'MAX'
                except:
                    LOG.warning("Option 'max-percentage' must be an integer")
                    LOG.warning("No value will be used for this option")

        check(flac_path, folder, report_file, age, percentage, percentage_limit)

    except getopt.GetoptError as ex:
        usage(argv[0], EXIT_CODE_ERR_OPTION)


def get_integrity_entries(folder: str, report_file: str):

    integrity_entries = list()
    if folder is not None:
        intergity_file = IntegrityFile(report_file)
        ier_list = intergity_file.entries

        ier_dict = dict()
        if ier_list is not None:
            for integrity_entry in ier_list:
                ier_dict[integrity_entry.get_file_path()] = integrity_entry

        # List files
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_name, file_extension = os.path.splitext(file)

                if file_extension.lower() in (".flac"):
                    file_path = os.path.join(root, file)

                    ied = IntegrityEntry()
                    ied.set_file_path(file_path)
                    ied.set_file_size(os.path.getsize(file_path))
                    ied.set_file_modtime(os.path.getmtime(file_path))
                    ied.set_date_checked(DATE_UNDEFINED_VAL)

                    ie_new = ied
                    if ied.get_file_path() in ier_dict:
                        ier = ier_dict[ied.get_file_path()]
                        if ier.get_file_size() == ied.get_file_size():
                            diff_time = abs(ier.get_file_modtime() - ied.get_file_modtime())
                            if diff_time <= MODTIME_TOLERANCE:
                                ie_new = ier
                                if diff_time != 0:
                                    ie_new.set_file_modtime(ied.get_file_modtime())

                    integrity_entries.append(ie_new)

    return integrity_entries


def check(flac_path, folder, report_file, age, percentage, percentage_threshold):

    LOG.error("BEG - Check")

    limit = 0
    date_begin = datetime.now()

    integrity_entries = get_integrity_entries(folder, report_file)
    integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)

    if len(integrity_entries) <= 0:
        LOG.warning("No item, nothing will be done")
    else:
        LOG.info("Total item(s): " + str(len(integrity_entries)))

        checked_date_oldest = integrity_entries[ 0].get_date_checked()
        checked_date_newest = integrity_entries[-1].get_date_checked()
        LOG.info("Oldest checked item: " + checked_date_oldest.strftime(DATE_FORMAT) + " / " + str( round( (datetime.now() - checked_date_oldest).total_seconds() / 60 ) ) + " minutes")
        LOG.info("Newest checked item: " + checked_date_newest.strftime(DATE_FORMAT) + " / " + str( round( (datetime.now() - checked_date_newest).total_seconds() / 60 ) ) + " minutes")

        limit_by_age = None
        if age is not None:
            limit_age_date = None
            if age >= 0:
                limit_age_date = datetime.now() - timedelta(minutes=age)
            elif age == -1:
                limit_age_date = DATE_UNDEFINED_VAL
            elif age == -2:
                limit_age_date = datetime.today()

            limit_by_age = bisect.bisect(integrity_entries, limit_age_date, 0, len(integrity_entries), key=lambda e: e.get_date_checked())
            LOG.info("Limit item(s) by age: " + str(limit_by_age))
        else:
            LOG.info("Limit item(s) by age: not defined")

        limit_by_percentage = None
        if percentage is not None and percentage > 0:
            limit_by_percentage = round(len(integrity_entries) * percentage / 100)
            limit_by_percentage = min(limit_by_percentage, len(integrity_entries))
            LOG.info("Limit item(s) by percentage: " + str(limit_by_percentage) + " " + str(percentage_threshold))
        else:
            LOG.info("Limit item(s) by percentage: not defined")

        limit = 0
        if limit_by_age is not None:
            limit = limit_by_age
            if limit_by_percentage is not None:
                if percentage_threshold == 'MIN':
                    if (limit_by_age < limit_by_percentage):
                        limit = limit_by_percentage
                        LOG.info("Limit item 'by age' changed by limit 'by percentage' from " + str(limit_by_age) + " to " + str(limit_by_percentage))
                elif percentage_threshold == 'MAX':
                    if (limit_by_age > limit_by_percentage):
                        limit = limit_by_percentage
                        LOG.info("Limit item 'by age' changed by limit 'by percentage' from " + str(limit_by_age) + " to " + str(limit_by_percentage))
        elif limit_by_percentage is not None:
            if percentage_threshold == 'MIN':
                limit = limit_by_percentage
        LOG.warning("Effective item(s) limit: " + str(limit))

        if (limit >= len(integrity_entries)):
            integrity_entries.sort(key=lambda e: e.get_file_path(), reverse=False)

        i = 0
        last_save = datetime.now()
        nb_format = "{0:"+str(len(str(limit)))+"d}"
        for file in integrity_entries:
            if (i < limit):
                if os.path.exists(file.get_file_path()):
                    flac_op = FlacOperation(flac_path, None, file.get_file_path())
                    LOG.warning("Verifying (" + nb_format.format(i + 1) + "/" + nb_format.format(limit) + " - " + "{0:6.2f}".format((i+1) / limit * 100) + "%): " + file.get_file_path())
                    if flac_op.test():
                        now = datetime.now()
                        file.set_date_checked(now)
                    else:
                        LOG.critical("KO")
                        sys.exit(EXIT_CODE_ERR_VALIDATION)

                i = i + 1

                if (datetime.now() - last_save).total_seconds() / 60 > MINUTES_BETWEEN_AUTO_SAVE:
                    IntegrityFile.write_integrity_entries(integrity_entries, report_file)
                    last_save = datetime.now()
            else:
                LOG.info("There are no more items satisfying 'age' or 'percentage' conditions")
                break

        if i != 0:
            integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)
            IntegrityFile.write_integrity_entries(integrity_entries, report_file)

    date_end = datetime.now()
    LOG.error("Elapsed time: " + str(date_end - date_begin) + " for " + str(limit) + " item(s)")
    LOG.error("END - Check")

if __name__ == "__main__":
    main(sys.argv)