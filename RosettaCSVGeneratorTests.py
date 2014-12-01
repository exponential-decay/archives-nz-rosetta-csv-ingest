from unittest import TestCase, TestLoader, TextTestRunner
from RosettaCSVGenerator import RosettaCSVGenerator

class RosettaCSVGeneratorTests(TestCase):

   def setup(self):
      self.rosettaCSVgen = RosettaCSVGenerator(False, False, False, False)

   def test_normalize_spaces(self):
      self.setup()
      
      #1
      case_blank_two_spaces = "  "
      result_blank_two_spaces = " "
      
      #2
      case_words_two_spaces = "one  two"
      result_words_two_spaces = "one two"
      
      #3
      case_words_three_spaces = "one   two"
      result_words_three_spaces = "one two"
      
      #4
      case_multiple_words_spaces = "one  two  three"
      result_multiple_words_spaces = "one two three"
      
      #5
      case_filename_xls = "001 SPREADSHEET  FILE.xls" 
      result_filename_xls = "001 SPREADSHEET FILE.xls"

      #5
      case_filename_doc = "001       DOCUMENT        FILE.xls" 
      result_filename_doc = "001 DOCUMENT FILE.xls"

      #7
      case_nospace = "word"
      result_nospace = "word"
      
      #8
      case_onespace = "word space"
      result_onespace = "word space"
      
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_blank_two_spaces), result_blank_two_spaces)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_words_two_spaces), result_words_two_spaces)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_words_three_spaces), result_words_three_spaces)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_multiple_words_spaces), result_multiple_words_spaces)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_filename_xls), result_filename_xls)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_filename_doc), result_filename_doc)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_nospace), result_nospace)
      self.assertEqual(self.rosettaCSVgen.normalize_spaces(case_onespace), result_onespace)

def main():
	suite = TestLoader().loadTestsFromTestCase(RosettaCSVGeneratorTests)
	TextTestRunner().run(suite)
	
if __name__ == "__main__":
	main()