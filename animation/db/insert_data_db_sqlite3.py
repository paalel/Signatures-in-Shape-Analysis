from db_helpers import set_up
from db_config import ANIMATION_FILE_DIR

import os, sys, wget, traceback, re


def get_general_description(subject_file):
    with open(subject_file, "r") as file:
        #second row in subject_file contains a header with a description in
        #paranthesis
        description_re  = re.search('\((.*)\)', file.readlines()[1])
        if description_re is not None:
            return description_re.group(1)
        return "NO LONGER IN MOCAP INDEX"

def get_description(subject_file, file_name, is_asf=False):
    if subject_file is None:
        print("subject_file not found")
        return "ERROR"

    general_description = get_general_description(subject_file)
    if is_asf: return general_description

    with open(subject_file, "r") as file:
        for line in file:
            line = line.split("\t")
            if file_name in line:
                description = line[-2]
                if ".avi" in description:
                    description = line[-1]
                if len(description) > 2:
                    return description.rstrip("\r")
    
    #no description found, use general one
    return general_description + " (subject description)"

def fetch_subject_file(_dir):
    file_number = int(_dir.split("/")[-1])
    subject_dir = "subject_files"
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)

    subject_file = subject_dir  + "/subject%d.txt" % file_number
    if not os.path.isfile(subject_file):
        print("%s not found, downloading from mocap.cs.cmu.edu." % subject_file)
        try:
            url = "http://mocap.cs.cmu.edu/search.php?subjectnumber="+str(file_number)+"&motion=%%%&maincat=%&subcat=%&subtext=yes"
            subject_file = wget.download(url, subject_file)
        except: 
            print("Caught exception:")
            print(traceback.format_exc())
            subject_file = None

    return subject_file

def insert_db(file_name, dirpath, subject_file, subject_fkey, cursor):
    if file_name.endswith("asf"):
        description = get_description(subject_file, file_name, is_asf = True)
        cursor.execute("""
            INSERT INTO 
            subject(file_name, file_path, file_type, description)
            VALUES (?, ?, ?, ?);
            """, ( file_name, dirpath + "/" + file_name, "asf", description, )
        )
        subject_fkey = cursor.lastrowid
    if file_name.endswith("amc"):
        description = get_description(subject_file, file_name)
        cursor.execute("""
            INSERT INTO 
            animation (file_name, file_path, file_type, description, subject_id)
            VALUES (?,?,?,?,?);
            """, ( file_name, dirpath + "/" + file_name, "amc",
                   description, subject_fkey, )
        )

    #return subject_fkey
    return subject_fkey

if __name__ == "__main__":
    connection, cursor = set_up()
    #walk thru all files and directories, and add them to the db
    for _dir in [x[0] for x in os.walk(ANIMATION_FILE_DIR)]:
        for (dirpath, dirnames, filenames) in os.walk(_dir):
            if _dir is ANIMATION_FILE_DIR:
                continue
            subject_file = fetch_subject_file(_dir)
            subject_fkey = None
            #sort list to ensure .asf file is inserted first
            for file_name in sorted(filenames, key=lambda x: x[-3:], reverse=True): 
                subject_fkey = insert_db(file_name, dirpath, subject_file, subject_fkey, cursor)
                connection.commit()

    cursor.close()
