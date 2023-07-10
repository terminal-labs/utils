import os
import json
import hashlib
from functools import reduce

from ruamel import yaml


class Dirdict:
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def __directorystructure(self, rootdir):
        def __remove_none(obj):
            result = {}
            for key, value in obj.items():
                if value == None:
                    result[key] = "None"
                else:
                    result[key] = value
            return result
        dir = {}
        rootdir = rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = __remove_none(subdir)
        return dir

    def __walk(self, path):
        folders = []
        files = []
        for r, d, f in os.walk(path):
            for folder in d:
                folders.append(os.path.abspath(os.path.join(r, folder)))
            for file in f:
                files.append(os.path.abspath(os.path.join(r, file)))
        return (sorted(folders), sorted(files))

    def __foldersize(self, folder):
        total_size = os.path.getsize(folder)
        for item in os.listdir(folder):
            itempath = os.path.join(folder, item)
            if os.path.isfile(itempath):
                total_size += os.path.getsize(itempath)
            elif os.path.isdir(itempath):
                total_size += self.__foldersize(itempath)
        return total_size

    def size(self):
        print(self.__foldersize(self.path))

    def allfilepaths(self):
        print(self.__walk(self.path)[1])

    def alldirpaths(self):
        print(self.__walk(self.path)[0])
        return self.__walk(self.path)[0]

    def allfilenames(self):
        filenames = []
        for p in self.__walk(self.path)[1]:
            filename = os.path.basename(p)
            filenames.append(filename)
        print(filenames)
        return filenames

    def alldirnames(self):
        dirnames = []
        for d in self.__walk(self.path)[0]:
            dirname = os.path.basename(d)
            dirnames.append(dirname)
        print(dirnames)
        return dirnames

    def getcontent(self, path):
        if os.path.isfile(path):
            f = open(path, "r")
            print(f.read())
        else:
            print("File not exist")

    def countdirs(self):
        print(len(self.alldirnames()))

    def countfiles(self):
        print(len(self.allfilenames()))

    def dir(self):
        print(self.__directorystructure(self.path))

    def dirjson(self):
        json_string = json.dumps(self.__directorystructure(self.path))
        print(json_string)
        return json_string

    def diryaml(self):
        dic = json.loads(self.dirjson())
        yaml_string = yaml.dump(dic, Dumper=yaml.RoundTripDumper)
        print(yaml_string)

    def fileexists(self, filename):
        if filename in self.allfilenames():
            print("True")
        else:
            print("False")

    def pathtofile(self, filename):
        files = self.__walk(self.path)[1]
        files_dic = {}
        for file in files:
            files_dic[os.path.basename(file)] = file
        print(files_dic[filename])
        return os.path.abspath(files_dic[filename])

    def hashcontent(self, path):
        if os.path.isfile(path):
            f = open(path, "r")
            print(hashlib.sha256(f.read().encode('utf-8')).hexdigest())
            return hashlib.sha256(f.read().encode('utf-8')).hexdigest()
        else:
            print("File not exist")

    def getline(self, path, index):
        if os.path.isfile(path):
            f = open(path, "r")
            lines = f.readlines()
            print(lines[index])
            return lines[index]
        else:
            print("File not exist")

    def setoffileexts(self):
        exts = []
        for name in self.allfilenames():
            filename, file_extension = os.path.splitext(name)
            exts.append(file_extension)
        print(set(exts))
        return set(exts)



data = Dirdict(somepath)
data.allfilepaths()
data.alldirpaths()
data.allfilenames()
data.alldirnames()
data.size()
data.countfiles()
data.countdirs()
data.dir()
data.dirjson()
data.diryaml()
data.setoffileexts()
#data.fileexists("filename")
#data.pathtofile("filename")
#data.getcontent("path")
#data.hashcontent("path")
#data.getline("path", 1)
