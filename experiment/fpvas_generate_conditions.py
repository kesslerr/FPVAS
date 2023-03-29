#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 17:00:30 2023

script to create sequence of conditions for each subject

@author: roman
"""
import numpy as np
import pandas as pd
import random
import pickle
random.seed(42)
import os
from shutil import rmtree
os.chdir("/Users/roman/GitHub/PRAWN/experiment")
if not os.path.isdir("conditions"):
	pass
else:
	rmtree("conditions")
os.makedirs("conditions")

def flatten(l):
    return [item for sublist in l for item in sublist]

Nsubs = 20;
Nsess = 10;


# VISION (old)
"""
conditions_vision = ["rossion",
					  100,
					  50,
					  0,
					  ]
Nrep_vision = 8
N_blocks_vision = Nrep_vision * len(conditions_vision)


ll = []
for i in range(Nsubs):
	for s in range(Nsess):
		l = flatten([random.sample(conditions_vision, len(conditions_vision)) for i in range(Nrep_vision)])
		sub_string = str(i).zfill(3)
		sess_string = str(s+1).zfill(3)
		ll.append([sub_string, sess_string] + l)
		#with open("condition_orders/FPVS_" + sub_string + "_session_" + sess_string + ".pkl", "wb") as file:
		#	pickle.dump(l, file)

vision_df = pd.DataFrame(columns=["subject", "session"] + ["block_" + str(i) for i in range(1,N_blocks_vision+1)], data=ll)
vision_df.to_csv("conditions/vision_conditions.csv", index=False)
"""
# AUDIO


conditions_audio = [#"pair1_100",
								#"pair2_100",
								#"pair3_100",
								#"pair4_100",
								"pair5_100",
								"pair6_100",
								#"pair1_050",
								#"pair2_050",
								#"pair3_050",
								#"pair4_050",
								#"pair5_050",
								#"pair6_050",
								#"pair1_000",
								#"pair2_000",
								#"pair3_000",
								#"pair4_000",
								#"pair5_000",
								#"pair6_000",
								]
Nrep_audio = 15
N_blocks_audio = Nrep_audio * len(conditions_audio)

ll = []
for i in range(Nsubs):
	for s in range(Nsess):
		# new: with restrictions on the sampling
		sub_string = str(i).zfill(3)
		sess_string = str(s+1).zfill(3)

		diff_conditions = ["100"] #"050", , "000" 
		rep_per_diff_condition = np.unique([i for i in conditions_audio if "100" in i]).shape[0] * Nrep_audio
		l = flatten([random.sample(diff_conditions, len(diff_conditions)) for i in range(rep_per_diff_condition)])

		pairs = ["pair5", "pair6"]
		pairs_100_order = flatten([random.sample(pairs, len(pairs)) for i in range(Nrep_audio)])
		#pairs_50_order = flatten([random.sample(pairs, len(pairs)) for i in range(Nrep_audio)])
		pairs_0_order = flatten([random.sample(pairs, len(pairs)) for i in range(Nrep_audio)])

		# write the pair name to the list l
		for z in range(len(l)):
			if l[z] == "100":
				l[z] = pairs_100_order.pop(0) + "_" + l[z]
			#elif l[z] == "050":
			#	l[z] = pairs_50_order.pop(0) + "_" + l[z]
			elif l[z] == "000":
				l[z] = pairs_0_order.pop(0) + "_" + l[z]
		
		ll.append([sub_string, sess_string] + l)
		

		# OLD: without restrictions on the sampling
		#l = flatten([random.sample(conditions_audio, len(conditions_audio)) for i in range(Nrep_audio)])
		#sub_string = str(i).zfill(3)
		#sess_string = str(s+1).zfill(3)
		#ll.append([sub_string, sess_string] + l)
		#with open("condition_orders/FPAS_" + sub_string + "_session_" + sess_string + ".pkl", "wb") as file:
		#	pickle.dump(l, file)

audio_df = pd.DataFrame(columns=["subject", "session"] + ["block_" + str(i) for i in range(1,N_blocks_audio+1)], data=ll)
audio_df.to_csv("conditions/audio_conditions.csv", index=False)


# NEW VISION: OWN_100, OTHER_100, Rossion

"""
conditions_vision = ["rossion",
					  "own_100",
					  "other_100",
					  ]
Nrep_vision = 10
N_blocks_vision = Nrep_vision * len(conditions_vision)


ll = []
for i in range(Nsubs):
	for s in range(Nsess):
		l = flatten([random.sample(conditions_vision, len(conditions_vision)) for i in range(Nrep_vision)])
		sub_string = str(i).zfill(3)
		sess_string = str(s+1).zfill(3)
		ll.append([sub_string, sess_string] + l)
		#with open("condition_orders/FPVS_" + sub_string + "_session_" + sess_string + ".pkl", "wb") as file:
		#	pickle.dump(l, file)

vision_df = pd.DataFrame(columns=["subject", "session"] + ["block_" + str(i) for i in range(1,N_blocks_vision+1)], data=ll)
vision_df.to_csv("conditions/vision_conditions.csv", index=False)
"""
# NEW VISION: ROSSION and Humans(Apes oddball)

conditions_vision = ["rossion",
					  "humans",
					  ]
Nrep_vision = 15
N_blocks_vision = Nrep_vision * len(conditions_vision)


ll = []
for i in range(Nsubs):
	for s in range(Nsess):
		l = flatten([random.sample(conditions_vision, len(conditions_vision)) for i in range(Nrep_vision)])
		sub_string = str(i).zfill(3)
		sess_string = str(s+1).zfill(3)
		ll.append([sub_string, sess_string] + l)
		#with open("condition_orders/FPVS_" + sub_string + "_session_" + sess_string + ".pkl", "wb") as file:
		#	pickle.dump(l, file)

vision_df = pd.DataFrame(columns=["subject", "session"] + ["block_" + str(i) for i in range(1,N_blocks_vision+1)], data=ll)
vision_df.to_csv("conditions/vision_conditions.csv", index=False)
