
# import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LogNorm

# TODO: write me.
class RBH(pd.DataFrame):

    def __init__(self, filepath=None, sep="\t"):
        self._df = pd.read_csv(filepath, sep=sep)

        for attr, value in vars(self._df).items():
            setattr(self, attr, value)


    def plot(self):

        """
        Plots two graphs:
        - A heatmap of query and subject coverage.
        - A distribution plot of RBH normalised bit-scores.

        Takes the output tabular file from BLAST_RBH tool on Galaxy.
        Takes file path to the tabular file as positional argument.
        """

        rbh = self._df

        #normalise bitscore
        rbh["norm_bitscore"] = rbh.bitscore/rbh.length

        # Plot 2D density histograms

        # Calculate 2D density histograms for counts of matches at several coverage levels
        (H, xedges, yedges) = np.histogram2d(rbh.A_qcovhsp, rbh.B_qcovhsp, bins=20)

        # Create a 1x1 figure array
        fig, ax = plt.subplots(1, 2, figsize=(6, 6))

        # Plot histogram for RBBH
        his = ax[0].imshow(H, cmap=plt.cm.Blues, norm=LogNorm(),
                        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
                        origin='lower', aspect=1)
        ax[0].set_title("RBH")
        ax[0].set_xlabel("Query")
        ax[0].set_ylabel("Subject")

        # Add colourbar
        fig.colorbar(his, ax=ax[0])

        # Plot distribution of RBH bitscores
        sns.distplot(rbh.norm_bitscore, color="b", axlabel="RBH normalised bitscores", ax=ax[1])

        plt.show()
