import unittest, os
from Tests import Support
from ImageServer import ImageEngine, Domain

NB_THREAD = 1

JPG_SAMPLE_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'sami.jpg')
JPG_SAMPLE_IMAGE_SIZE = (3264, 2448)
BROKEN_IMAGE_FILENAME = os.path.join('..', '..', '..','samples', 'brokenImage.jpg')

class ImageEngineTestsCase(Support.AbstractIntegrationTestCase):
    
    def testImageIdShouldOnlyContainAlphanumericCharacters(self):
        try:
            self.imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId-')
        except ImageEngine.IDNotAuthorized, ex:
            assert ex.imageId == 'sampleId-'
    
    def testSaveBrokenImageShouldThrowException(self):
        try:
            self.imgProcessor.saveFileToRepository(BROKEN_IMAGE_FILENAME, 'sampleId')
        except ImageEngine.ImageFileNotRecognized, ex:
            pass
    
    def testSaveImageWithExistingIDShouldThrowException(self):
        self.imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        try:
            self.imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')    
        except ImageEngine.ImageIDAlreadyExistingException, ex:
            assert ex.imageId == 'sampleId'
    
    def testSaveImageShouldUpdateFileSystemAndDatabase(self):
        self.imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        assert os.path.exists(os.path.join(Support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'pictures', 'sampleId.jpg')) == True
        
        item = self.itemRepository.findOriginalItemById('sampleId')
        assert item is not None
        assert item.id == 'sampleId'
        assert item.format == Domain.IMAGE_FORMAT_JPEG
        assert item.size == JPG_SAMPLE_IMAGE_SIZE
        assert item.status == Domain.STATUS_OK
        
    def testPrepareTransformationWithNonExistingOriginalIdShouldThrowException(self):
        try:
            request = ImageEngine.TransformationRequest('nonexisting', (100,100), Domain.IMAGE_FORMAT_JPEG)
        except Exception:
            pass
    
    def testPrepareRequestShouldUpdateFileSystemAndDatabase(self):
        self.imgProcessor.saveFileToRepository(JPG_SAMPLE_IMAGE_FILENAME, 'sampleId')
        
        request = ImageEngine.TransformationRequest('sampleId', (100,100), Domain.IMAGE_FORMAT_JPEG)
        result = self.imgProcessor.prepareTransformation(request)
        assert os.path.exists(os.path.join(Support.AbstractIntegrationTestCase.DATA_DIRECTORY, 'cache', 'sampleId-100x100.jpg')) == True
        
        item = self.itemRepository.findDerivedItemByOriginalItemIdSizeAndFormat('sampleId', (100,100), Domain.IMAGE_FORMAT_JPEG)
        assert item is not None
        assert item.id == 'sampleId-100x100-JPEG'
        assert item.format == Domain.IMAGE_FORMAT_JPEG
        assert item.size == (100,100)
        assert item.status == Domain.STATUS_OK
        assert item.originalItem.id == 'sampleId'
        
        # result should be consistent across calls (caching..)
        result2 = self.imgProcessor.prepareTransformation(request)
        assert result == os.path.join('cache', 'sampleId-100x100.jpg')
        assert result2 == os.path.join('cache', 'sampleId-100x100.jpg')
    
    def testImageRequestProcessorMultithreadedTestCase(self):
        #imageProcessor = Factory.ImageServerFactory().createImageServer('/tmp/imgserver', [(100,100), (800,800)])

        for i in range(NB_THREAD):
            self.imgProcessor.saveFileToRepository('../../../samples/sami.jpg', 'sami%s' %(i))

            
                              
       # request = ImageEngine.TransformationRequest('sami', (100,100), 'jpg')
        #print imageProcessor.prepareTransformation(request)

    
def suite():
    return unittest.makeSuite(ImageEngineTestsCase, 'test')