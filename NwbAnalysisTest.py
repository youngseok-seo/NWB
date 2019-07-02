#Retrieving sweep data from Prajay's NWB files

import h5py
import numpy as np
from AllenSDK.allensdk.ephys.ephys_extractor import EphysSweepFeatureExtractor


class NWBDataSet(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def get_sweep(self, sweep_number):

        with h5py.File(self.file_name, 'r') as f:

            stimulus_dataset = f['stimulus']['presentation']['ccss']['data']
            stimulus = stimulus_dataset.value[sweep_number]

            response_dataset = f['acquisition']['ccs']['data']
            response = response_dataset.value[sweep_number]

            stimulus_unit = stimulus_dataset.attrs['unit']

            sampling_rate = f['stimulus']['presentation']['ccss']['starting_time'].attrs['rate']

            return {
                'stimulus': stimulus,
                'response': response,
                'stimulus_unit': stimulus_unit,
                ''
                'sampling_rate': sampling_rate
            }

file_name = '/Users/youngseo/Documents/Research/nwb/18125012.nwb'
data_set = NWBDataSet(file_name)

sweep_data = data_set.get_sweep(24)

stimulus = sweep_data['stimulus']
response = sweep_data['response']

stimulus *= 1e12
response *= 1e3

sampling_rate = 10e4

t = np.arange(0, len(response)) * (1.0 / sampling_rate)

sweep_ext = EphysSweepFeatureExtractor(t=t, v=response, i=stimulus)
sweep_ext.process_spikes()

print("Avg spike threshold: %.01f mV" % sweep_ext.spike_feature("threshold_v").mean())
print("Avg spike width: %.02f ms" % (1e3 * np.nanmean(sweep_ext.spike_feature("width"))))



