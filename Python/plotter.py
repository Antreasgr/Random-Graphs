import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt


class Plotter:
    def __init__(self):
        self.data = {}
        self.labels = {}

    def add_time(self, key, time, err=0):
        self.data[key] = (time * 1000, err)

    def add_label(self, key, label):
        self.labels[key] = label

    def show(self):
        n_groups = len(self.data)
        fig, ax = plt.subplots()

        index = np.arange(n_groups)
        bar_width = 0.35

        opacity = 0.4
        error_config = {'ecolor': '0.3'}

        i = 0
        for key, datum in self.data.items():
            color = matplotlib.cm.Accent(float(i + 1) / (n_groups + 1))
            label = self.labels[key] if key in self.labels else key
            plt.bar(i, datum[0], bar_width, alpha=opacity,
                    color=color, yerr=datum[1], error_kw=error_config, label=label)
            i += 1

        plt.xlabel('Method')
        plt.ylabel('Time')
        plt.title('time per method')
        plt.xticks(index, [])
        ax.legend(loc='best', fancybox=True, framealpha=0.5)

        plt.tight_layout()
        plt.show()
