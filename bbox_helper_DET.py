#!/usr/bin/env python
import os
from PIL import Image
import sys
import zipfile
import xml.etree.ElementTree as ET
import argparse

def scanAnnotationFolder(annotationFolderPath):
    annotationFiles = []
    for root, dirs, files in os.walk(annotationFolderPath):
        for file in files:
            if file.endswith('.xml'):
                annotationFiles.append(os.path.join(root, file))
    if len(annotationFiles) is 0:
        print("check input path")
    return annotationFiles

# Bounding Box Helper
class BBoxHelper:
    def __init__(self, annotation_file, image_path=None):
        self.annotation_file = annotation_file
        xmltree = ET.parse(annotation_file)
        filename = xmltree.find('filename').text
        wnid = filename.split('_')[0]
        image_id = filename.split('_')[1]
        # create a dict to save filename, wnid, image id, etc..
        self.annotation_filename = filename
        self.wnid = wnid
        self.image_id = image_id
        # find bounding box
        objects = xmltree.findall('object')
        self.rects = []
        for object_iter in objects:
                bndbox = object_iter.find("bndbox")
                # self.rects.append([int(it.text) for it in bndbox])
                self.rects.append([int(bndbox[0].text), int(bndbox[2].text), int(bndbox[1].text), int(bndbox[3].text)])

        localPath = xmltree.find('path')

        self.imgPath = None
        if localPath is not None and os.path.exists(localPath.text):
            self.imgPath = localPath.text

        if image_path is not None:
            self.imgPath = image_path


    def saveBoundBoxImage(self, imgPath=None, image_dir=None):
        if imgPath is not None:
            self.imgPath = imgPath

        if imgPath is None and self.imgPath is None:
            self.imgPath = self.findImagePath()

        outputFolder = os.path.join(image_dir, 'bounding_box_imgs')

        # annotation_file_dir = os.path.dirname(os.path.realpath(self.annotation_file))
        # outputFolder = os.path.join(annotation_file_dir, savedTargetDir)
        if not os.path.exists(outputFolder):
            os.mkdir(outputFolder)

        try:
            # Get crop images
            bbs = []
            im = Image.open(self.imgPath)
            for box in self.rects:
                 bbs.append(im.crop(box))
            # Save them to target dir
            count = 0
            for box in bbs:
                    count = count + 1
                    outPath = str(os.path.join(outputFolder, self.annotation_filename + '_box' + str(count) + '.jpg'))
                    box.save(outPath)
                    print ('save to ' + outPath)
        except Exception as e:
            if self.imgPath is None:
                print("File not found, next")

    def get_BoudingBoxs(self):
        return self.rects

        def getWnid(self):
            return self.wnid

    def findImagePath(self, search_folder='./downloaded_images/DET'):
        filename = self.annotation_filename + str('.JPEG')
        for root, dirs, files in os.walk(search_folder):
            for file in files:
                if filename == file:
                    return os.path.join(root, file)
        print (filename + ' not found')
        return None


def saveAsBoudingBoxImg(xmlfile, image_path=None, image_dir=None):
    bbhelper = BBoxHelper(xmlfile)
    print (bbhelper.findImagePath())
    # if image_dir:
    #     print (bbhelper.findImagePath(image_dir))
    # Search image path according to bounding box xml, and crop it
    if shouldSaveBoundingBoxImg:
        print (bbhelper.get_BoudingBoxs())
        bbhelper.saveBoundBoxImage(image_dir=image_dir)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Help the user to download, crop, and handle images from ImageNet')
    p.add_argument('--bxmlpath', help='Boudingbox xml path')
    p.add_argument('--bxmldir', help='Boudingbox dir path')
    p.add_argument('--save_boundingbox', help='Search images and crop the bounding box by image paths', action='store_true', default=False)
    args = p.parse_args()
    # Give bounding_box XML and show its JPEG path and bounding rects
    boundingbox_xml_file = args.bxmlpath
    boundingbox_xml_dir = args.bxmldir
    shouldSaveBoundingBoxImg = args.save_boundingbox

    if boundingbox_xml_file is not None:
        saveAsBoudingBoxImg(boundingbox_xml_file, image_dir=boundingbox_xml_dir)

    if boundingbox_xml_dir is not None:
        allAnnotationFiles = scanAnnotationFolder(os.path.join(boundingbox_xml_dir, 'Annotation'))
        for xmlfile in allAnnotationFiles:
            saveAsBoudingBoxImg(xmlfile, image_dir=boundingbox_xml_dir)
