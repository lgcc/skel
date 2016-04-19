import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import numpy as np


def display(points, codes=None):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # if not isinstance(points, np.ndarray):
    #     points = np.array(points)

    # x, y = points[:,0], points[:,1]
    x = [a for a, _ in points]
    y = [b for _, b in points]

    # aff2d = transforms.Affine2D()
    # aff2d.scale(1,-1)
    # ax.transScale.set(transforms.BlendedAffine2D(transforms.IdentityTransform(), aff2d))

    if codes:
        path = Path(points, codes)
        patch = patches.PathPatch(path, ec='.5', fill=False, fc='.75', lw=1)
        ax.add_patch(patch)

    else:
        # Draw polyline
        ax.plot(x, y)

    # Draw scatter points
    ax.scatter(x, y)

    # # Set tick limit
    # margin_factor = .2
    # xlim_range = min(x) * (1 - margin_factor), max(x) * (1 + margin_factor)
    # ylim_range = min(y) * (1 - margin_factor), max(y) * (1 + margin_factor)
    # ax.set_xlim(*xlim_range)
    # ax.set_ylim(*ylim_range)

    ax.set_aspect(1)

    # plt.show()
    return plt


def display_multi(segs):
    """
    Draw all in one ax
    """

    points = reduce(lambda x, y: x.extend(y) or x, segs, [])
    codes = [Path.LINETO] * len(points)
    codes[0] = Path.MOVETO

    cnt = 0
    for s in segs:
        codes[cnt] = Path.MOVETO
        cnt += len(segs)

    plt = display(points, codes)
    return plt


def display_sep(segs, codes=None):
    fig = plt.figure()

    num = int(np.ceil(np.sqrt(len(segs))))

    for i in range(len(segs)):
        ax = fig.add_subplot(num, num, i+1)
        points = segs[i]

        # if not isinstance(points, np.ndarray):
        #     points = np.array(points)

        # x, y = points[:,0], points[:,1]
        x = [a for a, _ in points]
        y = [b for _, b in points]

        # # ? upside down (I do not known a better way to do this for now)
        # for j in range(len(y)):
        #     y[j] = 600 - y[j]
        #     points[j] = (x[j], y[j])

        # aff2d = transforms.Affine2D()
        # aff2d.scale(1,-1)
        # ax.transScale.set(transforms.BlendedAffine2D(transforms.IdentityTransform(), aff2d))

        if codes:
            path = Path(points, codes)
            patch = patches.PathPatch(path, ec='.5', fill=False, fc='.75', lw=1)
            ax.add_patch(patch)

        else:
            # Draw polyline
            ax.plot(x, y)

        # Draw scatter points
        ax.scatter(x, y)

        # Set tick limit
        margin_factor = .3
        xlim_range = min(x) * (1 - margin_factor), max(x) * (1 + margin_factor)
        ylim_range = min(y) * (1 - margin_factor), max(y) * (1 + margin_factor)
        ax.set_xlim(*xlim_range)
        ax.set_ylim(*ylim_range)

        # ax.set_aspect(1)

    # plt.show()
    return plt


if __name__ == '__main__':
    segs = [[(10, 10), (100, 100)], [(50, 100), (100, 10)]]
    points = [(10, 10), (100, 100), (10, 100), (100, 10)]

    # plt = display_multi(segs)
    # plt = display(points)
    plt = display_sep(segs)

    plt.show()
