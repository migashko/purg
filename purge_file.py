#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import math
import shutil
import datetime
import purge_exif
import purge_config


class PurgeFile:
  
  # full_path полный путь к файлу
  # prefix_len длина префикса строки включая /
  def __init__(self, full_path, prefix_len = 0 ):
    item_list = PurgeFile.split_(full_path[prefix_len:])
    self.filename = item_list[-1]
    self.dt = None
    self.src_path = full_path
    self.dst_path = None
    self.src_prefix = full_path[:prefix_len]
    self.dst_prefix = None
    if len(item_list) > 2:
      self.path_list = item_list[:-1]
    else:
      self.path_list = []
    self.geo_list = []
    self.basename = os.path.splitext(self.filename)[0]
    self.extname = os.path.splitext(self.filename)[1]
    self.dub_counter = 0
 
    pass    
  
  #def __str__(self):
  #  print("__str__")
  #  return u"Source: {0}\nDestination: {1}\nPrefix: {2}\nList: {3}\nName:{4}\nExtention: {5}".format(self.src_path, self.dst_path, self.src_prefix, self.path_list, self.basename, self.extname)

  def __unicode__(self):
    return u"Source: {0}\nDestination: {1}\nPrefix: {2}\nList: {3}\nName:{4}\nExtention: {5}".format(self.src_path, self.dst_path, self.src_prefix, self.path_list, self.basename, self.extname)
  
  # Формирует новае имя файла (self.basename) [PREFIX][DATETIME][EXT] из:
  #   1. exif data
  #   2. Время создания файла
  # С префиксом IMG_, VID_ или UNK_:
  #   1. Есть exif data: это IMG_
  #   2. Расширение в списке purge_config.image: это IMG_
  #   3. Расширение в списке purge_config.video: это VID_
  #   4. Для остальных: это UNK_
  def make_name(self):
    prefix = self._file_prefix();
    suffix = self._file_suffix();
    self.basename = prefix + suffix
    
  def make_dt_path_list(self):
    dt = self.dt
    self.path_list = [unicode(dt.year), purge_config.months[dt.month-1] ]

  def make_geo_list(self):
    self.geo_list = []
    geoitems = purge_exif.get_geo_items(self.src_path)
    
    if geoitems!=None:
      # Если есть гео, то формируем список длиной, определенной в конфиге
      self.geo_list = [None]*len(purge_config.geo_types["items"])
      
      # В root определены типы address_components в порядке приоритета
      for root in purge_config.geo_types["root"]:
        # перебераем все элементы, что вернул google
        for geoitem in geoitems:
          # если нужного типа нет, то продолжаем
          if root not in geoitem["types"]:
            continue
          # перебераем все items, котрые определяют уровень вложенности
          for i in range( len(purge_config.geo_types["items"]) ):
            # если для данного уровня уже определили, то игнор
            if self.geo_list[i]!=None:
              continue
            # допустимые типы для элемента address_components в порядке приоритета
            types = purge_config.geo_types["items"][i]
            # перебираем допустимые типы
            for e in types:
              # перебираем все элементы address_components 
              for addritem in geoitem["address_components"]:
                # если нужного типа нет, то игнор
                if e not in addritem["types"]:
                  continue
                # если еще не инициализирован для уровня вложености i
                if self.geo_list[i]==None:
                  self.geo_list[i]=addritem["long_name"]
                  
      # то, что не определили
      for i in range( len(self.geo_list) ):
        if self.geo_list[i]==None:
          self.geo_list[i]="unk"
    
    '''
    self.geo_list = []
    geoitems = purge_exif.get_geo_items(self.src_path)
    if geoitems:
      for root in purge_config.geo_types["root"]:
        for geoitem in geoitems:
          if root not in geoitem["types"]:
            continue
          for item in purge_config.geo_types["items"]:
            for elem in item:
              flag = False
              for addritem in geoitem["address_components"]:
                if elem not in addritem["types"]:
                  continue
                self.geo_list += [addritem["long_name"]]
                flag = True
                break
              if flag:
                break
          break
    '''
    
  # формирует имя выходного файлв
  def make_dst_path(self, dst = None):
    if not dst:
      dst = self.dst_prefix
    else:
      self.dst_prefix = dst
    dstlist = [dst] + self.geo_list + self.path_list + [self.basename]
    self.dst_path = os.path.join(*dstlist) + self.extname
    
  def create_link(self):
    
    if not self.src_path or not self.dst_path:
      raise Exception("invalid path")
    
    while True:
      try:
        os.symlink(self.src_path, self.dst_path)
        print(u"OK: {0}".format(self.dst_path))
        break
      except OSError as e:
        if e.errno == 2:
          print ("сделать директорию")
          os.makedirs(os.path.dirname(self.dst_path))
          continue
        elif e.errno != 2:
          print(u"FAIL: {0}".format(self.dst_path))
          self.dub_counter += 1
          self.make_name()
          self.make_dst_path()
      except:
        raise
      
  def move(self):

    if not self.src_path or not self.dst_path:
      raise Exception("invalid path")

    while os.path.isfile(self.dst_path):
      self.dub_counter += 1
      self.make_name()
      self.make_dst_path()
      
    while True:
      try:
        os.rename(self.src_path, self.dst_path)
        print(u"OK: {0}".format(self.dst_path))
        break
      except OSError as e:
        if e.errno == 2:
          print ("сделать директорию")
          os.makedirs(os.path.dirname(self.dst_path))
          continue
        elif e.errno != 2:
          print(u"FAIL: {0}".format(self.dst_path))
          self.dub_counter += 1
          self.make_name()
          self.make_dst_path()
      except:
        raise

  def delete(self):
    print(u" UNLINK {0}".format(self.src_path) )
    os.unlink(self.src_path)

  def copy(self):

    if not self.src_path or not self.dst_path:
      raise Exception("invalid path")

    while os.path.isfile(self.dst_path):
      self.dub_counter += 1
      self.make_name()
      self.make_dst_path()
      
    while True:
      try:
        if os.path.islink(self.src_path):
          linkto = os.readlink(self.src_path)
          os.symlink(linkto, self.dst_path)
        else:
          shutil.copy(self.src_path, self.dst_path)

        print(u"OK: {0}".format(self.dst_path))
        break
      except OSError as e:
        if e.errno == 2:
          print ("сделать директорию")
          os.makedirs(os.path.dirname(self.dst_path))
          continue
        elif e.errno != 2:
          print(u"FAIL: {0}".format(self.dst_path))
          self.dub_counter += 1
          self.make_name()
          self.make_dst_path()
      except:
        raise

