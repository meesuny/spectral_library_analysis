
import pandas as pd
import numpy as np
import importlib.util
import glob
import os
import csv

def find_row_with_wavelengths(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for index, row in enumerate(reader):
            if 'Wavelengths' in row:
                return index

def get_surface_type(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for index, row in enumerate(reader):
            if 'Surface type' in row:
                return index

def get_surface_thickness(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for index, row in enumerate(reader):
            if 'Surface thickness (cm)' in row:
                return index
            
class spectral_library:
  def __init__(self, wl):
    self.spectra = np.zeros((0))
    self.spectra8b = np.zeros((0))
    self.spectra4b = np.zeros((0))
    self.wl = wl
    self.wl8b = np.asarray([443, 490 ,531 ,565, 610, 665, 705, 865])
    self.wl4b = np.asarray([490, 565, 665, 865])
    self.nBands = len(wl)
    self.nSpec = 0
    self.names = []
  def add(self, spec, name=''): 
    if len(self.spectra) == 0:
        self.spectra = spec
    else:
        self.spectra = np.row_stack((self.spectra, spec))
    self.names.append(name)
    self.nSpec = self.nSpec + 1
  def resample_planet8b(self):
    self.spectra8b = np.zeros((self.nSpec,8))
    band_ranges = [[431,451],[465,515],[513,549],[547,583],[600,620],[650,682],[697,713],[845,885]]
    for spec_idx in range(self.nSpec):
        for band_idx in range(8):
            low = band_ranges[band_idx][0]
            high = band_ranges[band_idx][1]
            val = 0
            count = 0
            idx_list = np.where((self.wl>low)*(self.wl<high))
            #print(idx_list)
            for i in idx_list[0]:
                #print(spec_idx)
                #print(i)
                #print(np.isfinite(self.spectra[spec_idx,i]))
                if np.isfinite(self.spectra[spec_idx,i]):
                    val = val + self.spectra[spec_idx,i]
                    count = count + 1
            if count>0:
                self.spectra8b[spec_idx,band_idx] = val/count
            else:
                self.spectra8b[spec_idx,band_idx] = np.NaN

                
def read_library(csv_files):
    idx = find_row_with_wavelengths(csv_files[0])
    df = pd.read_csv(csv_files[0], header=idx)
    wl = df.iloc[:, 0]
    sli = spectral_library(wl)
    
    # Iterate through each CSV file and perform the desired operations
    for csv_file in csv_files:
        #print (csv_file)
        idx = find_row_with_wavelengths(csv_file)
        surface_type_idx = get_surface_type(csv_file)
        surface_thickness_idx = get_surface_thickness(csv_file)
        if csv_file[-3:]=='csv':
            # read the spectra into a dataframe
            #idx = find_row_with_wavelengths(csv_file)
            df = pd.read_csv(csv_file, header=idx)
            surface_type_df = pd.read_csv(csv_file, skiprows=lambda x: x != surface_type_idx, header=None)
            surface_thickness_df = pd.read_csv(csv_file, skiprows=lambda x: x != surface_thickness_idx, header=None)
            # add to the spectral library
            for i, (col_name) in enumerate(df.columns[1:]):
                try:
                    #print(col_name, surface_type_df.loc[0,i+1])
                    if ('S' in str(surface_type_df.loc[0,i+1])) or ('P' in str(surface_type_df.loc[0,i+1])):
                    #if (surface_type_df.loc[0,i] != 'NaN'):
                        name = col_name + '-' + surface_type_df.loc[0,i+1].strip()
                    else:
                        name = col_name
                    sli.add(df[col_name], name) #+'_S' or '_P' depending on snow or pond)
                    #print(name)
                except:
                    name = col_name
                    sli.add(df[col_name], name)
                ##### RECORD IN MEMORY WHETHER THE ALBEDO IS SNOW OR POND AS WELL AS THE DEPTH/THICKNESS #####
            #print('Done:', csv_file)
    return sli
                