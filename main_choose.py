# coding=UTF-8
import cv2
import getpass
import os
import json
from os import listdir, mkdir
from os.path import isfile, join, isdir
import tkinter as tk

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

ix, iy, cx, cy = -1, -1, -1, -1
w, h = 0, 0
changeObject = False


def disable_mouse_callback(*args):  # Assign *args in order to suppress TypeError raised by disable_mouse_callback().
    pass


def plate_text_input_windows():
    global plate_text

    cv2.setMouseCallback(str(file_name), disable_mouse_callback)

    root = tk.Tk()
    root.title("input plate text")

    mission = tk.Label(root, text="input plate text")
    mission.pack()

    default_input = tk.StringVar()
    plate_text_input = tk.Entry(root, textvariable=default_input)
    default_input.set("_")
    plate_text_input.pack()

    def buttom_on_click():
        global plate_text
        plate_text = plate_text_input.get()
        print('your input is:' + plate_text)
        root.destroy()

    tk.Button(root, text="Enter", command=buttom_on_click).pack()

    root.mainloop()

    cv2.setMouseCallback(str(file_name), click_boundingbox)

    return plate_text
    pass


def class_input_windows():
    global class_key
    root = tk.Tk()

    cv2.setMouseCallback(str(file_name), disable_mouse_callback)

    root.title("choose class")

    instructions = tk.Label(root, text="Hint")
    instructions.pack()

    hint = tk.Label(root, text="'w':'plate','y':'yellow_plate','g':'green_plate','r':'red_plate'")
    hint.pack()

    mission = tk.Label(root, text="class name:")
    mission.pack()

    default_input = tk.StringVar()
    class_input = tk.Entry(root, textvariable=default_input)
    default_input.set("W")
    class_input.pack()

    def buttom_on_click():
        global class_key
        class_key = class_input.get()
        print('your input is:' + class_key)
        root.destroy()

    tk.Button(root, text="Enter", command=buttom_on_click).pack()

    root.mainloop()

    cv2.setMouseCallback(str(file_name), click_boundingbox)

    return class_key
    pass


# mouse callback function
def click_boundingbox(event, x, y, flags, param):
    global changeObject, now_JSON, clickcounter, ix, iy, cx, cy, w, h, box_mode, display_im, im, class_dict, obj_list

    if event == cv2.EVENT_LBUTTONDOWN:
        if box_mode == 'Initial mode':
            if clickcounter % 2 == 0:
                ix, iy = int(x), int(y)
                print('ix')
                print(ix)
                print('iy')
                print(iy)
            else:
                cx, cy = int(x), int(y)
                print('cx')
                print(cx)
                print('cy')
                print(cy)

                class_key = None
                while not class_key in class_dict:
                    class_key = class_input_windows()
                class_name = class_dict[class_key]

                if class_name in class_dict.values():
                    plate_text_number = plate_text_input_windows()
                    print(plate_text_number)
                    one_JSON_object = {"label": class_name, "plate_text_number": plate_text_number,
                                       "topleft": {"x": ix, "y": iy},
                                       "bottomright": {"x": cx, "y": cy}}
                else:
                    one_JSON_object = {"label": class_name, "topleft": {"x": ix, "y": iy},
                                       "bottomright": {"x": cx, "y": cy}}

                now_JSON.append(one_JSON_object)
                draw_box_for_one_JSON(one_JSON_object)
            changeObject = True
            clickcounter += 1
            pass
        elif box_mode == 'Revised mode':
            if clickcounter % 2 == 0:
                ix, iy = int(x), int(y)
                print('ix')
                print(ix)
                print('iy')
                print(iy)
            else:
                cx, cy = int(x), int(y)
                print('cx')
                print(cx)
                print('cy')
                print(cy)

                class_key = None
                while not class_key in class_dict:
                    class_key = class_input_windows()
                class_name = class_dict[class_key]

                if class_name in class_dict.values():
                    plate_text_number = plate_text_input_windows()
                    print(plate_text_number)
                    one_JSON_object = {"label": class_name, "plate_text_number": plate_text_number,
                                       "topleft": {"x": ix, "y": iy},
                                       "bottomright": {"x": cx, "y": cy}}
                else:
                    one_JSON_object = {"label": class_name, "topleft": {"x": ix, "y": iy},
                                       "bottomright": {"x": cx, "y": cy}}

                revised_index = find_best_IOU(one_JSON_object, now_JSON)

                now_JSON[revised_index] = one_JSON_object
                display_im = im.copy()
                draw_box_for_all_JSON(now_JSON)
            changeObject = True
            clickcounter += 1
            pass
        elif box_mode == 'Delete mode':
            ix, iy = int(x), int(y)
            print('ix')
            print(ix)
            print('iy')
            print(iy)
            remove_index = click_which_one([ix, iy], now_JSON)
            if remove_index is not None:
                del now_JSON[remove_index]
                display_im = im.copy()
                draw_box_for_all_JSON(now_JSON)
            pass


