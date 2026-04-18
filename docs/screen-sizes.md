# Supported screen sizes

| Layout file              | W   | H   | Shape  | Scale | Notes                              |
| ------------------------ | --- | --- | ------ | ----- | ---------------------------------- |
| `round_240.yaml`         | 240 | 240 | round  | 0.75  | Small round panels                 |
| `round_360.yaml`         | 360 | 360 | round  | 1.00  | Reference target (Waveshare 1.85") |
| `square_240.yaml`        | 240 | 240 | square | 0.75  | Cheap square panels                |
| `square_320.yaml`        | 320 | 320 | square | 0.90  |                                    |
| `tall_240x320.yaml`      | 240 | 320 | tall   | 0.80  | Portrait                           |
| `tall_240x536.yaml`      | 240 | 536 | tall   | 0.85  | LilyGo T-Display-S3 AMOLED 1.91" (portrait) |
| `wide_480x320.yaml`      | 480 | 320 | wide   | 1.00  | 3.5" landscape TFT                 |
| `wide_536x240.yaml`      | 536 | 240 | wide   | 0.85  | LilyGo T-Display-S3 AMOLED 1.91" (landscape; needs `rotation: 90`) |

Adding a new size? See [`authoring-a-layout.md`](./authoring-a-layout.md)
and append a row above.
