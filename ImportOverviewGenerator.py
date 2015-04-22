#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import ConfigParser
from droidcsvhandlerclass import *

class ImportOverviewGenerator:

   def __init__(self, droidcsv=False, configfile=False):
      self.config = ConfigParser.RawConfigParser()
      if configfile is not False:
         self.config.read(configfile)      
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

      #If we need to output agency and accession for just the first row... 
      #sys.stdout.write('"' + agency + '",' + '"' + accession + '",' + '"' + series + '",' + '"' + folderlist[0] + '"' + '\n')
      
      for folder in folderlist:
         sys.stdout.write('"' + agency + '",' + '"' + accession + '",' + '"' + series + '",' + '"' + folder + '"' + '\n') 
      
   def readDROIDCSV(self):
      if self.droidcsv != False:
         droidcsvhandler = droidCSVHandler()
         droidlist = droidcsvhandler.readDROIDCSV(self.droidcsv)     
         return droidcsvhandler.retrievefolderlist(droidlist)

   def createOverviewSheet(self):
      if self.droidcsv != False:
         self.droidlist = self.readDROIDCSV()
         self.outputOverview()