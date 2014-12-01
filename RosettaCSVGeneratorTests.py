from unittest import TestCase, TestLoader, TextTestRunner
from RosettaCSVGenerator import RosettaCSVGenerator

class RosettaCSVGeneratorTests(TestCase):

   def setup(self):
      self.rosettaCSVgen = RosettaCSVGenerator(False, False, False, False)

   def test_normalize_spaces(self):
      self.setup()
      
      case_blank_two_spaces = "  "
      result_blank_two_spaces = " "
      
      case_words_two_spaces = "one  two"
      result_words_two_spaces = "one two"
      
      case_words_three_spaces = "one   two"
      result_words_three_spaces = "one two"
      
      case_multiple_words_spaces = "one  two  three"
      result_multiple_words_spaces = "one two three"
      
      case_filename = "001 SPREADSHEET  FILE.xls" 
      result_filename = "001 SPREADSHEET FILE.xls"
      
      case_nospace = "word"
      result_nospace = "word"
      
      case_onespace = "word space"
      result_onespace = "word space"
      
      self.assertEqual(" ", self.rosettaCSVgen.normalize_spaces("  "))

def main():
	suite = TestLoader().loadTestsFromTestCase(RosettaCSVGeneratorTests)
	TextTestRunner(verbosity=2).run(suite)
	
if __name__ == "__main__":
	main()