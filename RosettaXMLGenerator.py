#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import ConfigParser
from ProvenanceCSVHandlerClass import *
from droidcsvhandlerclass import *
from ImportSheetGenerator import ImportSheetGenerator
import xml.etree.ElementTree as etree

class RosettaXMLGenerator:

   #item list struct to aid mapping between droid and list control
   exportdict = {'hash': '', 'title': '', 'itemcode': ''};

   def __init__(self, droidcsv=False, exportsheet=False, rosettaschema=False, configfile=False, provenance=False):
   
      if configfile is not False:
         self.config = ConfigParser.RawConfigParser()
         self.config.read(configfile)   
         
         self.droidcsv = droidcsv
         self.exportsheet = exportsheet
         
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
         sys.exit('ERROR: No configuration file provided.\n')
         
      #Get some functions from ImportGenerator
      self.impgen = ImportSheetGenerator()
      
      #List duplicate items to check...
      self.duplicateitemsaddedset = set()

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
         sys.stderr.write("WARNING: Filename checksum duplicate likely. Check list control: " + listcontroltitle.encode('utf-8') + " vs. DROID export: " + droid_filename_title.encode('utf-8') + "\n")
      
      return comparison

   def __setpathmask__(self):
      pathmask = ''
      if self.config.has_option('path values', 'pathmask'):
         pathmask = self.config.get('path values', 'pathmask')
      return pathmask

   def __typeencode__(self, value):
      if type(value) is int:              #TODO: probably a better way to do this (type-agnostic)
         field = str(value).replace('\r', '').replace('\n', '')
      else:
         field = value.replace('\r', '').replace('\n', '')  #.encode('utf=8')
      return field

   def __getmapping__(self, key, value, item):
      code = False
      if self.config.has_option(key, value):
         code = self.config.get(key, value)
         code = item[code]
         if value == 'File Original Path':
            code = code.replace(self.pathmask, '').replace('\\','/')
         if value == 'File Location':
            code = code.replace(self.pathmask, '').replace('\\','/') + '/'
         if value == 'Access':
            if self.config.has_option('access values', item['Restriction Status']):
               code = self.config.get('access values', item['Restriction Status'])
      if code == False:
         sys.stderr.write("WARNING: No value mapped: " + key + " " + value + "\n")
         code = ''

      return self.__typeencode__(code)
      
   def __accessmapping__(self, value):
      print value

   #todo: need r number
   def __addvalue__(self, elementtext, listcontrol, droiditem):
      xmlvalue = ''
      elementtext = elementtext.replace('{{ ', '').replace(' }}', '')
      if self.config.has_section('xml template'):
                  
         #handle provenance
         if elementtext == 'dnx.event.datetime':
            elementtext = "TODO: Provenance date goes here"
         elif elementtext == 'dnx.event.provenancenote':
            elementtext = "TODO: Provenance text goes here"
         else:
            mapvalue = ''
            
            if self.config.has_option('xml template', elementtext):
               mapvalue = self.config.get('xml template', elementtext)

            #Overwrite default, if manually specified...
            #self.provfile = self.config.get('provenance', 'file')
         
            key = mapvalue.split('.', 1)[0]
            
            if len(mapvalue.split('.', 1)) > 1:
               value = mapvalue.split('.', 1)[1]
            
            xmlvalue = ''  #verbose but clear variable
            if key == 'droid mapping':
               xmlvalue = self.__getmapping__(key, value, droiditem)
            elif key == 'rosetta mapping':
               xmlvalue = self.__getmapping__(key, value, listcontrol)
            else:
               xmlvalue = mapvalue
      else:
         sys.stderr.write("ERROR: No XML mapping available to map to. Exiting." + "\n")
         sys.exit(1)
      return xmlvalue   #xmlvalue.encode('utf-8')

   #def __getmatchtext__(self, value):
   #   if re.match("(^{{\s[a-z]+.[a-z]+.[a-z]+\s}}$)", value):  #{{ template.template.template }}
      
   def recurse_xml(self, xml, listcontrol, droiditem):   
      elist = []
      for x in xml:
         value = x.text
         if value != None:
            if value.strip() != '':
               if re.match("(^{{\s[a-z]+.[a-z]+.[a-z]+\s}}$)", value):  #{{ template.template.template }}
                  x.text = self.__addvalue__(x.text, listcontrol, droiditem)
            else:
               elist.append(x)
         attr = x.attrib
         if attr != {}:
            for a in attr:
               if re.match("(^{{\s[a-z]+.[a-z]+.[a-z]+\s}}$)", x.get(a)):
                  x.set(a, self.__addvalue__(x.get(a), listcontrol, droiditem))
      for e in elist:
         self.recurse_xml(e, listcontrol, droiditem)

   def __gettree__(self):
      tree = False
      try:
         parser = etree.XMLParser(encoding="utf-8")
         tree = etree.parse('xml-template/template-ie-events.xml', parser=parser)
      except IOError as (errno, strerror):
         sys.stderr.write("IO error({0}): {1}".format(errno, strerror) + ' : ' + file_string + '\n')
         sys.exit("ERROR: Cannot read XML template." + "\n")
      return tree

   def createrosettaxml(self):
      sys.stderr.write("INFO: Creating Rosetta XML." + "\n")
      no = 1
      for item in list(self.exportlist):
         self.exportdict['hash'] = item['Missing Comment']
         self.exportdict['itemcode'] = item['Item Code']
         self.exportdict['title'] = item['Title']
         
         droiditem = self.__getDroidItem__(self.exportdict)
         if droiditem == False: 
            self.__notinlist__(self.exportdict)

         tree = self.__gettree__()  #TODO: Avoid File I/O a second time...
         if tree != False:
            root = tree.getroot()
            xml_iter = iter(root)
            self.recurse_xml(xml_iter, item, droiditem)
                     
            output = True
            if output == True:
               #tree.write('output/ie' + str(no) + ".xml")
               tree.write('output/' + self.exportdict['itemcode'] + ".xml") #, encoding='UTF-8')
               no+=1
         
         #preserve memory as we go...
         self.exportlist.remove(item)
               
   def __getDroidItem__(self, itemdict):
      match = False
      for droiditem in list(self.droidlist):
         if droiditem['MD5_HASH'] == itemdict['hash']:
            if self.compare_filenames_as_titles(droiditem, itemdict['title']):
               match = droiditem
               self.droidlist.remove(droiditem)    #preserve memory as we go...
      return match
   
   def __notinlist__(self, item):
      sys.stderr.write(item['Item Code'] + ": " + item['Title'] + " not in DROID list input.")
  
   #TODO: unit tests for this...
   def listduplicates(self):
      seen = []
      dupe = []
      for row in self.droidlist:
         cs = row['MD5_HASH']
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
         
         if self.prov is True:
            provhandler = provenanceCSVHandler()
            self.provlist = provhandler.readProvenanceCSV(self.provfile)
            if self.provlist is None:
               self.prov = False
         
         self.duplicates = self.listduplicates()
         
         for dupes in self.duplicates:
            sys.stderr.write("INFO: One duplicate checksum in sheet: " + dupes + "\n")

         self.createrosettaxml()
