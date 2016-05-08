#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import purge_file
import purge_config
import purge_cat
import purge_flt
import purge_pre
import purge_geo
import purge_ini
import purge_fin

def final():
  print(u"Вы всегда можете продолжить с нужного места")
  sys.exit(0)

def count_files_folder(path):
  if not os.path.isdir(path):
    return 0
  result = 0
  names = os.listdir(path)
  for n in names:
    curpath = os.path.join(path,n)
    if  os.path.isdir(curpath):
      result += count_files_folder( curpath )
    elif os.path.isfile(curpath):
      result += 1
  return result

def ini():
  return False



def src():
  count = count_files_folder(purge_config.path_files_src)
  if count == 0:
    return final()
  print("***********************************************")
  print("Этап 1. Сортировка по датам.")
  print("\t{0} файлов из {1}".format(count, purge_config.path_files_src) )
  print("\tв папку {0}".format(purge_config.src))
  print("На этом этапе будут созданны символические ссылки осортированые по годам и месяцам.")
  print("Следующий этап - гео-сортровка")
  ready = raw_input('Готовы? [yes or no]: ')
  if ready=="yes":
    purge_ini.doit(purge_config.path_files_src, purge_config.src)
    return True
  return False

def ready_retry(path):
  ready = raw_input('Готовы? [yes, no or retry]: ')
  while ready=="retry":
    count = count_files_folder(path)
    print("Файлов {0} для текущего этапа".format(count))
    ready = raw_input('Готовы? [yes, no or retry]: ')
  return ready=="yes"
    

def fin():
  count = count_files_folder(purge_config.cat)
  if count == 0:
    return src()
  print("***********************************************")
  print("Этап 7. Финальное перемещение отсортированных файлов.")
  print("\t{0} файлов из {1}".format(count, purge_config.cat) )
  print("\tв папку {0}".format(purge_config.path_files_dst))
  if ready_retry(purge_config.cat):
    purge_fin.doit()
    return True
  return False
  

def geo():
  count = count_files_folder(purge_config.src)
  if count == 0:
    return fin()
  print("***********************************************")
  print("Этап 2. Гео-сортировка.")
  print("\t{0} файлов из {1}".format(count, purge_config.src) )
  print("\tв папку {0}".format(purge_config.geo))
  print("На этом этапе будут созданны символические ссылки осортированые по гео-данным в два этапа:")
  print("\t1. Для файлов с гео-данными будет сделан запрос в google и ссылка будет перемещена в соотвествующую директорию")
  print("\t2. Для файлов без гео-данными, локация будет определена исходя из файлов с гео, с ближайшей датой, для последющей ручной сортировки")
  print("Внимание! Процесс долгий и есть лимиты у googl. Если файлов много, то рекомендую удалить часть ссылок")
  print("Рекомендации по удалению:")
  print("\ta. Если архив за несколько лет, оставьте один год")
  print("\tb. Если файлов за год слишком много, оставте один или несколько месяцев")
  print("\tс. Если вы сменяли локацию на границе месяцев, оставте файлы за оба месяца")
  print("\td. Если вы сменяли локацию на границе года, оставте файлы за декабрь предыдущего и январь следующего")
  print("\te. Если файлов все равно много, оставте файлы для предпологаемой локации изходя из даты создания")
  if ready_retry(purge_config.src):
    purge_geo.doit()
    return True
  return False

def geo_handmade():
  print("1 - ###")
  count_year = count_files_folder(purge_config.geo + "_year_")
  count_month = count_files_folder(purge_config.geo + "_month_")
  count_week = count_files_folder(purge_config.geo + "_week_")
  count_day = count_files_folder(purge_config.geo + "_day_")
  print(purge_config.geo + "_day_")
  count_unk = count_files_folder(purge_config.geo + "_unk_")
  print("2 - ###")
  flag = count_year + count_month + count_day + count_week + count_unk

  print("***********************************************")
  print("Этап 3. Ручная гео-сортировка.")
  
  if flag!=0:
    print("{0} файлов не содержат гео данных, они распределены исходя ".format(flag)
          + "из дат ближайших файлов с гео-данными. Их нужно обработать вручную.")
    print("На этом этапе не рекомендую удалять ссылки, а только перемещать их внутри директории {0}".format(purge_config.geo))
    print("Также можно перемещать ссылки в определенных гео, если определил неправильно.")
    print("\tИсходная папка {0}".format(purge_config.geo))
    if count_day!=0:
      print("\t_day_ - {0} файлов. Это...".format(count_day))
    if count_week!=0:
      print("\t_week_ - {0} файлов. Это...".format(count_week))
    if count_month!=0:
      print("\t_month_ - {0} файлов. Это...".format(count_month))
    if count_year!=0:
      print("\t_year_ - {0} файлов. Это...".format(count_year))
    if count_unk!=0:
      print("\t_unk_ - {0} файлов. Это...".format(count_unk))
    return False
  print("Все файлы отсортированы по гео")
  return True
    

def pre():
  # если нет гео-файлов, то копируем их
  count = count_files_folder(purge_config.geo)
  if count == 0:
    return geo()
  # Пока есть файлы для ручной гео-сортировки
  while not geo_handmade():
    ready = raw_input('Продолжить? [yes or no]: ')
    if ready=="no":
      return False
  print("***********************************************")
  print("Этап 4. Подготовка к категоризации.")
  print("\tкопирование {0} ссылок из папки {1}".format(count, purge_config.geo) )
  print("\tв папку {0}".format(purge_config.pre))
  print("Будут скопированы все ссылки ({0}), для дальнейшего распределения по категориям.".format(count))
  print("(чтобы повторно не дергать maps.google)")
  print("Проверте, что сортировка городам и странам прошла успешно и нажимте yes")

  ready = raw_input('Готовы? [yes or no]: ')
  if ready=="yes":
    purge_pre.doit()
    return True
  return False

def flt():  
  count = count_files_folder(purge_config.pre)
  if count == 0:
    return pre()
  print("***********************************************")
  print("Этап 5. Формирование плоского списка категоризации.")
  print("\tкопирование {0} ссылок из папки {1}".format(count, purge_config.pre) )
  print("\tв папку {0}".format(purge_config.flt))
  print("Для облегчения определения категории, все файлы из {0}".format(purge_config.pre))
  print("будут перенесены в папку плоским списком")
  print("Если файлов слишком много, удалите папки для определенных категорий")
  if ready_retry(purge_config.pre):
    purge_flt.doit()
    return True
  return False

def cat():
  count = count_files_folder(purge_config.flt)
  if count == 0:
    return flt()

  print("***********************************************")
  print("Этап 6. Определение категории.")
  print("\tперемещение {0} ссылок из папки {1} и других папок".format(count, purge_config.flt) )
  print("\tв папку {0}".format(purge_config.cat))
  print("На этом этапе все сыллки будут перемещены в соответсвующую категорию")
  print("Оставте только файлы одной категории и нажмите yes")
  
  if ready_retry(purge_config.flt):
    purge_cat.doit()
    return True
  return False

def main():
  while cat():
    pass
  print(u"Скоируйте файлы в {0} для того, чтобы продолжить сортировку фотографий по регионам, датам и категорям"
        .format(purge_config.path_files_src))


if __name__ == '__main__':
  main()
