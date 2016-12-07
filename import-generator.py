#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import ConfigParser
from libs.RosettaCSVGenerator import RosettaCSVGenerator
from libs.RosettaXMLGenerator import RosettaXMLGenerator
from libs.ImportOverviewGenerator import ImportOverviewGenerator
from libs.ImportSheetGenerator import ImportSheetGenerator
         
def createImportOverview(droidcsv, configfile):
   createoverview = ImportOverviewGenerator(droidcsv, configfile)
   createoverview.createOverviewSheet()

def importsheetDROIDmapping(droidcsv, importschema, configfile):
   importgenerator = ImportSheetGenerator(droidcsv, importschema, configfile)
   importgenerator.droid2archwayimport()
   
def exportsheetRosettamapping(droidcsv, exportsheet, rosettaschema, configfile, provenance, xml=False):
   if xml == True:
      #temporary solution - draw out common components between CSV and XML when we have opportunity...
      sys.stderr.write("INFO: Outputting XML data." + "\n")
      xmlgen = RosettaXMLGenerator(droidcsv, exportsheet, rosettaschema, configfile, provenance)
      xmlgen.export2rosettacsv()   
   else:
      csvgen = RosettaCSVGenerator(droidcsv, exportsheet, rosettaschema, configfile, provenance)
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
   parser.add_argument('--exp', help='Archway list control sheet to map to Rosetta ingest CSV', default=False, required=False)
   parser.add_argument('--ros', help='Rosetta CSV validation schema', default=False, required=False)
   parser.add_argument('--cfg', help='Config file for field mapping.', default=False, required=False)
   parser.add_argument('--pro','--prov', help='Flag to enable use of prov.notes file.', default=False, required=False, action="store_true")
   parser.add_argument('--args','--arg', help='Concatenate arguments into a file for ease of use.', default=False, required=False)

   parser.add_argument('--xml', help='Flag to create XML SIP.', default=False, required=False, action="store_true")

   if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

   #	Parse arguments into namespace object to reference later in the script
   global args
   args = parser.parse_args()
   
   #TODO: Additional help text to describe two discrete sets of options
   if args.args:
   
      config = ConfigParser.RawConfigParser()
      config.read(args.args)   
      
      if config.has_option('arguments', 'title'):
         sys.stderr.write("INFO: Using " + config.get('arguments', 'title') + " configuration file." + "\n")
      else:
         sys.stderr.write("Using an arguments configuration file." + "\n\n")

      if config.has_option('arguments', 'droidexport'):
         args.csv = config.get('arguments', 'droidexport')
         args.ros = config.get('arguments', 'schemafile')
         args.cfg = config.get('arguments', 'configfile')
         if config.get('arguments', 'ingest').lower() == "true":    #we need a list control for ingest
            args.exp = config.get('arguments', 'listcontrol')
         else:
            args.exp = False
            if config.has_option('arguments', 'impschema'):
               args.imp = config.get('arguments', 'impschema')
            
      if args.imp != '' and args.exp == False:
         if config.has_option('arguments', 'impconfig'):
            args.cfg = config.get('arguments', 'impconfig')
   
      #special option for creating an import cover sheet
      if config.has_option('arguments', 'coversheet'):
         if config.get('arguments', 'configfile').lower() == 'true':
            args.ros = False
            args.exp = False

      if config.has_option('arguments', 'xml'):
         if config.get('arguments', 'xml').lower() == 'true':
            args.xml = True
   
   #creating an import sheet for Archway...
   if args.csv and args.imp and args.cfg:
      importsheetDROIDmapping(args.csv, args.imp, args.cfg)
   #creating an ingest sheet for Rosetta...
   elif args.csv and args.exp and args.ros and args.cfg:
      exportsheetRosettamapping(args.csv, args.exp, args.ros, args.cfg, args.pro, args.xml)
   #creating a cover sheet for Archway...
   elif args.csv and args.cfg:
      createImportOverview(args.csv, args.cfg)
   #we're not doing anything sensible...
   else:
      parser.print_help()
      sys.exit(1)

if __name__ == "__main__":
   main()
