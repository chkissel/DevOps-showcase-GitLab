#!/usr/bin/env python3

from flask import Flask, json, request, jsonify
from flask_cors import CORS
import numpy as np
from scipy import ndimage
from scipy.ndimage.filters import convolve
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image
from random import randint
import os


app = Flask(__name__)
CORS(app)


@app.route("/", methods=['POST'])
def rest_api():
    data = request.get_json()
    print(request.files['file'])

    img_class = ImageHandling(request.files['file'])
    img = img_class.load_img()
    processed_img = EdgeDetection(img,
                                kernel_size=5,
                                low_threshold=3.5,
                                high_threshold=36.5,
                                weak_pixel=100,
                                strong_pixel=255,
                                sigma=1).canny()
    uuid = random_digits(6)
    processed_img = processed_img.astype(np.uint8)
    img = Image.fromarray(processed_img, 'L')
    img.save('./static/' + str(uuid) + '.png')
    
    return str(uuid)+'.png'

@app.route("/fetch", methods=['GET'])
def fetch():
    images = []
    print('test')
    for file in os.listdir("static"):
        if file.endswith(".png"):	
            images.append(file)
    return jsonify(images)

class ImageHandling:

    def __init__(self, img_file):
        self.img_file = img_file

    def load_img(self):
        img = mpimg.imread(self.img_file)
        grey_img = self.make_grayscale(img)
        return grey_img

    def make_grayscale(self, rgb):
        r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray


class EdgeDetection:

    # based on: https://github.com/FienSoP/canny_edge_detector

    def __init__(self, image, kernel_size, low_threshold, high_threshold, weak_pixel, strong_pixel, sigma):
        self.image = image
        self.magnitude_mat = None
        self.direction_mat = None
        self.kernel_size = kernel_size
        self.weak_pixel = weak_pixel
        self.strong_pixel = strong_pixel
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.sigma = sigma

    def gauss_filter(self):
        sigma = self.sigma
        size = self.kernel_size // 2
        x, y = np.mgrid[-size:size + 1, -size:size + 1]
        # sigma is ignored since it is one for normal distribution
        g = np.exp(-((x ** 2 + y ** 2) / 2 * sigma ** 2)) * (1 / (2 * np.pi * sigma ** 2))
        g = g / g.max() * 255
        smoothed_image = convolve(self.image, g)
        return smoothed_image

    def sobel_filter(self, img):
        x_kernel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], np.float32)
        y_kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], np.float32)

        x_result = ndimage.filters.convolve(img, x_kernel)
        y_result = ndimage.filters.convolve(img, y_kernel)

        magnitude = np.hypot(x_result, y_result)
        magnitude = magnitude / magnitude.max() * 255
        edge_direction = np.arctan2(y_result, x_result)

        return magnitude, edge_direction

    def non_max_suppression(self, img, gradient):

        height, width = img.shape
        value_matrix = np.zeros((height, width), dtype=np.int32)
        angle = gradient * 180. / np.pi
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                pixel_angle = 180 if angle[y, x] < 0 else angle[y, x]
                # 22.5 = 180 / 8
                intensity = (pixel_angle / 22.5) - ((pixel_angle % 22.5) / 22.5)

                def angle_0():
                    n = img[y, x + 1]
                    m = img[y, x - 1]
                    return n, m

                def angle_45():
                    n = img[y + 1, x - 1]
                    m = img[y - 1, x + 1]
                    return n, m

                def angle_90():
                    n = img[y + 1, x]
                    m = img[y - 1, x]
                    return n, m

                def angle_135():
                    n = img[y - 1, x - 1]
                    m = img[y + 1, x + 1]
                    return n, m

                switch = {
                    0: angle_0,
                    1: angle_45,
                    2: angle_45,
                    3: angle_90,
                    4: angle_90,
                    5: angle_135,
                    6: angle_135,
                    7: angle_0,
                    8: angle_0,
                }
                try:
                    q, r = switch[intensity]()
                except KeyError as e:
                    q, r = switch[round(intensity)]()
                value_matrix[y, x] = img[y, x] if (img[y, x] >= q) and (img[y, x] >= r) else 0

        return value_matrix

    def threshold(self, img):

        height, width = img.shape
        res = np.zeros((height, width), dtype=np.int32)

        strong_y, strong_x = np.where(img >= self.high_threshold)
        zeros_i, zeros_j = np.where(img < self.low_threshold)
        weak_y, weak_x = np.where((img <= self.high_threshold) & (img >= self.low_threshold))

        res[strong_y, strong_x] = self.strong_pixel
        res[weak_y, weak_x] = self.weak_pixel
        res[zeros_i, zeros_j] = 0
        return res

    def hysteresis(self, img):

        height, width = img.shape

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if img[y, x] == self.weak_pixel:

                    neighbours = [img[y + 1, x - 1], img[y + 1, x], img[y + 1, x + 1], img[y, x - 1],
                                  img[y, x + 1], img[y - 1, x - 1], img[y - 1, x], img[y - 1, x + 1]]
                    neighbours = sum(neighbours)
                    try:
                        if neighbours > (8 * self.weak_pixel):
                            img[y, x] = self.strong_pixel
                        else:
                            img[y, x] = 0
                    except IndexError as e:
                        pass
        return img

    def canny(self):
        blurred_img = self.gauss_filter()
        self.magnitude_mat, self.direction_mat = self.sobel_filter(blurred_img)
        thin_lines_image = self.non_max_suppression(self.magnitude_mat, self.direction_mat)
        threshold_image = self.threshold(thin_lines_image)
        final_img = self.hysteresis(threshold_image)
        return final_img

def random_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
