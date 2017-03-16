import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import math

class Plotter:
    def __init__(self):
        self.data = {}
        self.labels = {}
        self.no_runs = 0

    def add_time(self, key, time, err=0, output=False):
        if not key in self.data :
            self.data[key] = []
        self.data[key].append((time, err))
        self.no_runs = max(self.no_runs, len(self.data[key]))
        if output:
            label = self.labels[key] if key in self.labels else key
            print("{0}: {1}".format(label, time))

    def add_label(self, key, label):
        self.labels[key] = label

    def show(self):
        n_groups = self.no_runs 
        n_pergroup = len(self.data)
        n_half =  math.floor(n_pergroup / 2.0)

        fig, ax = plt.subplots()

        index = np.arange(n_groups)
        bar_width = 1 / (n_pergroup + 1)

        opacity = 0.4
        error_config = {'ecolor': '0.3'}

        i = 0
        for key, data in self.data.items():
            color = matplotlib.cm.Dark2(float(i + 1) / (n_pergroup + 1))
            label = self.labels[key] if key in self.labels else key
            for sub_i, datum in enumerate(data):
                plt.bar(sub_i + (i - n_half) * bar_width, datum[0], bar_width, alpha=opacity,
                        color=color, yerr=datum[1], error_kw=error_config,
                        label=(None if sub_i > 0 else label))
            i += 1

        plt.xlabel('Method')
        plt.ylabel('Time')
        plt.title('time per method')
        plt.xticks(index, ["run {0}".format(r) for r in range(1, n_groups + 1)])
        ax.legend(loc='best', fancybox=True, framealpha=0.5)

        plt.tight_layout()
        plt.show()
