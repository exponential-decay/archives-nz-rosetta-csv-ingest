class RosettaCSVSections:
   
   sections = []
   
   def __init__(self):
      
      IE = {"IE": ["Title", "Access", "Archway Identifier for publishing", "Archway Identifier Type",	"Archway Identifier Value", "Series", "Agency", "Entity Type", "Submission Reason"]}

      REPRESENTATION = {"REPRESENTATION": ["Revision Number", "Usage Type", "Preservation Type"]}

      FILE = {"FILE": ["File Location", "File Original Path", "File Name", "File fixity type", "File fixity value"]}

      self.sections.append(IE)
      self.sections.append(REPRESENTATION)
      self.sections.append(FILE)
