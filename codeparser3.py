import subprocess
import re
import os
from collections import defaultdict
from itertools import compress


dir2 = "/home/jferrer/slambench/benchmarks/orbslam2/src/original"
dir3 = "/home/jorge/slambench/benchmarks/orbslam3/src/original"


def find_declarations(dir, casual=False):
    data_type = "mutex"
    cmd = f"grep -rnw -E '(std::)?{data_type}\s+[a-zA-Z_][a-zA-Z0-9_]*\s*;' {dir}/src {dir}/include"
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = res.stdout.decode('utf-8').split('\n')
    
    casual_data = defaultdict(lambda:[])
    pro_data = list()

    
    for entry in output:
        if not entry: #empty line
            continue
        
        fields = re.split(f"(:)", entry)
        
        filename = os.path.basename(fields[0])
        linenumber = fields[2]
        text = "".join(fields[4:]).strip()#[:-1]

        classname, extension = filename.split('.')
        varname = re.findall("(?<=mutex\s).*(?=;)", text)[0]
        
        casual_data[classname].append(text)
        pro_data.append({"text":text, "varname":varname, "filepath":fields[0], "linenumber":linenumber, "classname":classname})
        
    return casual_data if casual else pro_data


def add_occurrences(data, dir, validate=False):
    """Add to the data dictionary a new entry with all the occurences of said variable"""
    def check_scope(var, lock):
        """Checks if the mutex of the lock falls in the scope of var.
        This happens when the file is the same (same class) or if referenced
        from another file. 
        This is necessary because some mutex have the same
        name even though they are from different classes."""
        lock_classname, lock_extension = os.path.basename(lock["filepath"]).split('.')
        if lock["mutexname"] == var["varname"] and lock_classname == var["classname"]:
            return True
        else: #It might still be a reference to the correct mutex. The reference can be object_name-> or class_name:: In my cases, all the object names have the format [something]class_name
            s = re.search(f".*{ var['classname'] }.{{2}}{ var['varname'] }", lock["mutexname"])
            if s:
                return True
            return False
        
    cmd = f"grep -rnw -E 'unique_lock' {dir}/src {dir}/include"
    res = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = res.stdout.decode('utf-8')

    for var in data:
        locks = re.findall(f"(.+):(\d+):.*\((.*{ var['varname'] })\);", output)
        locks = [dict(zip(("filepath", "linenumber", "mutexname"), lock)) for lock in locks]
        indices = [check_scope(var, lock) for lock in locks]
        
        locks = list(compress(locks, indices)) #Select locks that are within the scope
        var["occurences"] = locks

    
    if validate:
        validated = True
        locks = output.split('\n')[:-1]
        counts = [-1] * len(locks) #Ideally all entries are count once, so this should all be 0 at the end
        
        for var in data:
            for occ in var["occurences"]:
                pattern = f"{occ['filepath']}:{occ['linenumber']}:.*"
                idx = [i for i, x in enumerate(locks) if re.match(pattern, x)]
                
                #This should never happen
                if len(idx)>1:
                    print('ERROR: lock found twice???')
                    validated = False
                if not len(idx):
                    print('ERROR: lock NOT found????')
                    validated = False
        
                counts[idx[0]] += 1
        
        for i, c in enumerate(counts):
            if c:
                validated = False
                print(f"lock {i} counted {c+1} times. >:(\n\t{locks[i]}")
        
        print(f"\nValidation {'NOT ' if not validated else ''}OK!")


def modify_files(variable, mode):
    """Modify the files so that all references to a variable are (un)commented.
    depending on the mode flag."""
    def change_file(filepath, linenumber):
        with open(filepath, 'r+') as file:
            lines = file.readlines()

            linenumber = int(linenumber) - 1 #Numeration of grep starts at 1

            commented = lines[linenumber][:2] == "//"
            if comment:
                if not commented:
                    new_line = "//" + lines[linenumber]
                else:
                    print("WARNING: Trying to comment an already commented line.")
                    print(f"\t{filepath}:{linenumber}:")
                    return
            else:
                if commented:
                    new_line = lines[linenumber][2:]
                else:
                    print("WARNING: Trying to uncomment an already uncommented line.")
                    print(f"\t{filepath}:{linenumber}:")
                    return

            lines[linenumber] = new_line
            
            file.seek(0)
            file.truncate(0)
            file.writelines(lines)
    
    if mode == "comment":
        comment = True
    elif mode == "uncomment":
        comment = False
    else:
        raise ValueError(f"Mode incorrect. Only 'comment' or 'uncomment' are accepted. Given {mode}")
    
    change_file(variable['filepath'], variable['linenumber'])
    
    for o in variable['occurences']:
        change_file(o['filepath'], o['linenumber'])
        

def classify_vars(data):
    """print al the variable found and which file/classes have a variable with that name"""
    vars = []
    for key_vars in data.values():
        vars.extend(key_vars)
        
    for var in vars:
        print(var)
        for key, keyvars in data.items():
            if var in keyvars:
                print("\t", key)


dat = find_declarations(dir2)
add_occurrences(dat, dir2, validate=True)

for var in dat:
    modify_files(var, "comment")
    res = subprocess.run("make -j slambench APPS=orbslam2", shell=True)
    res = subprocess.run(f"./backup_library.sh liborbslam2 mutex_experiments/{var['classname']}_{var['varname']}", shell=True)
    res = subprocess.run("make slambench APPS=orbslam2", shell=True)
    modify_files(var, "uncomment")










"""data_2 = find_declarations(dir2)
data_3 = find_declarations(dir3)

keys = []
keys.extend(list(data_2.keys()))
keys.extend(list(data_3.keys()))
keys = set(keys)


#print all vars (both data) for each class
for key in keys:
    print(key)
    ms = set()
    for data in [data_2, data_3]:
        for m in data[key]:
            ms.add(m)
    
    for m in ms:
        print(m)

print("*"*50)
check1 = data_3
check2 = data_2
for key in keys:
    print(key)
    for m in check1[key]:
        if m in check2[key]:
            continue
        print("\t",m)"""
    