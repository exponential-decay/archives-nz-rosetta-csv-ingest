#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema
import ConfigParser
import argparse
from droidcsvhandlerclass import *
from rosettacsvsectionsclass import RosettaCSVSections

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

class RosettaCSVGenerator:

   def __init__(self):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('rosetta-csv-mapping.cfg')   

      self.droidcsv = False
      self.exportcsv = False
      self.rosettaschema = False

   def __init__(self, droidcsv=False, exportsheet=False, rosettaschema=False):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('rosetta-csv-mapping.cfg')   
      
      self.droidcsv = droidcsv
      self.exportsheet = exportsheet
      
      #NOTE: A bit of a hack, compare with import schema work and refactor
      self.rosettaschema = rosettaschema
      self.readRosettaSchema()
      
      #Grab Rosetta Sections
      rs = RosettaCSVSections()
      self.rosettasections = rs.sections

   def add_csv_value(self, value):
      field = ''
      if type(value) is int:              #TODO: probably a better way to do this (type-agnostic)
         field = '"' + str(value) + '"'
      else:
         field = '"' + value.encode('utf-8') + '"'
      return field

   def readRosettaSchema(self):
      f = open(self.rosettaschema, 'rb')
      importschemajson = f.read()
      importschema = JsonTableSchema.JSONTableSchema(importschemajson)
      
      importschemadict = importschema.as_dict()
      importschemaheader = importschema.as_csv_header()

      self.rosettacsvheader = importschemaheader + "\n"  #TODO: Add newline in JSON Handler class? 
      self.rosettacsvdict = importschemadict['fields']
      f.close()

   def createcolumns(self, columno):
      columns = ''
      for column in range(columno):
         columns = columns + '"",'
      return columns

   def createrosettacsv(self):
   
      CSVINDEXSTARTPOS = 2
      csvindex = CSVINDEXSTARTPOS
      rowlen = len(self.rosettacsvdict)
      
      fields = []

      for item in self.exportlist:
         itemrow = []
         for sections in self.rosettasections:
            sectionrow = [None] * rowlen
            sectionrow[0] = self.add_csv_value(sections.keys()[0])
            
            for field in sections[sections.keys()[0]]:
               
               if field == self.rosettacsvdict[csvindex]['name']:
                  #if self.config.has_option('rosetta mapping', field):
                  #   print field
                  if self.config.has_option('static values', field):
                     rosettafield = self.config.get('static values', field)
                     sectionrow[csvindex] = self.add_csv_value(rosettafield)
                  else:
                     sectionrow[csvindex] = self.add_csv_value(field)
               else:
                  sys.exit(0)
               csvindex+=1

            itemrow.append(sectionrow)
         
         fields.append(itemrow)
         csvindex=CSVINDEXSTARTPOS
      
      
      csvrows = self.rosettacsvheader
      
      for aggregate in fields:
         rowdata = ""
         for sect in aggregate:
            for val in sect:
               if val == None:
                  rowdata = rowdata + '""'
               else:
                  rowdata = rowdata + val
               rowdata = rowdata + ','
            rowdata = rowdata.rstrip(',') + '\n'
         csvrows = csvrows + rowdata
      print csvrows
      
      #for item in self.exportlist:
      #   for column in self.rosettacsvdict:
      #      print column
            
      # for item in record
      # for column in roestta csv

      #Combine DROID cells and Export cells here... 
      #File Original Path: E1/Speeches/DSCN1872.JPG	 
      #File Name: DSCN1872.JPG

   def readExportCSV(self):
      if self.exportsheet != False:
         csvhandler = genericCSVHandler()
         exportlist = csvhandler.csvaslist(self.exportsheet)
         return exportlist
   
   def readDROIDCSV(self):
      if self.droidcsv != False:
         droidcsvhandler = droidCSVHandler()
         droidlist = droidcsvhandler.readDROIDCSV(self.droidcsv)
         droidlist = droidcsvhandler.removefolders(droidlist)
         return droidcsvhandler.removecontainercontents(droidlist)        
      
   def export2rosettacsv(self):
      if self.droidcsv != False and self.exportsheet != False:
         self.droidlist = self.readDROIDCSV()
         self.exportlist = self.readExportCSV()
         #self.readRosettaSchema()  #NOTE: Moved to constructor... TODO: Refactor
         self.createrosettacsv()

def importsheetDROIDmapping(droidcsv, importschema):
   importgenerator = ImportSheetGenerator(droidcsv, importschema)
   importgenerator.droid2archwayimport()

def exportsheetRosettamapping(droidcsv, exportsheet, rosettaschema):
   csvgen = RosettaCSVGenerator(droidcsv, exportsheet, rosettaschema)
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
   parser.add_argument('--ros', help='Rosetta CSV validation schema', default=False, required=False)

   if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

   #	Parse arguments into namespace object to reference later in the script
   global args
   args = parser.parse_args()
   
   #TODO: Additional help text to describe two discrete sets of options
   
   if args.csv and args.imp:
      importsheetDROIDmapping(args.csv, args.imp)
   elif args.csv and args.exp and args.ros:
      exportsheetRosettamapping(args.csv, args.exp, args.ros)
   else:
      parser.print_help()
      sys.exit(1)

if __name__ == "__main__":
   main()