# ---------------------------------------------

  def move_file(self):
    # переместить файл из ссылки и удалить ссылку
    if not self.src_path or not self.dst_path:
      raise Exception("invalid path")
    while os.path.isfile(self.dst_path):
      self.dub_counter += 1
      self.make_name()
      self.make_dst_path()
      
    while True:
      try:
        if os.path.islink(self.src_path):
          linkto = os.readlink(self.src_path)
          os.rename(linkto, self.dst_path)
          os.unlink(self.src_path)
        else:
          shutil.move(self.src_path, self.dst_path)

        print(u"OK: {0}".format(self.dst_path))
        break
      except OSError as e:
        if e.errno == 2:
          print ("сделать директорию")
          os.makedirs(os.path.dirname(self.dst_path))
          continue
        elif e.errno != 2:
          print(u"FAIL: {0}".format(self.dst_path))
          self.dub_counter += 1
          self.make_name()
          self.make_dst_path()
      except:
        raise



      
  def get_dt(self):
    if not self.dt:
      self.dt = self._get_datetime()
    return self.dt
  
  def get_dtu(self):
    return int(self.get_dt().strftime("%s"))
  
# private
  
  def _get_datetime(self):
    exif = purge_exif.load_exif_data(self.src_path)
    if exif:
      dt = purge_exif.get_datetime(exif)
      if dt != None:
        return dt
    stat = os.stat(self.src_path)
    mtime = stat.st_mtime
    dt = datetime.datetime.fromtimestamp(mtime)
    return dt

  def _file_suffix(self):
    dt = self.get_dt()
    return "{0:04}{1:02}{2:02}_{3:02}{4:02}{5:02}_{6:03}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, self.dub_counter)

  def _file_prefix(self):
    exif = purge_exif.load_exif_data(self.src_path)
    if exif:
      return purge_config.image[0]
    ext = self.extname.lower()
    if ext in purge_config.image[1]:
      return purge_config.image[0]
    if ext in purge_config.video[1]:
      return purge_config.video[0]
    return purge_config.unk[0]
      
