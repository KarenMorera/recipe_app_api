"""This file should be created when creating the project, in my case it did not so I created it myself"""

"""Sample tests"""

"""Import the test class we want to use, TesCase for database, SimpleTestCase no database"""
from django.test import SimpleTestCase

"""Import object to test"""
from app import calc 

"""Define a class and base it with SimpleTestCase or TestCase depending of the one we are using"""
class CalcTests(SimpleTestCase): 
    
    """Define test, method should have test_ at the start of the name"""
    def test_add_numbers(self):
        """Test adding numbers together"""
        
        res = calc.add(5,6)
        
        """The comparison of the result to see if it passes of fails"""
        self.assertEqual(res, 11)     
    
    def test_subtract_numbers(self): 
        res = calc.subtract(10, 15)
        self.assertEqual(res, 5)