def click_which_one(click_position, JSON_list):
    position = None
    minimum_area = 10 ** 8
    for counter in range(len(JSON_list)):
        in_box_flag, area = click_in_box(click_position, JSON_list[counter])
        if in_box_flag and (area < minimum_area):
            minimum_area = area
            position = counter
    return position
    pass


def click_in_box(click_position, one_JSON):
    in_box_flag = False
    box_area = 0
    left = one_JSON['topleft']['x']
    top = one_JSON['topleft']['y']
    right = one_JSON['bottomright']['x']
    bottom = one_JSON['bottomright']['y']
    box_width = right - left
    box_height = bottom - top
    box_area = box_width * box_height
    # if click_position[0] > left and click_position[0] < right and click_position[1] > top and click_position[
    #     1] < bottom:
    if left < click_position[0] < right and bottom < click_position[1] < top:
        in_box_flag = True
    return in_box_flag, box_area
    pass


def find_best_IOU(JSON_traget, JSON_list):
    position = 0
    best_iou = 0

    for counter in range(len(JSON_list)):
        one_JSON = JSON_list[counter]
        iou = check_IOU(JSON_traget, one_JSON)
        if iou > best_iou:
            best_iou = iou
            position = counter
    return position
    pass


def check_IOU(JSON_traget, JSON_compare):
    intersection_left = max(JSON_traget['topleft']['x'], JSON_compare['topleft']['x'])
    intersection_top = max(JSON_traget['topleft']['y'], JSON_compare['topleft']['y'])
    intersection_right = min(JSON_traget['bottomright']['x'], JSON_compare['bottomright']['x'])
    intersection_bottom = min(JSON_traget['bottomright']['y'], JSON_compare['bottomright']['y'])
    intersecion_width = intersection_right - intersection_left
    intersecion_height = intersection_bottom - intersection_top
    intersecion_area = intersecion_width * intersecion_height
    traget_area = (JSON_traget['bottomright']['x'] - JSON_traget['topleft']['x']) * (
            JSON_traget['bottomright']['y'] - JSON_traget['topleft']['y'])
    compare_area = (JSON_compare['bottomright']['x'] - JSON_compare['topleft']['x']) * (
            JSON_compare['bottomright']['y'] - JSON_compare['topleft']['y'])
    union_area = traget_area + compare_area - intersecion_area
    if union_area != 0 and intersecion_width > 0 and intersecion_height > 0:
        iou = float(intersecion_area) / float(union_area)
    else:
        iou = 0

    return iou
    pass


