import unittest
from ImageServer import Factory, ImageEngine
import sqlalchemy 
import os, shutil
 
class AbstractIntegrationTestCase(unittest.TestCase):
        
    DATA_DIRECTORY='/tmp/imgserver-test'
    
    def __cleanup__(self):
        if os.path.exists(AbstractIntegrationTestCase.DATA_DIRECTORY):
            shutil.rmtree(AbstractIntegrationTestCase.DATA_DIRECTORY)
            
                
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__cleanup__()
        sqlalchemy.orm.clear_mappers()
        self.imageServerFactory = Factory.ImageServerFactory()
        self.imgProcessor = self.imageServerFactory.createImageServer(AbstractIntegrationTestCase.DATA_DIRECTORY, 'sqlite:///:memory:', [(100,100), (800,800)])
        self.itemRepository = self.imageServerFactory.getItemRepository()
    
        (getattr(self, 'onSetUp') if hasattr(self, 'onSetUp') else (lambda: None))()  
        
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        (getattr(self, 'onTearDown') if hasattr(self, 'onTearDown') else (lambda: None))()
        self.imageServerFactory = None
        self.imgProcessor = None
        self.itemRepository = None
        
        #self.imageServerFactory.getConnection().close()
    
    