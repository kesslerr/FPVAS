
import numpy as np
from glob import glob
import random
#from psychopy import visual
from psychopy import visual, core, event, constants

def starship(win, moviepath):

    # window to present the video
    #win = visual.Window((800, 600), fullscr=False)

    # create a new movie stimulus instance
    #mov = visual.MovieStim(  
    #    win,
    #    moviepath,    # path to video file
    #    size=(int(1920/2), int(1080/2)),  #(512, 512),
    #    flipVert=False,
    #    flipHoriz=False,
    #    loop=True,
    #    noAudio=True, # WAS False
    #    volume=0.1,
    #    autoStart=False)
    mov = visual.MovieStim3(  
        win,
        moviepath,    # path to video file
        size=(int(1920/2), int(1080/2)),  # (512, 512),
        flipVert=False,
        flipHoriz=False,
        loop=True,
        noAudio=True,
        #volume=0.1,
        #autoStart=False
        )
    # print some information about the movie
    #print('orig movie size={}'.format(mov.frameSize))
    #print('orig movie duration={}'.format(mov.duration))

    # instructions
    #instrText = "`s` Start/Resume\n`p` Pause\n`r` Restart\n`y` Stop and Exit"
    #instr = visual.TextStim(win, instrText, pos=(0., -300.), units='', ori=0.0,)

    # main loop
    while mov.status != constants.FINISHED:
        # draw the movie
        mov.draw()
        # draw the instruction text
        #instr.draw()
        # flip buffers so they appear on the window
        win.flip()

        # process keyboard input
        if event.getKeys('y'):   # exit
            break
            #mov.stop()
        elif event.getKeys('s'):  # play/start
            mov.play()
        elif event.getKeys('p'):  # pause
            mov.pause()
        elif event.getKeys('r'):  # restart/replay
            mov.replay()
        #elif event.getKeys('m'):  # volume up 5%
        #    mov.volumeUp()
        #elif event.getKeys('n'):  # volume down 5%
        #    mov.volumeDown()

    # stop the movie, this frees resources too
    #mov.stop()
    

# rainbows

def rainbows(win, moviepath="movies/rainbows.mov"):
    mov = visual.MovieStim3(  
        win,
        moviepath,    # path to video file
        size=(int(1920/2), int(1080/2)),  # (512, 512),
        flipVert=False,
        flipHoriz=False,
        loop=False,  # True,
        noAudio=True,
        )

    # main loop
    while mov.status != constants.FINISHED:
        # draw the movie
        mov.draw()
        # flip buffers so they appear on the window
        win.flip()

        # process keyboard input
        if event.getKeys('y'):   # exit
            break
            #mov.stop()
        elif event.getKeys('s'):  # play/start
            mov.play()
        elif event.getKeys('p'):  # pause
            mov.pause()
        elif event.getKeys('r'):  # restart/replay
            mov.replay()

# trees
def trees(win, moviepath="movies/trees.mov"): 
    rainbows(win, moviepath)
    