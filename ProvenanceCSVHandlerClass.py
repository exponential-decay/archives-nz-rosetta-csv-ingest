import unicodecsv

from droidcsvhandlerclass import *

class provenanceCSVHandler:

   def readProvenanceCSV(self, provcsvname):
      csvhandler = genericCSVHandler()
      exportlist = csvhandler.csvaslist(provcsvname)
      return exportlist
      
      
test = provenanceCSVHandler()
print test.readProvenanceCSV('prov.notes')