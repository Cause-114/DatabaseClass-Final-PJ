# from django.test import TestCase

# # Create your tests here.
from .Crawler import Crawler

c = Crawler("https://www.badu.com")
c.crawl(10, 1)
