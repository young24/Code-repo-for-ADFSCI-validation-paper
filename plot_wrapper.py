import platform
import numpy as np
import matplotlib.pyplot as plt
from functools import wraps
from matplotlib.axes._axes import Axes


class PlotWrapper(object):
    """
    This class is a wrapper for future plots to share similar attributes.
    """

    def __init__(self):
        self.font = "Avenir Next LT Pro" if platform.system() == "Windows" else "Avenir"
        self.bl_color: str = "#848484"
        self.exp_color1: str = "#E30F17"
        self.exp_color2: str = "#F6797F"
        self.lw: float = 2.5  # line_width
        self.hidden_lw: float = 0  # hidden line widths
        self.tick_font_size: float = 12
        self.title_font_size: float = 18
        self.axis_font_size: float = 14
        self.figsize: tuple = (10, 6)

        self.palette = [self.bl_color, self.exp_color1, self.exp_color2]

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, new_font):
        self._font = new_font
        plt.rcParams["font.family"] = self.font

    def clean_up_axes(self, ax) -> None:
        for _line in ["bottom", "left"]:
            ax.spines[_line].set_linewidth(self.lw)
        for _line in ["top", "right"]:
            ax.spines[_line].set_linewidth(self.hidden_lw)
        ax.tick_params(width=2, length=4, labelsize=self.tick_font_size)

    @classmethod
    def init_figure(cls, func):
        """
        Decorator function to initialize a figure before plotting.
        This is not needed if using super().plot().
        """

        @wraps(func)
        def _init(instance, *args, **kwargs):
            if hasattr(instance, "mosaic_string"):
                instance.fig, instance.ax = plt.subplot_mosaic(
                    instance.mosaic_string,
                    figsize=getattr(instance, "figsize", (10, 6)),
                    sharex=getattr(instance, "sharex", False),
                    sharey=getattr(instance, "sharey", False),
                    per_subplot_kw=getattr(instance, "per_subplot_kw", None),
                    gridspec_kw=getattr(instance, "gridspec_kw", None),
                    **kwargs,
                )
            elif hasattr(instance, "plot_3D"):
                instance.fig = plt.figure(
                    figsize=getattr(instance, "figsize", (10, 10))
                )
                instance.ax = instance.fig.add_subplot(111, projection="3d")
            else:
                instance.fig, instance.ax = plt.subplots(
                    nrows=getattr(instance, "nrows", 1),
                    ncols=getattr(instance, "ncols", 1),
                    figsize=getattr(instance, "figsize", (10, 6)),
                    sharex=getattr(instance, "sharex", False),
                    sharey=getattr(instance, "sharey", False),
                    width_ratios=getattr(instance, "width_ratios", None),
                    **kwargs,
                )
            return func(instance, *args, **kwargs)

        return _init

    @classmethod
    def plot_wrapper(cls, func):
        """
        Decorator function to call clean_up_axes() and fig.tight_layout()
        to any plot.
        """

        @wraps(func)
        def _plot(instance, *args, **kwargs):
            if isinstance(instance.ax, np.ndarray):
                for sub_ax in instance.ax.flat:
                    instance.clean_up_axes(sub_ax)
            elif isinstance(instance.ax, Axes):
                instance.clean_up_axes(instance.ax)
            elif isinstance(instance.ax, dict):
                for key in instance.ax.keys():
                    instance.clean_up_axes(instance.ax[key])

            instance.fig.tight_layout()

            return func(instance, *args, **kwargs)

        return _plot

class EmptyPlot(PlotWrapper):
    """
    Code to create an empty plot with styling and class attributes with preset styling
    """

    def __init__(self, **kwargs):
        super().__init__()

        # Placeholders for fig & ax that get instanced in the init_figure decorator
        self.fig: plt.Figure = None
        self.ax: plt.Axes | np.ndarray = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.plot()

    @PlotWrapper.init_figure
    @PlotWrapper.plot_wrapper
    def plot(self, *args, **kwargs):
        pass