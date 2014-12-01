from unittest import TestCase, TestLoader, TextTestRunner
from RosettaCSVGenerator import RosettaCSVGenerator

class RosettaCSVGeneratorTests(TestCase):

   def setup(self):
      self.rosettaCSVgen = RosettaCSVGenerator(False, False, False, False)

   def test_normalize_spaces(self):
         self.setup()

def main():
	suite = TestLoader().loadTestsFromTestCase(RosettaCSVGeneratorTests)
	TextTestRunner(verbosity=2).run(suite)
	
if __name__ == "__main__":
	main()