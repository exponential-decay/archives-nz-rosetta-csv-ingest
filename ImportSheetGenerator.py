#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema
from datetime import datetime
from droidcsvhandlerclass import *

class ImportSheetGenerator:

   def __init__(self, droidcsv=False, importschema=False, configfile=False):
      self.config = ConfigParser.RawConfigParser()
      self.config.read(configfile)   
      
      self.droidcsv = droidcsv
      self.importschema = importschema
      
      self.pathmask = self.config.get('additional values', 'pathmask')

   def retrieve_year_from_modified_date(self, MODIFIED_DATE):
      year = ""
      if MODIFIED_DATE != '':
         inputdateformat = '%Y-%m-%dT%H:%M:%S'
         year = datetime.strptime(MODIFIED_DATE, inputdateformat).year
      else:
         sys.stderr.write("Date field used to extrave 'year' is blank.")
      return year

   def add_csv_value(self, value):
      field = ''
      if type(value) is int:              #TODO: probably a better way to do this (type-agnostic)
         field = '"' + str(value) + '"'
      else:
         field = '"' + value.encode('utf-8') + '"'
      return field

   def get_path(self, path):
      return path.replace(self.pathmask, "")

   def get_title(self, title):
      return title.rsplit('.', 1)[0].rstrip()  #split once at full-stop (assumptuon 'ext' follows)

   def maptoimportschema(self):
      
      if self.importschema != False:
         f = open(self.importschema, 'rb')
         
         importschemajson = f.read()

         importschema = JsonTableSchema.JSONTableSchema(importschemajson)
         importschemadict = importschema.as_dict()
         importschemaheader = importschema.as_csv_header()

         importcsv = importschemaheader + "\n"

         for filerow in self.droidlist:
            
            # Extract year from file modified date for open and closed year
            yearopenclosed = self.retrieve_year_from_modified_date(filerow['LAST_MODIFIED'])
         
            for column in importschemadict['fields']:
               entry = False
               if self.config.has_option('droid mapping', column['name']):
                  droidfield = self.config.get('droid mapping', column['name'])
                  fieldtext = ""
                  if droidfield == 'FILE_PATH':
                     dir = os.path.dirname(filerow['FILE_PATH'])
                     fieldtext = self.get_path(dir)
                  if droidfield == 'NAME':
                     fieldtext = self.get_title(filerow['NAME'])
                  if droidfield == 'MD5_HASH':
                     fieldtext = filerow['MD5_HASH']
                  if droidfield == 'LAST_MODIFIED':
                     if self.config.has_option('additional values', 'descriptiontext'):
                        fieldtext = self.config.get('additional values', 'descriptiontext') + " " + str(filerow[droidfield])
                  
                  importcsv = importcsv + self.add_csv_value(fieldtext)
                  entry = True
                  
               if self.config.has_option('static values', column['name']):
                  importcsv = importcsv + self.add_csv_value(self.config.get('static values', column['name']))
                  entry = True
               
               if column['name'] == 'Open Year' or column['name'] == 'Close Year':
                  importcsv = importcsv + self.add_csv_value(yearopenclosed)
                  entry = True
               
               if entry == False:
                  importcsv = importcsv + self.add_csv_value("")
                  
               importcsv = importcsv + ","

            importcsv = importcsv.rstrip(',') + "\n"
               
         sys.stdout.write(importcsv)

   def readDROIDCSV(self):
      if self.droidcsv != False:
         droidcsvhandler = droidCSVHandler()
         droidlist = droidcsvhandler.readDROIDCSV(self.droidcsv)     
         droidlist = droidcsvhandler.removefolders(droidlist)
         return droidcsvhandler.removecontainercontents(droidlist)   

   def droid2archwayimport(self):
      if self.droidcsv != False and self.importschema != False:
         self.droidlist = self.readDROIDCSV()
         self.maptoimportschema()
