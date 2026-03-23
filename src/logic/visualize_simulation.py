"""Render a time-lapse video of a simulated day of store activity.

Generates all data via the dataGenerator functions, then writes an MP4
showing customers (dots) flowing through the store over the course of
one business day (~7 AM – 10 PM), compressed into ~90 seconds of video.

Run from the project root:
    python -m src.logic.visualize_simulation
"""

import bisect
import sys
import os
from collections import defaultdict
from datetime import timedelta

import cv2
import numpy as np

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.logic.dataGenerator import (
    generate_store_and_aisles,
    generate_products,
    generate_customers,
    generate_checkouts_and_purchases,
    generate_paths,
    STORE_WIDTH,
    STORE_HEIGHT,
    ENTRANCE_X,
    ENTRANCE_Y,
    CHECKOUT_Y,
    CHECKOUT_X_POSITIONS,
    AISLE_CATEGORIES,
    SHELF_DEPTH,
)

# ── Video settings ────────────────────────────────────────────

SCALE = 10
MARGIN = 50
IMG_W = STORE_WIDTH * SCALE + 2 * MARGIN
IMG_H = STORE_HEIGHT * SCALE + 2 * MARGIN

SIM_STEP = 30
FPS = 20
DOT_RADIUS = 6

COL_FLOOR = (235, 238, 242)
COL_AISLE = (190, 190, 190)
COL_AISLE_BORDER = (130, 130, 130)
COL_CHECKOUT = (50, 190, 220)
COL_CHECKOUT_BORDER = (30, 150, 180)
COL_ENTRANCE = (60, 180, 60)
COL_DOT = (210, 140, 30)
COL_TEXT = (50, 50, 50)
COL_BG = (250, 250, 248)

OUTPUT_FILE = "store_simulation.mp4"


def grid_to_px(gx: float, gy: float) -> tuple[int, int]:
    """Convert grid (x, y) to pixel (col, row) with y-flip."""
    return (
        int(gx * SCALE + MARGIN),
        int((STORE_HEIGHT - gy) * SCALE + MARGIN),
    )


