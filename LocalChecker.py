import time

import PIL.ImageOps
import keyboard
import numpy as np
import pyautogui
import pyscreenshot as ImageGrab
import pytesseract
from playsound import playsound
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pyttsx3
import random


class LocalChecker:
    """
    This is a class for constant jumping through the next destination object (stargate/ansiblex gate/citadel) while any
    is present in overview. It works by selecting a detection area, finding a part with given color in it and pressing
    jump on this part.
    Attributes:
        red_colors: list of colors which belong to non-green characters in local chat which need to be detected
        engine: text-to-speech engine
        structure_mode: mode of warp out structure detection; 'mouse' for manual choice by putting mouse over the needed
                        row in overview, 'ocr' for automatic detection of given name
        structure_name: name of structure in overview which needs to found using OCR and to be used as warp out
                        structure (used only in 'ocr' mode)
        upper_left_x, upper_left_y: upper left corner of destination object detection area of screen
        bottom_right_x, bottom_right_y: bottom right corner of destination object detection area of screen
        warp_x, warp_y: screen coordinates of warp out structure row in overview window
    """

    def __init__(self, structure_mode, structure_name, start_timeout, red_colors):
        time.sleep(start_timeout)
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.say('Local checker has started')
        self.engine.runAndWait()
        self.structure_mode = structure_mode
        self.structure_name = structure_name
        self.red_colors = red_colors
        self.upper_left_x, self.upper_left_y = 0, 0
        self.bottom_right_x, self.bottom_right_y = 0, 0

        if self.structure_mode == 'ocr':
            result, self.warp_x, self.warp_y = self.find_structure()
        elif self.structure_mode == 'mouse':
            self.warp_x, self.warp_y = self.choose_structure()

    def check_contain(self, arr, color):
        """
        Check if pixel of given color is present on image (in np.array form) by simply scanning through the whole array.

        Parameters:
            -arr: image in np.array form
            -color: color to be found

        Returns:
            -result: True or False depending on whether the color was found
        """
        for x in range(arr.shape[1]):
            for y in range(arr.shape[0]):
                if list(arr[y, x, :]) == color:
                    return True
        return False

    def warp_to(self, x, y):
        """
        Warps to a structure by pressing S key on given screen coordinates.

        Parameters:
            -x: x coordinate of gate in overview window
            -y: y coordinate of gate in overview window
        Returns:
            None
        """
        pyautogui.keyDown('s')
        time.sleep(random.uniform(0.2, 0.3))
        pyautogui.click(x=x, y=y, clicks=2, interval=random.uniform(0.08, 0.12))
        pyautogui.keyUp('s')

    def align_to(self, x, y):
        """
        Aligns to a structure by pressing S key on given screen coordinates.

        Parameters:
            -x: x coordinate of gate in overview window
            -y: y coordinate of gate in overview window
        Returns:
            None
        """
        pyautogui.keyDown('a')
        time.sleep(random.uniform(0.2, 0.3))
        pyautogui.click(x=x, y=y, clicks=2, interval=random.uniform(0.08, 0.12))
        pyautogui.keyUp('a')

    def scoop_drones(self):
        """
        Scoops ship's drones pressing Shift+R key combination.

        Parameters:
            None
        Returns:
            None
        """
        pyautogui.hotkey('shift', 'r', interval=random.uniform(0.08, 0.12))

    def find_structure(self):
        """
        Finds the row with given structure name in overview window and saves its coordinates.

        Parameters:
            None
        Returns:
            None
        """

        im = ImageGrab.grab()
        resize_factor = 2
        orig_width, orig_height = im.size
        left = orig_width // 2
        top = 0
        right = orig_width
        bottom = orig_height
        im = im.crop((left, top, right, bottom))
        im.save('cropped.bmp')

        im = im.convert('L')
        im = PIL.ImageOps.invert(im)
        (width, height) = (im.width * resize_factor, im.height * resize_factor)
        im_resized = im.resize((width, height))
        data = pytesseract.image_to_data(im_resized, output_type=Output.DICT)
        for i in range(len(data['left'])):
            if data['text'][i] == self.structure_name:
                x = (data['left'][i] + data['width'][i] // 2) // resize_factor + orig_width // 2
                y = (data['top'][i] + data['height'][i] // 2) // resize_factor
                print(f'Found {self.structure_name} row in overview at X={x}, Y={y}')
                self.engine.say(f'Found {self.structure_name} row in overview')
                self.engine.runAndWait()
                return True, x, y
        print('Could not find given structure')
        self.engine.say(f'Could not find {self.structure_name} row in overview')
        self.engine.runAndWait()
        return False, 0, 0

    def choose_area(self):
        """
        Saves given coordinates of local chat window which are used to monitor present characters.

        Parameters:
            None
        Returns:
            None
        """
        self.engine.say('Put mouse on the upper left point and press J')
        self.engine.runAndWait()
        flag = True
        while flag:
            if keyboard.is_pressed('m'):
                flag = False
            if keyboard.is_pressed('j'):
                self.upper_left_x, self.upper_left_y = pyautogui.position()
                self.engine.say('Upper left point saved')
                self.engine.say('Put mouse on the bottom right point and press K')
                self.engine.runAndWait()
                print(f'Upper left point coordinates: X {self.upper_left_x}, Y {self.upper_left_y}')
            if keyboard.is_pressed('k'):
                self.bottom_right_x, self.bottom_right_y = pyautogui.position()
                self.engine.say('Bottom right point saved')
                self.engine.runAndWait()
                print(f'Bottom right point coordinates: X {self.bottom_right_x}, Y {self.bottom_right_y}')
                flag = False
        self.engine.say(f'All coordinates saved')
        self.engine.runAndWait()

    def choose_structure(self):
        """
        Saves coordinates of warp out structure row in overview window by taking mouse pointer position.

        Parameters:
            None
        Returns:
            mouse_x, mouse_y: coordinates of structure row in overview window
        """
        self.engine.say('Please put your mouse over the needed structure in overview and press N')
        self.engine.runAndWait()
        flag = True
        while flag:
            if keyboard.is_pressed('m'):
                mouse_x, mouse_y = 0, 0
                flag = False
            if keyboard.is_pressed('n'):
                mouse_x, mouse_y = pyautogui.position()
                flag = False
        print(f'Saved coordinates: X {mouse_x}, Y {mouse_y}')
        self.engine.say(f'Coordinates saved')
        self.engine.runAndWait()
        return mouse_x, mouse_y

    def check_local(self, signal=True, warp_out=True):
        """
        Monitors local chat window and gives out an audio signal and executes warp out procedure (scoop - align - warp)
        if any non-green character is detected. The detection if made by constantly checking if given "red" colors are
        present in the monitoring area.

        Parameters:
            signal: whether the audio signal should be played if a non-green character is detected
            warp_out: whether the wap out procedure should be executed if a non-green character is detected
        Returns:
            None
        """
        flag = True
        while flag:  # making a loop
            time.sleep(random.uniform(0.15, 0.25))
            im = ImageGrab.grab(bbox=(self.upper_left_x, self.upper_left_y, self.bottom_right_x, self.bottom_right_y))
            im_arr = np.array(im)
            # im.save('screen.bmp')

            for red_color in self.red_colors:
                if self.check_contain(im_arr, red_color):
                    print('Local is RED')
                    if warp_out:
                        self.scoop_drones()
                        self.align_to(self.warp_x, self.warp_y)
                        if signal:
                            playsound('alarm.wav')
                        time.sleep(random.uniform(2.75, 3.5
                                                  ))
                        self.warp_to(self.warp_x, self.warp_y)
                    elif signal:
                        playsound('alarm.wav')

            if keyboard.is_pressed('j'):
                flag = False
            else:
                print('Check is working')
