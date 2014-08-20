import sys
from datetime import datetime
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema
import ConfigParser

def retrieve_year_from_modified_date(MODIFIED_DATE):

   inputdateformat = '%Y-%m-%dT%H:%M:%S'
   moddate = datetime.strptime(MODIFIED_DATE, inputdateformat)
   return moddate.year



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


#sys.stdout.write(ross.as_csv_header())