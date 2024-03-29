# **MOTION DETECTION WITH PYTHON**
#### by [VHEED](https://twitter.com/The_Vheed)

---

#### _A simple cross-platform Motion Detection GUI application written entirely with python_

[![](https://camo.githubusercontent.com/2fb0723ef80f8d87a51218680e209c66f213edf8/68747470733a2f2f666f7274686562616467652e636f6d2f696d616765732f6261646765732f6d6164652d776974682d707974686f6e2e737667)](https://python.org)
---
## Description
This project was created to demonstrate the ease of interoperability of opencv-python with PyQt5, using beginner friendly code.

It's a Motion Detector that detects motion using changes in colors of pixels.
Although, only grayscale comparisons are used by default but this can easily be changed. More info in [Notes](#notes)

Explanatory code _Comments_ would added soon.

## Features
- All detected movements or changes are saved in a '_detected.avi_' file in the same directory as the script 

- Sensitivity can easily be adjusted using the gui containing multiple parameters

- IP Cameras can also be easily integrated with the code for seamless motion detection and automated recording

- All recordings are time-lapsed for easy analysis

- An alarm is automatically triggered when the motion has been confirmed as valid

---

## Usage

- Install all dependencies with '_pip3_'
    ```commandline
    pip3 install -r dependencies.txt
    ```
- Run the '_main.py_' script with python3
    ```commandline
    python3 main.py
    ```

---

## Notes

- The output filename can be changed by changing the '_file_name_' variable in line 23 of '_main.py_' without adding any file extension;
  ```python
  file_name = '<filename>'
  ```

- The video source can be changed by giving the chosen camera index, video source file, or network stream in '_main.py_' in line 24;
  ```python
  cap = cv2.VideoCapture('<source>')
  ```

- The frame comparison mode can also be changed to color comparison by changing the '_comparison_mode_' variable in line 25 from '_gray_' to '_color_';
  ```python
  comparison_mode = '<mode>'
  ```
