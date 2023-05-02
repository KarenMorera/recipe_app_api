"""Test custom Django management commands """

#Import is to moch the data. 
from unittest.mock import patch
#One of the possible errors when trying to connect to the db 
from psycopg2 import OperationalError as Psycopg2Error
#function provided by django, allows us to call the command that we are testing. 
from django.core.management import call_command 
#Possible error of the database connection. 
from django.db.utils import OperationalError
#We use simpleTestCase because we dont need an action database, we just need a simulation for this test. 
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase): 
    """Test commands"""
    def test_wait_for_db_ready(self, patched_check): 
        """Test waiting for database if database ready"""
        patched_check.return_value = True
        
        call_command('wait_for_db')
        
        patched_check.assert_called_once_with(databases =['default'])
        
    @patch('time.sleep')    
    def test_wait_for_db_delay(self, patched_sleep , patched_check):
        """test waiting for database when getting OperationalError"""
        """This says the first 2 times, raise error Psycopg2Error, and the next 3 times use OperationalError"""
        """We could change the 2 and 3 for the numbers that we want, in this case these are the most realistic."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]
            
        call_command('wait_for_db')
        
        #We are going to check that the command was called 6 times.    
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases = ['default'])

