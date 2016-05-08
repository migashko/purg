#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import purge_file
import purge_config

# Перемещение из pre в cat, те что остались в flt (отсюда удаляються)

def show():
  file_list = purge_file.PurgeFile.make_list(purge_config.flt)
  purge_file.PurgeFile.show_list(file_list)

def files_for_delete(file_list, path):
  result = []
  orig_list = purge_file.PurgeFile.make_list(path)
  for f1 in file_list:
    for f2 in orig_list:
      if f1.filename == f2.filename:
        result += [f2]
        break
  return result

def del_dirs(src_dir):
  for dirpath, _, _ in os.walk(src_dir, topdown=False):  # Listing the files
    if dirpath == src_dir:
      break
    try:
      os.rmdir(dirpath)
    except OSError as ex:
      pass
    
def prev():
  file_list = []
  pre_list = purge_file.PurgeFile.make_list(purge_config.pre)
  flt_list = purge_file.PurgeFile.make_list(purge_config.flt)
  for f1 in flt_list:
    for f2 in pre_list:
      if f1.filename == f2.filename:
        file_list += [f2]
        break
  src_list = files_for_delete(file_list, purge_config.src)
  geo_list = files_for_delete(file_list, purge_config.geo)
  
  for i in range( len(purge_config.cat_list)):
    print(u"{0}. {1}".format(i,purge_config.cat_list[i]) )
  i = input("select N: ")
  cat = purge_config.cat_list[i]
  supcat = ""
  for s in purge_config.cat_super:
    if cat in s[1]:
      supcat = s[0]
      break

  for f in file_list:
    if cat not in purge_config.cat_nogeodat:
      f.path_list = [supcat, cat] + f.path_list
    else:
      f.path_list = [supcat, cat]
    f.make_dst_path(purge_config.cat)
    
  purge_file.PurgeFile.show_prev(file_list)
  return (file_list, flt_list, geo_list, src_list)

def doit():
  file_list = prev()
  ready = raw_input('Ready [yes or no]: ')
  if ready=="yes":
    purge_file.PurgeFile.move_symlinks(file_list[0])
    purge_file.PurgeFile.delete_files(file_list[1])
    purge_file.PurgeFile.delete_files(file_list[2])
    purge_file.PurgeFile.delete_files(file_list[3])
    
    del_dirs(purge_config.src)
    # geo не чистим, чтоб легче было распределять
    #del_dirs(purge_config.geo)
    del_dirs(purge_config.pre)

    print("Done")


if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage:")
    print("\t --show\tсписок объектоа")
    print("\t --prev\tотобразить действия (но не делать)")
    print("\t --doit\tотобразить действия и сделать (если скажешь yes)")
    sys.exit(0)
  
  if sys.argv[1] == "--show":
    show()
  elif sys.argv[1] == "--prev":
    prev()
  elif sys.argv[1] == "--doit":
    doit()