def draw_box_for_one_JSON(one_JSON):
    global file_name, display_im, thick, class_dict

    if one_JSON["label"] in class_dict.values():
        cv2.rectangle(display_im, (one_JSON['topleft']['x'], one_JSON['topleft']['y']),
                      (one_JSON['bottomright']['x'], one_JSON['bottomright']['y']), (0, 255, 255), thick)
        cv2.putText(display_im, one_JSON["label"] + ':' + one_JSON["plate_text_number"],
                    (one_JSON['topleft']['x'], one_JSON['topleft']['y'] - 12), 0, 1e-3 * thick * 100, (0, 255, 255),
                    thick // 3)
    else:
        cv2.rectangle(display_im, (one_JSON['topleft']['x'], one_JSON['topleft']['y']),
                      (one_JSON['bottomright']['x'], one_JSON['bottomright']['y']), (0, 255, 255), thick)
        cv2.putText(display_im, one_JSON["label"], (one_JSON['topleft']['x'], one_JSON['topleft']['y'] - 12), 0,
                    1e-3 * thick * 100, (0, 255, 255), thick // 3)

    cv2.imshow(str(file_name), display_im)
    pass


def draw_box_for_all_JSON(all_JSON):
    global file_name, display_im
    for one_JSON in all_JSON:
        draw_box_for_one_JSON(one_JSON)
    cv2.imshow(str(file_name), display_im)
    pass


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


# def generateXML(classname, filename, outputpath, location, imagesize):
def generateXML(now_JSON, out_xml_path, imagesize, file_name):
    folderxml = ET.Element('folder')
    folderxml.text = str(getpass.getuser())

    filenamexml = ET.Element('filename')
    filenamexml.text = str(file_name)

    sourcexml = ET.Element('source')
    databasexml = ET.SubElement(sourcexml, 'database')
    databasexml.text = "record"  # ---------change

    sizexml = ET.Element('size')
    widthxml = ET.SubElement(sizexml, 'width')
    widthxml.text = str(imagesize[0])  # ---------change
    heightxml = ET.SubElement(sizexml, 'height')
    heightxml.text = str(imagesize[1])  # ---------change
    depthxml = ET.SubElement(sizexml, 'depth')
    depthxml.text = '3'

    segmentedxml = ET.Element('segmented')
    segmentedxml.text = '0'

    annotation = ET.Element('annotation')
    annotation.extend((folderxml, filenamexml, sourcexml, sizexml, segmentedxml))

    for i in range(len(now_JSON)):
        xmin = now_JSON[i]['topleft']['x']
        ymin = now_JSON[i]['topleft']['y']
        xmax = now_JSON[i]['bottomright']['x']
        ymax = now_JSON[i]['bottomright']['y']
        objectxml = ET.Element('object')
        namexml = ET.SubElement(objectxml, 'name')
        namexml.text = now_JSON[i]["label"]
        plate_text_xml = ET.SubElement(objectxml, 'plate_text')
        plate_text_xml.text = now_JSON[i]["plate_text_number"]
        posexml = ET.SubElement(objectxml, 'pose')
        posexml.text = 'Frontal'

        bndboxxml = ET.SubElement(objectxml, 'bndbox')
        xminxml = ET.SubElement(bndboxxml, 'xmin')
        xminxml.text = str(xmin)
        yminxml = ET.SubElement(bndboxxml, 'ymin')
        yminxml.text = str(ymin)
        xmaxxml = ET.SubElement(bndboxxml, 'xmax')
        xmaxxml.text = str(xmax)
        ymaxxml = ET.SubElement(bndboxxml, 'ymax')
        ymaxxml.text = str(ymax)
        annotation.append(objectxml)

    tree = ET.ElementTree(annotation)
    tree.write(out_xml_path + '/' + file_name + '.xml')


if __name__ == '__main__':
    videoinpath = "data/sample44/"
    outpath = "data/output44/"

    dirfold_img = 'image'
    out_img_path = join(outpath, dirfold_img)
    if not isdir(out_img_path):
        mkdir(out_img_path)

    dirfold_xml = 'xml'
    out_xml_path = join(outpath, dirfold_xml)
    if not isdir(out_xml_path):
        mkdir(out_xml_path)

    dis_height = 1150
    dis_width = 2000
    global now_JSON, display_im
    global box_mode, file_name, thick, clickcounter, im, class_dict
    box_mode = ''
    class_dict = {'w': 'plate', 'y': 'yellow_plate', 'g': 'green_plate', 'r': 'red_plate',
                  'W': 'plate', 'Y': 'yellow_plate', 'G': 'green_plate', 'R': 'red_plate'}
    clickcounter = 0

    all_files = [f for f in listdir(videoinpath) if isfile(join(videoinpath, f))]

    file_counter = 1
    while file_counter <= len(all_files):
        box_mode = ''
        now_file_counter = file_counter
        file_name = str(file_counter) + '.jpg'
        file_path = videoinpath + file_name

        im = cv2.imread(file_path)
        display_im = im.copy()

        height, width, _ = im.shape
        thick = int((height + width) // 700)

        now_JSON = []

        cv2.namedWindow(str(file_name), 0)
        cv2.resizeWindow(str(file_name), dis_width, dis_height)
        cv2.moveWindow(str(file_name), 0, 0)

        cv2.setMouseCallback(str(file_name), click_boundingbox)
        cv2.imshow(str(file_name), display_im)

        key_value = 0
        while key_value not in (ord('x'), ord('X'), ord('c'), ord('C'), ord('z'), ord('Z')):
            key_value = cv2.waitKey()
            if key_value in (ord('x'), ord('X')):  # 'x' or 'X' for next image.
                file_counter = file_counter + 1
            elif key_value in (ord('c'), ord('C')):
                file_counter = file_counter + 10
            elif key_value in (ord('z'), ord('Z')):
                file_counter = file_counter - 1
            elif key_value in (ord('i'), ord('I')):
                box_mode = 'Initial mode'
                print(box_mode)
            elif key_value in (ord('r'), ord('R')):
                box_mode = 'Revised mode'
                print(box_mode)
            elif key_value in (ord('d'), ord('D')):
                box_mode = 'Delete mode'
                print(box_mode)

        cv2.destroyWindow(str(file_name))

        if clickcounter != 0:
            output_all_files = [f for f in listdir(out_img_path) if isfile(join(out_img_path, f))]
            file_name = str(len(output_all_files) + 1)
            imagesize = [width, height]
            generateXML(now_JSON, out_xml_path, imagesize, file_name)
            cv2.imwrite(out_img_path + '/' + file_name + '.jpg', im)

        clickcounter = 0
        print('now_file_counter')
        print(now_file_counter)

    pass
