from __future__ import absolute_import
import DBface
import segment
import FEGAN
import APDrawingGan
import dependency_imports
from google.cloud import storage

client = storage.Client()
def onetake(originname,gcspath,mask,stroke,dbface = False,readdat = False):
    if readdat:
        mask = cv2.imread('extra/mask.png')
        #stroke = cv2.imread('extra/stroke.png')
    originimageread = cv2.imread('origin/'+originname)
    #please save landmark before this
    if dbface:
        DBFace.detect_singleimage(originimageread,originname)

    make_segment(originimageread,'masks/'+originname)
    sketch_image(originname)
    sketch = cv2.imread('sketch/'+originname)
    FEGAN.execute_FEGAN(mask,sketch,stroke,image = originimageread,read=False)

    #######################################################################

def sketch_image(imagename,foldername='origin/',savefoldername='sketch/',landmarkdir='landmark/',maskdir='mask/'):
    APDrawingGan.APDrawingGan(foldername,savefoldername,imagename,landmarkdir,maskdir)

def remove_presketch(originsketch):
    for filename in os.listdir('sketch/'):
        if originsketch in filename:
            os.remove('sketch/'+filename)

def make_segment(originimageread,imagepath):
    segment.segment(originimageread,imagepath)

def do_fegan(mask,sketch,stroke,originimageread,read):
    #already read files
    FEGAN.execute_FEGAN(mask,sketch,stroke,image = originimageread,read=read)
