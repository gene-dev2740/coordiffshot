import argparse
import os
import time
from datetime import datetime

import cv2
import numpy as np
from PIL import ImageGrab


class Capture:
    def __init__(self, xstart, ystart, width, height, threshold, output):
        self.xstart = xstart
        self.ystart = ystart
        self.width = width
        self.height = height
        self.threshold = threshold
        self.output = output
        self.run = True
        if not os.path.exists("screenshot"):
            os.mkdir("screenshot")

    def capture(self):
        img = ImageGrab.grab(
            (self.xstart, self.ystart, self.xstart + self.width, self.ystart + self.height), all_screens=True
        )
        new_image = np.array(img, dtype=np.uint8)
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        return new_image

    def capture_stop(self):
        self.run = False

    def capture_start(self):
        before_shot = self.capture()
        while self.run:
            time.sleep(0.5)
            screenshot = self.capture()
            diff = cv2.absdiff(before_shot, screenshot)
            diff_len = len(list(zip(*np.where(diff > self.threshold))))
            if diff_len > 0:
                out_file = os.path.join(self.output, f"screenshot_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                # filename = f"screenshot/{datetime.now().strftime('%Y%m%d%H%M%S')}_screenshot.jpg"
                cv2.imwrite(out_file, screenshot)
                print(f"shot is {out_file}")
                # yield filename

            before_shot = screenshot


if __name__ == "__main__":
    # xstart = 3090
    # ystart = 158
    # width = 740
    # height = 680
    parser = argparse.ArgumentParser(description="画面の指定した座標の範囲内に変化があるとスクリーンショットを撮るツールです")
    parser.add_argument("xstart", help="X座標の始点です", type=int, default=0)
    parser.add_argument("ystart", help="Y座標の視点です", type=int, default=0)
    parser.add_argument("width", help="キャプチャの幅です", type=int, default=1920)
    parser.add_argument("height", help="キャプチャの高さです", type=int, default=1080)
    parser.add_argument("threshold", help="画像差分の閾値です", type=int, default=100)
    parser.add_argument("output", help="出力先です", type=str)

    args = parser.parse_args()
    cap = Capture(args.xstart, args.ystart, args.width, args.height, args.threshold, args.output)
    cap.capture_start()
