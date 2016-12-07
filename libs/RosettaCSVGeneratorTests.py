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

   def test_compare_filenames_as_titles(self):
      self.setup()
      
      # Standard true comparison, expected result
      case_comparison_no_dot = {u'STATUS': u'Done', u'MIME_TYPE': u'application/msword', u'NAME': u'FILENAME', u'PUID': u'fmt/1'}   #truncated dict
      result_comparison_no_dot = "FILENAME"

      # Standard true comparison, expected result
      case_comparison_dot = {u'STATUS': u'Done', u'MIME_TYPE': u'application/msword', u'NAME': u'NEWFILENAME.DOC', u'PUID': u'fmt/1'}
      result_comparison_dot = "NEWFILENAME"
      
      # False result: Checks that stipping of extension happens
      case_false_result = {u'STATUS': u'Done', u'MIME_TYPE': u'application/msword', u'NAME': u'FALSENAME.DOC', u'PUID': u'fmt/1'}
      result_false_result = "FALSENAME.DOC"
      
      # Multiple dots should only see removal of one
      case_multiple_dots = {u'STATUS': u'Done', u'MIME_TYPE': u'application/msword', u'NAME': u'MANY.EXT.EXT.DOC', u'PUID': u'fmt/1'}
      result_multiple_dots = "MANY.EXT.EXT"
      
      #TRUE tests
      self.assertTrue(self.rosettaCSVgen.compare_filenames_as_titles(case_comparison_no_dot, result_comparison_no_dot))
      self.assertTrue(self.rosettaCSVgen.compare_filenames_as_titles(case_comparison_dot, result_comparison_dot))
      self.assertTrue(self.rosettaCSVgen.compare_filenames_as_titles(case_multiple_dots, result_multiple_dots))

      #FALSE tests
      self.assertFalse(self.rosettaCSVgen.compare_filenames_as_titles(case_false_result, result_false_result))

def main():
	suite = TestLoader().loadTestsFromTestCase(RosettaCSVGeneratorTests)
	TextTestRunner().run(suite)
	
if __name__ == "__main__":
	main()