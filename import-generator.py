import sys
from datetime import datetime
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema
import ConfigParser
import argparse
import csv

def retrieve_year_from_modified_date(MODIFIED_DATE):

   inputdateformat = '%Y-%m-%dT%H:%M:%S'
   moddate = datetime.strptime(MODIFIED_DATE, inputdateformat)
   return moddate.year


def do_stuff():
   config = ConfigParser.RawConfigParser()
   config.read('import-value-mapping.cfg')

   #tmpint = config.get('static values', 'Accession No.')
   #print tmpint


   #if config.has_option('Options', 'myoption'):

   f = open('import-csv-schema.json', 'rb')
   importschemajson = f.read()

   importschema = JsonTableSchema.JSONTableSchema(importschemajson)
   importschemadict = importschema.as_dict()

   #for row in DROID CSV...
      #for column in schema...

   for column in importschemadict['fields']:
      if config.has_option('droid mapping', column['name']):
         print config.get('droid mapping', column['name'])
         
      if config.has_option('static values', column['name']):
         print config.get('static values', column['name'])
         
      if column['name'] == 'Description':       #TODO: More dynamic in config file?
         if config.has_option('additional values', 'descriptiontext'):
            print config.get('additional values', 'descriptiontext')

      # TODO: search DROID CSV string for MODIFIED_DATE strip all but year
      # input here...
      if column['name'] == 'Open Year':  
         print "BBBBBBBBBBBBBBBBBB " + str(retrieve_year_from_modified_date('2006-03-10T14:31:49'))

      if column['name'] == 'Close Year':  
         print "CCCCCCCCCCCCCCCCCC " + str(retrieve_year_from_modified_date('2007-03-10T14:31:49'))

def getDROIDHeaders(csvcolumnheaders):
   header_list = []
   for header in csvcolumnheaders:      
      header_list.append(header)
   return header_list

def removefolders(droid_list):
   print len(droid_list)
   for row in droid_list:
      if row['TYPE'] == 'Folder':
         droid_list.remove(row)
   print len(droid_list)

def readDROIDCSV(droidcsv):
   
   droid_list = []

   with open(droidcsv, 'rb') as csvfile:
      droidreader = csv.reader(csvfile)
      for row in droidreader:      
         if droidreader.line_num == 1:		# not zero-based index
            header_list = getDROIDHeaders(row)
         else:
            droid_dict = {}
            for i,item in enumerate(row):
               droid_dict[header_list[i]] = item
               # get URI Scheme: urlparse(url).scheme
               # get DIRNAME os.path.dirname(item)
               
            droid_list.append(droid_dict)
   
   return droid_list

def importsheetDROIDmapping(droidcsv):
   droid_list = readDROIDCSV(droidcsv)
   droid_list = removefolders(droid_list)

def main():

   #	Usage: 	--csv [droid report]

   #	Handle command line arguments for the script
   parser = argparse.ArgumentParser(description='Analyse DROID results stored in a SQLite DB')
   parser.add_argument('--csv', help='Single DROID CSV to read.', default=False)
   #parser.add_argument('--csva', help='Optional: DROID CSV to read, and then analyse.', default=False)
   #parser.add_argument('--db', help='Optional: Single DROID sqlite db to read.', default=False)

   if len(sys.argv)==1:
      parser.print_help()
      sys.exit(1)

   #	Parse arguments into namespace object to reference later in the script
   global args
   args = parser.parse_args()
   
   if args.csv:
      importsheetDROIDmapping(args.csv)
   #if args.csva:
   #	handleDROIDCSV(args.csva, True)
   #if args.db:
   #	handleDROIDDB(args.db)
   
   else:
      sys.exit(1)

if __name__ == "__main__":
   main()




'''
f = open('import-csv-schema.json', 'rb')
test = f.read()

ross = JsonTableSchema.JSONTableSchema(test)

rs = ross.as_dict()

for x in rs['fields']:
   print x['name']'''
   
   # TODO: Read mapping Config file... 
   # TODO: Read values config file...
   # TODO: For each matching field, import data, else, blank cell

   # get URI Scheme: urlparse(url).scheme
   # get DIRNAME os.path.dirname(item)

#sys.stdout.write(ross.as_csv_header())