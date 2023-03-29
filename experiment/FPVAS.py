#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 2 2022
@author: Roman Kessler, rkesslerx@gmail.com

"""


# imports

#from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
import sys  # handy system and path functions
import os
import random  # , itertools
from fpvas_utils import *
from catchers import *
import timeit
import gc  # garbage collection
import datetime
import numpy as np
import pandas as pd
import pickle
from shutil import rmtree
# sound, gui ... parallel war ausgeklammert
from psychopy import visual, core, data, event, logging
from psychopy import prefs  # noqa
prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']  # noqa 
from psychopy import sound, core
print('Using %s (with %s) for sounds' % (sound.audioLib, sound.audioDriver))


global emulation

emulation = True  # False
wait = np.inf

combined = False # is it combined EEG/NIRS?
                 # if True: - then few parallel port triggers, more LSL triggers
                 #          - forced breaks for BOLD to recover 
                 # if False: NO LSL triggers, more parallel port triggers
                 #          - no forced break for BOLD
                 
if combined:
    forcedBreak = 8  # a forced break of X seconds to ensure BOLD recovers
else:
    forcedBreak = 0

fixationPoint = False # if the fixation point should be shown

if len(sys.argv) > 1:
    modality = sys.argv[1]
    if len(sys.argv) > 2:
        n_start = int(sys.argv[2])
    else:
        n_start = 1 # corresponds to 0 in python counting logic
else:
    modality = "vision" # audio or vision
    n_start = 1 
    # start with a later trial, if a previous run was aborted

print(f"N arguments given: {len(sys.argv)}, starting {modality} version with trial {n_start}")

n_start -= 1

if not emulation:
    from psychopy import parallel # parallel
    from psychopy import gui
    from pylsl import StreamInfo, StreamOutlet # LSL


''' ########################### define stuff above this line ###################################################### '''

# set directory
_thisDir = os.path.dirname(os.path.abspath(__file__)) + os.sep
print(__file__)
print(_thisDir)
os.chdir(_thisDir)
sys.path.append(_thisDir)  # to be able to import custom functions

#info_df = pd.read_excel("trigger_codes.xlsx", dtype={'name':'str','trigger':np.int32,'duration':np.int32})
info_df = pd.read_csv("fpvas_trigger_codes.csv", dtype={'name':'str','trigger':np.int32,'duration':np.int32}, sep=";")
info_df["name"] = [int(i) if i.isdigit() else i for i in info_df.name.tolist()]

trigger = dict(zip(info_df.name, info_df.trigger))
pres_dur = dict(zip(info_df.name, info_df.duration))

# which frequencies should be used as base- and oddballfrequency?
if modality == "vision":
    frequency = {"base": 6., "oddball": 1.2, "oddball_position": 4} # was 6, 1.2, 4
elif modality == "audio":
    frequency = {"base": 3., "oddball": 3/4., "oddball_position": 3} # was 4, 1.333, 2
#frequency = {"base": 6., "oddball": 1.2, "oddball_position": 4}
#frequency = {"base": 4., "oddball": 4/3, "oddball_position": 2} # it should not be the last position in a trial, but at least the second last!!
#frequency = {"base": 3., "oddball": 1, "oddball_position": 2} # it should not be the last position in a trial, but at least the second last!!

# allowed combinations: 6, 1.2, 4 // 4, 4/3, 2  // 3, 1, 2
oddball_every_nth_stim = int(frequency["base"] / frequency["oddball"])


##################################### START #################################

def shutdown():
    win.close()
    core.quit()

def get_keypress():
    keys = event.getKeys()
    if keys and keys[0] == 'Esc':
        shutdown()
    elif keys:
        return keys[0]
    else:
        return None

def garbage():
    collected = gc.collect()
    # Prints Garbage collector as 0 object
    print("Garbage collector: collected",
          "%d objects." % collected)

# set participant info
if modality == "vision":
    expName = 'FPVS'  # from the Builder filename that created this script
    expInfo = {'participant': 'FPVS_', 'session': '001'}
elif modality == "audio":
    expName = 'FPAS'  # from the Builder filename that created this script
    expInfo = {'participant': 'FPAS_', 'session': '001'}

if not emulation:
    # GUI
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
    if not dlg.OK:
        core.quit()  # user pressed cancel
    # parallel port / trigger
    p_port = parallel.ParallelPort(address='/dev/parport0')
    p_port.setData(trigger["off"])
    # LSL stream
    if combined:
        info = StreamInfo(name='LSL_trigger', type='Markers', channel_count=1,
                  channel_format='int32', source_id='LSL_trigger')  # it's not 
        # Initialize the stream.
        outlet = StreamOutlet(info)
else:
    expInfo['participant'] = expInfo['participant'] + "000" #str(random.randint(1, 99999))

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

logpathname = _thisDir + os.sep + 'log' + \
              os.sep + 'sub_' + expInfo['participant'] + \
              '_sess_' + expInfo['session']

try:
    os.mkdir(logpathname)
except:
    print(f"Error: subject {expInfo['participant']} session {expInfo['session']} already exists, I delete it!")
    rmtree(logpathname)
    os.mkdir(logpathname)

logFile = logging.LogFile(
    logpathname +
    '/data.log',
    level=logging.EXP,
    filemode='w')
logging.console.setLevel(logging.CRITICAL)

# import the list of conditions to be run
#condition_file = "conditions/" + expInfo['participant'] + "_session_" + expInfo['session'] + ".pkl"
dfcond = pd.read_csv("conditions/" + modality + "_conditions.csv")
conds = dfcond[(dfcond["subject"] == int(expInfo['participant'][-3:])) & (dfcond["session"] == int(expInfo['session']))].reset_index(drop=True)
condition_list = list(conds.iloc[0][2:])
condition_list = [int(i) if i.isdigit() else i for i in condition_list]

#try:
#    with open(condition_file, "rb") as file:
#        condition_list = pickle.load(file)
#except:
#    print(f"Error: no participant information found in {condition_file}")

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# BEGIN

# CREATE EXPERIMENTAL WINDOW
grayvalue = [0, 0, 0]

# on presentation monitor
if not emulation:  # todo: check is this fits to the lab computer
    win = visual.Window(size=(1024, 768), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
                        monitor='testMonitor', color=grayvalue, colorSpace='rgb',
                        winType='pyglet',  # new: should be faster
                        blendMode='avg', useFBO=True, units='pix',
                        )
else:  # on MacBook (built-in display)
    win = visual.Window(size=(1024, 768), fullscr=False,  # Better timing can be achieved in full-screen mode.
                        screen=0, allowGUI=True, allowStencil=False,
                        monitor='testMonitor', color=grayvalue, colorSpace='rgb',
                        winType='pyglet',  # new: should be faster
                        blendMode='avg', useFBO=True, units='pix',
                        # waitBlanking (bool or None) – After a call to flip() should we wait for the blank before
                        # the script continues. this might help but need to understand it first
                        # https://groups.google.com/g/psychopy-users/c/hi_kpDClQFE
                        # https://discourse.psychopy.org/t/waitblanking-false-disables-time-tracking-for-win-flip
                        # /1550/2
                        )

# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()  # A
if expInfo['frameRate'] is not None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

print(f"frameRate: {expInfo['frameRate']}")
print(f"frameDur: {frameDur}")

screenfreq = 60.0
t_per_frame = 1000 / screenfreq
stim_freq = frequency["base"] #6.0  # Hz
frames_per_stim = screenfreq / stim_freq

#time_for_subcycle = 1 / stim_freq
#time_for_subcycle *= 0.85
#time_for_cycle = 0.8333  # 1 # in seconds # TODO: this should be below 5/6 (cycle duration), not below 6/6! This might have caused overtime issues in the past
#oddball_occ = 5  # every 5th stimulus is an oddball

# contrast estimates
con = create_contrast_values(frames_per_stim=frames_per_stim)  # only 10 values (1 cycle, 1/6 seconds), and some buffer
print(f"contrast values: {con}")
# contrast values for the fading in and out
#fading_cycles = 3
#fading_subcycles = 3 * 5
#N_fading_frames = fading_subcycles * 10  # 3s
#fading_values = np.concatenate(
#    (np.linspace(0., 1., N_fading_frames),
#     [1, 1, 1, 1, 1]),
#    axis=0)

# fixation point
if fixationPoint:
    fixation = visual.GratingStim(
        win, mask='circle', size=16, pos=[
            0, 0], sf=0, rgb=[
            1, 0, 0])
    fixation.setAutoDraw(True)

# introduction
introtext = visual.TextStim(
    win, text='',
    font='', pos=(0., -300.), depth=0, color=(1.0, 1.0, 1.0),
    colorSpace='rgb', opacity=1.0, contrast=1.0, units='', ori=0.0,
    height=None, antialias=True, bold=False, italic=False,
    anchorHoriz='center', anchorVert='center', fontFiles=(),
    wrapWidth=None, flipHoriz=False, flipVert=False, name=None, autoLog=None)

# catcher movie
if modality == "vision":
    movie = "videos/stars.mov"
    #starship(win, movie)

#while mov.status != constants.FINISHED:
#    #mov.draw()
#    win.flip()

# stop the movie
#mov.stop()

# clocks and timers
clock_exp = core.Clock()  # clocks start at 0, experiment clock
clock_run = core.Clock()  # clock for each run
# new: start countdown for minimal break time
countdown_forcedBreak = core.CountdownTimer(start=forcedBreak) # to bring BOLD down, also keep at beginning
        
# countdown_cycle = core.CountdownTimer(start=5/6) # one second per super-cycle
#countdown_subcycle = core.CountdownTimer(start=1/frequency["base"])
# set this clock as the default logging time reference
logging.setDefaultClock(clock_exp)

# save experiment info to logfile
now = datetime.datetime.now()
with open(logpathname + os.sep + 'experiment_infos.txt', 'a') as thefile: 
    thefile.write(str(now.year) + "_" +
              str(now.month) + "_" +
              str(now.day) + "_" +
              str(now.hour) + "_" +
              str(now.minute) + "_" +
              str(now.second) + "\n")
    for item in condition_list:
        thefile.write("%s, " % item)

# draw some cute picture for the waiting time
cuties = sorted(glob(_thisDir + "/imgs/colorful/*jpg"))
cuteStim = visual.ImageStim(win=win, name='cuteStim', units='pix',
         image=random.choice(cuties),
         mask=None,
         ori=0, pos=[0, 0], size=[512, 512],
         color=[1, 1, 1], colorSpace='rgb', opacity=1,
         flipHoriz=False, flipVert=False,
         texRes=128, interpolate=True, depth=0.0)
cuteStim.setImage(random.choice(cuties))

print(condition_list)
for cond_counter, cond in enumerate(condition_list):
    # skip, if we don't start with first trial
    if cond_counter < n_start:
        continue

    repeat = True  # to repeat from experimenter feedback after run
    while repeat:

        timings = []
        events = []  # todo: choose more computationally efficient way than a list?

        # define specialties of the different conditions
        if cond == "rossion": # VISUAL: face localizer
            stim_path = _thisDir + 'imgs' + os.sep + 'rossion' + os.sep
            stim_path_frequent = stim_path + "frequent" + os.sep
            stim_path_oddball = stim_path + "oddball" + os.sep
            scaling=False

        elif cond in [0, 25, 50, 75, 100]:  # VISUAL: morph grade: 0 fully Caucasian, 100: fully Asian
            stim_path = _thisDir + 'imgs' + os.sep + 'kessler' + os.sep
            stim_path_frequent = stim_path + "frequent" + os.sep
            stim_path_oddball = stim_path + "oddball_" + str(cond) + os.sep
            scaling=False

        elif cond == "own_100":  # VISUAL: morph grade: 100, own race
            stim_path = _thisDir + 'imgs' + os.sep + 'within_own' + os.sep
            stim_path_frequent = stim_path + "frequent" + os.sep
            stim_path_oddball = stim_path + "oddball" + os.sep
            scaling=False
            
        elif cond == "other_100":  # VISUAL: morph grade: 100, other race
            stim_path = _thisDir + 'imgs' + os.sep + 'within_other' + os.sep
            stim_path_frequent = stim_path + "frequent" + os.sep
            stim_path_oddball = stim_path + "oddball" + os.sep
            scaling=False
            
        elif cond == "humans":  # VISUAL: Human frequent, Ape rare
            stim_path = _thisDir + 'imgs' + os.sep + 'apes' + os.sep
            stim_path_frequent = stim_path + "humans_crops" + os.sep
            stim_path_oddball = stim_path + "apes_crops" + os.sep
            scaling=True
            
        elif cond == "apes":  # VISUAL: Ape frequent, Human rare
            stim_path = _thisDir + 'imgs' + os.sep + 'apes' + os.sep
            stim_path_frequent = stim_path + "apes_crops" + os.sep
            stim_path_oddball = stim_path + "humans_crops" + os.sep
            scaling=True
            
        elif "pair" in cond:  # AUDIO stimuli
            stim_path = _thisDir + 'sounds' + os.sep + "hh" + os.sep + cond[:5] + os.sep
            stim_path_frequent = stim_path + "frequent" + os.sep
            stim_path_oddball = stim_path + "oddball_" + str(cond[-3:]) + os.sep

        win.callOnFlip(timings.append, clock_exp.getTime())
        win.callOnFlip(events.append, trigger[cond])



        # create and buffer stimuli
        print(stim_path)
        print(f'condition {cond_counter + 1} of {len(condition_list)}')

        stimuli, stimuli_types = draw_stimuli(frequent_dir=stim_path_frequent,
                                              oddball_dir=stim_path_oddball,
                                              exp_dur=pres_dur[cond],
                                              base_freq=frequency["base"], #6.,
                                              oddball_proba=1/oddball_every_nth_stim, #1 / 5,
                                              oddball_position=frequency["oddball_position"],  # 4
                                              modality=modality) # modality is vision or audio

        TheStimulusList = []
        for s in stimuli:
            if modality == "vision":
                # variable stimulus size, depending on condition
                scale_factor = 1
                if scaling:
                    scale_factor *= np.random.uniform(low=0.8, high=1.2, size=None)
                TheStimulusList.append(
                    # CREATE STIMULUS OBJECT - VISION
                    visual.ImageStim(win=win, name='TheStimulus', units='pix',
                                     image=s,
                                     mask=None,
                                     ori=0, pos=[0, 0], size=[768*scale_factor, 768*scale_factor],
                                     color=[1, 1, 1], colorSpace='rgb', opacity=1,
                                     flipHoriz=False, flipVert=False,
                                     texRes=128, interpolate=True, depth=0.0))
            elif modality == "audio":
                    TheStimulusList.append(
                        sound.Sound(s, secs=0.3, hamming=True, blockSize=512, name='TheStimulus', autoLog=False)) # TODO: adj secs
                        # autoLog = False is important to avoid de-referencing of the stimulus list object which leads to blocking space on the soundcard
                    # new is the blocksize to avoid the sound ptb error --> haven't worked, audiodevice used instead
                    #audio.setVolume(1.0, log=False)
            
        Nstim = len(stimuli)
        print(f"total of {Nstim} stimuli created")
        
        # save single stimulus identities filenames to logfile
        with open(logpathname + os.sep + 'single_stimuli.txt', 'a') as thefile: 
            # condition
            for s, st in zip(stimuli, stimuli_types):
                thefile.write("%s,%s,%s\n" % (str(cond_counter), s, st) )
        
        # get the latest timepoints for each stimuli for presentation
        end_times = create_time_bins(
            stim_per_sec=frequency["base"], ##6,
            total_time=pres_dur[cond])  # TODO. stim_per_sec in variable
            
        if end_times.shape[0] != len(TheStimulusList):
            print("Error: End Times do not match number of stimuli created")

        # catcher movie
        if modality == "vision":
            movie = "videos/stars.mov"
            starship(win, movie)

        # introduction screen
        print('introduction')
        cuteStim.draw(win=win)
        introtext.setText(f'Runde #{cond_counter + 1} von {len(condition_list)} startet nach Knopfdruck!')
        introtext.draw()
        if fixationPoint:
            fixation.draw()
        win.flip()

        key = event.waitKeys(maxWait = wait)     # wait for a key press to continue
        if key == 'q':  # esc
            shutdown()
        win.flip()
        garbage()
        cuteStim.draw(win=win)
        win.flip()
        
        # check if BOLD is recovered
        print(f"waiting for BOLD to recover")
        while countdown_forcedBreak.getTime() > 0:
            core.wait(0.1)
        
        # send block triggers
        if not emulation:
            win.callOnFlip(p_port.setData, trigger[cond])  # pport
            if combined:
                win.callOnFlip(outlet.push_sample, x=[trigger[cond]])  # LSL
            cuteStim.draw()
            win.flip()
            win.callOnFlip(p_port.setData, trigger["off"])
            cuteStim.draw()
            win.flip()
        
        
        print('running')

        #fade_counter = 0
        #fadingOn = True  # are we in a fade-in or fade-out phase?

        # is this synchronous to the first stimulus?
        win.callOnFlip(clock_run.reset)
        # win.flip()

        for i, (TheStimulus, stim_type, end) in enumerate(
                zip(TheStimulusList, stimuli_types, end_times)):

            # send trigger & save timing
            if not emulation:
                #if fadingOn:
                #    win.callOnFlip(
                #        p_port.setData, trigger["fade_" + stim_type])
                #else:
                # Send the "frequent" and "oddball" triggers only via LSL, not PPort
                if not combined:
                    win.callOnFlip(p_port.setData, trigger[stim_type])
                else:
                    win.callOnFlip(outlet.push_sample, x=[trigger[stim_type]])

            #if fadingOn:
            #    win.callOnFlip(timings.append, clock_exp.getTime())
            #    win.callOnFlip(events.append, trigger["fade_" + stim_type])
            #else:
            win.callOnFlip(timings.append, clock_exp.getTime())
            win.callOnFlip(events.append, trigger[stim_type])

            if modality == 'audio':
                TheStimulus.play() # Todo: play on flip? # Todo: only play once at beginning of framecounter

            frame_counter = 0
            continueSubCycle = True

            while continueSubCycle:

                # check if super-cycle is already overtime
                #print(f"frame_counter: {frame_counter}")
                #print(f"clock_run.getTime: {clock_run.getTime()}, end: {end}")
                if frame_counter > 1:

                    if (clock_run.getTime() + frameDur) > end:
                        continueSubCycle = False
                        if modality == 'audio':
                            TheStimulus.stop()
                        #print("abort subcycle ")  # after this frame!
                        break

                frame_counter += 1  # this should work even tho it's now earlier

                if frame_counter == 2:
                    # turn trigger off
                    if not emulation:
                        win.callOnFlip(p_port.setData, trigger["off"])


                # fading in and out
                #if i < 15:  # first two full cycles
                #    print("fade_counter " + str(fade_counter))
                #    print("frame_counter ")
                #    print(frame_counter)
                #    TheStimulus.contrast = con[frame_counter - 1] * fading_values[fade_counter]
                #    fade_counter += 1
                #    fadingOn = True
                #elif i > (Nstim - 15):  # last two full cycles
                #    # the fade_counter is 1 to as counted to 120 in the
                #    # beginning
                #    TheStimulus.contrast = con[frame_counter - 1] * fading_values[fade_counter - 1]
                #    fade_counter -= 1
                #    fadingOn = True
                #else:  # just set the contrast
                if modality=='vision':
                    TheStimulus.contrast = con[frame_counter - 1]
                    #fadingOn = False
                    TheStimulus.draw(win=win)  # debug to test autodraw
                if fixationPoint:
                    fixation.draw()
                win.flip()

                # abort experiment if desired
                key = get_keypress()
                if key == 'q':  # esc
                    shutdown()

        # new: start countdown for minimal break time
        countdown_forcedBreak = core.CountdownTimer(start=forcedBreak) # to bring BOLD down

        # feedback from experimentor: was subject compliant?
        print('feedback')
        cuteStim.setImage(random.choice(cuties))
        cuteStim.draw()
        introtext.setText(
            "Trial verwenden?\n y = ja\n n = nein, wiederholen\n s = nein, skippen")
        introtext.draw()
        if fixationPoint:
            fixation.draw()
        win.flip()
        # wait for a key press to continue
        feedback_key = event.waitKeys(maxWait=wait, keyList=["y", "n", "s"])

    # if no answer given, assume it's a good trial
        if not feedback_key:
            feedback_key = ["y"]
        if feedback_key[0] == "y":
            if not emulation:
                # mark it as good, continue
                p_port.setData(trigger["good_trial"])
                if combined:
                    outlet.push_sample(x=[trigger["good_trial"]])
            win.callOnFlip(timings.append, clock_exp.getTime())
            win.callOnFlip(events.append, trigger["good_trial"])
            repeat = False
        elif feedback_key[0] == "s":
            if not emulation:
                # just mark it as bad, continue
                p_port.setData(trigger["bad_trial"])
                if combined:
                    outlet.push_sample(x=[trigger["bad_trial"]])
            win.callOnFlip(timings.append, clock_exp.getTime())
            win.callOnFlip(events.append, trigger["bad_trial"])
            repeat = False
        elif feedback_key[0] == "n":
            if not emulation:
                # mark it as bad, and repeat trial
                p_port.setData(trigger["bad_trial"])
                if combined:
                    outlet.push_sample(x=[trigger["bad_trial"]])
            win.callOnFlip(timings.append, clock_exp.getTime())
            win.callOnFlip(events.append, trigger["bad_trial"])
            repeat = True
        cuteStim.draw()
        win.flip()
        if not emulation:
            p_port.setData(trigger["off"])
        cuteStim.draw()
        win.flip()

        # append to logfile
        append_log(
            timings,
            events,
            logpathname +
            os.sep +
            'timings_events.txt')
        logging.flush()  # write to the official log file

        garbage()
win.close()
