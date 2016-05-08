#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import purge_file
import purge_config



# Копирование из geo в pre
# НЕ ДКЛАТЬ если pre не пуста
# TODO: сделать проверку, что нет _day_ _unk_ и прочее

def show():
  file_list = purge_file.PurgeFile.make_list(purge_config.geo)
  purge_file.PurgeFile.show_list(file_list)

def prev():
  file_list = purge_file.PurgeFile.make_list(purge_config.geo)
  for f in file_list:
    f.make_dst_path(purge_config.pre)
    #f.create_link()
  purge_file.PurgeFile.show_prev(file_list)
  return file_list

def doit():
  file_list = prev()
  ready = raw_input('Ready [yes or no]: ')
  if ready=="yes":
    purge_file.PurgeFile.copy_files(file_list)
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
