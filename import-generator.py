import sys
from datetime import datetime
sys.path.append(r'JsonTableSchema/')
import JsonTableSchema


inputdate = '2006-03-10T14:31:49'
inputdateformat = '%Y-%m-%dT%H:%M:%S'

mydate = datetime.strptime(inputdate, inputdateformat)
#print mydate.year

f = open('import-csv-schema.json', 'rb')
test = f.read()

ross = JsonTableSchema.JSONTableSchema(test)

sys.stdout.write(ross.as_csv_header())