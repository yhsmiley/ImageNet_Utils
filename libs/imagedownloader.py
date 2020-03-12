import sys
import os
import time
import tarfile


# import urllib.request as urllib2
import urllib.parse as urlparse
import requests

from PIL import Image
from io import StringIO

class ImageNetDownloader:
    def __init__(self):
        self.host = 'http://www.image-net.org'

    def download_file(self, url, desc=None, renamed_file=None, replace_if_exists=False):
        # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        # u = requests.get(url, headers=headers)
        resp = requests.get(url, timeout=5)

        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        if not filename:
            filename = 'downloaded.file'

        if not renamed_file is None:
            filename = renamed_file

        if desc:
            filename = os.path.join(desc, filename)

        # if the file should not be replaced if already present 
        # then check if is already exists, if it does then just return the file name
        if replace_if_exists is False:
            if os.path.isfile(filename):
                print("Image already downloaded: {}".format(filename))
                return filename

        with open(filename, 'wb') as f:
            meta_length = len(resp.content)
            file_size = None
            if meta_length:
                # file_size = int(meta_length[0])
                file_size = int(meta_length)
            print("Downloading: {} Bytes: {}".format(url, file_size))

            f.write(resp.content)

        return filename

    def extractTarfile(self, filename):
        print(filename)
        tar = tarfile.open(filename)
        tar.extractall()
        tar.close()

    def downloadBBox(self, wnid):
        filename = str(wnid) + '.tar.gz'
        url = self.host + '/downloads/bbox/bbox/' + filename
        try:
            filepath = self.download_file(url, self.mkWnidDir(wnid))
            currentDir = os.getcwd()
            os.chdir('./downloaded_images/' + wnid)
            self.extractTarfile(filename)
            print ('Download bbbox annotation from ' + url + ' to ' + filename)
            os.chdir(currentDir)
        except Exception as error:
            print ('Fail to download' + url)

    def getImageURLsOfWnid(self, wnid):
        url = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=' + str(wnid)
        # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        # f = requests.get(url, headers=headers)
        f = requests.get(url)
        contents = f.content.decode('utf-8').split('\n')
        imageUrls = []

        for each_line in contents:
            # Remove unnecessary char
            each_line = each_line.replace('\r', '').strip()
            if each_line:
                imageUrls.append(each_line)

        return imageUrls

    def getImageURLsMappingOfWnid(self, wnid):
        url = 'http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid=' + str(wnid)
        # headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        # f = requests.get(url, headers=headers)
        f = requests.get(url, timeout=5)
        contents = f.content.decode('utf-8').split('\n')
        imageUrlsMapping = []

        for each_line in contents:
            # Remove unnecessary char
            each_line = each_line.replace('\r', '').strip()
            if each_line:
                # parsing each line into filename and imageUrl
                each_line_split = each_line.split(' ')

                if len(each_line_split) != 2:
                    continue

                filename = each_line_split[0]
                imageUrl = each_line_split[1]
                
                imageUrlsMapping.append({
                    'filename': filename,
                    'url': imageUrl
                })

        return imageUrlsMapping

    def mkWnidDir(self, wnid):
        if not os.path.exists(os.path.join('downloaded_images',wnid)):
            os.mkdir(os.path.join('downloaded_images',wnid))
        return os.path.abspath(os.path.join('downloaded_images',wnid))

    def downloadImagesByURLs(self, wnid, imageUrls, replace_if_exists=False):
        # save to the dir e.g: n005555_urlimages/
        wnid_urlimages_dir = os.path.join(self.mkWnidDir(wnid), str(wnid) + '_urlimages')
        if not os.path.exists(wnid_urlimages_dir):
            os.mkdir(wnid_urlimages_dir)

        for url in imageUrls:
            try:
                self.download_file(url, wnid_urlimages_dir, replace_if_exists=replace_if_exists)
            except Exception as error:
                print ('Fail to download : ' + url)
                print (str(error))

    def downloadImagesByURLsMapping(self, wnid, imageUrlsMapping, replace_if_exists=False):
        # save to the dir e.g: n005555_urlimages/
        wnid_urlimages_dir = os.path.join(self.mkWnidDir(wnid), str(wnid) + '_urlimages')
        if not os.path.exists(wnid_urlimages_dir):
            os.mkdir(wnid_urlimages_dir)

        for imageInfo in imageUrlsMapping:
            try:
                filename = self.download_file(imageInfo['url'], wnid_urlimages_dir, imageInfo['filename']+'.JPEG', replace_if_exists=replace_if_exists)

                # check image file for corruption
                try:
                    img = Image.open(filename) # open the image file
                    img.verify() # verify that it is, in fact an image
                except (IOError, SyntaxError) as e:
                    print('Bad file, removing: {}'.format(filename)) # print out the names of corrupt files
                    os.remove(filename)

            except Exception as error:
                print ('Fail to download : ' + imageInfo['url'])
                print (str(error))


    def downloadOriginalImages(self, wnid, username, accesskey):
        download_url = 'http://www.image-net.org/download/synset?wnid=%s&username=%s&accesskey=%s&release=latest&src=stanford' % (wnid, username, accesskey)

        try:
             download_file = self.download_file(download_url, self.mkWnidDir(wnid), wnid + '_original_images.tar')
             print("download_file: {}".format(download_file))
        except Exception as error:
            print ('Fail to download : ' + download_url)

        currentDir = os.getcwd()
        extracted_folder = os.path.join('downloaded_images', wnid, wnid + '_original_images')
        if not os.path.exists(extracted_folder):
            os.mkdir(extracted_folder)
        os.chdir(extracted_folder)
        self.extractTarfile(download_file)
        os.chdir(currentDir)
        print ('Extract images to ' + extracted_folder)

