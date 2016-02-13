import matplotlib
import numpy
import pandas


def visualize_orders(data_dict, cvs_file):
    odf = pandas.DataFrame.from_csv(cvs_file, encoding='utf-8')
