#!/usr/bin/env python3
"""
Generate static PNG figures for the ToolShell micro-postmortem kit using only Python standard libraries.
Creates:
  - attack-mini.png : ATT&CK technique highlight grid
  - decision-tree.png : Early-response decision tree diagram
"""

from __future__ import annotations

import os
import struct
import zlib
from typing import Dict, Iterable, Tuple

WIDTH_ATTACK = 900
HEIGHT_ATTACK = 420
WIDTH_DECISION = 900
HEIGHT_DECISION = 500

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (34, 34, 34)
COLOR_GREY = (210, 210, 210)
COLOR_DARK_GREY = (120, 120, 120)
COLOR_ACCENT = (180, 210, 250)

FONT_DATA: Dict[str, Tuple[str, ...]] = {
    "A": ("  #  ", " # # ", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "#  ##", "#   #", "#   #", " ####"),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   #", "   #", "   #", "#  #", "#  #", " ## "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  ##", " ####"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "# #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": (" ### ", "#   #", "    #", "  ## ", "    #", "#   #", " ### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#    ", "#### ", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     ")
}

DEFAULT_CHAR = "?"


class Canvas:
    def __init__(self, width: int, height: int, bg: Tuple[int, int, int] = COLOR_WHITE):
        self.width = width
        self.height = height
        row = bytearray()
        for _ in range(width):
            row.extend(bg)
        self.pixels = [bytearray(row) for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = x * 3
            self.pixels[y][idx: idx + 3] = bytes(color)

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]) -> None:
        lx = max(0, min(x0, x1))
        hx = min(self.width - 1, max(x0, x1))
        ly = max(0, min(y0, y1))
        hy = min(self.height - 1, max(y0, y1))
        for y in range(ly, hy + 1):
            row = self.pixels[y]
            for x in range(lx, hx + 1):
                idx = x * 3
                row[idx: idx + 3] = bytes(color)

    def draw_rect(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]) -> None:
        self.draw_line(x0, y0, x1, y0, color)
        self.draw_line(x0, y1, x1, y1, color)
        self.draw_line(x0, y0, x0, y1, color)
        self.draw_line(x1, y0, x1, y1, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set_pixel(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def draw_text(self, x: int, y: int, text: str, color: Tuple[int, int, int]) -> None:
        cursor_x = x
        cursor_y = y
        for ch in text:
            if ch == "\n":
                cursor_x = x
                cursor_y += 9
                continue
            glyph = FONT_DATA.get(ch.upper(), FONT_DATA[DEFAULT_CHAR])
            for row_idx, row_pattern in enumerate(glyph):
                for col_idx, symbol in enumerate(row_pattern):
                    if symbol == "#":
                        self.set_pixel(cursor_x + col_idx, cursor_y + row_idx, color)
            cursor_x += 6


def write_png(path: str, canvas: Canvas) -> None:
    raw = b"".join(b"\x00" + bytes(row) for row in canvas.pixels)
    compressor = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png_data = [
        b"\x89PNG\r\n\x1a\n",
        chunk(b"IHDR", header),
        chunk(b"IDAT", compressor),
        chunk(b"IEND", b""),
    ]
    with open(path, "wb") as fh:
        for part in png_data:
            fh.write(part)


def render_attack_grid(output_path: str) -> None:
    canvas = Canvas(WIDTH_ATTACK, HEIGHT_ATTACK, COLOR_WHITE)
    title = "ATT&CK EMPHASIS"
    canvas.draw_text(20, 20, title, COLOR_BLACK)
    techniques = [
        "T1190", "T1059.001", "T1505.003", "T1078", "T1027",
        "T1003", "T1082", "T1021", "T1071", "T1567"
    ]
    cols = 2
    box_w = 380
    box_h = 70
    start_x = 40
    start_y = 70
    x_gap = 40
    y_gap = 20
    for idx, tech in enumerate(techniques):
        row = idx // cols
        col = idx % cols
        x0 = start_x + col * (box_w + x_gap)
        y0 = start_y + row * (box_h + y_gap)
        x1 = x0 + box_w
        y1 = y0 + box_h
        canvas.fill_rect(x0, y0, x1, y1, COLOR_ACCENT if idx % 2 == 0 else COLOR_GREY)
        canvas.draw_rect(x0, y0, x1, y1, COLOR_DARK_GREY)
        id_text = tech
        canvas.draw_text(x0 + 18, y0 + 20, id_text, COLOR_BLACK)
        # Derived short descriptors (all uppercase to match font)
        descriptor = {
            "T1190": "EXPLOIT PUBLIC INTERFACE",
            "T1059.001": "POWERSHELL EXECUTION",
            "T1505.003": "WEB SHELL PERSIST",
            "T1078": "VALID ACCOUNT ABUSE",
            "T1027": "OBFUSCATED PAYLOAD",
            "T1003": "CREDENTIAL ACCESS",
            "T1082": "SYSTEM DISCOVERY",
            "T1021": "REMOTE SERVICES",
            "T1071": "APP LAYER COMM",
            "T1567": "EXFIL WEB SERVICES"
        }[tech]
        canvas.draw_text(x0 + 18, y0 + 40, descriptor, COLOR_BLACK)
    write_png(output_path, canvas)


def render_decision_tree(output_path: str) -> None:
    canvas = Canvas(WIDTH_DECISION, HEIGHT_DECISION, COLOR_WHITE)
    canvas.draw_text(260, 20, "EARLY RESPONSE DECISION TREE", COLOR_BLACK)

    def draw_box(x: int, y: int, text: str) -> Tuple[int, int, int, int]:
        w = 320
        h = 90
        canvas.fill_rect(x, y, x + w, y + h, (235, 242, 255))
        canvas.draw_rect(x, y, x + w, y + h, COLOR_DARK_GREY)
        lines = text.split("\n")
        text_y = y + 20
        for line in lines:
            canvas.draw_text(x + 20, text_y, line, COLOR_BLACK)
            text_y += 18
        return x, y, x + w, y + h

    start_box = draw_box(290, 80, "START")
    cred_box = draw_box(80, 210, "CRED THEFT\nSUSPECTED?")
    cred_action = draw_box(80, 340, "ROTATE MACHINE KEYS\nREFRESH APP POOL CREDS\nMONITOR TOKEN ISSUANCE")
    egress_box = draw_box(290, 210, "EGRESS\nCONFIRMED?")
    egress_action = draw_box(290, 340, "BLOCK DESTINATION\nCAPTURE PCAPS\nRUN OUTBOUND IOC SWEEP")
    webshell_box = draw_box(500, 210, "WEBSHELL\nFOUND?")
    webshell_action = draw_box(500, 340, "ISOLATE HOST\nPULL DISK AND MEMORY\nHUNT LATERAL MOVES")
    steady_state = draw_box(290, 440, "NO POSITIVE SIGNALS\nCONTINUE LOG REVIEW\nHARDEN SHAREPOINT FARM")

    def connect(box_from: Tuple[int, int, int, int], box_to: Tuple[int, int, int, int], label: str) -> None:
        x0 = (box_from[0] + box_from[2]) // 2
        y0 = box_from[3]
        x1 = (box_to[0] + box_to[2]) // 2
        y1 = box_to[1]
        canvas.draw_line(x0, y0, x0, y0 + 20, COLOR_DARK_GREY)
        canvas.draw_line(x0, y0 + 20, x1, y0 + 20, COLOR_DARK_GREY)
        canvas.draw_line(x1, y0 + 20, x1, y1, COLOR_DARK_GREY)
        if label:
            canvas.draw_text(min(x0, x1) + 10, y0 + 5, label, COLOR_BLACK)

    connect(start_box, cred_box, "YES")
    connect(start_box, egress_box, "NO → CHECK EGRESS")
    connect(cred_box, cred_action, "YES")
    connect(egress_box, egress_action, "YES")
    connect(egress_box, webshell_box, "NO → CHECK WEBSHELL")
    connect(webshell_box, webshell_action, "YES")
    connect(webshell_box, steady_state, "NO")
    connect(cred_box, egress_box, "NO")
    connect(egress_action, steady_state, "")
    connect(cred_action, steady_state, "")
    connect(webshell_action, steady_state, "")
    write_png(output_path, canvas)


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    attack_path = os.path.join(base_dir, "attack-mini.png")
    decision_path = os.path.join(base_dir, "decision-tree.png")
    render_attack_grid(attack_path)
    render_decision_tree(decision_path)
    print(f"Wrote {attack_path}")
    print(f"Wrote {decision_path}")


if __name__ == "__main__":
    main()

