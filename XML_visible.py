# coding=UTF-8
import cv2
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from os import listdir, mkdir
from os.path import isfile, join, isdir


if __name__ == '__main__':
    picinpath = "C:/Users/ee303/Desktop/out/extreme/img/"
    xmlinpath = "C:/Users/ee303/Desktop/out/extreme/xml/"
    outputpath='C:/Users/ee303/Desktop/out/'
    visible=False

    onlyfiles = [f for f in listdir(xmlinpath) if isfile(join(xmlinpath, f))]
    for counter in range(1, len(onlyfiles) + 1):
        tree = ET.parse(xmlinpath + str(counter) + '.xml')
        root = tree.getroot()
        one_pic_platetext=[]
        one_pic_location=[]
        for object in root.findall('object'):
            label_name = object.find('name').text
            platetext=object.find('plate_text').text
            bndbox = object.find('bndbox')
            xmin = bndbox.find('xmin').text
            xmax = bndbox.find('xmax').text
            ymin = bndbox.find('ymin').text
            ymax = bndbox.find('ymax').text
            location = [int(xmin), int(xmax), int(ymin), int(ymax)]
            one_pic_platetext.append([label_name,platetext])
            one_pic_location.append(location)
        im=cv2.imread(picinpath + str(counter) + '.jpg')
        dis_height = 1150
        dis_width = 2000
        if visible:
            cv2.namedWindow(str(counter), 0)
            cv2.resizeWindow(str(counter), dis_width, dis_height)
            cv2.moveWindow(str(counter), 0, 0)
        thick = int((dis_height + dis_width) // 300)
        for i in range(len(one_pic_platetext)):
            if one_pic_platetext[i][1]=='_':
                cv2.rectangle(im, (int(one_pic_location[i][0]), int(one_pic_location[i][2])), (int(one_pic_location[i][1]), int(one_pic_location[i][3])), (255,0,255), thick)
                cv2.putText(im, one_pic_platetext[i][0] + ':' + one_pic_platetext[i][1],
                            (int(one_pic_location[i][0]), int(one_pic_location[i][2] - 10)), 0, 1e-3 * dis_height,
                            (255, 0, 255), thick // 3)
            else:
                cv2.rectangle(im, (int(one_pic_location[i][0]), int(one_pic_location[i][2])),
                              (int(one_pic_location[i][1]), int(one_pic_location[i][3])), (0, 255, 255), thick)
                cv2.putText(im, one_pic_platetext[i][0] + ':' + one_pic_platetext[i][1],
                            (int(one_pic_location[i][0]), int(one_pic_location[i][2] - 10)), 0, 1e-3 * dis_height,
                            (0, 255, 255), thick // 3)
        if visible:
            cv2.imshow(str(counter), im)
            cv2.waitKey()
            cv2.destroyWindow(str(counter))
        else:
            cv2.imwrite(outputpath +  str(counter) + '.jpg', im)

    print('Work Over!! Congratulations!!')

    pass