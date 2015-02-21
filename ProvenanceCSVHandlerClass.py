import unicodecsv
import sys

from droidcsvhandlerclass import *

class provenanceCSVHandler:

   #TODO: Better error handlin? Format error handling? Validation?
   provheaders = ['RECORDNUMBER','NOTEDATE','NOTETEXT']

   def readProvenanceCSV(self, provcsvname):
      csvhandler = genericCSVHandler()
      exportlist = csvhandler.csvaslist(provcsvname)
      #counter a blank sheet
      if len(exportlist) < 1:
         exportlist = None
      if exportlist is not None:
         for h in self.provheaders:
            if h in exportlist[0]:
               sys.stderr.write(str(h) + '\n')
            else:
               exportlist = None
               break
      return exportlist
      
      
test = provenanceCSVHandler()
print test.readProvenanceCSV('prov.notes')