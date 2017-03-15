#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(r'JsonTableSchema/')
import ConfigParser
import JsonTableSchema
from ProvenanceCSVHandlerClass import *
from droidcsvhandlerclass import *
from rosettacsvsectionsclass import RosettaCSVSections
from ImportSheetGenerator import ImportSheetGenerator

class RosettaCSVGenerator:

   def __init__(self, droidcsv=False, exportsheet=False, rosettaschema=False, configfile=False, provenance=False):
   
      if configfile is not False:
         self.config = ConfigParser.RawConfigParser()
         self.config.read(configfile)   
         
         self.droidcsv = droidcsv
         self.exportsheet = exportsheet
         
         #NOTE: A bit of a hack, compare with import schema work and refactor
         self.rosettaschema = rosettaschema
         self.readRosettaSchema()
         
         #Grab Rosetta Sections
         rs = RosettaCSVSections(configfile)
         self.rosettasections = rs.sections
         
         #set provenance flag and file
         self.prov = False
         if provenance is True:
            self.prov = True
            self.provfile = 'prov.notes'
            if self.config.has_option('provenance', 'file'):
               #Overwrite default, if manually specified...
               self.provfile = self.config.get('provenance', 'file')
          
         self.pathmask = self.__setpathmask__()
      else:
         sys.exit('No config file')
         
      #Get some functions from ImportGenerator
      self.impgen = ImportSheetGenerator()
      
      #List duplicate items to check...
      self.duplicateitemsaddedset = set()

   def add_csv_value(self, value):
      field = ''
      if type(value) is int:              #TODO: probably a better way to do this (type-agnostic)
         field = '"' + str(value).replace('\r', '').replace('\n', '')
      else:
         field = '"' + value.encode('utf-8').replace('\r', '').replace('\n', '') + '"'
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

   def normalize_spaces(self, filename):
      if filename.find("  ") is not -1:
         filename = filename.replace("  ", " ")
         return self.normalize_spaces(filename)
      return filename

   def compare_filenames_as_titles(self, droidrow, listcontroltitle):

      comparison = False

      # DROID NAME column used to generate title in Import Sheet
      droid_filename_title = self.impgen.get_title(droidrow['NAME'])

      # normalize spaces and compare (for when list control adopts original title)
      if self.normalize_spaces(droid_filename_title) == self.normalize_spaces(listcontroltitle):
         comparison = True
      else:
         #Fail but don't exit desirable(?) so as to see all errors at once
         sys.stderr.write("Filename comparison has failed. Check list control: " + listcontroltitle.encode('utf-8') + " vs. DROID export: " + droid_filename_title.encode('utf-8') + "\n")
      
      return comparison

   #NOTE: itemtitle is title from Archway List Control...
   def grabdroidvalue(self, md5, itemtitle, subseries, field, rosettafield, pathmask):
   
      #TODO: Potentially index droidlist by MD5 or SHA-256 in future...
      returnfield = ""      
      for drow in self.droidlist:
         addtorow = False

         checksumfromdroid = ''
         if 'MD5_HASH' in drow:
            checksumfromdroid = drow['MD5_HASH']
         elif 'SHA1_HASH' in drow:
            checksumfromdroid = drow['SHA1_HASH']
         else:
            sys.stderr.write("No hash available to use in DROID export.\n")
            os.exit(1)         
         
         if checksumfromdroid == md5:
            if self.compare_filenames_as_titles(drow, itemtitle):

               #Performance, only do more work, if we have to care about it...
               if checksumfromdroid in self.duplicates:
               
                  #recreate subseries so that we can do comparison for path alignment... 
                  subseriesfromdroid = os.path.dirname(drow['FILE_PATH']).replace(self.subseriesmask, '')
               
                  if subseries == subseriesfromdroid:
                     addtorow = True
                     self.duplicateitemsaddedset.add(subseries + "\\" + itemtitle + " checksum: " + checksumfromdroid)
               else:
                  addtorow = True
                 
         if addtorow == True:
            droidfield = drow[rosettafield]
            if field == 'File Location':
               returnfield = os.path.dirname(droidfield).replace(pathmask, '').replace('\\','/') + '/'
            elif field == 'File Original Path':
               returnfield = os.path.dirname(droidfield).replace(pathmask, '').replace('\\','/') + "/"
            else:
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
      
      #SIP Title... 
      if self.config.has_option('rosetta mapping', 'SIP Title'):
         SIPROW[1] = '"' + self.config.get('rosetta mapping', 'SIP Title') + '",'
      else:
         SIPROW[1] = '"CSV Load",'
     
      csvrows = csvrows + ''.join(SIPROW).rstrip(',') + '\n'
      
      #write utf-8 BOM
      # NOTE: Don't write UTF-8 BOM... Rosetta doesn't like this. 
      #sys.stdout.write(u'\uFEFF'.encode('utf-8'))
      
      for sectionrows in csvlist:
         rowdata = ""
         for sectionrow in sectionrows:
            for fielddata in sectionrow:
               rowdata = rowdata + fielddata + ','
            rowdata = rowdata.rstrip(',') + '\n'
         csvrows = csvrows + rowdata
         
      #this is the best i can think of because ExLibris have named two fields with the same
      #title in CSV which doesn't help us when we're trying to use unique names for populating rows
      #replaces SIP Title with Title (DC)
      csvrows = csvrows.replace('"Object Type","SIP Title"','"Object Type","Title (DC)"')         
         
      sys.stdout.write(csvrows)
      
      for dupe in self.duplicateitemsaddedset:
         sys.stderr.write("Duplicates to monitor: " + dupe + "\n")

   def handleprovenanceexceptions(self, PROVENANCE_FIELD, sectionrow, field, csvindex, rnumber):
      ignorefield = False
      if self.prov == True:
         for p in self.provlist:
            if p['RECORDNUMBER'] == rnumber:
               #These values overwrite the defaults from DROID list...
               #Double-check comparison to ensure we're inputting the right values...
               if (PROVENANCE_FIELD == 'CHECKSUM' and field == 'File fixity value') or \
                  (PROVENANCE_FIELD == 'ORIGINALPATH' and field == 'File Original Path'):
                  if p[PROVENANCE_FIELD].lower().strip() != 'ignore':
                     ignorefield=True
                     sectionrow[csvindex] = self.add_csv_value(p[PROVENANCE_FIELD])
      return ignorefield

   def __setpathmask__(self):
      pathmask = ''
      if self.config.has_option('path values', 'pathmask'):
         pathmask = self.config.get('path values', 'pathmask')
      return pathmask

   def populaterows(self, field, listcontrolitem, sectionrow, csvindex, rnumber):
   
      #populate cell with static values from config file
      if self.config.has_option('static values', field):
         rosettafield = self.config.get('static values', field)
         sectionrow[csvindex] = self.add_csv_value(rosettafield)

      #if there is a mapping configured to the list control, grab the value
      if self.config.has_option('rosetta mapping', field):
         rosettafield = self.config.get('rosetta mapping', field)
         addvalue = listcontrolitem[rosettafield]
         
         #****MULTIPLE ACCESS RESTRICTIONS****#
         #If the field we've got in the config file is Access, we need to
         #Then grab the Rosetta access code for the correct restriction status
         #Following a trail somewhat, but enables more flexible access restrictions in
         if field == 'Access Rights Policy ID (IE)':
            if self.config.has_option('access values', addvalue):
               #addvalue becomes the specific code given to a specific restriction status...
               addvalue = self.config.get('access values', addvalue)

         ignorefield = self.handleprovenanceexceptions('CHECKSUM', sectionrow, field, csvindex, rnumber)

         #place value into the cell within the row...
         if ignorefield == False:
            sectionrow[csvindex] = self.add_csv_value(addvalue)
         
      #if there is a mapping to a value in the droid export...
      elif self.config.has_option('droid mapping', field):          
         rosettafield = self.config.get('droid mapping', field)         
         ignorefield = self.handleprovenanceexceptions('ORIGINALPATH', sectionrow, field, csvindex, rnumber)
         if ignorefield == False:
            sectionrow[csvindex] = self.add_csv_value(self.grabdroidvalue(listcontrolitem['Missing Comment'], listcontrolitem['Title'], listcontrolitem['Sub-Series'], field, rosettafield, self.pathmask))

      elif self.prov == True:
         for p in self.provlist:
            if p['RECORDNUMBER'] == rnumber:
               if field == 'Event Identifier Type':
                  sectionrow[csvindex] = self.add_csv_value("EXTERNAL")
               if field == 'Event Identifier Value':
                  sectionrow[csvindex] = self.add_csv_value("EXT_1")  
               if field == 'Event Type':
                  sectionrow[csvindex] = self.add_csv_value("CREATION")  
               if field == 'Event Description':
                  sectionrow[csvindex] = self.add_csv_value("Provenance Note")
               if field == 'Event Date':
                  sectionrow[csvindex] = self.add_csv_value(p['NOTEDATE'])  
               if field == 'Event Outcome1':
                  sectionrow[csvindex] = self.add_csv_value("SUCCESS")
               if field == 'Event Outcome Detail1':
                  sectionrow[csvindex] = self.add_csv_value(p['NOTETEXT'])
  
   def createrosettacsv(self):
      
      self.subseriesmask = ''
      if self.duplicates:
         if self.config.has_option('path values', 'subseriesmask'):
            self.subseriesmask = self.config.get('path values', 'subseriesmask')
         else:
            sys.stderr.write("We have duplicate checksums, ensure they don't align with duplicate filenames")
            sys.stderr.write("Warning: '[path values] subseriesmask' not set in configuration.")
            
      CSVINDEXSTARTPOS = 2
      csvindex = CSVINDEXSTARTPOS
      
      self.rnumber = 0
      fields = []

      for item in self.exportlist:
      
         itemfixity = False
         itemoriginalpath = False
      
         itemrow = []
         
         #self.rosettasections, list of dictionaries generated from CFG file...
         for sections in self.rosettasections:
            #sections, individual dictionaries from CFG file... 
            
            #section row is entire length of x-axis in spreadsheet from CSV JSON Config file...
            sectionrow = ['""'] * len(self.rosettacsvdict)
            
            #Add key to the Y-axis of spreadsheet from dict...
            sectionrow[0] = self.add_csv_value(sections.keys()[0])
            
            #driven by CFG file, not JSON, so field occurs in CFG file first...
            #e.g. IE, REPRESENTATION, FILE, then each field in each of those...
            for field in sections[sections.keys()[0]]:

               #store for record level handling like provenance
               if field == 'Archway Identifier Value':
                  self.rnumber = item['Item Code']            
               
               #if we have a matching field in the cfg, and json, populate it... 
               if field == self.rosettacsvdict[csvindex]['name']:
                  self.populaterows(field, item, sectionrow, csvindex, self.rnumber)
               else:
                  #we have a misalignment between cfg and json...
                  #TODO: Output a more useful error message? 
                  sys.exit("CSV configuration and schema file do not match. Look for missing fields in either. Failed on: " + str(field) + " " + str(self.rosettacsvdict[csvindex]['name']))
               
               #increment csvindex along the x-axis...
               csvindex+=1
            
            itemrow.append(sectionrow)
         fields.append(itemrow)
         csvindex=CSVINDEXSTARTPOS
      
      self.csvstringoutput(fields)

   #TODO: unit tests for this...
   def listduplicates(self):
      seen = []
      dupe = []
      for row in self.droidlist:
         cs = ''
         if 'MD5_HASH' in row:
            cs = row['MD5_HASH']
         elif 'SHA1_HASH' in row:
            cs = row['SHA1_HASH']
         else:
            sys.stderr.write("No hash available to use in DROID export.\n")
            os.exit(1)
         if cs not in seen:
            seen.append(cs)
         else:
            dupe.append(cs)
      return set(dupe)

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
         
         if self.prov is True:
            provhandler = provenanceCSVHandler()
            self.provlist = provhandler.readProvenanceCSV(self.provfile)
            if self.provlist is None:
               self.prov = False
         
         self.duplicates = self.listduplicates()
         self.createrosettacsv()
