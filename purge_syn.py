#!/usr/bin/python
# -*- coding: utf-8 -*-

# копирует ссылки из src кторых нет в cat
# TODO: УБРАТЬ!! в cat мы удаляем все ссылки из других дерикторий

import sys
import purge_file
import purge_config

def load_src():
  file_list = purge_file.PurgeFile.make_list(purge_config.geo)
  return file_list

def load_cat():
  file_list = purge_file.PurgeFile.make_list(purge_config.cat)
  if not file_list:
    return []
  return file_list

def load_pre():
  src_list = load_src()
  cat_list = load_cat()
  result = []
  for s in src_list:
    found = False
    for c in cat_list:
      cf = c.filename
      sf = s.filename
      if cf == sf:
        found = True
        break
    if not found:
      result += [s]
  return result

def make():
  file_list = load_pre()
  for f in file_list:
    f.make_dst_path(purge_config.pre)
  return file_list
  
def show():
  file_list = load_pre()
  purge_file.PurgeFile.show_list(file_list)

def prev():
  file_list = make()
  purge_file.PurgeFile.show_prev(file_list)
  return file_list

def doit():
  file_list = prev()
  ready = raw_input('Ready [yes or no]: ')
  if ready=="yes":
    purge_file.PurgeFile.copy_files(file_list)
    print("Done")

if __name__ == '__main__':
  print(u"Устарело")
  sys.exit(0)

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
