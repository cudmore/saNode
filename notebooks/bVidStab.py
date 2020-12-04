from vidstab import VidStab
import matplotlib.pyplot as plt

inPath = '/media/cudmore/data/20201124/1_cropped.avi'
outPath = '/media/cudmore/data/20201124/1_cropped_stab.avi'

inPath = '/media/cudmore/data/20201124/1_cropped_bs.avi'
outPath = '/media/cudmore/data/20201124/1_cropped_bs_stab.avi'

stabilizer = VidStab()
stabilizer.stabilize(input_path=inPath, output_path=outPath)

stabilizer.plot_trajectory()
plt.show()

stabilizer.plot_transforms()
plt.show()
