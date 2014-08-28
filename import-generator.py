#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema
import ConfigParser
import argparse
from droidcsvhandlerclass import droidCSVHandler

class ImportSheetGenerator:

   def __init__(self):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('import-value-mapping.cfg')   

      self.droidcsv = False
      self.importschema = False

   def __init__(self, droidcsv=False, importschema=False):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('import-value-mapping.cfg')   
      
      self.droidcsv = droidcsv
      self.importschema = importschema

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
                     fieldtext = dir.replace(self.config.get('additional values', 'pathmask'), "")
                  if droidfield == 'NAME':
                     fieldtext = filerow['NAME'].rsplit('.', 1)[0]  #split once at full-stop (assumptuon 'ext' follows)
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
            importcsv = importcsv + "\n"
               
         sys.stdout.write(importcsv)

   def readDROIDCSV(self):
      if self.droidcsv != False:
         droidcsvhandler = droidCSVHandler()
         return droidcsvhandler.readDROIDCSV(self.droidcsv)        

   def droid2archwayimport(self):
      if self.droidcsv != False and self.importschema != False:
         droidlist = self.readDROIDCSV()
         if droidlist:
            droidcsvhandler = droidCSVHandler()
            droidlist = droidcsvhandler.removefolders(droidlist)
            self.droidlist = droidcsvhandler.removecontainercontents(droidlist)
         self.maptoimportschema()

class RosettaCSVGenerator:

   def __init__(self):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('rosetta-csv-mapping.cfg')   

      self.droidcsv = False
      self.exportcsv = False

   def __init__(self, droidcsv=False, exportsheet=False):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('import-value-mapping.cfg')   
      
      self.droidcsv = droidcsv
      self.exportsheet = exportsheet

   def readExportCSV(self):
      if self.exportsheet != False:
         print "exportcsv"

   def readDROIDCSV(self):
      if self.droidcsv != False:
         csvhandler = genericCSVHandler()
         return csvhandler.csvaslist(self.droidcsv)     

   def export2rosettacsv(self):
      print "ok"
      if self.droidcsv != False and self.exportsheet != False:
         droidlist = self.readDROIDCSV()
         print droidlist
         #droidlist = self.removefolders(droidlist)
         #self.droidlist = self.removecontainercontents(droidlist)
         #self.maptoimportschema()

  #Combine DROID cells and Export cells here... 
  #File Original Path: E1/Speeches/DSCN1872.JPG	 
  #File Name: DSCN1872.JPG

def importsheetDROIDmapping(droidcsv, importschema):
   importgenerator = ImportSheetGenerator(droidcsv, importschema)
   importgenerator.droid2archwayimport()

def exportsheetRosettamapping(droidcsv, exportsheet):
   csvgen = RosettaCSVGenerator(droidcsv, exportsheet)
   csvgen.export2rosettacsv()

def main():

   #	Usage: 	--csv [droid report]
   #	Handle command line arguments for the script
   parser = argparse.ArgumentParser(description='Generate Archway Import Sheet and Rosetta Ingest CSV from DROID CSV Reports.')

   #TODO: Consider optional and mandatory elements... behaviour might change depending on output...
   #other options droid csv and rosetta schema
   #NOTE: class on its own might be used to create a blank import csv with just static options
   parser.add_argument('--csv', help='Single DROID CSV to read.', default=False, required=False)
   parser.add_argument('--imp', help='Archway import schema to use.', default=False, required=False)
   parser.add_argument('--exp', help='Archway export sheet to map to Rosetta ingest CSV', default=False, required=False)

   if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

   #	Parse arguments into namespace object to reference later in the script
   global args
   args = parser.parse_args()
   
   if args.csv and args.imp:
      importsheetDROIDmapping(args.csv, args.imp)
   if args.csv and args.exp:
      exportsheetRosettamapping(args.csv, args.exp)
   else:
      sys.exit(1)

if __name__ == "__main__":
   main()
