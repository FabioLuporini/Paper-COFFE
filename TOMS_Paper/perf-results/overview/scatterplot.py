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
nfs = [0, 1, 2, 3]

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
    mapper.setdefault((prob, nf, q), {})[mode] = (int(v), runtime)


# Set up chart global properties
plt.style.use('ggplot')
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title("Correlation between flop reductions and achieved speed-ups", fontsize=12, y=1.03)
# x-axis
ax.set_xlabel(r'$\frac{\mathtt{baseline}\ \mathregular{flops}}{\mathtt{cfO2}\ \mathregular{flops}}$',
              fontsize=15, color='black', labelpad=6.5)
ax.set_xlim([0.0, 1.0])
ax.set_xscale('log')
# y-axis
ax.set_ylabel(r'Speedup relative to baseline', fontsize=12, color='black', labelpad=12.0)
ax.set_ylim([0.0, 1.0])

cm = brewer2mpl.get_map('Spectral', 'diverging', 4)
markers = ['v', '^', '<', '>']
legend_font = FontProperties(size='small')

# Add points
legend_points = []
for (prob, nf, q), flops_by_mode in mapper.items():
    index = problems.index(prob)
    flops_gain = flops_by_mode['original'][0] / float(flops_by_mode['coffee'][0])
    speedup = flops_by_mode['original'][1] / flops_by_mode['coffee'][1]

    if flops_gain > ax.get_xlim()[1]:
        ax.set_xlim([0.0, flops_gain + 1000])
    if speedup > ax.get_ylim()[1]:
        ax.set_ylim([0.0, speedup + 1.0])

    color = cm.hex_colors[nf]

    ax.plot(flops_gain, speedup,
            marker=markers[index], ms=3*q,
            mew=1, mfc=color, mec=color,
            clip_on=False)

    # Uber hack for fancy legend
    if nf == 0 and q == 1 and prob == 'mass':
        handle = ax.plot([], [], ms=0, mew=0, lw=0)[0]
        legend_points.append((handle, ''))
    if nf == 0 and q == 1:
        handle = ax.plot([], [], ms=0, mew=0, lw=0)[0]
        legend_points.append((handle, prob[:5]))
    if nf == 0 and prob == 'mass':
        handle = ax.plot([], [], ms=0, mew=0, lw=0)[0]
        legend_points.append((handle, '$\mathrm{q=%d}$' % q))
    if nf == 0:
        handle = ax.plot([], [],
                         marker=markers[index],
                         ms=3*q, mew=1, mfc='black', mec='black', lw=0)[0]
        legend_points.append((handle, ''))


# Colorbar
discrete_cm = cm.get_mpl_colormap().from_list('Custom cmap', cm.mpl_colors, len(nfs))
sm = plt.cm.ScalarMappable(cmap=discrete_cm, norm=plt.Normalize(0, 3))
sm._A = []
cbar = fig.colorbar(sm, ax=ax)
cbar.set_ticks(np.array([0, 1, 2, 3], dtype=np.int32))
cbar.set_ticklabels(np.array([r'$\mathrm{nf = 0}$', r'$\mathrm{nf = 1}$',
                              r'$\mathrm{nf = 2}$', r'$\mathrm{nf = 3}$']))

# Legend
def swap(l, i, j):
    tmp = l[i]
    l[i] = l[j]
    l[j] = tmp
swap(legend_points, 1, 2)
swap(legend_points, 2, 4)
swap(legend_points, 3, 6)
swap(legend_points, 4, 8)
swap(legend_points, 5, 8)

from IPython import embed; embed()

probs, qs = zip(*legend_points)
legend = ax.legend(probs, qs, loc='upper left', ncol=5, prop=legend_font,
                   numpoints=1)

plt.tight_layout()
plt.savefig('overview.pdf')
