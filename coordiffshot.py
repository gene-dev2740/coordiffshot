import ctypes
import os
import sys
import threading
import time

import pyautogui
import PySimpleGUI as sg

from capture import Capture


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def msg_right_now(window: sg.Window, msg: str, text_color="blue"):
    window["txt_msg"].update(msg, text_color=text_color)  # type: ignore
    # readを待たずに即時反映
    window.refresh()


def check_val(val):
    ret_val = 0
    try:
        ret_val = int(val)
    except ValueError:
        ret_val = -1
    return ret_val


def image_button(text: str, key: str, filepath: str) -> sg.Button:
    return sg.Button(
        button_text=text,
        button_color=(sg.theme_background_color(), sg.theme_background_color()),
        image_filename=resource_path(filepath),
        image_subsample=1,
        border_width=0,
        key=key,
    )


def set_point(window: sg.Window):
    click_count = 0
    loop_flg = True
    sx = 0
    sy = 0
    ex = 0
    ey = 0
    msg_right_now(window, "始点をクリックしてください", "white")
    while loop_flg:
        # time.sleep(0.5)
        if ctypes.windll.user32.GetAsyncKeyState(0x01) == 0x8000:
            x, y = pyautogui.position()
            if click_count == 0:
                # 始点クリック
                sx = x
                sy = y
                click_count += 1
                time.sleep(0.2)
                msg_right_now(window, "終点をクリックしてください", "white")
            elif click_count == 1:
                # 終点クリック
                # 始点終点座標のチェック
                if sx > x:
                    ex = sx
                    sx = x
                else:
                    ex = x
                if sy > y:
                    ey = sy
                    sy = y
                else:
                    ey = y

                w = ex - sx
                h = ey - sy

                window["x_start"].update(sx)
                window["y_start"].update(sy)
                window["width"].update(w)
                window["height"].update(h)
                # 即時反映
                window.refresh()
                loop_flg = False
                msg_right_now(window, "")


text_size = (10, 1)
input_size = (20, 1)
run_flg = False

col = [
    [
        sg.Text(text="始点X", size=text_size),
        sg.Input(key="x_start", size=input_size),
        sg.Text(text="始点Y", size=text_size),
        sg.Input(key="y_start", size=input_size),
    ],
    [
        sg.Text(text="幅", size=text_size),
        sg.Input(key="width", size=input_size),
        sg.Text(text="高さ", size=text_size),
        sg.Input(key="height", size=input_size),
    ],
]

point_frame = sg.Frame(
    "切取位置",
    [
        [
            image_button("位置設定", "btn_point", "img/button.png"),
            sg.Column(col, justification="l"),
        ]
    ],
)

run_button = image_button("実行", "btn_start", "img/run.png")

exit_button = image_button("終了", "btn_end", "img/exit.png")

folder_button = image_button("フォルダ選択", "btn_folder", "img/folder.png")

layout = [
    [point_frame],
    [sg.Text(text="閾値", size=text_size), sg.Input("100", key="threshold", size=input_size)],
    [sg.Text(text="保存場所"), sg.Input(key="save"), folder_button],
    [sg.Text(key="txt_msg", size=(75, 1))],
    [run_button, exit_button],
]

sg.theme("DarkBlack")
window = sg.Window("画面キャプチャ", layout=layout)
cap = None

while True:
    e, val = window.read()  # type: ignore

    if e == sg.WINDOW_CLOSED or e == "btn_end":
        # 終了ボタン
        if cap:
            cap.capture_stop()
            cap = None
        break

    elif e == "btn_point":
        # 位置設定
        set_point(window)
    elif e == "btn_folder":
        # フォルダ選択
        folder = sg.popup_get_folder("フォルダを選択してください")
        window["save"].update(folder)
    elif e == "btn_start":
        # 実行ボタン
        if run_flg:
            # 実行中はスレッドを停止する
            window["btn_point"].update(disabled=False)
            if cap:
                cap.capture_stop()
                cap = None
            window["txt_msg"].update("停止!", text_color="blue")  # type: ignore
            window["btn_start"].update("実行", button_color="blue")  # type: ignore
            run_flg = False
        else:
            # 停止中はスレッドを実行する
            x_s = check_val(val["x_start"])
            x_e = check_val(val["y_start"])
            w = check_val(val["width"])
            h = check_val(val["height"])
            t = check_val(val["threshold"])
            f = val["save"]
            if x_s == -1 or x_e == -1 or w == -1 or h == -1:
                window["txt_msg"].update("数値を入力してください", text_color="red")  # type: ignore
            elif f == "":
                window["txt_msg"].update("出力先を入力してください", text_color="red")  # type: ignore
            else:
                # 全て正しく入力済み
                # 位置設定ボタンを非活性
                window["btn_point"].update(disabled=True)
                # 実行中メッセージ表示
                window["txt_msg"].update("実行中!", text_color="blue")  # type: ignore
                # ボタンを停止ボタンに変更
                window["btn_start"].update("停止", button_color="red")  # type: ignore
                run_flg = True
                cap = Capture(x_s, x_e, w, h, t, f)
                thread = threading.Thread(target=cap.capture_start)
                thread.start()


window.close()
