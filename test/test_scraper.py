import unittest
from scraper import Scraper
from selenium.common.exceptions import ElementNotInteractableException
import os.path

class Test_scrape(unittest.TestCase):

    def setUp(self):
         self.bot = Scraper()
        
    def test_url(self):
        expected_value = 'https://www.asos.com/men/sale/cat/?cid=8409&nlid=mw|sale|shop+sale+by+product|sale+view+all'
        actual_value = self.bot.url
        self.assertEqual(expected_value, actual_value)

    def test_cookies(self):
        self.bot.cookies() #accepts cookies
        with self.assertRaises(ElementNotInteractableException): #element should no longer be found
            self.bot.cookies()

    def test_clothes_container(self):
        expected_value = True
        all_links = self.bot.clothe_container()
        actual_value = all('https://www.asos.com/' in link for link in all_links)
        self.assertEqual(expected_value, actual_value)

    def test_make_dict(self):
        expected_value = type({})
        actual_value = self.bot.make_dict()
        self.assertIs(expected_value, type(actual_value))

    def test_make_json(self):
        actual_value = os.path.isfile('raw_data/data.json') 
        self.assertTrue(actual_value)

if __name__ == "__main__": #it only runs if this file is run directly rather than on any import 
    unittest.main(verbosity=2, exit=False)