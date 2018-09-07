import os
import subprocess
from io import StringIO
import csv
from csv import reader  # this should import your custom parser instead
import json


# DEFAULT GIVEN
test_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))

CSV_PATH = os.path.join(test_folder, 'tmp', 'test.csv')
ARGS_JSON_PATH = os.path.join(test_folder, 'tmp', 'args.json')
MODULE_PATH = os.path.abspath(os.path.join(test_folder, os.pardir, 'library', 'include_csv'))
execute_cmd = "python " + MODULE_PATH + " " + ARGS_JSON_PATH
IN_MEM_CSV = StringIO(u"""col1,col2,col3
1,3,foo
2,5,bar
-1,7,baz""")
KEY = os.path.basename(os.path.splitext(CSV_PATH)[0])


def set_up():
    test_reader = reader(IN_MEM_CSV, delimiter=',')
    for line in test_reader:
        with open(CSV_PATH, 'a') as testfile:
            wr = csv.writer(testfile, quoting=csv.QUOTE_ALL)
            wr.writerow(line)

    with open(CSV_PATH, 'rb') as file_obj:
        dict_reader = csv.DictReader(file_obj)
        data = {"{0}".format(KEY): [i for i in dict_reader]}
    return data


def truncate_tmp_csv():
    # opening the file with w+ mode truncates the file
    f = open(CSV_PATH, "w+")
    f.close()


def update_args_json():
    with open(ARGS_JSON_PATH, "r") as jsonFile:
        data = json.load(jsonFile)

    data["ANSIBLE_MODULE_ARGS"]['src'] = CSV_PATH

    with open(ARGS_JSON_PATH, "w") as jsonFile:
        json.dump(data, jsonFile)


def test_include_csv():
    # GIVEN & WHEN
    truncate_tmp_csv()
    set_up()
    update_args_json()

    data = str(set_up()).replace("\'", "\"")
    expected_data = json.loads(data)

    output = subprocess.check_output(execute_cmd, shell=True)
    json_decoded = json.loads(output)
    actual_data = json_decoded['ansible_facts']

    # THEN
    assert cmp(expected_data, actual_data) == 0
