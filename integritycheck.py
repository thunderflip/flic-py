import bisect
import getopt
import logging
import os
import sys
from datetime import datetime, timedelta

from model.integrityentry import IntegrityEntry
from model.integrityfile import IntegrityFile
from flac.flacoperation import FlacOperation

    # ANCIENNETÉ + MAX=100  --> ANCIENNETÉ  
    # ANCIENNETÉ + MIN=0    --> ANCIENNETÉ
    # Tous les fichiers dépassant l'ancienneté sont vérifiés
    #
    # ANCIENNETÉ + MIN<100  --> MAX(ANCIENNETÉ, MIN)
    # Tous les fichiers dépassant l'ancienneté sont vérifiés
    # Un minimum de x% des fichiers sont vérifiés
    #
    # ANCIENNETÉ + MAX<100  --> MIN(ANCIENNETÉ, MAX)
    # Un maximum de x% des fichiers sont vérifés    
    # Les fichiers dépassant l'ancienneté sont vérifiés 
    # Tous les fichiers dépassant l'ancienneté pourraient ne pas être vérifiés.
    # 
    # ANCIENNETÉ + MIN=100  --> MIN=100
    # Tous les fichiers sont vérifiés


DATE_FORMAT                 = "%Y-%m-%d %H:%M:%S"
DATE_UNDEFINED_VAL          = datetime(1900, 1, 1)
DATE_UNDEFINED_VAL_STR      = DATE_UNDEFINED_VAL.strftime(DATE_FORMAT)

EXIT_CODE_OK                =  0
EXIT_CODE_ERR_OPTION        = -1
EXIT_CODE_ERR_VALIDATION    = -2

LOG                         = None


def init_logging():
    logging.root.setLevel(logging.INFO)

    # Add console handler
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-8s] [%(filename)-20s%(lineno)-3s] %(message)s')
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)


def usage(argv_0, exit_val):

    print("FLAC Collection Integrity Checker\n")

    print("A python script to check FLAC integrity\n")
    print("Usage: %s [-h  || --help] --flac <flac-path> --folder <folder-path> --report <report-path> [--age <number-minutes>] [--min-percentage <number-percentage> || --max-percentage <number-percentage>]" % argv_0)

    print("\t-h / --help        :    This HELP.")
    print("\t--flac             :    Path to the FLAC executable.")    
    print("\t--folder           :    Root FOLDER path for recursive search.")
    print("\t--report           :    Path to the REPORT file.")
    print("\t--age              :    AGE minimum since last check.")
    print("\t--min-percentage   :    MINimum PERCENTAGE to check.")
    print("\t--max-percentage   :    MAXimum PERCENTAGE to check.")

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
                        LOG.critical("A 'xxx-percentage' argument has already been provided")
                        sys.exit(EXIT_CODE_ERR_OPTION)
                    percentage = int(arg)
                    percentage_limit = 'MIN'
                except:
                    LOG.warning("Option 'min-percentage' must be an integer")
                    LOG.warning("No value will be used for this option")
            elif opt == "--max-percentage":
                try:                
                    if (percentage_limit is not None):
                        LOG.critical("A 'xxx-percentage' option has already been provided")
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

                    ieb = IntegrityEntry()
                    ieb.set_file_path(file_path)
                    ieb.set_file_size(os.path.getsize(file_path))
                    ieb.set_file_modtime(os.path.getmtime(file_path))
                    ieb.set_date_checked(DATE_UNDEFINED_VAL_STR)

                    ie_new = ieb
                    if ieb.get_file_path() in ier_dict:
                        ier = ier_dict[ieb.get_file_path()]
                        if ier.get_file_size() == str(ieb.get_file_size()):
                            if ier.get_file_modtime() == str(ieb.get_file_modtime()):
                                ie_new = ier

                    integrity_entries.append(ie_new)

    return integrity_entries


def check(flac_path, folder, report_file, age, percentage, percentage_threshold):

    LOG.critical("BEG - Check")

    integrity_entries = get_integrity_entries(folder, report_file)
    integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)

    if len(integrity_entries) <= 0:
        LOG.warning("No entry, nothing will be done")
    else:
        limit_by_age = None
        if age is not None:
            limit_age_date = None
            if age >= 0:
                limit_age_date = datetime.now() - timedelta(minutes=age)
            elif age == -1:
                limit_age_date = DATE_UNDEFINED_VAL
            elif age == -2:
                limit_age_date = datetime.today()

            limit_by_age = bisect.bisect(integrity_entries, limit_age_date.strftime(DATE_FORMAT), 0, len(integrity_entries), key=lambda e: e.get_date_checked())
            LOG.info("Limit item by age: " + str(limit_by_age))
        else:
            LOG.info("Limit item by age: not defined")

        limit_by_percentage = None
        if percentage is not None and percentage > 0:
            limit_by_percentage = round(len(integrity_entries) * percentage / 100)
            limit_by_percentage = min(limit_by_percentage, len(integrity_entries))
            LOG.info("Limit item by percentage: " + str(limit_by_percentage) + " " + str(percentage_threshold))
        else:
            LOG.info("Limit item by percentage: not defined")

        limit = 0
        if limit_by_age is not None:
            limit = limit_by_age
            if limit_by_percentage is not None:
                if percentage_threshold == 'MIN':
                    limit = max(limit_by_age, limit_by_percentage)
                    if (limit_by_age < limit_by_percentage):
                        LOG.info("Limit item by age changed by limit by percentage from " + str(limit_by_age) + " to " + str(limit_by_percentage))
                elif percentage_threshold == 'MAX':
                    limit = min(limit_by_age, limit_by_percentage)
                    if (limit_by_age > limit_by_percentage):
                        LOG.info("Limit item by age changed by limit by percentage from " + str(limit_by_age) + " to " + str(limit_by_percentage))
        elif limit_by_percentage is not None:
            if percentage_threshold == 'MIN':
                limit = limit_by_percentage
        LOG.info("Effective item limit: " + str(limit))

        limit_auto_save = limit // 10
        limit_auto_save = max(limit_auto_save, 50)

        i = 0
        for file in integrity_entries:
            if os.path.exists(file.get_file_path()):
                if (i < limit):
                    now = datetime.now().strftime(DATE_FORMAT)

                    flac_op = FlacOperation(flac_path, None, file.get_file_path())
                    LOG.info("Verifying: '" + file.get_file_path() + "'")
                    if flac_op.test():
                        file.set_date_checked(now)
                    else:
                        LOG.critical("KO")
                        sys.exit(EXIT_CODE_ERR_VALIDATION)

                    i = i + 1
                    if limit_auto_save > 0 and i % limit_auto_save == 0:
                        IntegrityFile.write_integrity_entries(integrity_entries, report_file)
                else:
                    LOG.info("There are no more items satisfying 'age' or 'percentage' conditions")
                    break

        integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)
        IntegrityFile.write_integrity_entries(integrity_entries, report_file)

    LOG.critical("END - Check")

if __name__ == "__main__":
    main(sys.argv)