#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 11:57:45 2022

experimental utils for FPVS (new from scratch implementation)

@author: kessler
"""

import numpy as np
from glob import glob
import random
from psychopy import visual


def test_func():
    print("blub")
    

def create_contrast_values(frames_per_stim):
    """
    Returns
    -------
    contrast_values : TYPE
        returns one list of contast values for stimulus presentation
        for one cycle (1/6 s), from 0 to 1 to 0.
    """
    half_frames = int(frames_per_stim/2)
    a = list(range(half_frames))
    b = [np.pi / half_frames * i for i in a]
    c = (np.cos(b) + 1) / 2
    contrast_values = np.concatenate([1-c, c, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]) # the list of zeros for buffer
    return contrast_values



def draw_stimuli(frequent_dir, oddball_dir, exp_dur, base_freq=6., oddball_proba=1/5, oddball_position=4,
                 #nstim_fadein=15, nstim_fadeout=30)
                 modality="vision",
                 ):
    """
    Assuming the following: 6Hz base rate, 
                    1.2Hz oddball rate (every 5th stimulus)
    
    Parameters
    ----------
    frequent_dir : string
        Directory which contains all possible images for presentation.
    oddball_dir : string
        Directory which contains all possible images for presentation.
    exp_dur: int
        total duration of the experiment.
    base_freq: float
        base stimulation frequency
    oddball_proba: float
        probability of oddball occurence (per stimulus onset)

    Returns
    -------
    stimuli : list
        list of presented stimuli

    """
    if modality == "vision":
        frequent_files = sorted(glob(frequent_dir + "*jpg") + glob(frequent_dir + "*png"))
        oddball_files  = sorted(glob(oddball_dir + "*jpg") + glob(oddball_dir + "*png"))
    elif modality == "audio":
        frequent_files = sorted(glob(frequent_dir + "*wav"))
        oddball_files  = sorted(glob(oddball_dir + "*wav"))
        
    #n_frequent_files = len(frequent_files)
    #n_oddball_files = len(oddball_files)
    
    n_stimuli_total = exp_dur * base_freq
    n_stimuli_frequent = n_stimuli_total * (1-oddball_proba)
    n_stimuli_oddball  = n_stimuli_total * oddball_proba
    
    #if not n_stimuli_frequent.is_integer():
    #    print("warning: number of stimuli doesn't follow the programmed logic!")
    #if (n_stimuli_frequent > n_frequent_files) or (n_stimuli_oddball > n_oddball_files):
    #    print("warning: more hypothetical stimuli needed than actually provided in the dataset")

    frequent_stimuli = np.random.choice(a=frequent_files, size=int(n_stimuli_frequent), replace=True)
    oddball_stimuli = np.random.choice(a=oddball_files, size=int(n_stimuli_oddball), replace=True)
    
    # 2-back no stimulus repetition (only vision, in audio we don't have that many files)
    #if modality == "vision":
    #    while not valid_single_spacing(frequent_stimuli):
    #        frequent_stimuli = np.random.choice(a=frequent_files, size=int(n_stimuli_frequent), replace=True)
    #    while not valid_single_spacing(oddball_stimuli):        
    #        oddball_stimuli = np.random.choice(a=oddball_files, size=int(n_stimuli_oddball), replace=True)

    # concatenate the two lists, so that every n-th position is an oddball
    stimuli_types_frequent = np.repeat("frequent", n_stimuli_frequent).tolist()
    stimuli_types_oddball = np.repeat("oddball", n_stimuli_oddball).tolist()
    
    stimuli = []
    stimuli_types = []
    
    oddball_every = int(1 / oddball_proba)
    odd_counter = 0
    odd_pos_python = oddball_position - 1 # one less than the actual oddball position, as python counts from 0
    for i, (stim, stim_type) in enumerate(zip(frequent_stimuli, stimuli_types_frequent)):
        if i % (oddball_every - 1) == odd_pos_python: # as i'm only counting the freq positions, i MOD 4 instead of 5
            stimuli.append(oddball_stimuli[odd_counter])
            stimuli_types.append(stimuli_types_oddball[odd_counter])
            odd_counter += 1
        
        stimuli.append(stim)
        stimuli_types.append(stim_type)
        
    # replace the oddball stimuli of fade-in and fade-out period with frequent stimuli
    #for i, (stim, stim_type) in enumerate(zip(stimuli, stimuli_types)):
    #    if stim_type == "oddball":
    #        if (i < nstim_fadein) or (i > (len(stimuli) - nstim_fadeout - 1)):
    #            new_stim = np.random.choice(a=frequent_files, size=1, replace=True)[0]
    #            stimuli[i] = new_stim
    #            stimuli_types[i] = "frequent"
                
            # also check for repetitions, TODO
    
    return stimuli, stimuli_types



def statistics_on_image_properties(imagelist):
    """

    Parameters
    ----------
    imagelist : list of pathnames to images
        Load all images, and compare statistical image properties such as
        luminance, spatial frequencies, contrasts,.. between both groups,
        frequent stimuli and oddball stimuli.

    Returns
    -------
    dict of statistical properties, or binary variable if the groups are
    statistically not different.

    """
    a = 1
    return a
    


#def reset_cycle_clocks(clock):

#def append_list(t, e):
#    timings.append(t)
#    events.append(e)
    

def append_log(timings, events, filename):
    
    thefile = open(filename, 'a')
    for t, e in zip(timings, events):
      thefile.write("%s,%s\n" %(t, e)) # is it written as intended, not as string?
    thefile.close()



def valid_duplicate_spacing(x):
    for i, elem in enumerate(x):
        if elem in x[i+1:i+3]:
            return False
    return True

def valid_single_spacing(x):
    for i, elem in enumerate(x):
        if elem in x[i+1:i+2]:
            return False
    return True

def create_time_bins(stim_per_sec = 6, total_time = 30):
    bin_left_edges = np.linspace(0, total_time, total_time * int(stim_per_sec), endpoint=False)
    bin_width = bin_left_edges[1] - bin_left_edges[0]
    bin_right_edges = bin_left_edges + bin_width
    return bin_right_edges

"""
# debug
frequent_dir = "/data/tu_kessler/PRAWN/experiment/imgs/rossion/frequent/"
oddball_dir = "/data/tu_kessler/PRAWN/experiment/imgs/rossion/oddball/"
exp_dur = 30
base_freq=6
oddball_proba=1/5

"""