import getopt
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

from model.integrityentry import IntegrityEntry
from model.integrityfile import IntegrityFile


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

def usage(argv_0, exit_val):

    print("FLAC Integrity Checker\n")

    print("A Python script for FLAC integrity check.\n")
    print("Usage: %s [-h] --flac <flac-path> --folder <folder-path> --report <report-path> [--age <number-minutes>] [--min-percentage <number-percentage> || --max-percentage <number-percentage>]" % argv_0)

    print("\t-h / --help        :    Show this help.")
    print("\t--flac             :    Path to the 'flac' executable.")    
    print("\t--folder           :    Root folder path for recursive search.")
    print("\t--report           :    Path to the 'report' file.")
    print("\t--age              :    Age minimum since last check.")
    print("\t--min-percentage   :    Minimum percentage to check.")
    print("\t--max-percentage   :    Maximum percentage to check.")

    sys.exit(exit_val)  
  

def main(argv):

    flac_path = None
    folder = None
    report_file = None
    age = None
    percentage = None
    percentage_limit = None

    try:
        opts, args = getopt.getopt(argv[1:], '', ['help', 'folder=', 'flac=', 'report=', 'age=', 'min-percentage=', 'max-percentage='])

        if len(argv) >= 1:
            for opt, arg in opts:
                if opt in ("-h", "--help"):
                    usage(argv[0], 0)
                elif opt == "--folder":
                    folder = arg
                elif opt == "--flac":
                    flac_path = arg
                elif opt == "--report":
                    report_file = arg
                elif opt == "--age":
                    age = arg
                elif opt == "--min-percentage":
                    if (percentage_limit is not None):
                        sys.exit(-1)                    
                    percentage = arg
                    percentage_limit = 'MIN'
                elif opt == "--max-percentage":
                    if (percentage_limit is not None):
                        sys.exit(-1)                    
                    percentage = arg
                    percentage_limit = 'MAX'

            check(flac_path, folder, report_file, age, percentage, percentage_limit)

    except getopt.GetoptError as ex:
        usage(argv[0], 2)


def get_integrity_entries(folder: str, report_file: str):

    integrity_entries = list()
    if folder is not None:
        ieb_list = list()

        # lister les fichiers
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_name, file_extension = os.path.splitext(file)

                if file_extension.lower() in (".flac"):
                    file_path = os.path.join(root, file)

                    ieb = IntegrityEntry()
                    ieb.set_file_path(file_path)
                    ieb.set_file_size(os.path.getsize(file_path))
                    ieb.set_file_modtime(os.path.getmtime(file_path))
                    ieb.set_date_checked("1900-01-01 00:00:00")

                    ieb_list.append(ieb)

        intergity_file = IntegrityFile(report_file)
        ier_list = intergity_file.entries

        ier_dict = dict()
        if ier_list is not None:
            for integrity_entry in ier_list:
                ier_dict[integrity_entry.get_file_path()] = integrity_entry

        for ieb in ieb_list: #type: IntegrityEntry
            ie_new = ieb
            if ieb.get_file_path() in ier_dict:
                ier = ier_dict[ieb.get_file_path()]
                if ier.get_file_size() == str(ieb.get_file_size()):
                    if ier.get_file_modtime() == str(ieb.get_file_modtime()):
                        ie_new = ier

            integrity_entries.append(ie_new)

    return integrity_entries


def check(flac_path, folder, report_file, age, percentage, percentage_threshold):

    print("BEG         : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    integrity_entries = get_integrity_entries(folder, report_file)
    integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)

    if len(integrity_entries) <= 0:
        print("NFO         : no entry, nothing will be done")
    else: 
        limit_age = datetime.today()
        if age is not None:
            if int(age) >= 0:
                limit_age = datetime.today() - timedelta(minutes=int(age))
            else:
                limit_age = datetime(1900, 1, 1)
        
        limit_item = None
        if percentage is not None and int(percentage) >= 0:
            limit_item = round(len(integrity_entries) * int(percentage) / 100)

        limit_auto_save = len(integrity_entries) / 100

        print("LIMIT AGE   : " + limit_age.strftime("%Y-%m-%d %H:%M:%S"))
        print("LIMIT ITEM  : " + str(limit_item) + " " + str(percentage_threshold))

        i = 0
        for file in integrity_entries:

            if os.path.exists(file.get_file_path()):
                if (file.get_date_checked() <= limit_age.strftime("%Y-%m-%d %H:%M:%S") or \
                        (percentage_threshold is not None and percentage_threshold == 'MIN' \
                            and limit_item is not None and i < limit_item)):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    cmd = [flac_path, '-V', file.get_file_path(), '-t']
                    proc_encode = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    (cmd_out, cmd_err) = proc_encode.communicate()
                    if proc_encode.returncode != 0:
                        cmd_err = cmd_err.strip()
                        print(cmd_err)
                        sys.exit(-3)
                    else:
                        cmd_err = cmd_err.strip()
                        if cmd_err is not None:
                            r = cmd_err.split("\n")
                            if r is None:
                                print("FLAC output not found")
                                sys.exit(-3)
                            r = r[len(r) - 1]
                            m = re.match(r'.*ok', r)
                            if m is None:
                                print("FLAC verification failed")
                                sys.exit(-3)

                            print("OK: " + file.get_file_path())
                            file.set_date_checked(now)
                        else:
                            print("FLAC output expected")
                            sys.exit(-3)

                    i = i + 1                
                    if (percentage_threshold is not None and percentage_threshold == 'MAX' \
                            and limit_item is not None and i > limit_item):
                        print("ITEM MAX reached")
                        break

                    if limit_auto_save > 0 and i % limit_auto_save == 0:
                        IntegrityFile.write_integrity_entries(integrity_entries, report_file)
                else:
                    break

        integrity_entries.sort(key=lambda e: e.get_date_checked(), reverse=False)
        IntegrityFile.write_integrity_entries(integrity_entries, report_file)
    
    print("END         : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main(sys.argv)