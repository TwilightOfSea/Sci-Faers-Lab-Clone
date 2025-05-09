import warnings

warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from venn import venn 
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    signal_tmp_df = pd.read_excel(data_path)
    # Apply filters to get the sets
    # ror_set = set(ror_choose(signal_tmp_df).index)
    ror_set = set(signal_tmp_df[(signal_tmp_df['a'] >= 3) & (signal_tmp_df['low_95cl_ror'] > 1)].index)
    # prr_set = set(prr_choose(signal_tmp_df).index)
    prr_set = set(signal_tmp_df[(signal_tmp_df['a'] >= 3) & (signal_tmp_df['prr'] >= 2) & (signal_tmp_df['x_sq'] >= 4)].index)
    # gps_set = set(gps_choose(signal_tmp_df).index)
    gps_set = set(signal_tmp_df[ (signal_tmp_df['ebgm05'] > 2)].index)
    # bcpnn_set = set(bcpnn_choose(signal_tmp_df).index)
    bcpnn_set = set(signal_tmp_df[ (signal_tmp_df['IC025'] > 0)].index)
    # Create a dictionary of sets for the venn library
    sets = {
        'ROR': ror_set,
        'PRR': prr_set,
        'MGPS': gps_set,
        'BCPNN': bcpnn_set
    }

    # Plot the Venn diagram
    plt.figure(figsize=(10, 10))
    venn(sets)
    plt.title("Venn Diagram of Signal Conditions")
    plt.savefig(output_path)
    plt.show()