## Recipe to manually annotate vessel diameter with Fiji

### Overview

For now, I have uploaded one SAN prep dataset. This has endothelial cells labeled with CD31 (channel 2) and cardiac myocytes labeled with HCN4 (channel 1).

I started tracing a few lines along the main artery at the top of the stack and saved the ROIs as RoiSet.zip

    /SAN3/tracing/SAN3_head_BIG__ch1.tif
    /SAN3/tracing/SAN3_head_BIG__ch2.tif
    /SAN3/tracing/RoiSet.zip

Each large .tif stack is a fused stack from the .tif file grids coming off the fv3000. Please note, I have chosen to not pre-process these stacks, there will be some discrepancies at boundaries between the original stacks. For example, alignment and intensity. We can 'use or eyes' to get beyond this much better than any algorithm.

### Definitions

#### Vessel Segment: A vascular tube between branch points.

### Recipe

Open .tif stack in Fiji (use the _ch2.tif stack)

Open 'ROI Manager'

**Important**, remember to open any existing RoiSet.zip

Starting with the main artery (usually runs from top to bottom)

Select the `line` tool and draw a line representing the vessel diameter.

Add newly drawn line ROI to ROI manager with keyboard `t`.

Once all diameters are drawn for a given 'Vessel Segment', select the set of ROIs corresponding to the new segment (in the ROI manager list), and specify a `Group` with `Properties...`.

This is **important**, each Group represents the branch order from primary artery (Group 1), to first branch (Group 2), to the second branch (Group3), etc, etc.

Groups are integers as follows
 - 1: primary artery
 - 2: first branch
 - 3: second branch
 - 4: third branch

If there is what seems to be an intermediate branch, for example
	between groups 1 and 2, then name it 11
	between groups 3 and 4, then name it 33

### Save ROIs

**Important** ... Select all ROIs in ROI manager

Click button `More >> Save`. This will save 'RoiSet.zip'

As your working, each time you save just replace the previous file. Make sure you save it in the proper /tracing folder, for example SAN3/tracing

### Hints

- When in 'line draw' mode, hold the `spacebar` to activate dragging the image with left-mouse-click-drag.
- When saving ROIs be sure to select all the ROIS in the list.
- Be sure to check your z-plane. Scroll up/down to verify a vessel is emanating from your vessel of interest. It is often the case that what looks like a branch in one plane is actually another vessel passing above/below your vessel of interest.
- Don't worry if your overall 'vessel segments' are out of order. For example, feel free to go way down into inferior and trace a 3rd order 'vessel segment' and then jump back up to superior and trace a 2nd order 'vessel segment'.
- That said, within a 'vessel segment', create successive line ROIs and add them to the ROI manager (keyboard t) in the order along the vessel. If this is done properly, we can extract an estimate of 'vessel segment length' and 'vessel segment tortuosity' in post analysis.
- Have fun