# static private

  # формирует из пути список [folder][folder][folder][filename]
  @staticmethod
  def split_(path):
    folders=[]
    while 1:
      path,folder=os.path.split(path)

      if folder!="":
        folders.append(folder)
      else:
        if path!="":
          folders.append(path)
        break
    folders.reverse()
    return folders
  
  @staticmethod
  def create_(full_path, prefix_len = 0):
    return PurgeFile(full_path, prefix_len)
  
  # Формирует рекурсивно плоский спискок PurgeFile
  # @params path путь к директории (только)
  @staticmethod
  def make_from_dir_(path, prefix_len = 0):
    result = []
    if prefix_len==0 :
      prefix_len = len(path)
      
    names = os.listdir(path)
    for n in names:
      curpath = os.path.join(path,n)
      if  os.path.isdir(curpath):
        result += PurgeFile.make_list(curpath, prefix_len)
      elif os.path.isfile(curpath):
        result += [ PurgeFile.create_(curpath, prefix_len) ]
    return result

# static public

  # Формирует рекурсивно плоский спискок PurgeFile
  # @params path путь к директории или файлу
  @staticmethod
  def make_list(path, prefix_len = 0):
    if  os.path.isdir(path):
      return PurgeFile.make_from_dir_(path, prefix_len)
    elif os.path.isfile(path):
      return [PurgeFile.create_(path, prefix_len) ]
  
  @staticmethod
  def create_symlinks(file_list):
    for f in file_list:
      f.create_link()

  @staticmethod
  def move_files(file_list):
    for f in file_list:
      f.move_file()

  @staticmethod
  def move_symlinks(file_list):
    for f in file_list:
      f.move()

  @staticmethod
  def copy_files(file_list):
    for f in file_list:
      f.copy()

  @staticmethod
  def delete_files(file_list):
    for f in file_list:
      f.delete()


  @staticmethod
  def smart_geo(file_list):
    with_geo = []
    without_geo = []
    for f in file_list:
      if len(f.geo_list) > 0:
        with_geo+=[f]
      else:
        without_geo+=[f]
        
    for wog in without_geo:
      minspan = 3600 * 24 * 365 * 100
      near = None
      for wg in with_geo:
        span = abs(wg.get_dtu() - wog.get_dtu())
        if span < minspan:
          near = wg 
          minspan = span
      if near:
        lst = near.geo_list
      else:
        lst = []
      if minspan == 3600 * 24 * 365 * 100:
        wog.geo_list = ["_unk_"] +  lst 
      elif minspan > 3600 * 24 * 365:
        wog.geo_list = ["_year_"] +  lst 
      elif minspan > 3600 * 24 * 30:
        wog.geo_list = ["_month_"] +  lst 
      elif minspan > 3600 * 24 * 7:
        wog.geo_list = ["_week_"] +  lst 
      elif minspan > 3600 * 24:
        wog.geo_list = ["_day_"] +  lst 
      else:
        wog.geo_list = lst

  @staticmethod
  def smart_geoX(file_list):
    ready1 = False
    while not ready1:
      ready1 = True
      for i1 in file_list:
        if len(i1.geo_list) > 0:
          continue
        #curspan = 3600 * 24 * 2
        minspan = 3600 * 24 * 365 * 100
        ready2 = False
        lst = []
        for i2 in file_list:
          if i1.basename == i2.basename:
            continue
          if len(i2.geo_list) == 0:
            continue
          span = abs(i2.get_dtu() - i1.get_dtu())
          if span < minspan:
            ready2 = True
            lst = i2.geo_list
            minspan = span
            if minspan == 3600 * 24 * 365 * 100:
              i1.geo_list = ["_unk_"] +  lst 
            elif minspan > 3600 * 24 * 365:
              i1.geo_list = ["_year_"] +  lst 
            elif minspan > 3600 * 24 * 30:
              i1.geo_list = ["_month_"] +  lst 
            elif minspan > 3600 * 24 * 7:
              i1.geo_list = ["_week_"] +  lst 
            elif minspan > 3600 * 24:
              i1.geo_list = ["_day_"] +  lst 
            else:
              i1.geo_list = lst
            break

          #if span < curspan:
          #  curspan = span
        if ready2:
          #if minspan > curspan:
            # Если не детектровали с точностью до двух суток
          ready1 = False
          break
        
          
            


    
# static show 

  @staticmethod
  def show_list(file_list):
    print(file_list)
    for f in file_list:
      print(u"{0}".format(f))
      print("----------------------")
    

  @staticmethod
  def show_prev(file_list):
    for f in file_list:
      print(u"'{0}' - > '{1}'".format(f.src_path, f.dst_path))
 
  
if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit(0)
  path=sys.argv[1]
  print (path)
  file_list = PurgeFile.make_list(path)
  PurgeFile.show_list(file_list)
  
#  for f in file_list:
#    print f
#    print("----------------------")
  
