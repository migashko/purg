#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import purge_file
import purge_config

def make_name(src):
  file_list = purge_file.PurgeFile.make_list(src)
  for l in file_list:
    l.path_list = []
    l.make_name()
  return file_list

def make_dst_path(src, dst):
  file_list = make_name(src)
  for l in file_list:
    l.make_dt_path_list()
    l.make_dst_path(dst)
  return file_list

def show(src):
  file_list = rename(src)
  purge_file.PurgeFile.show_list(file_list)

def prev(src, dst):
  if not dst:
    dst = purge_config.src
  file_list = make_dst_path(src, dst)
  purge_file.PurgeFile.show_prev(file_list)
  return file_list

def doit(src, dst):
  if not dst:
    dst = purge_config.src
  file_list = prev(src, dst)
  ready = raw_input('Ready [yes or no]: ')
  if ready=="yes":
    purge_file.PurgeFile.create_symlinks(file_list)
    print("Done")

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print("Usage:")
    print("\t --show\tсписок объектоа")
    print("\t --prev\tотобразить действия (но не делать)")
    print("\t --doit\tотобразить действия и сделать (если скажешь yes)")
    sys.exit(0)
  
  if sys.argv[1] == "--show":
    show(purge_config.path_files_src)
  elif sys.argv[1] == "--prev":
    prev(purge_config.path_files_src, purge_config.src)
  elif sys.argv[1] == "--doit":
    doit(purge_config.path_files_src, purge_config.src)