def draw_background(aisles) -> np.ndarray:
    """Render the static store layout once."""
    img = np.full((IMG_H, IMG_W, 3), COL_BG, dtype=np.uint8)

    floor_tl = grid_to_px(0, STORE_HEIGHT)
    floor_br = grid_to_px(STORE_WIDTH, 0)
    cv2.rectangle(img, floor_tl, floor_br, COL_FLOOR, -1)
    cv2.rectangle(img, floor_tl, floor_br, (0, 0, 0), 2)

    for i, aisle in enumerate(aisles):
        lx = aisle.bottom_left_x
        rx = aisle.top_right_x
        by = aisle.bottom_left_y
        ty = aisle.top_right_y

        left_tl = grid_to_px(lx, ty)
        left_br = grid_to_px(lx + SHELF_DEPTH, by)
        cv2.rectangle(img, left_tl, left_br, COL_AISLE, -1)
        cv2.rectangle(img, left_tl, left_br, COL_AISLE_BORDER, 1)

        right_tl = grid_to_px(rx - SHELF_DEPTH, ty)
        right_br = grid_to_px(rx, by)
        cv2.rectangle(img, right_tl, right_br, COL_AISLE, -1)
        cv2.rectangle(img, right_tl, right_br, COL_AISLE_BORDER, 1)

        cx_px = (grid_to_px(lx, 0)[0] + grid_to_px(rx, 0)[0]) // 2
        label_y = grid_to_px(0, ty)[1] - 8
        label = AISLE_CATEGORIES[i]["name"]
        sz = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
        cv2.putText(
            img, label, (cx_px - sz[0] // 2, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, COL_TEXT, 1, cv2.LINE_AA,
        )

    for x in CHECKOUT_X_POSITIONS:
        tl = grid_to_px(x - 3, CHECKOUT_Y + 1.5)
        br = grid_to_px(x + 3, CHECKOUT_Y - 1.5)
        cv2.rectangle(img, tl, br, COL_CHECKOUT, -1)
        cv2.rectangle(img, tl, br, COL_CHECKOUT_BORDER, 1)
        cp = grid_to_px(x, CHECKOUT_Y)
        sz = cv2.getTextSize("C", cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)[0]
        cv2.putText(
            img, "C", (cp[0] - sz[0] // 2, cp[1] + sz[1] // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA,
        )

    ep = grid_to_px(ENTRANCE_X, ENTRANCE_Y)
    cv2.arrowedLine(
        img, (ep[0], ep[1] + 25), (ep[0], ep[1] + 5),
        COL_ENTRANCE, 2, tipLength=0.4,
    )
    lbl = "ENTRANCE / EXIT"
    sz = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
    cv2.putText(
        img, lbl, (ep[0] - sz[0] // 2, ep[1] + 40),
        cv2.FONT_HERSHEY_SIMPLEX, 0.4, COL_ENTRANCE, 1, cv2.LINE_AA,
    )

    return img


def main():
    print("=== SimMart Day Simulation ===\n")

    print("[1/5] Generating store & products...")
    store, aisles = generate_store_and_aisles()
    products = generate_products(store.store_id, aisles)

    print("[2/5] Generating customers...")
    customers = generate_customers(store.store_id)

    print("[3/5] Generating checkouts & purchases...")
    checkouts, purchases = generate_checkouts_and_purchases(
        store.store_id, customers, products,
    )

    print("[4/5] Generating paths (this takes a moment)...")
    paths = generate_paths(customers, checkouts, purchases, products, aisles)

    print(
        f"       {len(customers):,} customers  |  {len(checkouts):,} checkouts  |  "
        f"{len(purchases):,} purchases  |  {len(paths):,} path points\n"
    )

    # ── Pre-index path points for fast per-frame lookup ───────

    raw: dict[int, list] = defaultdict(list)
    for p in paths:
        raw[p.customer_id].append((p.timestamp, p.location_x, p.location_y))

    cust_ts: dict[int, list] = {}
    cust_xs: dict[int, list] = {}
    cust_ys: dict[int, list] = {}
    for cid, pts in raw.items():
        pts.sort()
        cust_ts[cid] = [p[0] for p in pts]
        cust_xs[cid] = [p[1] for p in pts]
        cust_ys[cid] = [p[2] for p in pts]

    cust_enter = {c.customer_id: c.entered_at for c in customers}
    cust_exit = {c.customer_id: c.exited_at for c in customers}

    min_time = min(cust_enter.values())
    max_time = max(cust_exit.values())
    total_sim_secs = (max_time - min_time).total_seconds()
    num_frames = int(total_sim_secs / SIM_STEP) + 1
    video_secs = num_frames / FPS

    # ── Render ────────────────────────────────────────────────

    print(f"[5/5] Rendering {num_frames:,} frames @ {FPS} fps  "
          f"({video_secs:.0f}s video) ...")

    bg = draw_background(aisles)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (IMG_W, IMG_H))

    if not writer.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        alt = OUTPUT_FILE.replace(".mp4", ".avi")
        writer = cv2.VideoWriter(alt, fourcc, FPS, (IMG_W, IMG_H))
        print(f"       (mp4v unavailable — falling back to {alt})")

    peak_count = 0

    for fi in range(num_frames):
        cur_time = min_time + timedelta(seconds=fi * SIM_STEP)
        frame = bg.copy()

        count = 0
        for cid in cust_enter:
            if cust_enter[cid] > cur_time or cust_exit[cid] < cur_time:
                continue
            ts_list = cust_ts.get(cid)
            if not ts_list:
                continue

            idx = bisect.bisect_left(ts_list, cur_time)
            if idx >= len(ts_list):
                idx = len(ts_list) - 1
            elif idx > 0:
                dt_before = (cur_time - ts_list[idx - 1]).total_seconds()
                dt_after = (ts_list[idx] - cur_time).total_seconds()
                if dt_before < dt_after:
                    idx -= 1

            px, py = grid_to_px(cust_xs[cid][idx], cust_ys[cid][idx])
            cv2.circle(frame, (px, py), DOT_RADIUS, COL_DOT, -1, cv2.LINE_AA)
            count += 1

        peak_count = max(peak_count, count)

        time_str = cur_time.strftime("%I:%M %p")
        cv2.putText(
            frame, time_str, (IMG_W - 175, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, COL_TEXT, 2, cv2.LINE_AA,
        )
        cv2.putText(
            frame, f"Customers: {count}", (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, COL_TEXT, 1, cv2.LINE_AA,
        )

        writer.write(frame)

        if fi % 200 == 0 or fi == num_frames - 1:
            pct = (fi + 1) / num_frames * 100
            print(f"       {pct:5.1f}%  {time_str}  ({count} customers)")

    writer.release()
    print(f"\nDone!  Peak customers at once: {peak_count}")
    print(f"Video saved to: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()
