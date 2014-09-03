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

class ImportOverviewGenerator:

   def __init__(self):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('import-value-mapping.cfg')   

      self.droidcsv = False

   def __init__(self, droidcsv=False):
      self.config = ConfigParser.RawConfigParser()
      self.config.read('import-value-mapping.cfg')   
      
      self.droidcsv = droidcsv

   #TODO: Quick and dirty... rework so it's a little more refined
   def outputOverview(self):
      uniquefolderlist = set(self.droidlist)
      folderlist = []
      
      #TODO: Check for existence of key...?
      pathmask = self.config.get('additional values', 'pathmask')
 
      for folder in uniquefolderlist:
         foldertext = str(folder).replace(pathmask, "")
         #replace doesn't seem to capture all options
         if foldertext not in pathmask:     # foldertext subset of pathmask
            folderlist.append(foldertext)
      
      sys.stdout.write('"Archway Listing Template"' + '\n')
      sys.stdout.write('"Access Restrictions:"' + '\n')
      sys.stdout.write('"Agency Comment:"' + '\n\n')

      sys.stdout.write('"Agency","Accession","Series","Sub Series"' + '\n')
      
      agency = self.config.get('static values', 'Agency')
      series = self.config.get('static values', 'Actual Series')
      accession = self.config.get('static values', 'Accession No.')

      sys.stdout.write('"' + agency + '",' + '"' + accession + '",' + '"' + series + '",' + '"' + folderlist[0] + '"' + '\n')
      
      for folder in folderlist[1:]:
         sys.stdout.write('"","","","' + folder + '"' + '\n') 
      
   def readDROIDCSV(self):
      if self.droidcsv != False:
         droidcsvhandler = droidCSVHandler()
         droidlist = droidcsvhandler.readDROIDCSV(self.droidcsv)     
         return droidcsvhandler.retrievefolderlist(droidlist)

   def createOverviewSheet(self):
      if self.droidcsv != False:
         self.droidlist = self.readDROIDCSV()
         self.outputOverview()

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

   def grabdroidvalue(self, md5, field, rosettafield, pathmask):
      #TODO: Potentially index droidlist by MD5 or SHA-256 in future...
      returnfield = ""      
      for drow in self.droidlist:
         if drow['MD5_HASH'] == md5:
            droidfield = drow[rosettafield]
            
            if field == 'File Location':
               returnfield = os.path.dirname(droidfield).replace(pathmask, '').replace('\\','/') + '/'
            if field == 'File Original Path':
               returnfield = droidfield.replace(pathmask, '').replace('\\','/')
            if field == 'File Name':
               returnfield = droidfield
      return returnfield
     
   def csvstringoutput(self, csvlist):
      #String output...
      csvrows = self.rosettacsvheader

      #TODO: Understand how to get this in rosettacsvsectionclass
      #NOTE: Possibly put all basic RosettaCSV stuff in rosettacsvsectionclass?
      #Static ROW in CSV Ingest Sheet
      SIPROW = ['"",'] * len(self.rosettacsvdict)
      SIPROW[0] = '"SIP",'
      SIPROW[1] = '"CSV Load",'
     
      csvrows = csvrows + ''.join(SIPROW).rstrip(',') + '\n'
      
      for sectionrows in csvlist:
         rowdata = ""
         for sectionrow in sectionrows:
            for fielddata in sectionrow:
               rowdata = rowdata + fielddata + ','
            rowdata = rowdata.rstrip(',') + '\n'
         csvrows = csvrows + rowdata
      sys.stdout.write(csvrows)

   def createrosettacsv(self):
      
      CSVINDEXSTARTPOS = 2
      csvindex = CSVINDEXSTARTPOS
      
      fields = []

      for item in self.exportlist:
         itemrow = []
         
         for sections in self.rosettasections:
            sectionrow = ['""'] * len(self.rosettacsvdict)
            sectionrow[0] = self.add_csv_value(sections.keys()[0])            
            for field in sections[sections.keys()[0]]:
               if field == self.rosettacsvdict[csvindex]['name']:
                  if self.config.has_option('rosetta mapping', field):
                     rosettafield = self.config.get('rosetta mapping', field)
                     addvalue = item[rosettafield]
                     if field == 'Access':
                        if self.config.has_option('access values', addvalue):
                           addvalue = self.config.get('access values', addvalue)
                     sectionrow[csvindex] = self.add_csv_value(addvalue)                     
                  elif self.config.has_option('static values', field):
                     rosettafield = self.config.get('static values', field)
                     sectionrow[csvindex] = self.add_csv_value(rosettafield)
                  elif self.config.has_option('droid mapping', field):          
                     rosettafield = self.config.get('droid mapping', field)
                     
                     #get pathmask for location values...
                     pathmask = ""
                     if self.config.has_option('path values', 'pathmask'):
                        pathmask = self.config.get('path values', 'pathmask')
     
                     sectionrow[csvindex] = self.add_csv_value(self.grabdroidvalue(item['Missing Comment'], field, rosettafield, pathmask))
                  else:
                     sectionrow[csvindex] = self.add_csv_value(field)
               else:
                  sys.exit(0)
               csvindex+=1
               
            itemrow.append(sectionrow)
         fields.append(itemrow)
         csvindex=CSVINDEXSTARTPOS
      
      self.csvstringoutput(fields)

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

def createImportOverview(droidcsv):
   createoverview = ImportOverviewGenerator(droidcsv)
   createoverview.createOverviewSheet()

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
   elif args.csv:
      createImportOverview(args.csv)
   else:
      parser.print_help()
      sys.exit(1)

if __name__ == "__main__":
   main()
