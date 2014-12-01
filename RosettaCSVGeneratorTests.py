from unittest import TestCase, TestLoader, TextTestRunner
from RosettaCSVGenerator import RosettaCSVGenerator

class RosettaCSVGeneratorTests(TestCase):

   def setup(self):
      self.rosettaCSVgen = RosettaCSVGenerator()
   
def main():
	suite = TestLoader().loadTestsFromTestCase(RosettaCSVGeneratorTests)
	TextTestRunner(verbosity=2).run(suite)
	
if __name__ == "__main__":
	main()