## Nathan

nathanDistanceMap1.py

nathanHeatMap1.py

make a pixelated (chunk) heatmap from either (i) a vascular mask or (ii) a hcn4 distance map with each pixel being distance to vasculature

Assuming 15% trimming

raw (640,640) after 0.15% trim is (592,592)

# 20210322, now trimming 15% from all of left/top/right/bottom
#			ws previously just trimming the bottom
#trimming 48 left/top/right/bottom pixels
#original shape: (104, 640, 640)
#final shape: (104, 544, 544)
