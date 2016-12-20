"""
Generate a scatter plot 'coffee vs original'
"""

from collections import OrderedDict

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import brewer2mpl

import sys
import os


if len(sys.argv) != 3:
    print "Usage: python scatterplot.py directory-of-counted_flops.py directory-of-dats"
    sys.exit(0)

converter = {'original': 'plain', 'coffee': 'coffee-O4'}

problems = ['mass', 'helmholtz', 'elasticity', 'hyperelasticity']

# Bring 'flops' in scope
filename = os.path.join(sys.argv[1], 'counted_flops.py')
with open(filename, 'r') as f:
    content = f.read()
exec(content) in globals(), locals()

mapper = OrderedDict()
for (prob, mode, nf, q), v in flops.items():
    assert prob in problems

    # Bring 'timings' in scope
    filename = os.path.join(sys.argv[2], '%s.dat' % prob)
    retrieved = {}
    with open(filename, 'r') as f:
        content = f.read()
    results = eval(content)['timings']
    key = (q, q, prob, converter[mode])
    runtime = results[key]['nf %d' % nf]

    # Append (flops, runtime) for a <prob, nf, q> test case
    mapper.setdefault((prob, nf, q), {})[mode] = (v, runtime)


plt.style.use('ggplot')

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_ylabel(r'Speedup', fontsize=11, color='black')
ax.set_xlabel(r'Operation count ratio', fontsize=11, color='black')
ax.set_ylim([0.0, 5.0])
ax.set_xlim([1.0, 3.0])
ax.set_title("Scatter plot")

set2 = brewer2mpl.get_map('Set1', 'qualitative', 4).hex_colors
markers = ['x', 'v', '+', 'o']
legend_font = FontProperties(size='xx-small')

for (prob, nf, q), flops_by_mode in mapper.items():
    index = problems.index(prob)

    # Append (flops gain, speed up)
    flops_gain = flops_by_mode['original'][0] / float(flops_by_mode['coffee'][0])
    speedup = flops_by_mode['original'][1] / flops_by_mode['coffee'][1]

    # Plot the point
    print flops_gain, speedup
    ax.plot(flops_gain, speedup,
            marker=markers[index], ms=5*(nf + 1), mew=1, mec=set2[index])


ax.legend(loc='upper center', prop=legend_font, frameon=False,
          ncol=4, nrows=4, borderaxespad=-1.2)

plt.savefig('overview.pdf')
