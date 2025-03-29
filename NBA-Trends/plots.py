import numpy as np
import pandas as pd
from pandas import DataFrame
from plotnine.ggplot import ggplot
from plotnine import (
    aes,
    labs,
    geom_density,
    theme,
    theme_xkcd,
    # theme_538,
    guide_legend,
    guides,
    element_text,
    element_blank,
    element_rect,
    scale_fill_manual,
    scale_x_continuous,
    # scale_x_discrete,
    scale_y_continuous,
    geom_point,
    geom_smooth,
    scale_color_manual,
    # facet_wrap,
)
from mizani.formatters import percent_format

colors = [
    '#0057e7',
    '#d62d20',
    '#008744',
    '#ffa700',
    # '#f4522b',
    '#4d1b7b',
]


def plt_dist(df1: DataFrame, var: str, group: str):
    scale_x = []
    kwargs_legend = {"alpha":0.0}
    if "%" in var:
        scale_x = scale_x_continuous(labels=percent_format())
        if var == "FT %":
            limits = [.50,1.00]
            scale_x = scale_x_continuous(labels=percent_format(), limits = limits)
    elif var in ["ORtg","DRtg"]:
        x_breaks = np.arange(90,140,5)
        x_labels = list(x_breaks.astype(str))
        # scale_x = scale_x_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
        scale_x = scale_x_continuous(limits = [x_breaks[0],x_breaks[-1]])
    elif var in ["NRtg"]:
        x_breaks = np.arange(-25,25,5)
        x_labels = list(x_breaks.astype(str))
        scale_x = scale_x_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
    plot = (
        ggplot(df1)  
        + geom_density(
            aes(x=var,fill=group),
            alpha=0.5,
        )
        + scale_fill_manual(values=colors)
        + scale_x
        + labs(
            x=var,
            y="Frequency",
            title=f"NBA Stat Distribution:  {var}",
            caption="@sradjoker",
        )
        + theme_xkcd(base_size=14)
        + theme(
            plot_title=element_text(face="bold", size=22),
            plot_subtitle=element_text(size=14),
            plot_margin=0.025,
            figure_size=[8,6]
        )
        + theme(
            legend_title=element_blank(),
            legend_position = [0.82,0.78],
            legend_box_margin=0,
            legend_background=element_rect(color="grey", size=0.001,**kwargs_legend),
            legend_box_background = element_blank(),
            legend_text=element_text(size=12),
        )
        +  guides(fill=guide_legend(ncol=1))
    )

    return plot

def plt_trends(df1: DataFrame, var: str, group: str):
    scale_y = []
    kwargs_legend = {"alpha":0.0}
    if "%" in var:
        scale_y = scale_y_continuous(labels=percent_format())
        if var == "FT %":
            limits = [.50,1.00]
            scale_y = scale_y_continuous(labels=percent_format(), limits = limits)
    elif var in ["ORtg","DRtg"]:
        x_breaks = np.arange(90,140,5)
        x_labels = list(x_breaks.astype(str))
        # scale_y = scale_y_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
        scale_y = scale_y_continuous(limits = [x_breaks[0],x_breaks[-1]])
    elif var in ["NRtg"]:
        x_breaks = np.arange(-25,25,5)
        x_labels = list(x_breaks.astype(str))
        scale_y = scale_y_continuous(breaks=x_breaks, labels= x_labels, limits = [x_breaks[0],x_breaks[-1]])
    plot = (
        ggplot(df1,aes(x="Games Played",y=var,color=group))  
        + geom_point()
        + geom_smooth(size=2,se=False,method="lowess", alpha=0.5,span=0.5)
        # + facet_wrap(facets = "~ Player Season",ncol=1)
        + scale_color_manual(values=colors)
        + scale_y
        + labs(
            x="Games Played",
            y=var,
            title=f"NBA Stat Trends:  {var}",
            caption="@sradjoker",
        )
        + theme_xkcd(base_size=14)
        # + theme_538(base_size=14)
        + theme(
            plot_title=element_text(face="bold", size=22),
            plot_subtitle=element_text(size=14),
            plot_margin=0.025,
            figure_size=[8,6]
        )
        + theme(
            legend_title=element_blank(),
            legend_position = [0.82,0.78],
            legend_box_margin=0,
            legend_background=element_rect(color="grey", size=0.001,**kwargs_legend),
            legend_box_background = element_blank(),
            legend_text=element_text(size=12),
        )
        +  guides(color=guide_legend(ncol=1))
    )

    return plot  