##
## advc.021b: Latest changes to PerfectWorld in MongooseMod (v3.3) ported back
## to the latest standalone version of the script (v3.2) and enhanced and
## customized for the AdvCiv mod. The AdvCiv changes are marked with
## "advc" comments, "advc.001" for bugfixes, "advc.027" for the integration of
## AdvCiv's starting position algorithm.
## Also corrected some debug output that used "FairWeather" as the map name.
## Version history up to v3.3 moved to the end of the file.
##
##############################################################################
##
## Based on:
## PerfectMongoose_v320_MM_Edition.py
## Copyright (C) 2011 Kenny Welch aka LunarMongoose
##
##############################################################################
##
## And on:
##
## PerfectMongoose_v33_MM_Edition_v20.py
## for MongooseMod 4.1; 20 Jan 2013
## Copyright (C) 2013 Kenny Welch
##############################################################################
##
## And on:
##
## PerfectWorld_v2.06.py (for Civ4)
##
## Copyright 2007-2010 Rich Marinaccio aka Cephalo
## Used [by Kenny Welch] with Permission
##
##############################################################################
##
## And on:
##
## PerfectWorld3_v2.lua (for Civ5)
##
## Copyright 2010 Rich Marinaccio aka Cephalo
## Used with Permission
##

from CvPythonExtensions import *
import CvUtil
import CvMapGeneratorUtil

from array  import array
from random import random, randint, seed, shuffle
import math
import sys
import time
import os


##############################################################################
## GLOBAL CONTROL CONSTANTS: Change these to customize the map
##############################################################################

class MapConstants:
	def __init__(self):
		return


	def initialize(self):
		#This variable sets how much land the map will have, and thus how large its oceans will be.
		#self.SeaLevel          = 0 # advc: Use the standard option (low/medium/high) for this

		#This variable sets whether to use the new PW3 landmass generator or the old PW2 one.
		self.LandmassGenerator = 0

		#This variable sets whether to use Average Slope or Absolute Height to determine which tiles are Hills and Peaks.
		self.HillPeakStyle     = 0

		#This variable sets whether to use the new PW3 climate system or the old PW2 one.
		self.ClimateSystem     = 0

		#This variable sets whether to use the PW2 river generator or the Vanilla Civ4 one.
		self.RiverGenerator    = 0

		#If this variable is set to False, a shower of colossal meteors will attempt to
		#break up any pangaea-like continents. Setting this variable to True will allow
		#pangaeas to sometimes occur and should be greatly favored by any dinosaurs
		#that might be living on this planet at the time.
		self.AllowPangaeas = True # advc: Initial value gets overwritten, but let's still use the default.

		#This variable can be used to turn off 'New world' logic and place starting positions
		#anywhere in the world. For some mods, a new world doesn't make sense.
		#self.AllowNewWorld = False
		# advc: Renamed b/c, apparently, AllowNewWorld stands for "allow there to be a New World", which really means that starts in the New World are disallowed! Gets overwritten when custom options are read.
		self.OldWorldStarts = False

		#Percent of land vs. water
		#LM - Exact Real Earth Value. Actual results vary depending on map size, meteors, and which landmass generator was used.
		#self.landPercent = 0.2889
		# advc.137: At Medium sea level, Fractal only aims at 23% land (BtS: 22). PM has more bad, marginal and initially inaccessible terrain, but also a longer coastline and thus more seafood.
		self.landPercent = 0.2315

		#Percentage of land squares high enough to be Hills or Peaks.
		self.HillPercent = 0.225 # advc: was 0.42

		#Percentage of land squares high enough to be Peaks.
		self.PeakPercent = 0.048 # advc: was 0.12

		#Percentage of land squares cold enough to be Snow.
		#self.SnowPercent = 0.1
		#Percentage of land squares cold enough to be Snow or Tundra.
		#self.TundraPercent = 0.24 + self.SnowPercent
		# <advc> Replacing the above
		self.TemperateSnowPercent = 0.05
		self.TemperateTundraPercent = 0.07 + self.TemperateSnowPercent
		# These percentages now apply only to plots with the proper latitude
		self.SnowPercent = 0.24
		self.TundraPercent = 0.8
		# The original script uses Tundra and Snow also to represent high plateaus. I'm not allowing this in the tropics, and, outside the polar circles, I'm adding rainfall constraints. This means that the final terrain distribution will deviate from the target terrain-percent values.
		self.snowPlateauMinLatitude = 67 # (polar circles)
		self.snowHillMinLatitude = 24 # (tropics)
		#self.tundraMinLatitude = 24
		# Better disable temperate Tundra. More weird than interesting.
		self.tundraMinLatitude = 58
		self.taigaMinLatitude = 58 # (taiga is forested Tundra in my mind)
		self.tundraSnowRainfallTarget = 0.45
		# </advc>

		#Of the squares too warm to be Snow or Tundra, percentage dry enough to be Desert.
		#(Use the first number to set the percent of TOTAL land area. I'm using 18%, while the
		#Google Consensus for a Real Earth Desert Value seems to be 20%.)
		#self.DesertPercent = 0.18 / (1.0 - self.TundraPercent)
		# advc: TundraPercent has a different meaning now. Those 20% figures include Antarctica. So around 15% should be realistic. Go a bit higher b/c the default terrain generator does so too.
		self.DesertPercent = 0.165

		#Of the squares too warm to be Snow or Tundra, percentage dry enough to be Desert or Plains.
		#The remainder will be Grassland. (This code auto-sets Plains and Grassland to be equal.)
		#self.PlainsPercent = ((1.0 - self.DesertPercent) / 2.0) + self.DesertPercent
		# advc: 34% Plains instead of 50%. (And a portion of that will be placed under Jungle.)
		self.PlainsPercent = ((1.0 - self.DesertPercent) * 0.34) + self.DesertPercent

		#Sets the threshold for Jungle rainfall by modifying plainsRainfall by this factor.
		# advc: Was 1.2; want to allow Jungle on Plains.
		self.JungleFactor = 0.28

		#Percentage of high-rainfall Grassland [advc: or non-low-rainfall Plains] squares hot enough to be Jungle.
		self.JunglePercent = 0.8 # advc: Was 0.5. Latitude checks added to prevent jungle too far from the equator.

		#Percentage of Plains and sub-Jungle Grassland squares warm enough to have Deciduous Forest.
		#The remainder will have Evergreen Forest.
		self.DeciduousPercent = 0.55 # advc: was 0.5
		# advc: Tundra area assumed to be warm enough for tree growth
		self.TreelinePercent = 0.67

		#Chance Forest and Jungle will be placed when their temperature and rainfall conditions are met.
		#Note there will still be plenty of tiles without tree coverage even when this is at maximum.
		#Use a value between 0.0 and 1.0.
		# <advc> Was 1.0. For Forests, the chance is further multiplied by the new settings below.
		self.MaxTreeChance = 0.75
		self.TemperateForestChance = 0.46
		self.BorealForestChance = 1.0
		# </advc>

		#Chance an Oasis will appear. A tile must be Desert, not be on a hill, not be near another Oasis,
		#and be surrounded by Desert on all sides.
		#self.OasisPercent   = 0.5
		#self.OasisMinChance = 0.5
		#self.OasisMaxChance = 1.0
		# <advc> This works differently now, and the enclosure conditions are also less strict (i.e. not as described above).
		self.OasisMinChance = 0.015
		self.OasisMaxChance = 0.03 # </advc>

		#This variable adjusts the amount of bonuses on the map. Values above 1.0 will add bonus bonuses.
		#People often want lots of bonuses, and for those people, this variable is definately a bonus.
		self.BonusBonus = 1.0

		#This value modifies LakeSizePerDrainage when a lake begins in desert
		self.DesertLakeModifier = 0.4 # advc: was 0.6

		#This value controls the amount of siltification in lakes when using the Default Civ4 SDK River Generator
		self.maxSiltPanSizeSDK = 5

		#This value controls the amount of siltification in lakes when using Cephalo's PerfectWorld 2 River Generator
		self.maxSiltPanSizePW2 = 0

		#This value sets the minimum altitude of lake depressions. They
		#generally look better higher up.
		self.minLakeAltitude = 0.0

		#Degrees latitude for the top and bottom of the map. This allows
		#for more specific climate zones
		# advc: Was 90, -90. That results in one whole row for 90 and -90 each, which, with an equal-area projection, should take up at most one plot each.
		self.topLatitude    = 85
		self.bottomLatitude = -85

		#Horse latitudes and polar fronts plus and minus in case you
		#want some zones to be compressed or emphasized.
		self.horseLatitude      = 30
		self.polarFrontLatitude = 60

		#Tropics of Cancer and Capricorn plus and minus respectively
		self.tropicsLatitude = 23

		#Monsoon uplift factor. This value is an ajustment so that monsoon uplift
		#matches geostrophic uplift.
		self.monsoonUplift = 500.0

		#Controls wrapping (not sure if this makes sense yet)
		self.WrapX = True
		self.WrapY = False

		#Too many meteors will simply destroy the Earth, and just
		#in case the meteor shower can't break the pangaea, this will also
		#prevent and endless loop.
		# advc (note): Set in initInGameOptions now.
		self.maximumMeteorCount = 15

		#Minimum size for a meteor strike that attemps to break pangaeas.
		#Don't bother to change this it will be overwritten depending on
		#map size.
		self.minimumMeteorSize = 6

		#---These values are for evaluating starting locations

		#Minimum number of hills in fat cross
		self.MinHillsInFC = 2

		#Max number of peaks in fat cross
		self.MaxPeaksInFC = 3 # advc: was 5

		#Max number of bad features (jungle) in fat cross
		self.MaxBadFeaturesInFC = 4 # advc: was 10

		#The following values are used for assigning starting locations. For now,
		#they have the same ratio that is found in CvPlot::getFoundValue
		#self.FoodValue       = 16
		self.ProductionValue = 16
		#self.CommerceValue   = 16
		# advc: v3.2 had used 10/40/20 (also weird); The MongooseMod changelog from 19 Jan 2013 says 16/16/8, and a comment elsewhere cites commerce being worth half as much as the other yields as the "standard rule for yield balance". So this might be a bug. Let's give food a little less weight though - b/c lack of food is easily amended during normalization - and commerce a little more because it's difficult to come by in the very early game.
		self.FoodValue       = 14
		self.CommerceValue   = 10

		#Coastal cities are important, how important is determined by this value.
		# advc (note): I think this was intended for discouraging starts one off the coast and turned out not to be needed (at 1, it has no effect). Was 1.3 in v1.32.
		self.CoastalCityValueBonus = 1.0

		#River cities are important, how important is determined by this value.
		self.RiverCityValueBonus = 1.2

		#Hill cities are important, how important is determined by this value.
		# advc: Was 1.1 (and equivalent to 1 in v1.32) This is specifically about hill defense, which is really quite unimportant in the capital.
		self.HillCityValueBonus = 1.015

		#Secure resources are important, how important is determined by this value.
		# advc: Was 1.1, 1.05. Secure access (and w/o worker turns) is, again, not an important consideration for a capital.
		self.StrategicBonusCityValueBonus = 1.03
		self.OtherBonusCityValueBonus     = 1.0

		#Bonus resources to add depending on difficulty settings
		self.SettlerBonus   = 2
		self.ChieftainBonus = 2
		self.WarlordBonus   = 1
		# advc: Was 1. I'm disabling these bonuses anyway (at the end of SetStartingPlots), but if someone turns them back on, I still doubt they'd want an extra bonus on Noble.
		self.NobleBonus     = 0
		self.PrinceBonus    = 0
		self.MonarchBonus   = 0
		self.EmperorBonus   = 0
		self.ImmortalBonus  = 0
		self.DeityBonus     = 0

		#Decides whether to use the Python random generator or the one that is
		#intended for use with civ maps. The Python random has much higher precision
		#than the civ one. 53 bits for Python result versus 16 for getMapRand. The
		#rand they use is actually 32 bits, but they shorten the result to 16 bits.
		#However, the problem with using the Python random is that it may create
		#syncing issues for multi-player now or in the future, therefore it must
		#be optional.
		# advc (note): See AIAndy's comment in the seed function. This should be fine.
		# But, for debugging with fixed seeds, it might be best to toggle this off.
		self.UsePythonRandom = True

		#Below here are static defines. If you change these, the map won't work.
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		self.L  = 0
		self.N  = 1
		self.S  = 2
		self.E  = 3
		self.W  = 4
		self.NE = 5
		self.NW = 6
		self.SE = 7
		self.SW = 8

		self.NO_SEPARATION          = 0
		self.NORTH_SOUTH_SEPARATION = 1
		self.EAST_WEST_SEPARATION   = 2

		self.width  = 0
		self.height = 0

		self.WATER = 0
		self.LAND  = 1
		self.HILLS = 2
		self.PEAK  = 3

		self.OCEAN  = 0
		self.COAST  = 1
		#self.MARSH  = 2
		self.GRASS  = 3
		self.PLAINS = 4
		self.DESERT = 5
		self.TUNDRA = 6
		self.SNOW   = 7

		self.minimumLandInChoke = 0.5


		##############################################################################
		## PW3 Settings
		##############################################################################
		# advc: twistMinFreq was 0.02. Gets adjusted in ElevationMap3.GenerateElevationMap. Greater values (closer to twistMaxFreq) seem to result in somewhat larger landmasses (or maybe not ...). Fwiw, cephalo uses 0.05 in PerfectWorld6.lua.
		self.twistMinFreq = 0.045
		self.twistMaxFreq = 0.12
		self.twistVar     = 0.042
		self.mountainFreq = 0.078

		# Weight of the mountain elevation map versus the coastline elevation map.
		self.mountainWeight = 0.8

		# These set the water temperature compression that creates the land/sea
		# seasonal temperature differences that cause monsoon winds.
		self.minWaterTemp = 0.1
		self.maxWaterTemp = 0.6

		# Strength of geostrophic rainfall versus monsoon rainfall
		self.geostrophicFactor              = 3.0
		self.geostrophicLateralWindStrength = 0.6

		# Wind Zones
		self.NOZONE     = -1
		self.NPOLAR     = 0
		self.NTEMPERATE = 1
		self.NEQUATOR   = 2
		self.SEQUATOR   = 3
		self.STEMPERATE = 4
		self.SPOLAR     = 5

		# Fill in any lakes smaller than this. It looks bad to have large
		# river systems flowing into a tiny lake.
		self.minOceanSize = 50

		# Crazy rain tweaking variables. I wouldn't touch these if I were you.

		# Minimum amount of rain dropped by default before other factors
		# add to the amount of rain dropped
		self.minimumRainCost = 0.0001
		self.upLiftExponent  = 4
		self.polarRainBoost  = 0.0

		# These attenuation factors lower the altitude of the map edges. This is
		# currently used to prevent large continents in the uninhabitable polar
		# regions. East/west attenuation is set to zero, but modded maps may
		# have need for them.
		# advc (note): Now set in initInGameOptions
		self.northAttenuationFactor = 0.0
		self.northAttenuationRange  = 0.0 #percent of the map height.
		self.southAttenuationFactor = 0.0
		self.southAttenuationRange  = 0.0
		# east west attenuation may be desired for flat maps.
		self.eastAttenuationFactor = 0.0
		self.eastAttenuationRange  = 0.0 #percent of the map width.
		self.westAttenuationFactor = 0.0
		self.westAttenuationRange  = 0.0

		#This value controls the number of mid-altitude lake depressions per map square.
		#It will become a lake if enough water flows into the depression.
		# (advc: Gets set based on world size now)
		self.numberOfLakesPerPlot3 = 0.008
		# advc: Was 3 (as a magic constant)
		self.expandedLakeMinSize = 1

		#How many squares are added to a lake for each unit of drainage flowing into it.
		# (advc: Gets set based on world size now)
		self.LakeSizePerDrainage3 = 30.0

		#This value is used to decide if enough water has accumulated to form a river.
		#A lower value creates more rivers over the entire map.
		# advc: Was 0.05, but is now on a different scale. Also, I want the script to place only a few rivers and let the DLL do most of the work.
		self.RiverThreshold3 = 0.95


		##############################################################################
		## PW2 Settings
		##############################################################################

		#Height and Width of main climate and height maps. This does not
		#reflect the resulting map size. Both dimensions( + 1 if wrapping in
		#that dimension = False) must be evenly divisible by self.hmMaxGrain
		# advc.137: Increased both by 16
		self.hmWidth  = 160
		self.hmHeight = 113

		#Size of largest map increment to begin midpoint displacement. Must
		#be a power of 2.
		self.hmMaxGrain = 16

		#These are not mountain peaks, but points on the height map initialized
		#to 1.0 before the midpoint displacement process begins. This sets the
		#percentage of 'peaks' for points that are not on the grain margin.
		self.hmInitialPeakPercent = 0.3

		#Scales the heuristic for random midpoint displacement. A higher number
		#will create more noise(bumpy), a smaller number will make less
		#noise(smooth).
		self.hmNoiseLevel = 2.0

		#Number of tectonic plates. advc: Set in PerformTectonics.
		#self.hmNumberOfPlates = int(float(self.hmWidth * self.hmHeight) * 0.0016)

		# advc: Exponent for the chance of re-rolling plate seeds near a
		# wrapping(!) edge of the map. A higher exponent makes such re-rolls
		# less likely. Use 0 to disable re-rolls, i.e. to use an entirely
		# uniform distribution of plate seeds across the map.
		self.plateSeedRerollExp = 8

		#Influence of the plate map, or how much of it is added to the height map.
		self.plateMapScale = 1.1

		#Minimun distance from one plate seed to another
		self.minSeedRange = 15

		#Minimum distance from a plate seed to edge of map
		self.minEdgeRange = 5

		#Chance for plates to grow. Higher chance tends to make more regular
		#shapes. Lower chance makes more irregular shapes and takes longer.
		# advc: Was 0.3, both. Also randomized now.
		self.plateGrowthChanceX = 0.5
		self.plateGrowthChanceY = 0.5

		#This sets the amount that tectonic plates differ in altitude.
		self.plateStagger = 0.1

		#This sets the max amount a plate can be staggered up to on the heightmap
		self.plateStaggerRange = 1.0

		#This is the chance for a plate to sink into the water when it is on map edge
		self.chanceForWaterEdgePlate = 0.45

		#This is the frequency of the cosine ripple near plate boundaries.
		self.rippleFrequency = 0.5

		#This is the amplitude of the ripples near plate boundaries.
		# advc: Was 0.75; will increase with world size. Also randomized a little.
		self.rippleAmplitude = 0.25

		#This is the amount of noise added to the plate map.
		self.plateNoiseFactor = 1.2

		#Filter size for altitude smoothing and distance finding. Must be odd number.
		# advc: Was 5; also randomized now.
		self.distanceFilterSize = 9

		#It is necessary to eliminate small inland lakes during the initial
		#heightmap generation. Keep in mind this number is in relation to
		#the initial large heightmap (mc.hmWidth, mc.hmHeight) before the
		#shrinking process
		self.minInlandSeaSize = 100

		#Option to divide map into two continents as far as the midpoint
		#displacement is concerned. For guaranteed continent separation, further
		#steps will be needed but this option will cause more ocean in the
		#middle of the map. The possible choices are 0 = NO_SEPARATION,
		#1 = NORTH_SOUTH_SEPARATION and 2 = EAST_WEST_SEPARATION.
		self.hmSeparation = 0

		#Creates a water margin around the map edges.
		self.northMargin = False
		self.southMargin = False
		self.eastMargin  = False
		self.westMargin  = False

		#If you sink the margins all the way to 0.0, they become too obvious.
		#This variable sets the maximum amount of sinking
		self.hmMarginDepth = 0.6

		#Margin of ocean around map edge when not wrapping and also through
		#middle when using separation.
		self.hmGrainMargin = 2

		#After generating the heightmap, bands of ocean can be added to the map
		#to allow a more consistent climate generation. These bands are useful
		#if you are generating part of a world where the weather might be coming
		#in from off the map. These bands can be kept if needed or cropped off
		#later in the process.
		self.northWaterBand = 0
		self.southWaterBand = 0
		self.eastWaterBand  = 0
		self.westWaterBand  = 0

		#These variables are intended for use with the above water band variables
		#but you can crop the map edge after climate generation for any reason.
		self.northCrop = 0
		self.southCrop = 0
		self.eastCrop  = 0
		self.westCrop  = 0

		#Oceans are slow to gain and lose heat, so the max and min temps
		#are reduced and raised by this much.
		self.oceanTempClamp = 0.1

		#Filter size for temperature smoothing. Must be odd number
		self.filterSize = 15

		#This sets the amount of heat lost at the highest altitude. 1.0 loses all heat
		#0.0 loses no heat.
		self.heatLostAtOne = 0.8 # advc: was 1.0

		#This value is an exponent that controls the curve associated with
		#temperature loss. Higher values create a steeper curve.
		self.temperatureLossCurve = 1.3

		#This value controls the number of mid-altitude lake depressions per
		#map square. It will become a lake if enough water flows into the
		#depression.
		self.numberOfLakesPerPlot2 = 0.003

		#How many squares are added to a lake for each unit of drainage flowing into it.
		self.LakeSizePerDrainage2 = 8.0

		#This value is used to decide if enough water has accumulated to form a river.
		#A lower value creates more rivers over the entire map.
		self.RiverThreshold2 = 0.33 # advc: Was 0.25; see RiverThreshold3.


		##############################################################################
		## Mongoose Settings
		##############################################################################

		# Factors to modify mc.landPercent by if a Low or High Sea Level is chosen
		#self.SeaLevelFactor1 = 1.75
		#self.SeaLevelFactor2 = 0.75
		#self.SeaLevelFactor3 = 1.5 # advc: was 2.5 (but I'm removing choices 3 and 4 anyway)
		#self.SeaLevelFactor4 = 0.5
		# advc:
		self.SeaLevelFactor = 1 # advc: Set this properly in initInGameOptions


		##############################################################################
		## Fuyu Settings
		##############################################################################

		#This variable adjusts the maximum number of identical bonuses to be placed in a
		#single group. People tend not to like all instances of a bonus type to be found within
		#a single 3x3 area. When set to -1 (default), the maximum group size is between 3 and 6,
		#based on WorldSize. When set to 0, the maximum group size is a random number between
		# zero and (number of players). When set to 1, this will disable all bonus grouping.
		# advc (comment): Doesn't apply b/c I'm letting CvMapGenerator handle resource placement, and I have my own changes in that class that reduce resource grouping.
		self.BonusMaxGroupSize = -1

		#Randomly allows strategic bonuses to be used to sweeten starting positions.
		#(Chance per starting position to allow 1 Classical Era or earlier strategic resource)
		self.allowWonderBonusChance = 0.0

		#Randomly allows bonuses with continent limiter to be used to sweeting starting positions.
		#(Chance per attempt to place an area-restricted resource in the wrong area)
		self.ignoreAreaRestrictionChance = 0.0


	def initInGameOptions(self):
		gc = CyGlobalContext()
		mmap = gc.getMap()
		# Sea Level
		#self.SeaLevel          = mmap.getCustomMapOption(0)
		# <advc> Use the standard sea level option instead
		seaChg = gc.getSeaLevelInfo(CyMap().getSeaLevel()).getSeaLevelChange()
		self.SeaLevelFactor -= 0.0425 * seaChg
		# Some other changes to options below ...
		# Landmass Generator (renumbered to option index 0; was 1)
		self.LandmassGenerator  = mmap.getCustomMapOption(0)
		# I'm making the hex-based generator unavailable. So the PW2 generator takes choice id 1 on the menu, but is still represented by id 2 within the script (b/c a lot of code would have to be changed otherwise).
		if self.LandmassGenerator == 1:
			self.LandmassGenerator = 2
		if self.LandmassGenerator == 0:
			# advc: The PW3 generator leads to a lot of seafood. I think that outweighs a higher chance of landmasses without starting sites.
			self.landPercent -= 0.004
		# Hill/Peak Style
		# Always place hills and peaks based (mainly) on differences in altitude. Using absolute altitude is pretty much only good for concluding that it's a bad idea.
		#self.HillPeakStyle     = mmap.getCustomMapOption(2)
		# Climate System
		# Always use PW3. The older system is working, but I see no compelling reason to prefer it.
		#self.ClimateSystem     = mmap.getCustomMapOption(3)
		# River Generator
		# Always use the PM river generator (but only for placing a portion of the rivers; best of both worlds, hopefully).
		#self.RiverGenerator     = mmap.getCustomMapOption(4)
		# Pangaea Rules
		# Allow them unless the Old World Starts option is used
		#self.AllowPangaeas      = (mmap.getCustomMapOption(5) == 0)
		# Wrap Options (renumbered to option index 2; was 6)
		selectionID            = mmap.getCustomMapOption(2)
		# New World Rules (renumbered to option index 1; was 7)
		self.OldWorldStarts    = mmap.getCustomMapOption(1)
		# Break Pangaea if and only if there has to be an Old World
		self.AllowPangaeas = not self.OldWorldStarts
		# </advc>
		if selectionID == 1: # advc: was 0
			self.eastWaterBand  = 0
			self.westWaterBand  = 0
			self.eastCrop       = 0
			self.westCrop       = 0
		elif selectionID == 2: # advc: was 1
			self.WrapY = True
			self.hmHeight -= 1
			self.northWaterBand = 0
			self.southWaterBand = 0
			self.eastWaterBand  = 0
			self.westWaterBand  = 0
			self.northCrop      = 0
			self.southCrop      = 0
			self.eastCrop       = 0
			self.westCrop       = 0
		elif selectionID == 0: # advc: was 2
			self.WrapX = False
			self.hmWidth += 1
		# <advc>
		# Portion of desert tiles that receive an oasis
		self.OasisPercent = self.OasisMinChance + (self.OasisMaxChance - self.OasisMinChance) * PRand.random() 
		# Far fewer than the 15 set initially
		self.maximumMeteorCount = (3 * mmap.getWorldSize()) // 2 + 1
		if self.SeaLevelFactor > 1.2:
			self.maximumMeteorCount += 1
		elif self.SeaLevelFactor < 0.85:
			self.maximumMeteorCount -= 1
		# Caveat: Need to keep an eye on isHmWaterMatch when adjusting the min. meteor size. Smaller meteors affect fewer plots but are also more likely to create peaks and hills through steep slopes.
		self.minimumMeteorSize = 1
		if mmap.getWorldSize() > 0:
			self.minimumMeteorSize += 1
		if mmap.getWorldSize() > 2:
			self.minimumMeteorSize += 1
		if mmap.getWorldSize() > 4:
			self.minimumMeteorSize += 1
		# Smaller value means less land near the poles
		self.northAttenuationFactor = 0.59
		# Avoid elongated Antarctica; likelier to occur when land ratio is high.
		self.northAttenuationFactor += (1 - self.SeaLevelFactor) / 4.25
		self.northAttenuationFactor = max(0.0, min(1.0, self.northAttenuationFactor))
		self.northAttenuationRange = (1 - self.northAttenuationFactor) / 3.15
		self.southAttenuationRange = self.northAttenuationRange
		self.southAttenuationFactor = self.northAttenuationFactor
		if not self.WrapX:
			self.eastAttenuationRange  = self.northAttenuationRange
			self.westAttenuationRange  = self.northAttenuationRange
			self.eastAttenuationFactor = self.northAttenuationFactor
			self.westAttenuationFactor = self.northAttenuationFactor
		if self.ClimateSystem != 0: # High-altitude plots seem to be wetter with the PW2 climate system
			self.tundraSnowRainfallTarget *= 1.4
		# Some extra Jungle for the PM3 land generator b/c it tends to place less land near the equator.
		if self.LandmassGenerator < 2:
			self.JungleFactor -= 0.03
			self.JunglePercent += 0.03
		self.numberOfLakesPerPlot3 = (0.024 / self.SeaLevelFactor) - mmap.getWorldSize() * 0.0028
		self.LakeSizePerDrainage3 = (50.0 / self.SeaLevelFactor) - mmap.getWorldSize() * 3
		# </advc>
		# advc: Deleted; can be looked up in-game in AdvCiv. And it's tedious to keep it up to date here.
		#self.optionsString = 


mc = MapConstants()


##############################################################################
## PW2/PW3 Random
##############################################################################

class PythonRandom:
	def __init__(self):
		return


	def seed(self):
		#Python randoms are not usable in network games.
		#AIAndy - I disagree. Python randoms are deterministic so the only important thing is to seed from a synchronized source like MapRand.
		if mc.UsePythonRandom:
			if CyGame().isNetworkMultiPlayer():
				# advc (note): Would be nice to use this branch also - automatically - when a nonzero seed is set in CivilizationIV.ini. As it is, the script will have to be changed manually (in addition to the .ini) when a fixed seed is desired.
				#AIAndy - seed Python random with MapRand
				gc = CyGlobalContext()
				self.mapRand = gc.getGame().getMapRand()
				seedValue = self.mapRand.get(65535, "Seeding mapRand - PerfectMongoose.py")
				seed(seedValue)
				self.seedString = "Random seed (Using getMapRand) for this map is %(s)20d" % {"s" :seedValue}
			else:
				#Python 'long' has unlimited precision, while the random generator
				#has 53 bits of precision, so I'm using a 53 bit integer to seed the map!
				seed() #Start with system time
				seedValue = randint(0, 9007199254740991)
				seed(seedValue)
				self.seedString = "Random seed (Using Python rands) for this map is %(s)20d" % {"s" :seedValue}
		else:
			gc = CyGlobalContext()
			self.mapRand = gc.getGame().getMapRand()
			seedValue = self.mapRand.get(65535, "Seeding mapRand - PerfectMongoose.py")
			self.mapRand.init(seedValue)
			self.seedString = "Random seed (Using getMapRand) for this map is %(s)20d" % {"s" :seedValue}


	def random(self):
		if mc.UsePythonRandom:
			return random()
		else:
			#This formula is identical to the getFloat function in CvRandom. It
			#is not exposed to Python so I have to recreate it.
			fResult = float(self.mapRand.get(65535, "Getting float -PerfectMongoose.py")) / float(65535)
			return fResult


	def randint(self, rMin, rMax):
		#if rMin and rMax are the same, then return the only option
		if rMin == rMax:
			return rMin
		#returns a number between rMin and rMax inclusive
		if mc.UsePythonRandom:
			return randint(rMin, rMax)
		else:
			#mapRand.get() is not inclusive, so we must make it so
			return rMin + self.mapRand.get(rMax + 1 - rMin, "Getting a randint - PerfectMongoose.py")


PRand = PythonRandom()


##############################################################################
## PW2/PW3 AreaMap
##############################################################################

class AreaMap:
	def __init__(self, width, height, b8connected, bSwitch4Or8OnFalseMatch):
		self.width  = width
		self.height = height
		self.length = self.width * self.height
		self.data   = array('i')
		for i in range(self.length):
			self.data.append(0)
		self.b8connected = b8connected
		self.bSwitch4Or8OnFalseMatch = bSwitch4Or8OnFalseMatch


	def defineAreas(self, matchFunction):
		self.areaList = list()
		areaID = 0
		#make sure map is erased in case it is used multiple times
		for i in range(self.length):
			self.data[i] = 0
		for i in range(self.length):
			if self.data[i] == 0: #not assigned to an area yet
				areaID += 1
				areaSize, avgX, avgY, bWater = self.fillArea(i, areaID, matchFunction)
				area = Area(areaID, areaSize, avgX, avgY, bWater)
				self.areaList.append(area)


	def getAreaByID(self, areaID):
		for i in range(len(self.areaList)):
			if self.areaList[i].ID == areaID:
				return self.areaList[i]
		return None


	def getOceanID(self):
		self.areaList.sort(lambda x, y:cmp(x.size, y.size))
		self.areaList.reverse()
		for a in self.areaList:
			if a.water:
				return a.ID


	def getIndex(self, x, y):
		if mc.WrapX:
			xx = x % self.width
		elif x < 0 or x >= self.width:
			return -1
		else:
			xx = x
		if mc.WrapY:
			yy = y % self.height
		elif y < 0 or y >= self.height:
			return -1
		else:
			yy = y
		return yy * self.width + xx


	def fillArea(self, index, areaID, matchFunction):
		#first divide index into x and y
		y = index / self.width
		x = index % self.width
		#We check 8 neigbors for land,but 4 for water. This is because
		#the game connects land squares diagonally across water, but
		#water squares are not passable diagonally across land
		self.segStack = list()
		self.size = 0
		self.totalX = 0
		self.totalY = 0
		bWater = matchFunction(x, y)
		#place seed on stack for both directions
		seg = LineSegment(y, x, x, 1)
		self.segStack.append(seg)
		seg = LineSegment(y + 1, x, x, -1)
		self.segStack.append(seg)
		while(len(self.segStack) > 0):
			seg = self.segStack.pop()
			self.scanAndFillLine(seg, areaID, bWater, matchFunction)
		#LM - set landmass position values
		avgX = float(self.totalX) / float(self.size)
		avgY = float(self.totalY) / float(self.size)
		if avgX < 0:
			avgX += self.width
		elif avgX >= self.width:
			avgX -= self.width
		if avgY < 0:
			avgY += self.height
		elif avgY >= self.height:
			avgY -= self.height
		return self.size, avgX, avgY, bWater


	def scanAndFillLine(self, seg, areaID, bWater, matchFunction):
		#check for y + dy being off map
		i = self.getIndex(seg.xLeft, seg.y + seg.dy)
		if i < 0:
			return
		debugReport = False
		#for land tiles we must look one past the x extents to include
		#8-connected neighbors
		if self.b8connected:
			if self.bSwitch4Or8OnFalseMatch and bWater:
				landOffset = 0
			else:
				landOffset = 1
		else:
			if self.bSwitch4Or8OnFalseMatch and bWater:
				landOffset = 1
			else:
				landOffset = 0
		lineFound = False
		#first scan and fill any left overhang
		if mc.WrapX:
			xStop = 0 - (self.width * 20)
		else:
			xStop = -1
		for xLeftExtreme in range(seg.xLeft - landOffset, xStop, -1):
			i = self.getIndex(xLeftExtreme, seg.y + seg.dy)
			if self.data[i] == 0 and bWater == matchFunction(xLeftExtreme, seg.y + seg.dy):
				self.data[i] = areaID
				self.size += 1
				#LM - set landmass position values
				self.totalX += xLeftExtreme
				self.totalY += seg.y + seg.dy
				lineFound = True
			else:
				#if no line was found, then xLeftExtreme is fine, but if
				#a line was found going left, then we need to increment
				#xLeftExtreme to represent the inclusive end of the line
				if lineFound:
					xLeftExtreme += 1
				break
		#now scan right to find extreme right, place each found segment on stack
		xRightExtreme = seg.xLeft #needed sometimes? one time it was not initialized before use.
		if mc.WrapX:
			xStop = self.width * 20
		else:
			xStop = self.width
		for xRightExtreme in range(seg.xLeft + lineFound - landOffset, xStop, 1):
			i = self.getIndex(xRightExtreme, seg.y + seg.dy)
			if self.data[i] == 0 and bWater == matchFunction(xRightExtreme, seg.y + seg.dy):
				self.data[i] = areaID
				self.size += 1
				#LM - set landmass position values
				self.totalX += xRightExtreme
				self.totalY += seg.y + seg.dy
				if not lineFound:
					lineFound = True
					xLeftExtreme = xRightExtreme #starting new line
			elif lineFound: #found the right end of a line segment!
				lineFound = False
				#put same direction on stack
				newSeg = LineSegment(seg.y + seg.dy, xLeftExtreme, xRightExtreme - 1, seg.dy)
				self.segStack.append(newSeg)
				#determine if we must put reverse direction on stack
				if xLeftExtreme < seg.xLeft or xRightExtreme >= seg.xRight:
					#out of shadow so put reverse direction on stack also
					newSeg = LineSegment(seg.y + seg.dy, xLeftExtreme, xRightExtreme - 1, -seg.dy)
					self.segStack.append(newSeg)
					if debugReport:
						print "opposite direction to stack",str(newSeg)
				if xRightExtreme >= seg.xRight + landOffset:
					if debugReport:
						print "finished with line"
					break #past the end of the parent line and this line ends
			elif not lineFound and xRightExtreme >= seg.xRight + landOffset:
				break #past the end of the parent line and no line found
			else:
				continue #keep looking for more line segments
		if lineFound: #still a line needing to be put on stack
			if debugReport:
				print "still needing to stack some segs"
			lineFound = False
			#put same direction on stack
			newSeg = LineSegment(seg.y + seg.dy, xLeftExtreme, xRightExtreme - 1, seg.dy)
			self.segStack.append(newSeg)
			if debugReport:
				print str(newSeg)
			#determine if we must put reverse direction on stack
			if xLeftExtreme < seg.xLeft or xRightExtreme - 1 > seg.xRight:
				#out of shadow so put reverse direction on stack also
				newSeg = LineSegment(seg.y + seg.dy, xLeftExtreme, xRightExtreme - 1, -seg.dy)
				self.segStack.append(newSeg)


class LineSegment:
	def __init__(self, y, xLeft, xRight, dy):
		self.y  = y
		self.dy = dy
		self.xLeft  = xLeft
		self.xRight = xRight


	def __str__ (self):
		string = "y = %(y)3d, xLeft = %(xl)3d, xRight = %(xr)3d, dy = %(dy)2d" % {'y':self.y, 'xl':self.xLeft, 'xr':self.xRight, 'dy':self.dy}
		return string


class Area:
	def __init__(self, iD, size, avgX, avgY, water):
		self.ID			= iD
		self.size		= size
		self.avgX		= avgX
		self.avgY		= avgY
		self.distance	= 0.0
		self.water		= water

	# advc: (Based on what little info we have)
	def startScore(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		return self.size * max(0.18, 1 - 0.0135 * max(0, abs(mc.horseLatitude - abs(em.GetLatitudeForY(self.avgY))) - 10))


	def __str__(self):
		string = "{ID = %(i)4d, size = %(s)4d, water = %(w)1d}" % {'i':self.ID, 's':self.size, 'w':self.water}
		return string


class AreaPlot:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.avgDistance = -1


##############################################################################
## PW3 FloatMap
##
## This is for storing 2D map data. The 'data' field is a zero based, one
## dimensional array. To access map data by x and y coordinates, use the
## GetIndex method to obtain the 1D index, which will handle any needs for
## wrapping in the x and y directions.
##############################################################################

class FloatMap:
	def __init__(self):
		return


	def initialize(self, width, height, wrapX, wrapY):
		self.wrapX  = wrapX
		self.wrapY  = wrapY
		self.width  = width
		self.height = height
		self.length = self.width * self.height
		##These fields are used to access only a subset of the map
		##with the GetRectIndex function. This is useful for
		##making Perlin noise wrap without generating separate
		##noise fields for each octave
		self.rectX = 0
		self.rectY = 0
		self.rectWidth  = self.width
		self.rectHeight = self.height
		self.data = []
		for i in range(self.length):
			self.data.append(0.0)


	def GetIndex(self, x, y):
		if self.wrapX:
			xx = x % self.width
		elif x < 0 or x > self.width - 1:
			return -1
		else:
			xx = x
		if self.wrapY:
			yy = y % self.height
		elif y < 0 or y > self.height - 1:
			return -1
		else:
			yy = y
		return yy * self.width + xx


	def GetXYFromIndex(self, i):
		x = i % self.width
		y = (i - x) / self.width
		return x, y


	##quadrants are labeled
	##A B
	##D C
	def GetQuadrant(self, x, y):
		if x < self.width / 2:
			if y < self.height / 2:
				return "A"
			else:
				return "D"
		else:
			if y < self.height / 2:
				return "B"
			else:
				return "C"


	##Gets an index for x and y based on the current
	##rect settings. x and y are local to the defined rect.
	##Wrapping is assumed in both directions
	def GetRectIndex(self, x, y):
		xx = x % self.rectWidth
		yy = y % self.rectHeight
		xx = self.rectX + xx
		yy = self.rectY + yy
		return self.GetIndex(xx, yy)


	def Normalize(self):
		##find highest and lowest values
		maxAlt = -1000.0
		minAlt =  1000.0
		for i in range(self.length):
			alt = self.data[i]
			if alt > maxAlt:
				maxAlt = alt
			if alt < minAlt:
				minAlt = alt
		##subtract minAlt from all values so that
		##all values are zero and above
		for i in range(self.length):
			self.data[i] = self.data[i] - minAlt
		##subract minAlt also from maxAlt
		maxAlt = maxAlt - minAlt
		##determine and apply scaler to whole map
		if maxAlt == 0.0:
			scaler = 0.0
		else:
			scaler = 1.0 / maxAlt
		for i in range(self.length):
			self.data[i] = self.data[i] * scaler


	def GenerateNoise(self):
		for i in range(self.length):
			self.data[i] = PRand.random()


	def GenerateBinaryNoise(self):
		for i in range(self.length):
			self.data[i] = PRand.randint(0, 1)


	def GetLatitudeForY(self, y):
		if mc.LandmassGenerator == 2:
			if y > self.height - mc.northCrop:
				return mc.topLatitude
			elif y < mc.southCrop:
				return mc.bottomLatitude
			degreesPerDY = float(mc.topLatitude - mc.bottomLatitude) / float(self.height - mc.northCrop - mc.southCrop)
			return mc.bottomLatitude + round(float(y - mc.southCrop) * degreesPerDY)
		else:
			#AIAndy Bugfix - float division
			return mc.bottomLatitude + ((float(mc.topLatitude - mc.bottomLatitude) * float(y)) / float(self.height))


	def GetZone(self, y):
		if y < 0 or y >= self.height:
			return mc.NOZONE
		lat = self.GetLatitudeForY(y)
		if lat >= mc.polarFrontLatitude:
			return mc.NPOLAR
		elif lat >= mc.horseLatitude:
			return mc.NTEMPERATE
		elif lat >= 0.0:
			return mc.NEQUATOR
		elif lat >= -mc.horseLatitude:
			return mc.SEQUATOR
		elif lat >= -mc.polarFrontLatitude:
			return mc.STEMPERATE
		else:
			return mc.SPOLAR


	def GetYFromZone(self, zone, bTop):
		if bTop:
			y = self.height - 1
			while y >= 0:
				if zone == self.GetZone(y):
					return y
				y -= 1
		else:
			for y in range(self.height):
				if zone == self.GetZone(y):
					return y
		return -1


	def GetGeostrophicWindDirections(self, zone):
		if zone == mc.NPOLAR:
			return mc.SW, mc.W
		elif zone == mc.NTEMPERATE:
			return mc.NE, mc.E
		elif zone == mc.NEQUATOR:
			return mc.SW, mc.W
		elif zone == mc.SEQUATOR:
			return mc.NW, mc.W
		elif zone == mc.STEMPERATE:
			return mc.SE, mc.E
		else:
			return mc.NW, mc.W
		return -1, -1


	def GetGeostrophicPressure(self, lat):
		if lat > mc.polarFrontLatitude:
			latRange   = 90.0 - mc.polarFrontLatitude
			latPercent = (lat - mc.polarFrontLatitude) / latRange
			pressure   = 1.0 - latPercent
		elif lat >= mc.horseLatitude:
			latRange   = mc.polarFrontLatitude - mc.horseLatitude
			latPercent = (lat - mc.horseLatitude) / latRange
			pressure   = latPercent
		elif lat >= 0.0:
			latRange   = mc.horseLatitude - 0.0
			latPercent = (lat - 0.0) / latRange
			pressure   = 1.0 - latPercent
		elif lat > -mc.horseLatitude:
			latRange   = 0.0 + mc.horseLatitude
			latPercent = (lat + mc.horseLatitude) / latRange
			pressure   = latPercent
		elif lat >= -mc.polarFrontLatitude:
			latRange   = -mc.horseLatitude + mc.polarFrontLatitude
			latPercent = (lat + mc.polarFrontLatitude) / latRange
			pressure   = 1.0 - latPercent
		else:
			latRange   = -mc.polarFrontLatitude + 90.0
			latPercent = (lat + 90.0) / latRange
			pressure   = latPercent
		return pressure


	def ApplyFunction(self, func):
		for i in range(self.length):
			self.data[i] = func(self.data[i])


	def GetAverageInHex(self, x, y, radius):
		list = pb.getCirclePoints(x, y, radius)
		avg = 0.0
		for n in range(len(list)):
			hex = list[n]
			i = self.GetIndex(hex.x, hex.y)
			avg = avg + self.data[i]
		avg = avg / len(list)
		return avg


	def GetStdDevInHex(self, x, y, radius):
		list = pb.getCirclePoints(x, y, radius)
		avg = 0.0
		for n in range(len(list)):
			hex = list[n]
			i = self.GetIndex(hex.x, hex.y)
			avg = avg + self.data[i]
		avg = avg / len(list)
		deviation = 0.0
		for n in range(len(list)):
			hex = list[n]
			i = self.GetIndex(hex.x, hex.y)
			sqr = self.data[i] - avg
			deviation = deviation + (sqr * sqr)
		deviation = math.sqrt(deviation / len(list))
		return deviation


	def Smooth(self, radius):
		dataCopy = {}
		for y in range(self.height):
			for x in range(self.width):
				i = self.GetIndex(x, y)
				dataCopy[i] = self.GetAverageInHex(x, y, radius)
		self.data = dataCopy


	def Deviate(self, radius):
		dataCopy = {}
		for y in range(self.height):
			for x in range(self.width):
				i = self.GetIndex(x, y)
				dataCopy[i] = self.GetStdDevInHex(x, y, radius)
		self.data = dataCopy


	def IsOnMap(self, x, y):
		i = self.GetIndex(x, y)
		if i == -1:
			return False
		return True


##############################################################################
## PW3 Interpolation and Perlin
##############################################################################

def CubicInterpolate(v0, v1, v2, v3, mu):
	mu2 = mu * mu
	a0 = v3 - v2 - v0 + v1
	a1 = v0 - v1 - a0
	a2 = v2 - v0
	a3 = v1
	return (a0 * mu * mu2 + a1 * mu2 + a2 * mu + a3)


def BicubicInterpolate(v, muX, muY):
	a0 = CubicInterpolate(v[1],  v[2],  v[3],  v[4],  muX)
	a1 = CubicInterpolate(v[5],  v[6],  v[7],  v[8],  muX)
	a2 = CubicInterpolate(v[9],  v[10], v[11], v[12], muX)
	a3 = CubicInterpolate(v[13], v[14], v[15], v[16], muX)
	return CubicInterpolate(a0, a1, a2, a3, muY)


def CubicDerivative(v0, v1, v2, v3, mu):
	mu2 = mu * mu
	a0 = v3 - v2 - v0 + v1
	a1 = v0 - v1 - a0
	a2 = v2 - v0
	return ((3 * a0 * mu2) + (2 * a1 * mu + a2))


def BicubicDerivative(v, muX, muY):
	a0 = CubicInterpolate(v[1],  v[2],  v[3],  v[4],  muX)
	a1 = CubicInterpolate(v[5],  v[6],  v[7],  v[8],  muX)
	a2 = CubicInterpolate(v[9],  v[10], v[11], v[12], muX)
	a3 = CubicInterpolate(v[13], v[14], v[15], v[16], muX)
	return CubicDerivative(a0, a1, a2, a3, muY)


##This function gets a smoothly interpolated value from srcMap.
##x and y are non-integer coordinates of where the value is to
##be calculated, and wrap in both directions. srcMap is an object
##of type FloatMap.
def GetInterpolatedValue(X, Y, srcMap):
	points = {}
	fractionX = X - math.floor(X)
	fractionY = Y - math.floor(Y)
	##wrappedX and wrappedY are set to -1,-1 of the sampled area
	##so that the sample area is in the middle quad of the 4x4 grid
	wrappedX = ((math.floor(X) - 1) % srcMap.rectWidth)  + srcMap.rectX
	wrappedY = ((math.floor(Y) - 1) % srcMap.rectHeight) + srcMap.rectY
	for pY in range(4):
		y = pY + wrappedY
		for pX in range(4):
			x = pX + wrappedX
			srcIndex = srcMap.GetRectIndex(x, y)
			points[(pY * 4 + pX) + 1] = srcMap.data[int(srcIndex)]
	finalValue = BicubicInterpolate(points, fractionX, fractionY)
	return finalValue


def GetDerivativeValue(X, Y, srcMap):
	points = {}
	fractionX = X - math.floor(X)
	fractionY = Y - math.floor(Y)
	##wrappedX and wrappedY are set to -1,-1 of the sampled area
	##so that the sample area is in the middle quad of the 4x4 grid
	wrappedX = ((math.floor(X) - 1) % srcMap.rectWidth)  + srcMap.rectX
	wrappedY = ((math.floor(Y) - 1) % srcMap.rectHeight) + srcMap.rectY
	for pY in range(4):
		y = pY + wrappedY
		for pX in range(4):
			x = pX + wrappedX
			srcIndex = srcMap.GetRectIndex(x, y)
			points[(pY * 4) + pX + 1] = srcMap.data[int(srcIndex)]
	finalValue = BicubicDerivative(points, fractionX, fractionY)
	return finalValue


##This function gets Perlin noise for the destination coordinates. Note
##that in order for the noise to wrap, the area sampled on the noise map
##must change to fit each octave.
def GetPerlinNoise(x, y, destMapWidth, destMapHeight, initialFrequency, initialAmplitude, amplitudeChange, octaves, noiseMap):
	finalValue = 0.0
	frequency = initialFrequency
	amplitude = initialAmplitude
	##slight adjustment for seamless wrapping
	for i in range(1, octaves + 1):
		if noiseMap.wrapX:
			noiseMap.rectX = math.floor(noiseMap.width / 2 - (destMapWidth * frequency) / 2)
			noiseMap.rectWidth = max(math.floor(destMapWidth * frequency), 1)
			frequencyX = noiseMap.rectWidth / destMapWidth
		else:
			noiseMap.rectX = 0
			noiseMap.rectWidth = noiseMap.width
			frequencyX = frequency
		if noiseMap.wrapY:
			noiseMap.rectY = math.floor(noiseMap.height / 2 - (destMapHeight * frequency) / 2)
			noiseMap.rectHeight = max(math.floor(destMapHeight * frequency), 1)
			frequencyY = noiseMap.rectHeight / destMapHeight
		else:
			noiseMap.rectY = 0
			noiseMap.rectHeight = noiseMap.height
			frequencyY = frequency
		finalValue = finalValue + GetInterpolatedValue(x * frequencyX, y * frequencyY, noiseMap) * amplitude
		frequency = frequency * 2.0
		amplitude = amplitude * amplitudeChange
	finalValue = finalValue / octaves
	return finalValue


def GetPerlinDerivative(x, y, destMapWidth, destMapHeight, initialFrequency, initialAmplitude, amplitudeChange, octaves, noiseMap):
	finalValue = 0.0
	frequency = initialFrequency
	amplitude = initialAmplitude
	##slight adjustment for seamless wrapping
	for i in range(1, octaves + 1):
		if noiseMap.wrapX:
			noiseMap.rectX = math.floor(noiseMap.width / 2 - (destMapWidth * frequency) / 2)
			noiseMap.rectWidth = math.floor(destMapWidth * frequency)
			frequencyX = noiseMap.rectWidth/destMapWidth
		else:
			noiseMap.rectX = 0
			noiseMap.rectWidth = noiseMap.width
			frequencyX = frequency
		if noiseMap.wrapY:
			noiseMap.rectY = math.floor(noiseMap.height / 2 - (destMapHeight * frequency) / 2)
			noiseMap.rectHeight = math.floor(destMapHeight * frequency)
			frequencyY = noiseMap.rectHeight/destMapHeight
		else:
			noiseMap.rectY = 0
			noiseMap.rectHeight = noiseMap.height
			frequencyY = frequency
		finalValue = finalValue + GetDerivativeValue(x * frequencyX, y * frequencyY, noiseMap) * amplitude
		frequency = frequency * 2.0
		amplitude = amplitude * amplitudeChange
	finalValue = finalValue / octaves
	return finalValue


def GenerateTwistedPerlinMap(width, height, wrapX, wrapY, minFreq, maxFreq, varFreq):
	inputNoise = FloatMap()
	freqMap    = FloatMap()
	twistMap   = FloatMap()
	inputNoise.initialize(width, height, wrapX, wrapY)
	freqMap.initialize(width,    height, wrapX, wrapY)
	twistMap.initialize(width,   height, wrapX, wrapY)
	inputNoise.GenerateNoise()
	inputNoise.Normalize()
	for y in range(freqMap.height):
		for x in range(freqMap.width):
			i = freqMap.GetIndex(x, y)
			#AIAndy Bugfix - Perlin hex evaluation
			if mc.LandmassGenerator == 0:
				freqMap.data[i] = GetPerlinNoise(x,  y, freqMap.width, freqMap.height, varFreq, 1.0, 0.1, 8, inputNoise)
			else:
				xx = x + ((y % 2.0) / 2.0)
				freqMap.data[i] = GetPerlinNoise(xx, y, freqMap.width, freqMap.height, varFreq, 1.0, 0.1, 8, inputNoise)
	freqMap.Normalize()
	for y in range(twistMap.height):
		for x in range(twistMap.width):
			i = twistMap.GetIndex(x, y)
			freq = freqMap.data[i] * (maxFreq - minFreq) + minFreq
			mid = (maxFreq - minFreq) / 2 + minFreq
			coordScale = freq / mid
			offset = (1.0 - coordScale) / mid
			ampChange = 0.85 - (freqMap.data[i] * 0.5)
			#AIAndy Bugfix - Perlin hex evaluation
			if mc.LandmassGenerator == 0:
				twistMap.data[i] = GetPerlinNoise(x  + offset, y + offset, twistMap.width, twistMap.height, mid, 1.0, ampChange, 8, inputNoise)
			else:
				xx = x + ((y % 2.0) / 2.0)
				twistMap.data[i] = GetPerlinNoise(xx + offset, y + offset, twistMap.width, twistMap.height, mid, 1.0, ampChange, 8, inputNoise)
	twistMap.Normalize()
	return twistMap


def GenerateMountainMap(width, height, wrapX, wrapY, initFreq):
	inputNoise1 = FloatMap()
	inputNoise2 = FloatMap()
	mountainMap = FloatMap()
	stdDevMap   = FloatMap()
	noiseMap    = FloatMap()
	moundMap    = FloatMap()
	inputNoise1.initialize(width, height, wrapX, wrapY)
	inputNoise2.initialize(width, height, wrapX, wrapY)
	mountainMap.initialize(width, height, wrapX, wrapY)
	stdDevMap.initialize(width,   height, wrapX, wrapY)
	noiseMap.initialize(width,    height, wrapX, wrapY)
	moundMap.initialize(width,    height, wrapX, wrapY)
	inputNoise1.GenerateBinaryNoise()
	inputNoise1.Normalize()
	inputNoise2.GenerateNoise()
	inputNoise2.Normalize()
	for y in range(mountainMap.height):
		for x in range(mountainMap.width):
			i = mountainMap.GetIndex(x, y)
			#AIAndy Bugfix - Perlin hex evaluation
			if mc.LandmassGenerator == 0:
				mountainMap.data[i] = GetPerlinNoise(x,  y, mountainMap.width, mountainMap.height, initFreq, 1.0, 0.4, 8, inputNoise1)
				noiseMap.data[i]    = GetPerlinNoise(x,  y, mountainMap.width, mountainMap.height, initFreq, 1.0, 0.4, 8, inputNoise2)
			else:
				xx = x + ((y % 2.0) / 2.0)
				mountainMap.data[i] = GetPerlinNoise(xx, y, mountainMap.width, mountainMap.height, initFreq, 1.0, 0.4, 8, inputNoise1)
				noiseMap.data[i]    = GetPerlinNoise(xx, y, mountainMap.width, mountainMap.height, initFreq, 1.0, 0.4, 8, inputNoise2)
			stdDevMap.data[i] = mountainMap.data[i]
	mountainMap.Normalize()
	stdDevMap.Deviate(7)
	stdDevMap.Normalize()
	noiseMap.Normalize()
	for y in range(mountainMap.height):
		for x in range(mountainMap.width):
			i = mountainMap.GetIndex(x, y)
			val = mountainMap.data[i]
			moundMap.data[i] = (math.sin(val * math.pi * 2.0 - math.pi * 0.5) * 0.5 + 0.5) * GetAttenuationFactor(mountainMap, x, y)
			if val < 0.5:
				val = val * 4.0
			else:
				val = (1.0 - val) * 4.0
			mountainMap.data[i] = moundMap.data[i]
	mountainMap.Normalize()
	for y in range(mountainMap.height):
		for x in range(mountainMap.width):
			i = mountainMap.GetIndex(x, y)
			val = mountainMap.data[i]
			mountainMap.data[i] = math.pow(math.pow(math.sin(val * 3.0 * math.pi + math.pi * 0.5), 16) * val, 0.5)
			if mountainMap.data[i] > 0.2:
				mountainMap.data[i] = 1.0
			else:
				mountainMap.data[i] = 0.0
	# advc: simplified
	land = mc.landPercent * mc.SeaLevelFactor
	stdDevThreshold = FindThresholdFromPercent(stdDevMap.data, stdDevMap.length, land, True)
	for y in range(mountainMap.height):
		for x in range(mountainMap.width):
			i = mountainMap.GetIndex(x, y)
			val = mountainMap.data[i]
			dev = 2.0 * stdDevMap.data[i] - 2.0 * stdDevThreshold
			mountainMap.data[i] = (val + moundMap.data[i]) * dev
	mountainMap.Normalize()
	return mountainMap


def GetAttenuationFactor(map, x, y):
	southY     = map.height * mc.southAttenuationRange
	southRange = map.height * mc.southAttenuationRange
	yAttenuation = 1.0
	if y < southY:
		yAttenuation = mc.southAttenuationFactor + (y / southRange) * (1.0 - mc.southAttenuationFactor)
	northY     = map.height - (map.height * mc.northAttenuationRange)
	northRange = map.height * mc.northAttenuationRange
	if y > northY:
		yAttenuation = mc.northAttenuationFactor + ((map.height - y) / northRange) * (1.0 - mc.northAttenuationFactor)
	eastY     = map.width - (map.width * mc.eastAttenuationRange)
	eastRange = map.width * mc.eastAttenuationRange
	xAttenuation = 1.0
	if x > eastY:
		xAttenuation = mc.eastAttenuationFactor + ((map.width - x) / eastRange) * (1.0 - mc.eastAttenuationFactor)
	westY     = map.width * mc.westAttenuationRange
	westRange = map.width * mc.westAttenuationRange
	if x < westY:
		xAttenuation = mc.westAttenuationFactor + (x / westRange) * (1.0 - mc.westAttenuationFactor)
	return yAttenuation * xAttenuation


##############################################################################
## PW3 Landmass Generator
##############################################################################

class ElevationMap3(FloatMap):
	def __init__(self):
		return


	def GenerateElevationMap(self):
		# <advc> Increased in MapConstants.initialize for larger landmasses. Not sure if it has that effect, but, if so, that'll make it more difficult to prevent a pangaea, so:
		twistMinFreq = mc.twistMinFreq
		if mc.OldWorldStarts:
			twistMinFreq *= 0.6 # </advc>
		twistMinFreq = 128.0 / self.width * twistMinFreq #0.02  / 128
		twistMaxFreq = 128.0 / self.width * mc.twistMaxFreq #0.12  / 128
		twistVar     = 128.0 / self.width * mc.twistVar     #0.042 / 128
		mountainFreq = 128.0 / self.width * mc.mountainFreq #0.05  / 128
		twistMap     = GenerateTwistedPerlinMap(self.width, self.height, mc.WrapX, mc.WrapY, twistMinFreq, twistMaxFreq, twistVar)
		mountainMap  = GenerateMountainMap(self.width,      self.height, mc.WrapX, mc.WrapY, mountainFreq)
		for y in range(self.height):
			for x in range(self.width):
				i = self.GetIndex(x, y)
				tVal = twistMap.data[i]
				tVal = math.pow(math.sin(tVal * math.pi - math.pi * 0.5) * 0.5 + 0.5, 0.25) #this formula adds a curve flattening the extremes
				self.data[i] = (tVal + ((mountainMap.data[i] * 2.0) - 1.0) * mc.mountainWeight)
		self.Normalize()
		##attenuation should not break normalization
		for y in range(self.height):
			for x in range(self.width):
				i = self.GetIndex(x, y)
				attenuationFactor = GetAttenuationFactor(self, x, y)
				self.data[i] *= attenuationFactor
		# <advc> Moved into new method (like it was already done for ElevationMap2)
		self.CalculateSeaLevel()


	def CalculateSeaLevel(self):
		land = mc.landPercent * mc.SeaLevelFactor
		self.seaLevelThreshold = FindThresholdFromPercent(self.data, self.length, land, True)
		# </advc>

	def IsBelowSeaLevel(self, x, y):
		i = self.GetIndex(x, y)
		if self.data[i] < self.seaLevelThreshold:
			return True
		return False


	def GetAltitudeAboveSeaLevel(self, x, y):
		i = self.GetIndex(x, y)
		if i == -1:
			return 0.0
		altitude = self.data[i]
		if altitude <= self.seaLevelThreshold:
			return 0.0
		altitude = (altitude - self.seaLevelThreshold) / (1.0 - self.seaLevelThreshold)
		return altitude


	def FillInLakes(self):
		am = AreaMap(self.width, self.height, True, True)
		am.defineAreas(self.IsBelowSeaLevel)
		oceanID = am.getOceanID()
		for y in range(self.height):
			for x in range(self.width):
				if self.IsBelowSeaLevel(x, y):
					i = self.GetIndex(x, y)
					if am.data[i] != oceanID:
						#check the size of this body of water, if too small, change to land
						for a in am.areaList:
							if a.ID == am.data[i] and a.size < mc.minOceanSize:
								self.data[i] = self.seaLevelThreshold


e3 = ElevationMap3()

# advc: Based on Totestra's "rotateMap" function
def centerMap(heightMap, width, height, indexfunc):
	minX = 0
	minVal = 10000.0
	# <advc>
	extraRange = width // 50
	#print("extraRange=" + str(extraRange)) # </advc>
	for x in range(width):
		val = 0.0
		for y in range(height):
			# advc: A wider ocean strip is better
			for i in range(x - extraRange, x + extraRange + 1):
				val += ( heightMap[indexfunc(#x, y)
						i % width, y)] / (abs(x - i) + 1) ) # advc
		#print "for x %d val is %f minVal %f" % (x,val,minVal)
		if val < minVal:
			minX = x
			minVal = val
	#print "minX is %d" % (minX) #DEBUG
	for y in range(height):
		tempRow = []
		for x in range(width):
			tempRow.append(heightMap[indexfunc(x, y)])
		for x in range(width):
			heightMap[indexfunc(x,y)] = tempRow[((x + minX) % width)]


##############################################################################
## PW2 Landmass Generator
##############################################################################

class ElevationMap2(FloatMap):
	def __init__(self):
		return


	def GenerateElevationMap(self):
		self.length = mc.hmWidth * mc.hmHeight
		self.data   = array('d')
		for i in range(self.length):
			self.data.append(0.0)
		self.GenerateMidpointDisplacement()


	def checkMaxGrain(self):
		#hm map dimensions (minus 1 if no wrapping) must be evenly divisible by max grain
		ok = True
		width  = mc.hmWidth
		height = mc.hmHeight
		if not mc.WrapX:
			width  -= 1
		if not mc.WrapY:
			height -= 1
		if width  % mc.hmMaxGrain != 0:
			ok = False
		if height % mc.hmMaxGrain != 0:
			ok = False
		if not ok:
			raise ValueError, "height map dimesions not divisible by mc.hmMaxGrain. also check wrapping options"


	def isPlotOnMargin(self, x, y):
		marginSize = mc.hmMaxGrain * mc.hmGrainMargin
		#first check top and bottom
		if mc.southMargin:
			if y < marginSize:
				return True
		if mc.northMargin:
			if y > mc.hmHeight - marginSize:
				return True
		#check right and left
		if mc.westMargin:
			if x < marginSize:
				return True
		if mc.eastMargin:
			if x > mc.hmWidth - marginSize:
				return True
		#now check middle
		if mc.hmSeparation != mc.NO_SEPARATION:
			if mc.hmSeparation == mc.NORTH_SOUTH_SEPARATION:
				dimension = y
				middle = mc.hmHeight / 2
			elif mc.hmSeparation == mc.EAST_WEST_SEPARATION:
				dimension = x
				middle = mc.hmWidth  / 2
			else:
				raise ValueError, "bad hmSeparation type"
			if dimension > middle - marginSize and dimension < middle + marginSize:
				return True
		return False


	def GenerateMidpointDisplacement(self):
		self.checkMaxGrain()
		#make list of map plots that aren't on margin for each
		#map quadrant. We want to place the initial peaks randomly, but we
		#also want to ensure fairly even distribution so that
		#not all the peaks are on one side of the map. For this purpose
		#we will treat each map quadrant separately.
		peaksNWList = list()
		peaksNEList = list()
		peaksSWList = list()
		peaksSEList = list()
		middleX = mc.hmWidth  / 2
		middleY = mc.hmHeight / 2
		for y in range(0, mc.hmHeight, mc.hmMaxGrain):
			for x in range(0, mc.hmWidth, mc.hmMaxGrain):
				if not self.isPlotOnMargin(x, y):
					if x < middleX and y < middleY:
						peaksSWList.append((x, y))
					elif x >= middleX and y < middleY:
						peaksSEList.append((x, y))
					elif x < middleX and y >= middleY:
						peaksNWList.append((x, y))
					elif x >= middleX and y >= middleY:
						peaksNEList.append((x, y))
		#shuffle the lists
		peaksNWList = ShuffleList(peaksNWList)
		peaksNEList = ShuffleList(peaksNEList)
		peaksSWList = ShuffleList(peaksSWList)
		peaksSEList = ShuffleList(peaksSEList)
		#place desired number of peaks in each quadrant
		totalNonMargin  = len(peaksNWList)
		totalNonMargin += len(peaksNEList)
		totalNonMargin += len(peaksSWList)
		totalNonMargin += len(peaksSEList)
		count = max(1, int(float(totalNonMargin) * mc.hmInitialPeakPercent * 0.25))
		for n in range(count):
			x, y = peaksNWList[n]
			i = GetHmIndex(x, y)
			self.data[i] = 1.0
			x, y = peaksNEList[n]
			i = GetHmIndex(x, y)
			self.data[i] = 1.0
			x, y = peaksSWList[n]
			i = GetHmIndex(x, y)
			self.data[i] = 1.0
			x, y = peaksSEList[n]
			i = GetHmIndex(x, y)
			self.data[i] = 1.0
		#Now use a diamond-square algorithm(sort of) to generate the rest
		currentGrain = float(mc.hmMaxGrain)
		while currentGrain > 1.0:
			#h is scalar for random displacement
			h = (currentGrain/float(mc.hmMaxGrain)) * float(mc.hmNoiseLevel)
			#First do the 'square' pass
			for y in range(0, mc.hmHeight, int(currentGrain)):
				for x in range(0, mc.hmWidth, int(currentGrain)):
					#on the square pass, GetHmIndex should handle all wrapping needs
					topLeft = GetHmIndex(x, y)
					topRight = GetHmIndex(x + int(currentGrain), y)
					if topRight == -1:
						continue #this means no wrap in x direction
					bottomLeft = GetHmIndex(x, y + int(currentGrain))
					if bottomLeft == -1:
						continue #this means no wrap in y direction
					bottomRight = GetHmIndex(x + int(currentGrain),       y + int(currentGrain))
					middle      = GetHmIndex(x + int(currentGrain / 2.0), y + int(currentGrain / 2.0))
					average = (self.data[topLeft] + self.data[topRight] + self.data[bottomLeft] + self.data[bottomRight]) / 4.0
					displacement = h * PRand.random() - h / 2.0
					self.data[middle] = average + displacement
					#now add that heuristic to the four points to diminish artifacts.
					#We don't need this on the diamond pass I don't think
					displacement = h * PRand.random() - h / 2.0
					self.data[topLeft] += displacement
					displacement = h * PRand.random() - h / 2.0
					self.data[topRight] += displacement
					displacement = h * PRand.random() - h / 2.0
					self.data[bottomLeft] += displacement
					displacement = h * PRand.random() - h / 2.0
					self.data[bottomRight] += displacement
			#Now do the 'diamond' pass, there are two diamonds for each x.
			#Possible wrapping is a big complication on this pass. Sorry!
			for y in range(0, mc.hmHeight, int(currentGrain)):
				for x in range(0, mc.hmWidth, int(currentGrain)):
					#first do the right facing diamond
					left = GetHmIndex(x,y)
					right = GetHmIndex(x + int(currentGrain),y)
					if right != -1: #if we're off map at this point go to next diamond
						average = self.data[left] + self.data[right]
						contributers = 2 #each diamond may have two or three contributers, 2 so far
						top = GetHmIndex(x + int(currentGrain / 2.0), y - int(currentGrain / 2.0))
						if top != -1:
							contributers += 1
							average += self.data[top]
						bottom = GetHmIndex(x + int(currentGrain / 2.0), y + int(currentGrain / 2.0))
						if bottom != -1:
							contributers += 1
							average += self.data[bottom]
						average = average/float(contributers)
						middle = GetHmIndex(x + int(currentGrain / 2.0), y)
						displacement = h * PRand.random() - h / 2.0
						self.data[middle] = average + displacement
					#now do the down facing diamond
					top = GetHmIndex(x,y)
					bottom = GetHmIndex(x,y + int(currentGrain))
					if bottom != -1:
						average = self.data[top] + self.data[bottom]
						contributers = 2
						right = GetHmIndex(x + int(currentGrain / 2.0), y + int(currentGrain / 2.0))
						if right != -1:
							contributers += 1
							average += self.data[right]
						left = GetHmIndex(x - int(currentGrain / 2.0), y + int(currentGrain / 2.0))
						if left != -1:
							contributers += 1
							average += self.data[left]
						average = average/float(contributers)
						middle = GetHmIndex(x,y + int(currentGrain / 2.0))
						displacement = h * PRand.random() - h / 2.0
						self.data[middle] = average + displacement
			currentGrain = currentGrain / 2.0
		NormalizeMap(self.data, mc.hmWidth, mc.hmHeight)


	def PerformTectonics(self):
		self.plateMap  = list()
		growthPlotList = list()
		plateList      = list()
		borderMap           = array('i') #this will help in later distance calculations
		self.plateHeightMap = array('d')
		preSmoothMap        = array('d')
		# <advc>
		# Sounds like this should have a big impact on the shape of the landmasses
		# and mountain chains, but I find it hard to tell a difference. I guess
		# a larger map should have more plates.
		fPlates = math.pow(mc.width * mc.height, 0.33) * mc.SeaLevelFactor / 2
		fPlates *= 0.75 + PRand.random() * 0.5
		mc.hmNumberOfPlates = int(round(fPlates))
		plateGrowthChanceRand = PRand.random() * 0.24 - 0.12
		plateGrowthChanceX = mc.plateGrowthChanceX + plateGrowthChanceRand
		plateGrowthChanceY = mc.plateGrowthChanceY + plateGrowthChanceRand
		distanceFilterSize = mc.distanceFilterSize + 2 * int(PRand.random() * 4 - 2)
		assert distanceFilterSize % 2 == 1
		rippleAmplitude = mc.rippleAmplitude + max(0, CyMap().getWorldSize() - 3) * 0.2
		rippleAmplitude += PRand.random() * 0.2 - 0.1
		# </advc>
		maxDistance = math.sqrt(pow(float(distanceFilterSize / 2), 2) + pow(float(distanceFilterSize / 2), 2))
		#initialize maps
		for y in range(mc.hmHeight):
			for x in range(mc.hmWidth):
				i = GetHmIndex(x, y)
				self.plateMap.append(PlatePlot(0, maxDistance))
				borderMap.append(False)
				self.plateHeightMap.append(0.0)
				preSmoothMap.append(0.0)
		plateList.append(Plate(0, -1, -1)) #zero placeholder (very silly I know)
		#seed plates
		for i in range(1, mc.hmNumberOfPlates + 1):
			#first find a random seed point that is not blocked by previous points
			iterations = 0
			while (True):
				iterations += 1
				if iterations > 10000:
					raise ValueError, "endless loop in region seed placement"
				seedX = PRand.randint(0, mc.hmWidth  + 1)
				seedY = PRand.randint(0, mc.hmHeight + 1)
				# <advc>
				if mc.plateSeedRerollExp > 0:
					if mc.WrapX and PRand.random() < pow(
							1.0 - min(mc.hmWidth + 1 - seedX, seedX) / (mc.hmWidth + 1.0),
							mc.plateSeedRerollExp):
						continue
					elif mc.WrapY and PRand.random() < pow(
							1.0 - min(mc.hmHeight + 1 - seedY, seedY) / (mc.hmHeight + 1.0),
							mc.plateSeedRerollExp):
						continue # </advc>
				n = GetHmIndex(seedX, seedY)
				if not self.isSeedBlocked(plateList, seedX, seedY):
					self.plateMap[n].plateID = i
					plate = Plate(i, seedX, seedY)
					plateList.append(plate)
					#Now fill a 3x3 area to insure a minimum region size
					for direction in range(1, 9):
						xx, yy = GetNeighbor(seedX, seedY, direction)
						nn = GetHmIndex(xx, yy)
						if nn != -1:
							self.plateMap[nn].plateID = i
							xx, yy = CoordsFromIndex(nn, self.width) # advc.001
							plot = (xx, yy, i)
							growthPlotList.append(plot)
					break
		#Now cause the seeds to grow into plates
		iterations = 0
		while(len(growthPlotList) > 0):
			iterations += 1
			if iterations > 200000:
				# <advc>
				print("plateGrowthChance=" + str(plateGrowthChanceY))
				print("distanceFilterSize=" + str(distanceFilterSize))
				# </advc>
				raise ValueError, "endless loop in plate growth"
			plot = growthPlotList[0]
			roomLeft = False
			for direction in range(1, 5):
				x, y, plateID = plot
				i = GetHmIndex(x, y)
				xx, yy = GetNeighbor(x, y, direction)
				ii = GetHmIndex(xx, yy)
				if ii == -1:
					plateList[plateID].isOnMapEdge = True
					continue
				if self.plateMap[ii].plateID != plateID and self.plateMap[ii].plateID != 0:
					borderMap[i]  = True
					borderMap[ii] = True
				elif self.plateMap[ii].plateID == 0:
					roomLeft = True
					if direction == mc.N or direction == mc.S:
						growthChance = plateGrowthChanceY
					else:
						growthChance = plateGrowthChanceX
					if PRand.random() < growthChance:
						self.plateMap[ii].plateID = plateID
						xx, yy = CoordsFromIndex(ii, self.width) # advc.001
						newPlot = (xx, yy, plateID)
						growthPlotList.append(newPlot)
			#move plot to the end of the list if room left,
			#delete it if no room left
			if roomLeft:
				growthPlotList.append(plot)
			del growthPlotList[0]
		#to balance the map we want at least one plate stagger upward
		#in each quadrant
		NWfound = False
		NEfound = False
		SEfound = False
		SWfound = False
		for plate in plateList:
			if plate.GetQuadrant() == plate.NW and not NWfound:
				plate.raiseOnly = True
				NWfound         = True
			if plate.GetQuadrant() == plate.NE and not NEfound:
				plate.raiseOnly = True
				NEfound         = True
			if plate.GetQuadrant() == plate.SE and not SEfound:
				plate.raiseOnly = True
				SEfound         = True
			if plate.GetQuadrant() == plate.SW and not SWfound:
				plate.raiseOnly = True
				SWfound         = True
		#Stagger the plates somewhat to add interest
		steps = int(mc.plateStaggerRange / mc.plateStagger)
		for i in range(self.length):
			if plateList[self.plateMap[i].plateID].isOnMapEdge and PRand.random() < mc.chanceForWaterEdgePlate:
				preSmoothMap[i] = 0.0
			elif plateList[self.plateMap[i].plateID].raiseOnly:
				preSmoothMap[i] = (float(self.plateMap[i].plateID % steps) * mc.plateStagger) / 2.0 + 0.5
			else:
				preSmoothMap[i] = float(self.plateMap[i].plateID % steps) * mc.plateStagger
		#Now smooth the plate height map and create the distance map at the same time
		#Since the algorithm is the same
		for y in range(mc.hmHeight):
			for x in range(mc.hmWidth):
				contributors = 0
				avg = 0
				i = GetHmIndex(x, y)
				isBorder = False
				if borderMap[i]:
					isBorder = True
				plateID = self.plateMap[i].plateID
				for yy in range(y - distanceFilterSize / 2, y + distanceFilterSize / 2 + 1, 1):
					for xx in range(x - distanceFilterSize / 2, x + distanceFilterSize / 2 + 1, 1):
						ii = GetHmIndex(xx, yy)
						if ii == -1:
							continue
						contributors += 1
						avg += preSmoothMap[ii]
						if isBorder and plateID != self.plateMap[ii].plateID:
							distance = math.sqrt(pow(float(y - yy), 2) + pow(float(x - xx), 2))
							if distance < self.plateMap[ii].distanceList[plateID]:
								self.plateMap[ii].distanceList[plateID] = distance
				if avg > 0: # advc.001
					avg = avg/float(contributors)
				self.plateHeightMap[i] = avg
		#Now add ripple formula to plateHeightMap
		for i in range(self.length):
			avgRippleTop    = 0.0
			avgRippleBottom = 0.0
			for plateID in range(1, mc.hmNumberOfPlates + 1):
				distanceWeight = maxDistance - self.plateMap[i].distanceList[plateID]
				if plateList[plateID].seedX < plateList[self.plateMap[i].plateID].seedX:
					angleDifference = AngleDifference(plateList[self.plateMap[i].plateID].angle, plateList[plateID].angle)
				else:
					angleDifference = AngleDifference(plateList[plateID].angle, plateList[self.plateMap[i].plateID].angle)
				ripple = (pow(math.cos(mc.rippleFrequency * self.plateMap[i].distanceList[plateID]) * (-self.plateMap[i].distanceList[plateID] / maxDistance + 1), 2) + (-self.plateMap[i].distanceList[plateID] / maxDistance + 1)) * rippleAmplitude * math.sin(math.radians(angleDifference))
				avgRippleTop += (ripple * distanceWeight)
				avgRippleBottom += distanceWeight
			if avgRippleBottom == 0.0:
				avgRipple = 0.0
			else:
				avgRipple = avgRippleTop / avgRippleBottom
			self.plateHeightMap[i] += avgRipple - (avgRipple * PRand.random() * mc.plateNoiseFactor)
		NormalizeMap(self.plateHeightMap, mc.hmWidth, mc.hmHeight)


	def CombineMaps(self):
		#Now add plateHeightMap to HeightMap
		for i in range(self.length):
			self.data[i] += self.plateHeightMap[i] * mc.plateMapScale
		#depress margins, this time with brute force
		marginSize = mc.hmMaxGrain * mc.hmGrainMargin
		for y in range(mc.hmHeight):
			for x in range(mc.hmWidth):
				i = GetHmIndex(x, y)
				if mc.westMargin:
					if x < marginSize:
						self.data[i] *= (float(x)/float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
				if mc.eastMargin:
					if mc.hmWidth - x < marginSize:
						self.data[i] *= (float(mc.hmWidth - x) / float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
				if mc.southMargin:
					if y < marginSize:
						self.data[i] *= (float(y) / float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
				if mc.northMargin:
					if mc.hmHeight - y < marginSize:
						self.data[i] *= (float(mc.hmHeight - y) / float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
				if mc.hmSeparation == mc.NORTH_SOUTH_SEPARATION:
					difference = abs((mc.hmHeight / 2) - y)
					if difference < marginSize:
						self.data[i] *= (float(difference) / float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
				elif mc.hmSeparation == mc.EAST_WEST_SEPARATION:
					difference = abs((mc.hmWidth / 2) - x)
					if difference < marginSize:
						self.data[i] *= (float(difference) / float(marginSize)) * (1.0 - mc.hmMarginDepth) + mc.hmMarginDepth
		NormalizeMap(self.data, mc.hmWidth, mc.hmHeight)


	def AddWaterBands(self):
		#validate water bands. Maps that wrap cannot have one in that direction
		if mc.WrapX and (mc.eastWaterBand  != 0 or mc.westWaterBand  != 0):
			raise ValueError,"east/west water bands cannot be used when wrapping in X direction."
		if mc.WrapY and (mc.northWaterBand != 0 or mc.southWaterBand != 0):
			raise ValueError,"north/south water bands cannot be used when wrapping in Y direction."
		newWidth  = mc.hmWidth  + mc.eastWaterBand  + mc.westWaterBand
		newHeight = mc.hmHeight + mc.northWaterBand + mc.southWaterBand
		newHeightMap = array('d')
		for y in range(newHeight):
			for x in range(newWidth):
				ii = GetHmIndex(x - mc.westWaterBand, y - mc.southWaterBand)
				if ii >= 0:
					newHeightMap.append(self.data[ii])
				else:
					newHeightMap.append(0.0)
		mc.hmWidth  = newWidth
		mc.hmHeight = newHeight
		self.data = newHeightMap


	def CalculateSeaLevel(self):
		land = mc.landPercent * mc.SeaLevelFactor # advc: simplified
		self.seaLevelThreshold = FindValueFromPercent(self.data, self.length, land, True)


	def IsBelowSeaLevel(self, x, y):
		i = GetHmIndex(x, y)
		if self.data[i] < self.seaLevelThreshold:
			return True
		return False


	## This function returns altitude in relation to sea level with
	## 0.0 being seaLevel and 1.0 being highest altitude
	def GetAltitudeAboveSeaLevel(self, x, y):
		i = GetHmIndex(x, y)
		if i == -1:
			return 0.0
		altitude = self.data[i]
		if altitude <= self.seaLevelThreshold:
			return 0.0
		altitude = (altitude - self.seaLevelThreshold) / (1.0 - self.seaLevelThreshold)
		return altitude


	def setAltitudeAboveSeaLevel(self, x, y, altitude):
		i = GetHmIndex(x, y)
		if i == -1:
			return
		self.data[i] = ((1.0 - self.seaLevelThreshold) * altitude) + self.seaLevelThreshold


	def isSeedBlocked(self, plateList, seedX, seedY):
		for plate in plateList:
			if seedX > plate.seedX - mc.minSeedRange and seedX < plate.seedX + mc.minSeedRange:
				if seedY > plate.seedY - mc.minSeedRange and seedY < plate.seedY + mc.minSeedRange:
					return True
		#Check for edge
		if seedX < mc.minEdgeRange or seedX >= (mc.hmWidth  + 1) - mc.minEdgeRange:
			return True
		if seedY < mc.minEdgeRange or seedY >= (mc.hmHeight + 1) - mc.minEdgeRange:
			return True
		return False


	def GetInfluFromDistance(self, sinkValue, peakValue, searchRadius, distance):
		influence = peakValue
		maxDistance = math.sqrt(pow(float(searchRadius), 2) + pow(float(searchRadius), 2))
		#minDistance = 1.0
		influence -= ((peakValue - sinkValue) * (distance - 1.0)) / (maxDistance - 1.0)
		return influence


	def FindDistanceToPlateBoundary(self, x, y, searchRadius):
		minDistance = 10.0
		i = self.GetIndex(x, y)
		for yy in range(y - searchRadius, y + searchRadius):
			for xx in range(x - searchRadius, x + searchRadius):
				ii = self.GetIndex(xx, yy)
				if self.plateMap[i] != self.plateMap[ii]:
					distance = math.sqrt(pow(float(xx - x), 2) + pow(float(yy - y), 2))
					if distance < minDistance:
						minDistance = distance
		if minDistance == 10.0:
			return 0.0
		return minDistance


	def FillInLakes(self):
		#smaller lakes need to be filled in for now. The river system will
		#most likely recreate them later due to drainage calculation
		#according to certain rules. This makes the lakes look much better
		#and more sensible.
		am = AreaMap(mc.hmWidth, mc.hmHeight, True, True)
		am.defineAreas(isWaterMatch)
		oceanID = am.getOceanID()
		for y in range(mc.hmHeight):
			for x in range(mc.hmWidth):
				i = GetHmIndex(x, y)
				if self.IsBelowSeaLevel(x, y) and am.data[i] != oceanID:
					#check the size of this body of water, if too small, change to land
					for a in am.areaList:
						if a.ID == am.data[i] and a.size < mc.minInlandSeaSize:
							self.data[i] = self.seaLevelThreshold


class Plate:
	def __init__(self, ID, seedX, seedY):
		self.ID    = ID
		self.seedX = seedX
		self.seedY = seedY
		self.isOnMapEdge = False
		self.raiseOnly   = False
		self.angle = (PRand.random() * 360) - 180
		self.NW = 0
		self.NE = 1
		self.SE = 2
		self.SW = 3


	def GetQuadrant(self):
		if self.seedY < mc.hmHeight / 2:
			if self.seedX < mc.hmWidth / 2:
				return self.SW
			else:
				return self.SE
		else:
			if self.seedX < mc.hmWidth / 2:
				return self.NW
			else:
				return self.NE


class PlatePlot:
	def __init__(self, plateID, maxDistance):
		self.plateID = plateID
		self.distanceList = list()
		for i in range(mc.hmNumberOfPlates + 1):
			self.distanceList.append(maxDistance)


e2 = ElevationMap2()


##############################################################################
## PW3 Climate System
##############################################################################

class ClimateMap3:
	def __init__(self):
		return


	def GenerateTemperatureMap(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		# advc: Make this map also available for GenerateRainfallMap
		self.aboveSeaLevelMap = FloatMap()
		self.summerMap        = FloatMap()
		self.winterMap        = FloatMap()
		self.TemperatureMap   = FloatMap()
		self.aboveSeaLevelMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		self.summerMap.initialize(em.width,        em.height, em.wrapX, em.wrapY)
		self.winterMap.initialize(em.width,        em.height, em.wrapX, em.wrapY)
		self.TemperatureMap.initialize(em.width,   em.height, em.wrapX, em.wrapY)
		for y in range(em.height):
			for x in range(em.width):
				i = self.aboveSeaLevelMap.GetIndex(x, y)
				if em.IsBelowSeaLevel(x, y):
					self.aboveSeaLevelMap.data[i] = 0.0
				else:
					self.aboveSeaLevelMap.data[i] = em.data[i] - em.seaLevelThreshold
		self.aboveSeaLevelMap.Normalize()
		# <advc>
		waterTempMap = FloatMap()
		waterTempMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		# </advc>
		zenith        = mc.tropicsLatitude
		topTempLat    = mc.topLatitude + zenith
		bottomTempLat = mc.bottomLatitude
		latRange = topTempLat - bottomTempLat
		# advc: Moved into new method
		self.fillLatitudeMap(self.summerMap, waterTempMap, bottomTempLat, latRange)
		zenith        = mc.tropicsLatitude * -1
		topTempLat    = mc.topLatitude
		bottomTempLat = mc.bottomLatitude + zenith
		latRange = topTempLat - bottomTempLat
		# advc: Moved into new method
		self.fillLatitudeMap(self.winterMap, waterTempMap, bottomTempLat, latRange)
		# advc:
		self.distToSea = createDistanceMap(False)
		for y in range(em.height):
			for x in range(em.width):
				i = self.TemperatureMap.GetIndex(x, y)
				self.TemperatureMap.data[i] = (self.winterMap.data[i] + self.summerMap.data[i]) * (1.0 - self.aboveSeaLevelMap.data[i])
				# <advc> Based on C2C_World.py
				# 1.0 would correspond to the C2C formula. (However, C2C computes the latitude-based temperatures differently - I think).
				maritimeWeight = 0.75
				if self.distToSea[i] > 0:
					if self.distToSea[i] <= 1 + CyMap().getWorldSize():
						seaDistMult = (waterTempMap.data[i] - self.TemperatureMap.data[i]) / float(self.distToSea[i])
					else:
						seaDistMult = (self.distToSea[i] + em.width / 12.0) / ((13.0/12.0) * em.width)
					self.TemperatureMap.data[i] *= 1 + maritimeWeight * seaDistMult
				# </advc>
		self.TemperatureMap.Normalize()


	# advc: Cut from GenerateTemperatureMap
	def fillLatitudeMap(self, tempMap, waterTempMap, bottomTempLat, latRange):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		for y in range(em.height):
			# advc.opt/ LM: Moved some stuff out of the inner loop
			lat = tempMap.GetLatitudeForY(y)
			latPercent = (lat - bottomTempLat) / latRange
			latTemp = math.sin(latPercent * math.pi * 2.0 - math.pi * 0.5) * 0.5 + 0.5
			waterTemp = latTemp * mc.maxWaterTemp + mc.minWaterTemp
			for x in range(em.width):
				i = tempMap.GetIndex(x, y)
				waterTempMap.data[i] += waterTemp
				if em.IsBelowSeaLevel(x, y):
					tempMap.data[i] = waterTemp
				else:
					tempMap.data[i] = latTemp
		tempMap.Smooth(int(math.floor(em.width / 8.0)))
		tempMap.Normalize()


	def GenerateRainfallMap(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		geoMap                 = FloatMap()
		moistureMap            = FloatMap()
		rainfallSummerMap      = FloatMap()
		rainfallWinterMap      = FloatMap()
		rainfallGeostrophicMap = FloatMap()
		self.RainfallMap       = FloatMap()
		geoMap.initialize(em.width,                 em.height, em.wrapX, em.wrapY)
		rainfallSummerMap.initialize(em.width,      em.height, em.wrapX, em.wrapY)
		rainfallWinterMap.initialize(em.width,      em.height ,em.wrapX, em.wrapY)
		rainfallGeostrophicMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		self.RainfallMap.initialize(em.width,       em.height, em.wrapX, em.wrapY)
		for y in range(em.height):
			lat      = em.GetLatitudeForY(y) #AIAndy - moved these 2 lines out of x loop
			pressure = em.GetGeostrophicPressure(lat)
			for x in range(em.width):
				i = em.GetIndex(x, y)
				geoMap.data[i] = pressure
		geoMap.Normalize()
		sortedSummerMap = []
		sortedWinterMap = []
		for y in range(em.height):
			for x in range(em.width):
				i = em.GetIndex(x, y)
				sortedSummerMap.append((x, y, self.summerMap.data[i]))
				sortedWinterMap.append((x, y, self.winterMap.data[i]))
		sortedSummerMap.sort(lambda a, b: cmp(a[2], b[2]))
		sortedWinterMap.sort(lambda a, b: cmp(a[2], b[2]))
		sortedGeoMap = []
		for i in range(em.length):
			sortedGeoMap.append((0, 0, 0.0))
		xStart = 0
		xStop  = 0
		yStart = 0
		yStop  = 0
		incX   = 0
		incY   = 0
		geoIndex = 0
		for zone in range(6):
			topY    = em.GetYFromZone(zone, True)
			bottomY = em.GetYFromZone(zone, False)
			if not (topY == -1 and bottomY == -1):
				if topY == -1:
					topY = em.height - 1
				if bottomY == -1:
					bottomY = 0
				dir1, dir2 = em.GetGeostrophicWindDirections(zone)
				if (dir1 == mc.SW) or (dir1 == mc.SE):
					yStart = topY
					yStop  = bottomY - 1
					incY   = -1
				else:
					yStart = bottomY
					yStop  = topY + 1
					incY   = 1
				if dir2 == mc.W:
					xStart = em.width - 1
					xStop  = -1
					incX   = -1
				else:
					xStart = 0
					xStop = em.width
					incX = 1
				for y in range(yStart, yStop, incY):
					##each line should start on water to avoid vast areas without rain
					xxStart = xStart
					xxStop  = xStop
					for x in range(xStart, xStop, incX):
						if em.IsBelowSeaLevel(x, y):
							xxStart = x
							xxStop = x + em.width * incX
							break
					for x in range(xxStart, xxStop, incX):
						i = em.GetIndex(x, y)
						if i >= 0: # advc.001 (from C2C_World)
							sortedGeoMap[geoIndex] = (x, y, geoMap.data[i])
							geoIndex += 1
		moistureMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		for i in range(len(sortedSummerMap)):
			x = sortedSummerMap[i][0]
			y = sortedSummerMap[i][1]
			self.DistributeRain(x, y, self.summerMap, rainfallSummerMap,      moistureMap, False)
		moistureMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		for i in range(len(sortedWinterMap)):
			x = sortedWinterMap[i][0]
			y = sortedWinterMap[i][1]
			self.DistributeRain(x, y, self.winterMap, rainfallWinterMap,      moistureMap, False)
		moistureMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		for i in range(len(sortedGeoMap)):
			x = sortedGeoMap[i][0]
			y = sortedGeoMap[i][1]
			self.DistributeRain(x, y, geoMap,         rainfallGeostrophicMap, moistureMap, True)
		##zero below sea level for proper percent threshold finding
		for y in range(em.height):
			for x in range(em.width):
				i = em.GetIndex(x, y)
				if em.IsBelowSeaLevel(x, y):
					rainfallSummerMap.data[i]      = 0.0
					rainfallWinterMap.data[i]      = 0.0
					rainfallGeostrophicMap.data[i] = 0.0
		rainfallSummerMap.Normalize()
		rainfallWinterMap.Normalize()
		rainfallGeostrophicMap.Normalize()
		for y in range(em.height):
			for x in range(em.width):
				i = em.GetIndex(x, y)
				# <advc> (from C2C_World): Take into account distance to sea, but only with a sqrt. Also adopted code for an altitude factor, but that leads to fragmentation across all terrain types, in particular too few large deserts, so I've commented that out again.
				if not em.IsBelowSeaLevel(x, y):
					numerator = rainfallSummerMap.data[i] + rainfallWinterMap.data[i] + rainfallGeostrophicMap.data[i] * mc.geostrophicFactor
					#numerator += 2 * self.aboveSeaLevelMap.data[i]
					self.RainfallMap.data[i] = numerator / math.sqrt(self.distToSea[i])
				# </advc>


	def DistributeRain(self, x, y, pressureMap, RainfallMap, moistureMap, boolGeostrophic):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		i = em.GetIndex(x, y)
		upLiftSource = max(math.pow(pressureMap.data[i], mc.upLiftExponent), 1.0 - self.TemperatureMap.data[i])
		if em.IsBelowSeaLevel(x, y):
			moistureMap.data[i] = max(moistureMap.data[i], self.TemperatureMap.data[i])
		##make list of neighbors
		nList = []
		if boolGeostrophic:
			zone = em.GetZone(y)
			dir1, dir2 = em.GetGeostrophicWindDirections(zone)
			x1, y1 = GetNeighbor(x, y, dir1)
			ii = em.GetIndex(x1, y1)
			##neighbor must be on map and in same wind zone
			if ii >= 0 and (em.GetZone(y1) == em.GetZone(y)):
				x1, y1 = CoordsFromIndex(ii, em.width) # advc.001
				nList.append((x1, y1))
			x2, y2 = GetNeighbor(x, y, dir2)
			ii = em.GetIndex(x2, y2)
			if ii >= 0:
				x2, y2 = CoordsFromIndex(ii, em.width) # advc.001
				nList.append((x2, y2))
		else:
			#AIAndy Bugfix - climate hex evaluation
			for direction in range(1, 9):
				xx, yy = GetNeighbor(x, y, direction)
				ii = em.GetIndex(xx, yy)
				if ii >= 0 and pressureMap.data[i] <= pressureMap.data[ii]:
					xx, yy = CoordsFromIndex(ii, em.width) # advc.001
					nList.append((xx, yy))
		if len(nList) == 0 or (boolGeostrophic and len(nList) == 1):
			cost = moistureMap.data[i]
			RainfallMap.data[i] = cost
			return
		moisturePerNeighbor = moistureMap.data[i] / float(len(nList))
		##drop rain and pass moisture to neighbors
		for n in range(len(nList)):
			xx = nList[n][0]
			yy = nList[n][1]
			ii = em.GetIndex(xx, yy)
			upLiftDest = max(math.pow(pressureMap.data[ii], mc.upLiftExponent), 1.0 - self.TemperatureMap.data[ii])
			cost = self.GetRainCost(upLiftSource, upLiftDest)
			bonus = 0.0
			if em.GetZone(y) == mc.NPOLAR or em.GetZone(y) == mc.SPOLAR:
				bonus = mc.polarRainBoost
			if boolGeostrophic and len(nList) == 2:
				if n == 1:
					moisturePerNeighbor = (1.0 - mc.geostrophicLateralWindStrength) * moistureMap.data[i]
				else:
					moisturePerNeighbor = mc.geostrophicLateralWindStrength * moistureMap.data[i]
			RainfallMap.data[i] = RainfallMap.data[i] + cost * moisturePerNeighbor + bonus
			##pass to neighbor.
			moistureMap.data[ii] = moistureMap.data[ii] + moisturePerNeighbor - (cost * moisturePerNeighbor)


	def GetRainCost(self, upLiftSource, upLiftDest):
		cost = mc.minimumRainCost
		cost = max(mc.minimumRainCost, cost + upLiftDest - upLiftSource)
		if cost < 0.0:
			cost = 0.0
		return cost


c3 = ClimateMap3()


##############################################################################
## PW2 Climate System
##############################################################################

class ClimateMap2:
	def __init__(self):
		return


	def CreateClimateMaps(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		summerSunMap        = array('d')
		winterSunMap        = array('d')
		self.summerTempsMap = array('d')
		self.winterTempsMap = array('d')
		self.moistureMap    = array('d')
		self.TemperatureMap = FloatMap()
		self.RainfallMap    = FloatMap()
		self.initializeTempMap(summerSunMap,  mc.tropicsLatitude)
		self.initializeTempMap(winterSunMap, -mc.tropicsLatitude)
		self.TemperatureMap.initialize(em.width, em.height, em.wrapX, em.wrapY)
		self.RainfallMap.initialize(em.width,    em.height, em.wrapX, em.wrapY)
		#smooth both sun maps into the temp maps
		for y in range(em.height):
			for x in range(em.width):
				contributers = 0
				summerAvg    = 0
				winterAvg    = 0
				i = GetHmIndex(x, y)
				for yy in range(y - mc.filterSize / 2, y + mc.filterSize / 2 + 1, 1):
					for xx in range(x - mc.filterSize / 2, x + mc.filterSize / 2 + 1, 1):
						ii = GetHmIndex(xx, yy)
						if ii >= 0:
							contributers += 1
							summerAvg += summerSunMap[ii]
							winterAvg += winterSunMap[ii]
				summerAvg = summerAvg / float(contributers)
				winterAvg = winterAvg / float(contributers)
				self.summerTempsMap.append(summerAvg)
				self.winterTempsMap.append(winterAvg)
		#create average temp map
		for y in range(em.height):
			for x in range(em.width):
				i = GetHmIndex(x, y)
				#average summer and winter
				avgTemp = (self.summerTempsMap[i] + self.winterTempsMap[i]) / 2.0
				#cool map for altitude
				self.TemperatureMap.data[i] = avgTemp * (1.0 - pow(em.GetAltitudeAboveSeaLevel(x, y), mc.temperatureLossCurve) * mc.heatLostAtOne)
		#init moisture and rain maps
		for i in range(em.length):
			self.moistureMap.append(0.0)
			self.RainfallMap.data[i] = 0.0
		#create sortable plot list for summer monsoon rains
		temperatureList = list()
		for y in range(em.height):
			for x in range(em.width):
				i = GetHmIndex(x, y)
				rainPlot = RainPlot(x, y, self.summerTempsMap[i], 0)
				temperatureList.append(rainPlot)
		#sort by temperature, coldest first
		temperatureList.sort(lambda x, y:cmp(x.order, y.order))
		#Drop summer monsoon rains
		self.dropRain(temperatureList, self.summerTempsMap, False, None)
		#clear moisture map
		for i in range(em.length):
			self.moistureMap[i] = 0.0
		#create sortable plot list for winter monsoon rains
		temperatureList = list()
		for y in range(em.height):
			for x in range(em.width):
				i = GetHmIndex(x, y)
				rainPlot = RainPlot(x, y, self.winterTempsMap[i], 0)
				temperatureList.append(rainPlot)
		#sort by temperature, coldest first
		temperatureList.sort(lambda x, y:cmp(x.order, y.order))
		#Drop winter monsoon rains
		self.dropRain(temperatureList, self.winterTempsMap, False, None)
		#clear moisture map
		for i in range(em.length):
			self.moistureMap[i] = 0.0
		#set up WindZones class
		wz = WindZones(em.height, mc.topLatitude, mc.bottomLatitude)
		#create ordered list for geostrophic rain
		orderList = list()
		for zone in range(6):
			topY    = wz.GetYFromZone(zone, True)
			bottomY = wz.GetYFromZone(zone, False)
			if topY == -1 and bottomY == -1:
				continue #This wind zone is not represented on this map at all so skip it
			if topY == -1: #top off map edge
				topY = em.height - 1
			if bottomY == -1:
				bottomY = 0
			dx, dy = wz.GetWindDirectionsInZone(zone)
			if dy < 0:
				yStart = topY
				yStop  = bottomY - 1
			else:
				yStart = bottomY
				yStop  = topY + 1
			if dx < 0:
				xStart = em.width - 1
				xStop  = -1
			else:
				xStart = 0
				xStop  = em.width
			order = 0.0
			for y in range(yStart, yStop, dy):
				for x in range(xStart, xStop, dx):
					rainPlot = RainPlot(x, y, order, abs(yStop - y))
					orderList.append(rainPlot)
					order += 1.0
		#Sort order list
		orderList.sort(lambda x, y:cmp(x.order, y.order))
		#drop geostrophic rain
		self.dropRain(orderList, self.TemperatureMap.data, True, wz)
		NormalizeMap(self.RainfallMap.data, em.width, em.height)


	def dropRain(self, plotList, tempMap, bGeostrophic, windZones):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		countRemaining = len(plotList)
		bDebug = False
		for plot in plotList:
			i = GetHmIndex(plot.x, plot.y)
			#First collect moisture from sea
			if em.IsBelowSeaLevel(plot.x, plot.y):
				self.moistureMap[i] += tempMap[i]
			nList = list()
			if bGeostrophic:
				#make list of neighbors in geostrophic zone, even if off map
				zone = windZones.GetZone(plot.y)
				dx, dy = windZones.GetWindDirectionsInZone(zone)
				nList.append((plot.x, plot.y + dy))
				nList.append((plot.x + dx, plot.y))
				nList.append((plot.x + dx, plot.y + dy))
			else:
				#make list of neighbors with higher temp
				for direction in range(1, 9):
					xx, yy = GetNeighbor(plot.x, plot.y, direction)
					ii = GetHmIndex(xx, yy)
					if ii >= 0 and tempMap[i] <= tempMap[ii]:
						xx, yy = CoordsFromIndex(ii, em.width) # advc.001
						nList.append((xx, yy))
				#divide moisture by number of neighbors for distribution
				if len(nList) == 0:
					continue #dead end, dump appropriate rain
			moisturePerNeighbor = self.moistureMap[i] / float(len(nList))
			if bGeostrophic:
				geostrophicFactor = mc.geostrophicFactor
			else:
				geostrophicFactor = 1.0
			for xx, yy in nList:
				#Get the rain cost to enter this plot. Cost is
				#percentage of present moisture available for this
				#neighbor
				if bGeostrophic:
					cost = self.getRainCost(plot.x, plot.y, xx, yy, plot.uplift)
				else:
					cost = self.getRainCost(plot.x, plot.y, xx, yy, countRemaining / mc.monsoonUplift)
				#Convert moisture into rain
				#self.moistureMap[i] -= cost * moisturePerNeighbor (this line is unecessary actually, we are finished with moisture map for this plot)
				self.RainfallMap.data[i] += cost * moisturePerNeighbor * geostrophicFactor #geostrophicFactor is not involved with moisture, only to weigh against monsoons
				#send remaining moisture to neighbor
				ii = GetHmIndex(xx, yy)
				if ii >= 0:
					self.moistureMap[ii] += moisturePerNeighbor - (cost * moisturePerNeighbor)
			countRemaining -= 1


	def getRainCost(self, x1, y1, x2, y2, distanceToUplift):
		cost = mc.minimumRainCost
		cRange = 1.0 - cost #We don't want to go over 1.0 so the range is reduced
		upliftCost = (1.0 / (float(distanceToUplift) + 1.0)) * cRange
		i  = GetHmIndex(x1, y1)
		ii = GetHmIndex(x2, y2)
		cost += max((self.TemperatureMap.data[ii] - self.TemperatureMap.data[i]) * 2.0 * cRange, upliftCost)
		return cost


	def initializeTempMap(self, tempMap, tropic):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		for y in range(em.height):
			for x in range(em.width):
				tempMap.append(self.getInitialTemp(x, y, tropic))


	def getInitialTemp(self, x, y, tropic):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		i = GetHmIndex(x, y)
		lat = em.GetLatitudeForY(y)
		latRange = 90.0 + abs(tropic)
		latDifference = abs(float(lat - tropic))
		if em.data[i] >= em.seaLevelThreshold:
			tempPerLatChange = 1.0 / latRange
			temp = 1.0 - (tempPerLatChange * latDifference)
		else:
			tempPerLatChange = (1.0 - (2.0 * mc.oceanTempClamp)) / latRange
			temp = 1.0 - mc.oceanTempClamp - (tempPerLatChange * latDifference)
		return temp


class RainPlot:
	def __init__(self, x, y, order, uplift):
		self.x = x
		self.y = y
		self.order  = order
		self.uplift = uplift


class WindZones:
	def __init__(self, height, topLat, botLat):
		self.NPOLAR     = 0
		self.NTEMPERATE = 1
		self.NEQUATOR   = 2
		self.SEQUATOR   = 3
		self.STEMPERATE = 4
		self.SPOLAR     = 5
		self.NOZONE     = 99
		self.height = height
		self.topLat = topLat
		self.botLat = botLat


	def GetZone(self, y):
		if y < 0 or y >= self.height:
			return self.NOZONE
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		lat = em.GetLatitudeForY(y)
		if lat >= mc.polarFrontLatitude:
			return self.NPOLAR
		elif lat >= mc.horseLatitude:
			return self.NTEMPERATE
		elif lat >= 0:
			return self.NEQUATOR
		elif lat >= -mc.horseLatitude:
			return self.SEQUATOR
		elif lat >= -mc.polarFrontLatitude:
			return self.STEMPERATE
		else:
			return self.SPOLAR


	def GetZoneName(self, zone):
		if zone == self.NPOLAR:
			return "NPOLAR"
		elif zone == self.NTEMPERATE:
			return "NTEMPERATE"
		elif zone == self.NEQUATOR:
			return "NEQUATOR"
		elif zone == self.SEQUATOR:
			return "SEQUATOR"
		elif zone == self.STEMPERATE:
			return "STEMPERATE"
		else:
			return "SPOLAR"


	def GetYFromZone(self, zone, bTop):
		if bTop:
			for y in range(self.height - 1, -1, -1):
				if zone == self.GetZone(y):
					return y
		else:
			for y in range(self.height):
				if zone == self.GetZone(y):
					return y
		return -1


	def GetZoneSize(self):
		latitudeRange = self.topLat - self.botLat
		degreesPerDY = float(latitudeRange) / float(self.height)
		size = 30.0 / degreesPerDY
		return size


	def GetWindDirections(self, y):
		z = self.GetZone(y)
		return self.GetWindDirectionsInZone(z)


	def GetWindDirectionsInZone(self, z):
		#get x,y directions
		if z == self.NPOLAR:
			return (-1, -1)
		elif z == self.NTEMPERATE:
			return (1,  1)
		elif z == self.NEQUATOR:
			return (-1, -1)
		elif z == self.SEQUATOR:
			return (-1, 1)
		elif z == self.STEMPERATE:
			return (1,  -1)
		elif z == self.SPOLAR:
			return (-1, 1)
		return (0, 0)


c2 = ClimateMap2()


################################################################################
## PW2/PW3 Global Functions
################################################################################

def errorPopUp(message):
	gc = CyGlobalContext()
	iPlayerNum = 0
	for iPlayer in range(gc.getMAX_PLAYERS()):
		player = gc.getPlayer(iPlayer)
		if player.isAlive():
			iPlayerNum = iPlayerNum + 1
			if player.isHuman():
				text = message
				# advc: disused
				#text += "\n\n" + mc.optionsString
				text += "\n" + PRand.seedString
				popupInfo = CyPopupInfo()
				popupInfo.setButtonPopupType(ButtonPopupTypes.BUTTONPOPUP_PYTHON)
				popupInfo.setText(text)
				popupInfo.setOnClickedPythonCallback("")
				popupInfo.addPythonButton("Ok", "")
				popupInfo.addPopup(iPlayer)


def GetIndex(x, y):
	if mc.WrapX:
		xx = x % mc.width
	elif x < 0 or x >= mc.width:
		return -1
	else:
		xx = x
	if mc.WrapY:
		yy = y % mc.height
	elif y < 0 or y >= mc.height:
		return -1
	else:
		yy = y
	return yy * mc.width + xx

# advc: To fix potential problems with GetNeighbor (q.v.)
def CoordsFromIndex(i, width):
	assert i >= 0
	y = i / width
	return i - y * width, y


def GetHmIndex(x, y):
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	if mc.WrapX:
		xx = x % em.width
	elif x < 0 or x >= em.width:
		return -1
	else:
		xx = x
	if mc.WrapY:
		yy = y % em.height
	elif y < 0 or y >= em.height:
		return -1
	else:
		yy = y
	return yy * em.width + xx


def GetIndexGeneral(x, y, width, height):
	if mc.WrapX:
		xx = x % width
	elif x < 0 or x >= width:
		return -1
	else:
		xx = x
	if mc.WrapY:
		yy = y % height
	elif y < 0 or y >= height:
		return -1
	else:
		yy = y
	return yy * width + xx


def NormalizeMap(fMap, width, height):
	maxAlt = 0.0
	minAlt = 0.0
	for y in range(height):
		for x in range(width):
			plot = fMap[GetIndexGeneral(x, y, width, height)]
			if plot > maxAlt:
				maxAlt = plot
			elif plot < minAlt:
				minAlt = plot
	if minAlt != 0.0:
		for y in range(height):
			for x in range(width):
				fMap[GetIndexGeneral(x, y, width, height)] -= minAlt
		maxAlt -= minAlt
	scaler = 1.0 / maxAlt
	for y in range(height):
		for x in range(width):
			fMap[GetIndexGeneral(x, y, width, height)] = fMap[GetIndexGeneral(x, y, width, height)] * scaler


def GetWeight(x, y, xx, yy, xScale, yScale):
	xWeight = 1.0
	if float(xx) < x * xScale:
		xWeight = 1.0 - ((x * xScale) - float(xx))
	elif float(xx + 1) > (x + 1) * xScale:
		xWeight = ((x + 1) * xScale) - float(xx)
	yWeight = 1.0
	if float(yy) < y * yScale:
		yWeight = 1.0 - ((y * yScale) - float(yy))
	elif float(yy + 1) > (y + 1) * yScale:
		yWeight = ((y + 1) * yScale) - float(yy)
	return xWeight * yWeight


def ShrinkMaps():
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	if mc.ClimateSystem == 0:
		cm = c3
	else:
		cm = c2
	em.data                = CropMap(em.data)
	cm.TemperatureMap.data = CropMap(cm.TemperatureMap.data)
	cm.RainfallMap.data    = CropMap(cm.RainfallMap.data)
	mc.hmWidth  = mc.hmWidth  - mc.westCrop  - mc.eastCrop
	mc.hmHeight = mc.hmHeight - mc.northCrop - mc.southCrop
	newHeightMap      = ShrinkMap(em.data,                mc.hmWidth, mc.hmHeight, mc.width, mc.height)
	newTemperatureMap = ShrinkMap(cm.TemperatureMap.data, mc.hmWidth, mc.hmHeight, mc.width, mc.height)
	newRainfallMap    = ShrinkMap(cm.RainfallMap.data,    mc.hmWidth, mc.hmHeight, mc.width, mc.height)
	em.width                 = mc.width
	em.height                = mc.height
	em.length                = mc.width * mc.height
	cm.TemperatureMap.width  = mc.width
	cm.TemperatureMap.height = mc.height
	cm.TemperatureMap.length = mc.width * mc.height
	cm.RainfallMap.width     = mc.width
	cm.RainfallMap.height    = mc.height
	cm.RainfallMap.length    = mc.width * mc.height
	em.data                = array('d')
	cm.TemperatureMap.data = array('d')
	cm.RainfallMap.data    = array('d')
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndexGeneral(x, y, mc.width, mc.height)
			if i >= 0:
				em.data.append(newHeightMap[i])
				cm.TemperatureMap.data.append(newTemperatureMap[i])
				cm.RainfallMap.data.append(newRainfallMap[i])
			else:
				em.data.append(em.seaLevelThreshold - 0.000001)
				cm.TemperatureMap.data.append(0.0)
				cm.RainfallMap.data.append(0.0)
	#Smooth coasts so there are fewer hills on coast
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			if em.data[i] < em.seaLevelThreshold:
				em.data[i] = em.seaLevelThreshold - 0.000001
	#smaller lakes need to be filled in again because the map
	#shrinker sometimes creates lakes.
	am = AreaMap(mc.width, mc.height, True, True)
	am.defineAreas(isWaterMatch)
	oceanID = am.getOceanID()
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			if em.data[i] < em.seaLevelThreshold and am.data[i] != oceanID:
				#check the size of this body of water, if too small, change to land
				for a in am.areaList:
					if a.ID == am.data[i] and a.size < mc.minInlandSeaSize:
						em.data[i] = em.seaLevelThreshold


def CropMap(theMap):
	newMap = array('d')
	for y in range(mc.hmHeight):
		if y < mc.southCrop or y >= mc.hmHeight - mc.northCrop:
			continue
		for x in range(mc.hmWidth):
			if x < mc.westCrop or x >= mc.hmWidth - mc.eastCrop:
				continue
			i = GetHmIndex(x, y)
			newMap.append(theMap[i])
	return newMap


def ShrinkMap(largeMap, lWidth, lHeight, sWidth, sHeight):
	smallMap = array('d')
	yScale = float(lHeight) / float(sHeight)
	xScale = float(lWidth)  / float(sWidth)
	for y in range(sHeight):
		for x in range(sWidth):
			weights      = 0.0
			contributors = 0.0
			# <advc.001> Using the scale ratios here can lead to out of bounds
			# indices due to floating-point inaccuracy.
			yyStart = (y * lHeight) // sHeight
			yyStop = ((y + 1) * lHeight + sHeight - 1) // sHeight
			# </advc.001>
			for yy in range(yyStart, yyStop):
				# <advc.001>
				xxStart = (x * lWidth) // sWidth
				xxStop = ((x + 1) * lWidth + sWidth - 1) // sWidth
				# </advc.001>
				for xx in range(xxStart, xxStop):
					weight = GetWeight(x, y, xx, yy, xScale, yScale)
					i = yy * lWidth + xx
					contributor = largeMap[i]
					weights += weight
					contributors += weight * contributor
			smallMap.append(contributors / weights)
	return smallMap


def AngleDifference(a1, a2):
	diff = a1 - a2
	while(diff < -180.0):
		diff += 360.0
	while(diff > 180.0):
		diff -= 360.0
	return diff


def AppendUnique(theList, newItem):
	if not IsInList(theList,newItem):
		theList.append(newItem)


def IsInList(theList, newItem):
	itemFound = False
	for item in theList:
		if item == newItem:
			itemFound = True
			break
	return itemFound


def DeleteFromList(theList, oldItem):
	for n in range(len(theList)):
		if theList[n] == oldItem:
			del theList[n]
			break


def ShuffleList(theList):
	if mc.UsePythonRandom:
		shuffled = list(theList)
		shuffle(shuffled)
		return shuffled
	else:
		preshuffle = list()
		shuffled   = list()
		numElements = len(theList)
		for i in range(numElements):
			preshuffle.append(theList[i])
		for i in range(numElements):
				n = PRand.randint(0, len(preshuffle) - 1)
				shuffled.append(preshuffle[n])
				del preshuffle[n]
		return shuffled


def GetInfoType(string):
	cgc = CyGlobalContext()
	return cgc.getInfoTypeForString(string)


def GetDistance(x, y, dx, dy):
	distance = math.sqrt(abs((float(x - dx) * float(x - dx)) + (float(y - dy) * float(y - dy))))
	return distance


def GetOppositeDirection(direction):
	opposite = mc.L
	if direction == mc.N:
		opposite = mc.S
	elif direction == mc.S:
		opposite = mc.N
	elif direction == mc.E:
		opposite = mc.W
	elif direction == mc.W:
		opposite = mc.E
	elif direction == mc.NW:
		opposite = mc.SE
	elif direction == mc.SE:
		opposite = mc.NW
	elif direction == mc.SW:
		opposite = mc.NE
	elif direction == mc.NE:
		opposite = mc.SW
	return opposite

# advc (note): Since this function does not apply world-wraps, the result should only be fed into one of the get-index functions, which do apply world-wraps. Where the PerfectMongoose code had used the coordinates for other purposes, I've added a call to the (new) CoordsFromIndex function - which maps the valid index to valid coordinates.
def GetNeighbor(x, y, direction):
	if direction == mc.L:
		return x, y
	elif direction == mc.N:
		return x, y + 1
	elif direction == mc.S:
		return x, y - 1
	elif direction == mc.E:
		return x + 1, y
	elif direction == mc.W:
		return x - 1, y
	elif direction == mc.NE:
		return x + 1, y + 1
	elif direction == mc.NW:
		return x - 1, y + 1
	elif direction == mc.SE:
		return x + 1, y - 1
	elif direction == mc.SW:
		return x - 1, y - 1
	return -1, -1


def FindThresholdFromPercent(map, length, percent, greaterThan):
	percentage = percent * 100.0
	if greaterThan:
		percentage = 100.0 - percentage
	if percentage >= 100.0:
		return  1.01 #whole map
	elif percentage <= 0.0:
		return -0.01 #none of the map
	mapList = []
	for i in range(length):
		mapList.append(map[i])
	mapList.sort(lambda a, b: cmp(a, b))
	threshIndex = math.floor(((len(mapList) - 1.0) * percentage) / 100.0)
	return mapList[int(threshIndex)]


##This function is a general purpose value tuner. It finds a value that will be greater
##than or less than the desired percent of a whole map within a given tolerance. Map values
##should be between 0 and 1. To exclude parts of the map, set them to value 0.0
# advc (comment): Is this function really needed? Seems that, apart from special treatment for 0s, FindThresholdFromPercent accomplishes the same thing (percentile calculation) more reliably. Not sure which is faster though.
def FindValueFromPercent(map, length, percent, greaterThan):
	if length == 0:
		if greaterThan:
			return 1.0
		else:
			return 0.0
	tolerance = percent / 50.0
	inTolerance = False
	#to speed things up a little, lets take some time to find the middle value
	#in the dataset and use that to begin our search
	minV = 100.0
	maxV = 0.0
	totalCount = 0
	for i in range(length):
		if map[i] != 0.0:
			totalCount += 1
			if minV > map[i]:
				minV = map[i]
			if maxV < map[i]:
				maxV = map[i]
	mid = (maxV - minV) / 2.0 + minV
	overMinCount  = 0
	equalMinCount = 0
	for i in range(length):
		if map[i] > minV:
			overMinCount += 1
		elif map[i] == minV:
			equalMinCount += 1
	threshold       = mid
	thresholdChange = mid
	iterations = 0
	lastAdded = False
	while not inTolerance:
		iterations += 1
		if(iterations > 500):
			print "can't find value within tolerance"
			print "threshold = %f, thresholdChange = %f" % (threshold, thresholdChange)
			break #close enough
		matchCount = 0
		for i in range(length):
			if map[i] != 0.0:
				if greaterThan:
					if map[i] > threshold:
						matchCount += 1
				else:
					if map[i] < threshold:
						matchCount += 1
		currentPercent = 0
		if totalCount > 0: # advc: Shouldn't be 0, but let's make sure.
			currentPercent = float(matchCount) / float(totalCount)
		if currentPercent < percent + tolerance and currentPercent > percent - tolerance:
			inTolerance = True
		elif greaterThan:
			if currentPercent < percent:
				threshold -= thresholdChange
				if lastAdded:
					#only cut thresholdChange when direction is changed
					thresholdChange = thresholdChange / 2.0
				lastAdded = False
			else:
				threshold += thresholdChange
				if not lastAdded:
					thresholdChange = thresholdChange / 2.0
				lastAdded = True
		else:
			if currentPercent > percent:
				threshold -= thresholdChange
				if lastAdded:
					#only cut thresholdChange when direction is changed
					thresholdChange = thresholdChange / 2.0
				lastAdded = False
			else:
				threshold += thresholdChange
				if not lastAdded:
					thresholdChange = thresholdChange / 2.0
				lastAdded = True
	#at this point value should be in tolerance or close to it
	return threshold


def isWaterMatch(x, y):
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	return em.IsBelowSeaLevel(x, y)


def isDeepWaterMatch(x, y):
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	if not em.IsBelowSeaLevel(x, y):
		return False
	plot = CyMap().plot(x, y)
	if plot.isImpassable():
		return True
	for direction in range(1, 9):
		xx, yy = GetNeighbor(x, y, direction)
		ii = GetIndex(xx, yy)
		#if ii >= 0 and not em.IsBelowSeaLevel(x, y):
		# <advc.001>
		if ii < 0:
			continue
		xx, yy = CoordsFromIndex(ii, mc.width)
		if not em.IsBelowSeaLevel(xx, yy): # </advc.001>
			return False
	return True


def isPeakWaterMatch(x, y): # advc.030 (note): disused
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	return em.IsBelowSeaLevel(x, y) or (tm.pData[GetIndex(x, y)] == mc.PEAK)


def isHmWaterMatch(x, y):
	i = GetHmIndex(x, y)
	#if pb.distanceMap[i] > mc.minimumMeteorSize / 3:
	# advc: Adjusted to decreased min. meteor size
	if pb.distanceMap[i] * 2 > mc.minimumMeteorSize:
		return True
	return False

# advc: Cut from PangaeaBreaker.createDistanceMap, which creates a table with distances to the nearest land plot. This global function can also create a table with distances to the closest sea plot (bToLand=False).
def createDistanceMap(bToLand):
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	distanceMap = array('i')
	processQueue = []
	for y in range(em.height):
		for x in range(em.width):
			# advc: Switched around if not bToLand
			if em.IsBelowSeaLevel(x, y) == bToLand:
				distanceMap.append(1000)
			else:
				distanceMap.append(0)
				processQueue.append((x, y))
	while len(processQueue) > 0:
		x, y = processQueue[0]
		i = GetHmIndex(x, y)
		del processQueue[0]
		dist = distanceMap[i]
		for direction in range(1, 9):
			xx, yy = GetNeighbor(x, y, direction)
			ii = GetHmIndex(xx, yy)
			if ii >= 0:
				neighborDist = distanceMap[ii]
				if neighborDist > dist + 1:
					distanceMap[ii] = dist + 1
					xx, yy = CoordsFromIndex(ii, em.width) # advc.001
					processQueue.append((xx, yy))
	return distanceMap

# advc: Need this in three places. The latitude check and plains as possible terrain are new. Not doing a canHaveFeature check b/c jungle doesn't really have restrictions.
def canHaveJungle(rfData, jungleRf, tData, pData, lat, tempData = 1.0, jungleTemp = 0.0):
	return (rfData >= jungleRf and (tData == mc.GRASS or tData == mc.PLAINS) and pData != mc.PEAK and abs(lat) * 2 <= mc.tropicsLatitude + mc.horseLatitude and tempData >= jungleTemp)

def canHaveOasis(x, y, tData, fOasis):
	# <advc> Checking these conditions already at this point should get us closer to the target frequency for oases
	if not CyMap().plot(x, y).canHaveFeature(fOasis):
		return False # </advc>
	'''
	for direction in range(1, 5):
		xx, yy = GetNeighbor(x, y, direction)
		ii = GetIndex(xx, yy)
		if ii >= 0 and tData[ii] != mc.DESERT:
			return False
		for yy in range(y - 2, y + 3):
			for xx in range(x - 2, x + 3):
				xx, yy = CoordsFromIndex(ii, mc.width) # advc.001
				surrPlot = CyMap().plot(xx, yy)
				if surrPlot != 0 and surrPlot.getFeatureType() == fOasis:
					return False
	'''
	# <advc> Use a single loop again, as in v3.2.
	adjNonDesertCount = 0
	for direction in range(1, 9):
		xx, yy = GetNeighbor(x, y, direction)
		ii = GetIndex(xx, yy)
		if ii < 0:
			continue
		xx, yy = CoordsFromIndex(ii, mc.width)
		adj = CyMap().plot(xx, yy)
		# Tbd.(?): Should perhaps ensure two tiles in between oases, not just one. (PerfectWorld6.lua puts at least three tiles in between oases, but Civ6 has a different scale than Civ4.)
		if adj.isWater() or adj.getFeatureType() == fOasis:
			return False
		# Only exclude tiles with more than 4 adjacent non-desert tiles
		if tData[ii] != mc.DESERT:
			adjNonDesertCount += 1
			if adjNonDesertCount > 4:
				return False
	# </advc>
	return True


class TerrainMap:
	def __init__(self):
		return


	def initialize(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		#self.dData = []
		# <advc> Separate values for hills and peaks
		self.hillData = []
		self.peakData = [] # </advc>
		self.pData = []
		self.tData = []
		for i in range(em.length):
			#self.dData.append(0.0)
			# <advc>
			self.hillData.append(0.0)
			self.peakData.append(0.0) # </advc>
			self.pData.append(mc.WATER)
			self.tData.append(mc.OCEAN)


	def GeneratePlotMap(self):
		print "-------------------"
		print "Generating Plot Map"
		print "-------------------"
		deAttenuate = False # advc (only e3 uses attenuation)
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
			deAttenuate = True # advc
		for y in range(mc.height):
			for x in range(mc.width):
				i = em.GetIndex(x, y)
				# <advc> Remove attenuation effect - b/c it should only affect the coastline, not elevation above sea.
				elevData = em.data[i]
				if deAttenuate:
					if elevData > 0: # Then the attenuation factor can't be 0 either
						elevData /= GetAttenuationFactor(em, x, y)
				# </advc>
				if mc.HillPeakStyle == 1:
					#self.dData[i] = elevData
					# <advc>
					self.hillData[i] = elevData
					self.peakData[i] = elevData # </advc>
				else:
					#create height difference map to allow for tuning
					#I tried using a deviation from surrounding average altitude
					#to determine hills and peaks but I didn't like the
					#results. Therefore I am using lowest neighbor.
					# <advc> This will be pretty arcane b/c I've tried several methods and only got it to work OK by combining them. Don't want hills to clump much, but peaks need to clump (in patterns that look natural) and should have surrounding foothills, so the hill placement can't be totally different. Also, mountain ranges need to appear near high-altitude tiles, otherwise the monsoon rain shadow won't make sense.
					neighbors = 0
					myAlt = elevData
					# Considering the lowest orthogonal and the lowest diagonal neighbor seems to yield reasonable clustering. The overall minumum clusters too much, in particular results in blocks, enclosures, straight chains too often. (If enclosures still occur, one should perhaps simply convert peaks with a high number of adjacent lower-altitude peaks into snow hills.)
					minAltOrth = 1.0
					minAltDiag = 1.0
					# And count the neighbors with greater altitude
					numHigher = 0
					numHigherButNotMuch = 0
					sumOfDiffs = 0
					# </advc>
					for direction in range(1, 9):
						xx, yy = GetNeighbor(x, y, direction)
						ii = em.GetIndex(xx, yy)
						if ii < 0:
							continue
						# <advc>
						xx, yy = CoordsFromIndex(ii, em.width)
						neighborElevData = em.data[ii]
						if deAttenuate:
							if neighborElevData > 0:
								neighborElevData /= GetAttenuationFactor(em, xx, yy)
						if neighborElevData < myAlt and em.IsBelowSeaLevel(xx, yy):
							# Adjacent water: assume that half of the slope is submerged (and thus shouldn't contribute to the land plot type)
							neighborElevData += (myAlt - neighborElevData) / 2
						elif neighborElevData > myAlt:
							numHigher += 1
							if 1.5 * myAlt > neighborElevData:
								numHigherButNotMuch += 1
						neighbors += 1
						distFactor = 1 # More weight for orth. neighbors
						if direction % 2 == 0:
							distFactor = 1.3
						# 1 would amount to computing the mean altitude difference. 0 would mean counting higher vs. lower neighbors (resulting in dispersed hills and peaks).
						diffExp = 0.4
						if myAlt > neighborElevData:
							sumOfDiffs += pow(myAlt - neighborElevData, diffExp) * distFactor
						if myAlt < neighborElevData:
							sumOfDiffs -= pow(abs(myAlt - neighborElevData), diffExp) * distFactor
						if direction % 2 == 0:
							if neighborElevData < minAltOrth:
								minAltOrth = neighborElevData
						else:
							if neighborElevData < minAltDiag:
								minAltDiag = neighborElevData
						# </advc>
					#self.dData[i] = myAlt - minAlt
					# <advc>
					if neighbors > 0:
						sumOfDiffs /= neighbors
						self.peakData[i] = sumOfDiffs
						self.hillData[i] = sumOfDiffs
					altDiff = myAlt - (minAltOrth * 3 + minAltDiag * 2) / 5
					# A high multiplier here aligns the hills better with the peaks, meaning also that hills clump together more. The randomness should help place at least a couple of hills near each group of peaks.
					self.hillData[i] += PRand.random() * 2 * altDiff
					# Not counting much higher neighbors here b/c I don't want to discourage hills near peaks. Not sure if I'm really accomplishing that.
					self.hillData[i] *= pow(0.95, numHigherButNotMuch)
					# High multiplier, meaning that peaks are mostly placed based on the maximal altitude differences, which results in fairly dense patterns.
					self.peakData[i] += 4.3 * altDiff
					# Extra weight for absolute altitude to discourage coastal peaks a bit
					self.peakData[i] += 0.1 * myAlt
					# Discourage long, uninterrupted chains
					if numHigher >= 2:
						self.peakData[i] *= 0.82
					# </advc>
		#NormalizeMap(self.dData, mc.width, mc.height)
		#landMap = []
		#for i in range(em.length):
		#	landMap.append(0.0)
		# <advc>
		NormalizeMap(self.hillData, mc.width, mc.height)
		NormalizeMap(self.peakData, mc.width, mc.height) # </advc>
		hillMap = []
		peakMap = []
		for i in range(em.length):
			hillMap.append(0.0)
			peakMap.append(0.0) # </advc>
		#zero out water tiles so percent is percent of land
		for y in range(mc.height):
			for x in range(mc.width):
				i = em.GetIndex(x, y)
				if not em.IsBelowSeaLevel(x, y):
					#landMap[i] = self.dData[i]
					# <advc>
					hillMap[i] = self.hillData[i]
					peakMap[i] = self.peakData[i] # </advc>
		# advc: Was landMap in both lines
		hillHeight = FindValueFromPercent(hillMap, em.length, mc.HillPercent, True)
		peakHeight = FindValueFromPercent(peakMap, em.length, mc.PeakPercent, True)
		for y in range(mc.height):
			for x in range(mc.width):
				i = em.GetIndex(x, y)
				if em.data[i] < em.seaLevelThreshold:
					self.pData[i] = mc.WATER
				# advc: Was landMap in both elifs
				elif hillMap[i] < hillHeight:
					self.pData[i] = mc.LAND
				elif peakMap[i] < peakHeight:
					self.pData[i] = mc.HILLS
				else:
					self.pData[i] = mc.PEAK
		#break up large clusters of hills and peaks
		# advc: Disable this. Had no b/c of bugs, but it's still bad with the
		# bugs fixed. Certain patterns should arguably be broken up probabi-
		# listically, but that'll require more thought.
		'''
		for y in range(mc.height):
			for x in range(mc.width):
				i = em.GetIndex(x, y)
				# advc.001: Fix missing index (from Totestra)
				if self.pData[i] == mc.HILLS:
					allHills = True
					for direction in range(1, 9):
						xx, yy = GetNeighbor(x, y, direction)
						ii = em.GetIndex(xx, yy)
						if ii >= 0 and self.pData[ii] != mc.HILLS:
							allHills = False
					if allHills:
						self.pData[i] = mc.LAND
				# advc.001: Fix missing index (from Totestra)
				if self.pData[i] == mc.PEAK:
					allPeaks = True
					for direction in range(1, 9):
						xx, yy = GetNeighbor(x, y, direction)
						ii = em.GetIndex(xx, yy)
						if ii >= 0 and self.pData[ii] != mc.PEAK:
							allPeaks = False
					if allPeaks:
						self.pData[i] = mc.HILLS
		'''

	def GenerateTerrainMap(self):
		print "----------------------"
		print "Generating Terrain Map"
		print "----------------------"
		gc = CyGlobalContext()
		mmap = gc.getMap()
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		if mc.ClimateSystem == 0:
			cm = c3
		else:
			cm = c2
		#Find minimum rainfall on land
		minRain = 10.0
		for i in range(em.length):
			if self.pData[i] != mc.WATER:
				if cm.RainfallMap.data[i] < minRain:
					minRain = cm.RainfallMap.data[i]
		#zero water tiles to obtain percent of land
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				if em.IsBelowSeaLevel(x, y):
					cm.RainfallMap.data[i] = 0.0
		#LM - Rewritten to use threshold values with Desert and Plains, and to exclude Peaks
		#from the percent coverage calculations since their terrain types don't actually matter.
		#(You could end up wasting most of your Snow tiles under polar mountain ranges and not
		#have very many on the map, for example.)
		#waterTiles  = []
		#waterLength = 0
		landTiles   = []
		landLength  = 0
		polarTiles = [] # advc
		landRf = [] # advc
		for y in range(mc.height):
			latitude = abs(em.GetLatitudeForY(y)) # advc
			for x in range(mc.width):
				i = GetIndex(x, y)
				if self.pData[i] != mc.WATER and self.pData[i] != mc.PEAK:
					landTiles.append(cm.TemperatureMap.data[i])
					landLength += 1
					# <advc>
					landRf.append(cm.RainfallMap.data[i])
					if latitude >= mc.taigaMinLatitude:
						polarTiles.append(cm.TemperatureMap.data[i])
					# </advc>
				'''
				if self.pData[i] == mc.WATER:
					waterTiles.append(em.data[i])
					waterLength += 1
				elif self.pData[i] != mc.PEAK:
					landTiles.append(cm.TemperatureMap.data[i])
					landLength += 1
				'''
		# <advc> Apply only the 'temperate' percentages to all land tiles
		snowTemp = FindValueFromPercent(landTiles, landLength, mc.TemperateSnowPercent, False)
		self.tundraTemp = FindValueFromPercent(landTiles, landLength, mc.TemperateTundraPercent, False)
		flatSnowTemp = FindValueFromPercent(polarTiles, len(polarTiles), mc.SnowPercent, False)
		taigaTemp = FindValueFromPercent(polarTiles, len(polarTiles), mc.TundraPercent, False)
		tundraSnowRainfallThreshold = FindValueFromPercent(landRf, len(landRf), mc.tundraSnowRainfallTarget, False)
		# </advc>
		warmTiles  = []
		warmLength = 0
		for y in range(mc.height):
			latitude = abs(em.GetLatitudeForY(y)) # advc
			for x in range(mc.width):
				i = GetIndex(x, y)
				bWarm = True # advc
				if self.pData[i] == mc.WATER:
					bWarm = False # advc
					for direction in range(1, 9):
						xx, yy = GetNeighbor(x, y, direction)
						ii = GetIndex(xx, yy)
						if ii >= 0 and self.pData[ii] != mc.WATER:
							self.tData[i] = mc.COAST
				# <advc>
				elif latitude < mc.taigaMinLatitude:
					if cm.RainfallMap.data[i] >= tundraSnowRainfallThreshold:
						# No snow near the equator, especially no flat snow, and non-polar snow mustn't be dry.
						if tm.pData[i] == mc.HILLS and latitude >= mc.snowHillMinLatitude and cm.TemperatureMap.data[i] < snowTemp:
							self.tData[i] = mc.SNOW
							bWarm = False
						# No tundra near the equator, and non-polar tundra mustn't be dry.
						elif latitude >= mc.tundraMinLatitude and cm.TemperatureMap.data[i] < self.tundraTemp:
							self.tData[i] = mc.TUNDRA
							bWarm = False
				else:
					# Very cold or topmost or bottommost row - those rows get shown with an icecap in Globe view (regardless of the true terrain).
					if (latitude >= mc.snowPlateauMinLatitude and cm.TemperatureMap.data[i] < flatSnowTemp) or (latitude > 77 and (y == 0 or y == mc.height - 1)):
						self.tData[i] = mc.SNOW
						bWarm = False
					elif cm.TemperatureMap.data[i] < taigaTemp or latitude >= mc.snowPlateauMinLatitude:
						self.tData[i] = mc.TUNDRA
						bWarm = False
				#elif self.pData[i] != mc.PEAK:
				if bWarm and self.pData[i] != mc.PEAK: # </advc>
					warmTiles.append(cm.RainfallMap.data[i])
					warmLength += 1
		self.desertRainfall = FindValueFromPercent(warmTiles, warmLength, mc.DesertPercent, False)
		#self.plainsRainfall = FindValueFromPercent(warmTiles, warmLength, mc.PlainsPercent, False)
		# <advc> Reserve a portion of plains for the wettest climate
		steppePlainsPercent = mc.PlainsPercent * 0.75
		junglePlainsPercent = mc.PlainsPercent - steppePlainsPercent
		junglePlainsThreshold = FindValueFromPercent(warmTiles, warmLength, 1 - junglePlainsPercent, False)
		self.plainsRainfall = FindValueFromPercent(warmTiles, warmLength, steppePlainsPercent, False) # </advc>
		self.jungleRainfall = self.plainsRainfall * mc.JungleFactor
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				# advc: Can no longer rely on the tundraTemp here. Instead simply treat all unassigned land as warm .
				if self.pData[i] != mc.WATER and self.tData[i] == mc.OCEAN:#cm.TemperatureMap.data[i] >= self.tundraTemp:
					# advc: Temperature clause added to reduce the frequency of cold deserts
					if cm.RainfallMap.data[i] < self.desertRainfall and cm.TemperatureMap.data[i] >= self.tundraTemp * 1.3:
						self.tData[i] = mc.DESERT
					# advc: '>' clause added
					elif cm.RainfallMap.data[i] < self.plainsRainfall or cm.RainfallMap.data[i] > junglePlainsThreshold:
						self.tData[i] = mc.PLAINS
					else:
						self.tData[i] = mc.GRASS
		print "Jungle Temperature"
		jungleTiles  = []
		jungleLength = 0
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				# advc: Checks moved into global function
				if canHaveJungle(cm.RainfallMap.data[i], self.jungleRainfall, self.tData[i], self.pData[i], em.GetLatitudeForY(y)):
					jungleTiles.append(cm.TemperatureMap.data[i])
					jungleLength += 1
		self.jungleTemp = FindValueFromPercent(jungleTiles, jungleLength, mc.JunglePercent, True)


tm = TerrainMap()


class PangaeaBreaker:
	def __init__(self):
		return


	def breakPangaeas(self):
		if mc.AllowPangaeas:
			#print "Pangaeas are allowed on this map and will not be suppressed."
			return
		''' # advc: Should be OK now (will at most throw a couple of small ones)
		gc = CyGlobalContext()
		if gc.getMap().getWorldSize() < 3:
			print "This map is too small for meteors to work properly, so they will not be used."
			return
		'''
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		self.areaMap = AreaMap(em.width, em.height, True, True)
		meteorThrown   = False
		pangaeaDetected = False
		self.createDistanceMap()
		self.areaMap.defineAreas(isHmWaterMatch)
		meteorCount = 0
		if not mc.AllowPangaeas: #and gc.getMap().getWorldSize() >= 3: # advc
			while self.isPangaea() and meteorCount < mc.maximumMeteorCount:
				pangaeaDetected = True
				x, y = self.getMeteorStrike()
				print "A meteor has struck the Earth at %(x)d, %(y)d!!" % {"x":x,"y":y}
				self.castMeteorUponTheEarth(x, y)
				meteorThrown = True
				meteorCount += 1
				em.CalculateSeaLevel() # advc: Restore land ratio (inspired by C2C_World.py)
				self.createDistanceMap()
				self.areaMap.defineAreas(isHmWaterMatch)
		if not pangaeaDetected:
			print "No pangaea detected on this map."
		if meteorThrown:
			print "The age of dinosaurs has come to a cataclysmic end."
		#if meteorCount == 15:
		if meteorCount == mc.maximumMeteorCount: # advc.001
			print "Maximum meteor count of %d has been reached." % meteorCount
			# <advc> Previously always said that "Pangaea may still exist"
			if self.isPangaea():
				print "Pangaea still exists" # </advc>


	def isPangaea(self):
		continentList = list()
		for a in self.areaMap.areaList:
			if not a.water:
				continentList.append(a)
		totalLand = 0
		for c in continentList:
			totalLand += c.size
		#sort all the continents by size, largest first
		continentList.sort(lambda x, y:cmp(x.size, y.size))
		continentList.reverse()
		biggestSize = continentList[0].size
		# advc: was 0.7 < ...
		if 0.73 < float(biggestSize) / float(totalLand):
			return True
		return False


	def getMeteorStrike(self):
		continentList = list()
		for a in self.areaMap.areaList:
			if not a.water:
				continentList.append(a)
		#sort all the continents by size, largest first
		continentList.sort(lambda x, y:cmp(x.size, y.size))
		continentList.reverse()
		biggestContinentID = continentList[0].ID
		x, y = self.getHighestCentrality(biggestContinentID)
		return x, y


	def isChokePoint(self, x, y, biggestContinentID):
		circlePoints = self.getCirclePoints(x, y, mc.minimumMeteorSize)
		waterOpposite = False
		landOpposite  = False
		for cp in circlePoints:
			if isHmWaterMatch(cp.x, cp.y):
				#Find opposite
				ox = x + (x - cp.x)
				oy = y + (y - cp.y)
				if isHmWaterMatch(ox, oy):
					waterOpposite = True
			else:
				#Find opposite
				ox = x + (x - cp.x)
				oy = y + (y - cp.y)
				if not isHmWaterMatch(ox, oy):
					landOpposite = True
		if landOpposite and waterOpposite:
			percent = self.getLandPercentInCircle(circlePoints, biggestContinentID)
			if percent >= mc.minimumLandInChoke:
				return True
		return False


	def getLandPercentInCircle(self, circlePoints, biggestContinentID):
		land  = 0
		water = 0
		circlePoints.sort(lambda n, m:cmp(n.y, m.y))
		for n in range(0, len(circlePoints), 2):
			cy = circlePoints[n].y
			if circlePoints[n].x < circlePoints[n + 1].x:
				x1 = circlePoints[n].x
				x2 = circlePoints[n + 1].x
			else:
				x2 = circlePoints[n].x
				x1 = circlePoints[n + 1].x
			landLine,waterLine = self.countCraterLine(x1, x2, cy, biggestContinentID)
			land += landLine
			water += waterLine
		percent = float(land) / float(land + water)
		return percent


	def countCraterLine(self, x1, x2, y, biggestContinentID):
		land  = 0
		water = 0
		for x in range(x1, x2 + 1):
			i = GetHmIndex(x, y)
			if self.areaMap.data[i] == biggestContinentID:
				land += 1
			else:
				water += 1
		return land, water


	def getContinentCenter(self, ID):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		IDCount = 0
		xTotal  = 0
		yTotal  = 0
		for y in range(em.height):
			for x in range(em.width):
				i = GetHmIndex(x, y)
				if self.areaMap.data[i] == ID:
					IDCount += 1
					xTotal  += x
					yTotal  += y
		xCenter = round(float(xTotal) / float(IDCount))
		yCenter = round(float(yTotal) / float(IDCount))
		center = xCenter, yCenter
		return center


	def getDistance(self,x, y, dx, dy):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		xx = x - dx
		if abs(xx) > em.width / 2:
			xx = em.width - abs(xx)
		distance = max(abs(xx), abs(y - dy))
		return distance


	def castMeteorUponTheEarth(self, x, y):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		#radius = PRand.randint(mc.minimumMeteorSize, max(mc.minimumMeteorSize + 1, em.width / 16))
		# advc:
		radius = PRand.randint(mc.minimumMeteorSize, max(mc.minimumMeteorSize + 1, 2 * mc.minimumMeteorSize))
		circlePointList = self.getCirclePoints(x, y, radius)
		circlePointList.sort(lambda n, m:cmp(n.y, m.y))
		for n in range(0, len(circlePointList), 2):
			cy = circlePointList[n].y
			if circlePointList[n].x < circlePointList[n + 1].x:
				x1 = circlePointList[n].x
				x2 = circlePointList[n + 1].x
			else:
				x2 = circlePointList[n].x
				x1 = circlePointList[n + 1].x
			# <advc> params centerX, centerY added
			self.drawCraterLine(x1, x2, cy, x, y)


	def drawCraterLine(self, x1, x2, y, centerX, centerY): # </advc>
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		if y < 0 or y >= em.height:
			return
		for x in range(x1, x2 + 1):
			i = GetHmIndex(x, y)
			#em.data[i] = 0.0
			# advc: 0 elevation leads to coastal peaks when using the lowest-neighbor slope option.
			em.data[i] *= min(0.88, 0.37 + math.sqrt((x - centerX) * (x - centerX) + (y - centerY) * (y - centerY)) / 7.0)


	def getCirclePoints(self, xCenter, yCenter, radius):
		circlePointList = list()
		x = 0
		y = radius
		p = 1 - radius
		self.addCirclePoints(xCenter, yCenter, x, y, circlePointList)
		while (x < y):
			x += 1
			if p < 0:
				p += 2 * x + 1
			else:
				y -= 1
				p += 2 * (x - y) + 1
			self.addCirclePoints(xCenter, yCenter, x, y, circlePointList)
		return circlePointList


	def addCirclePoints(self, xCenter, yCenter, x, y, circlePointList):
		circlePointList.append(CirclePoint(xCenter + x, yCenter + y))
		circlePointList.append(CirclePoint(xCenter - x, yCenter + y))
		circlePointList.append(CirclePoint(xCenter + x, yCenter - y))
		circlePointList.append(CirclePoint(xCenter - x, yCenter - y))
		circlePointList.append(CirclePoint(xCenter + y, yCenter + x))
		circlePointList.append(CirclePoint(xCenter - y, yCenter + x))
		circlePointList.append(CirclePoint(xCenter + y, yCenter - x))
		circlePointList.append(CirclePoint(xCenter - y, yCenter - x))


	def createDistanceMap(self):
		# advc: Moved into global function
		self.distanceMap = createDistanceMap(True)


	def getHighestCentrality(self, ID):
		C = self.createCentralityList(ID)
		C.sort(lambda x, y:cmp(x.centrality, y.centrality))
		C.reverse()
		# <advc> Kludge. I see meteors cast near the poles or twice in the same spot; ruling out water targets should help.
		for i in range(len(C)):
			centralPlot = CyMap().plot(C[i].x, C[i].y)
			if not centralPlot is None and centralPlot.getX() >= 0 and centralPlot.getY() >= 0 and not centralPlot.isWater():
				return C[i].x, C[i].y # </advc>
		return C[0].x, C[0].y


	def createContinentList(self, ID):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		C        = []
		indexMap = []
		gap = 5
		n   = 0
		for y in range(em.height):
			for x in range(em.width):
				i = GetHmIndex(x, y)
				if y % gap == 0 and x % gap == 0 and self.areaMap.data[i] == ID:
					C.append(CentralityScore(x, y))
					indexMap.append(n)
					n += 1
				else:
					indexMap.append(-1)
		n = 0
		for s in C:
			#Check 4 neighbors
			xx = s.x - gap
			if xx < 0:
				xx = em.width / (gap * gap)
			i = GetHmIndex(xx, s.y)
			if i != -1 and self.areaMap.data[i] == ID:
				s.neighborList.append(indexMap[i])
			xx = s.x + gap
			if xx >= em.width:
				xx = 0
			i = GetHmIndex(xx, s.y)
			if i != -1 and self.areaMap.data[i] == ID:
				s.neighborList.append(indexMap[i])
			yy = s.y - gap
			if yy < 0:
				yy = em.height / (gap * gap)
			i = GetHmIndex(s.x, yy)
			if i != -1 and self.areaMap.data[i] == ID:
				s.neighborList.append(indexMap[i])
			yy = s.y + gap
			if yy > em.height:
				yy = 0
			i = GetHmIndex(s.x, yy)
			if i != -1 and self.areaMap.data[i] == ID:
				s.neighborList.append(indexMap[i])
			n += 1
		return C


	def createCentralityList(self,ID):
		C = self.createContinentList(ID)
		for s in range(len(C)):
			S = []
			P = []
			sigma = []
			d = []
			delta = []
			for t in range(len(C)):
				sigma.append(0)
				d.append(-1)
				P.append([])
				delta.append(0)
			sigma[s] = 1
			d[s] = 0
			Q = []
			Q.append(s)
			while len(Q) > 0:
				v = Q.pop(0)
				S.append(v)
				for w in C[v].neighborList:
					if d[w] < 0:
						Q.append(w)
						d[w] = d[v] + 1
					if d[w] == d[v] + 1:
						sigma[w] = sigma[w] + sigma[v]
						P[w].append(v)
			while len(S) > 0:
				w = S.pop()
				for v in P[w]:
					delta[v] = delta[v] + (sigma[v]/sigma[w]) * (1 + delta[w])
					if w != s:
						C[w].centrality = C[w].centrality + delta[w]
		return C


	def isNeighbor(self, x, y, xx, yy):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		if mc.WrapX:
			mx = xx % em.width
		elif x < 0 or x >= em.width:
			return False
		else:
			mx = xx
		if mc.WrapY:
			my = yy % em.height
		elif y < 0 or y >= em.height:
			return False
		else:
			my = yy
		if abs(x - mx) <= 1 and abs(y - my) <= 1:
			if x == mx and y == my:
				return False
			else:
				return True
		return False


class CirclePoint:
	def __init__(self, x, y):
		self.x = x
		self.y = y


class CentralityScore:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.centrality = 0
		self.neighborList = []


def isNonCoastWaterMatch(x, y):
	i = GetIndex(x, y)
	if tm.tData[i] == mc.OCEAN:
		return True
	return False


pb = PangaeaBreaker()


class ContinentMap:
	def __init__(self):
		return


	def GenerateContinentMap(self):
		print "------------------------"
		print "Generating Continent Map"
		print "------------------------"
		self.areaMap = AreaMap(mc.width, mc.height, True, True)
		self.areaMap.defineAreas(isWaterMatch)
		#self.newWorldID = self.getNewWorldID()
		# <advc> Moved into separate method so that the new world can be designated later
		self.newWorldAreaID = 0
		self.newWorldRegionID = 0


	def designateNewWorld(self):
		# Want the New World to be separated from the Old World by deep water.
		self.regionMap = AreaMap(mc.width, mc.height, True, True)
		self.regionMap.defineAreas(isDeepWaterMatch)
		self.newWorldAreaID, self.newWorldRegionID = self._getNewWorldID() # </advc>


	def _getNewWorldID(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		continentList = list()
		# <advc> Try regionMap first
		bRegionID = True
		for a in self.regionMap.areaList: # </advc>
			if not a.water:
				continentList.append(a)
		if len(continentList) <= 1:
			# <advc> Fall back on areaMap
			continentList = list()
			for a in self.areaMap.areaList:
				if not a.water:
					continentList.append(a)
			if len(continentList) <= 1:
				return 0, 0
			bRegionID = False
			print "Pangaea; will at best be able to designate an area separated by shallow water as the New World"
			# </advc>
		#totalLand = 0
		#for c in continentList:
		#	totalLand += c.size
		# <advc> Could use AdvCiv's CyArea::getNumHabitableTiles (the map is pretty much finished), but it's awkward to map the Area object to a CvArea. So I've written only a one-liner (Area.startScore) that takes into account the average latitude. That should already be much better than area size alone.
		totalScore = 0
		for c in continentList:
			totalScore += c.startScore() # </advc>
		#sort all the continents by size, largest first
		#continentList.sort(lambda x, y:cmp(x.size, y.size))
		continentList.sort(lambda x, y:cmp(x.startScore(), y.startScore())) # advc
		continentList.reverse()
		#now remove a percentage of the landmass to be considered 'Old World'
		#biggest continent is automatically 'Old World'
		#oldWorldSize = continentList[0].size
		oldWorldScore = continentList[0].startScore() # advc
		oldWorldAvgX = continentList[0].avgX
		oldWorldAvgY = continentList[0].avgY
		print("%d continents, best one (%d tiles, %d avg. y-coord., %d score) added to Old World" % (len(continentList), continentList[0].size, continentList[0].avgY, round(oldWorldScore*100))) # advc
		del continentList[0]
		# <advc> Only reserve the second best continent if this still leaves enough room per civ in the Old World
		reserveSecondBest = False
		iCivs = CyGlobalContext().getGame().countCivPlayersEverAlive()
		if float(totalScore - continentList[0].startScore()) / float(iCivs) > 70:
			reserveSecondBest = True # </advc>
			#get the next largest continent and temporarily remove from list
			#add it back later and is automatically 'New World'
			mainNewWorld = continentList[0]
			print("Second best continent (%d tiles, %d avg. y-coord., %d score) reserved for New World" % (mainNewWorld.size, mainNewWorld.avgY, round(mainNewWorld.startScore()*100))) # advc
			del continentList[0]
		#LM - sort list by proximity
		for c in continentList:
			minX = abs(oldWorldAvgX - c.avgX)
			minY = abs(oldWorldAvgY - c.avgY)
			if mc.WrapX:
				minX = min(minX, mc.width  - minX)
			if mc.WrapY:
				minY = min(minY, mc.height - minY)
			c.distance = math.sqrt(pow(minX, 2) + pow(minY, 2))
		continentList.sort(lambda x, y:cmp(x.distance, y.distance))
		# advc: Was 0.55. The true ratio (Africa+Eurasia)/(Africa+EurasiaAmerica+Oceania) is 62.5%. An even larger Old World plays better. Use randomness to make a realistic size possible but rather unlikely.
		oldWorldTargetPercent = (60 + PRand.randint(0, 9)) / 100.0
		skipped = 0 # advc
		oldWorldPercent = 0 # advc
		for n in range(len(continentList)):
			# <advc> Small land masses are no use for the Old World b/c civs can't start there
			if continentList[0].size < 50 and skipped * 2 < len(continentList):
				skipped += 1
				continentList.append(continentList[0])
				del continentList[0]
				continue # </advc>
			#oldWorldSize += continentList[0].size
			oldWorldScore += continentList[0].startScore() # advc
			del continentList[0]
			#if float(oldWorldSize) / float(totalLand) > oldWorldTargetPercent:
			# advc: Put this in a variable (for debug output)
			oldWorldPercent = oldWorldScore / float(totalScore)
			if oldWorldPercent > oldWorldTargetPercent:
				break
		print "oldWorldPercent=" + str(oldWorldPercent) # advc
		#add back the mainNewWorld continent
		if reserveSecondBest:
			# <advc> A too small Old World is going to be unplayable; rather reserve no New World then (or just some islands).
			if float(oldWorldScore) / float(iCivs) < 60:
				print("Best New World continent added to Old World b/c tiles per civ in the Old World was only %d" % (oldWorldScore // iCivs))
			else: # </advc>
				continentList.append(mainNewWorld)
		#what remains in the list will be considered 'New World'
		#get ID for the next continent, we will use this ID for 'New World' designation
		nID = continentList[0].ID
		del continentList[0] #delete to avoid unnecessary overwrite
		#now change all the remaining continents to also have nID as their ID
		for i in range(em.length):
			for c in continentList:
				# <advc>
				if bRegionID:
					if c.ID == self.regionMap.data[i]:
						self.regionMap.data[i] = nID
				else: # </advc>
					if c.ID == self.areaMap.data[i]:
						self.areaMap.data[i] = nID
		#return nID
		# <advc>
		if bRegionID:
			return 0, nID
		return nID, 0 # </advc>


km = ContinentMap()


#OK! now that directions N,S,E,W are important, we have to keep in mind that
#the map plots are ordered from 0,0 in the SOUTH west corner! NOT the northwest
#corner! That means that Y increases as you go north.
class RiverMap:
	def __init__(self):
		#To provide global access without allocating alot of resources for
		#nothing, object initializer must be empty
		return


	def GenerateRiverMap(self):
		print "--------------------"
		print "Generating River Map"
		print "--------------------"
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		self.O = 9 #used for ocean or land without a river
		#averageHeightMap, flowMap, averageRainfallMap and drainageMap are offset from the other maps such that
		#each element coincides with a four tile intersection on the game map
		self.averageHeightMap   = array('d')
		self.flowMap            = array('i')
		self.averageRainfallMap = array('d')
		self.drainageMap        = array('d')
		self.riverMap           = array('i')
		#initialize maps with zeros
		for i in range(em.length):
			self.averageHeightMap.append(0.0)
			self.flowMap.append(0)
			self.averageRainfallMap.append(0.0)
			self.drainageMap.append(0.0)
			self.riverMap.append(self.O)
		#Get highest intersection neighbor
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				maxHeight = 0.0
				for yy in range(y, y - 2, -1):
					for xx in range(x, x + 2):
						ii = GetIndex(xx, yy)
						if ii >= 0:
							#use an average hight of <0 to denote an ocean border
							#this will save processing time later
							if (tm.pData[ii] == mc.WATER):
								maxHeight = -100.0
							elif maxHeight >= 0 and maxHeight < em.data[ii]:
								maxHeight = em.data[ii]
				self.averageHeightMap[i] = maxHeight
		#Now try to silt in any lakes
		self.siltifyLakes()
		self.createLakeDepressions()
		#create flowMap by checking for the lowest of each 4 connected
		#neighbor plus self
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				lowestAlt = self.averageHeightMap[i]
				if (lowestAlt < 0.0):
					#if height is <0 then that means this intersection is
					#adjacent to an ocean and has no flow
					self.flowMap[i] = self.O
				else:
					#First assume this place is lowest, like a 'pit'. Then
					#for each place that is lower, add it to a list to be
					#randomly chosen as the drainage path
					drainList    = list()
					nonDrainList = list()
					self.flowMap[i] = mc.L
					ii = GetIndex(x, y + 1)
					if ii >= 0 and self.averageHeightMap[ii] < lowestAlt:
						drainList.append(mc.N)
					else:
						nonDrainList.append(mc.N)
					ii = GetIndex(x, y - 1)
					if ii >= 0 and self.averageHeightMap[ii] < lowestAlt:
						drainList.append(mc.S)
					else:
						nonDrainList.append(mc.S)
					ii = GetIndex(x - 1, y)
					if ii >= 0 and self.averageHeightMap[ii] < lowestAlt:
						drainList.append(mc.W)
					else:
						nonDrainList.append(mc.W)
					ii = GetIndex(x + 1, y)
					if ii >= 0 and self.averageHeightMap[ii] < lowestAlt:
						drainList.append(mc.E)
					else:
						nonDrainList.append(mc.E)
					#never go straight when you have other choices
					count = len(drainList)
					if count == 3:
						oppDir = GetOppositeDirection(nonDrainList[0])
						for n in range(count):
							if drainList[n] == oppDir:
								del drainList[n]
								break
						count = len(drainList)
					if count > 0:
						choice = int(PRand.random() * count)
						self.flowMap[i] = drainList[choice]
		if mc.ClimateSystem == 0:
			cm = c3
		else:
			cm = c2
		#Create average rainfall map so that each intersection is an average
		#of the rainfall from rm.rainMap
		worldSz = CyMap().getWorldSize() # advc
		for y in range(mc.height):
			# <advc> Kludge for making the extreme latitudes less riverine. Those river exacerbate the problem with (supposed) rainforests being highly productive tiles, and such rivers weren't as important to human habitation as rivers through temperate areas or through deserts. Somehow, it seems that rivers tend to be placed in higher latitudes on larger maps. Hence the worldSz adjustment.
			latitudeMult = 1.0
			absLat = abs(em.GetLatitudeForY(y))
			vicinityToEquator = (mc.tropicsLatitude - absLat) / float(mc.tropicsLatitude)
			if vicinityToEquator > 0:
				latitudeMult = 1 - (max(1, min(7 - worldSz, 4))/5.) * math.sqrt(vicinityToEquator)
			else:
				intervalLength = 90 - mc.polarFrontLatitude + 3
				vicinityToPole = (intervalLength - abs(em.GetLatitudeForY(y))) / float(intervalLength)
				if vicinityToPole > 0:
					latitudeMult = 1 - (min(worldSz + 4, 9)/10.) * pow(vicinityToPole, 1.13)
			# (No penalty for plots _near_ the tropics or polar front - rivers starting there may well flow into less extreme latitudes.)
			# </advc>
			for x in range(mc.width):
				i = GetIndex(x, y)
				total = 0.0
				count = 0.0
				# <advc>
				minRf = 1.0
				maxRf = 0.0 # </advc>
				for yy in range(y, y - 2, -1):
					for xx in range(x, x + 2):
						ii = GetIndex(xx, yy)
						if ii >= 0:
							rfVal = cm.RainfallMap.data[ii]
							# <advc>
							rfVal *= latitudeMult
							minRf = min(minRf, rfVal)
							maxRf = max(maxRf, rfVal) # </advc>
							total += rfVal
							count += 1.0
				self.averageRainfallMap[i] = total / count
				# <advc> Another kludge, pretty much. Spreads rivers out more, it seems.
				if mc.ClimateSystem == 0:
					# Note that increasing rainfall values like this (or decreasing them through latitudeMult) requires adjustments to riverThreshold as well.
					self.averageRainfallMap[i] += 4 * (maxRf - minRf) # </advc>
		#Now use the flowMap as a guide to distribute average rainfall.
		#Wherever the most rainfall ends up is where the rivers will be.
		print "Distributing rainfall"
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				flow     = self.flowMap[i]
				rainFall = self.averageRainfallMap[i]
				xx = x
				yy = y
				while (flow != mc.L and flow != self.O):
					if (flow == mc.N):
						yy += 1
					elif (flow == mc.S):
						yy -= 1
					elif (flow == mc.W):
						xx -= 1
					elif (flow == mc.E):
						xx += 1
					ii = GetIndex(xx, yy)
					if ii >= 0:
						#dump rainfall here
						self.drainageMap[ii] += rainFall
						#reset flow
						flow = self.flowMap[ii]
					else:
						break
		if mc.ClimateSystem == 0:
			riverThreshold = mc.RiverThreshold3
		else:
			riverThreshold = mc.RiverThreshold2
		riversPlaced = 0 # advc
		for i in range(em.length):
			if (self.drainageMap[i] >= riverThreshold):
				self.riverMap[i] = self.flowMap[i]
				riversPlaced += 1
			else:
				self.riverMap[i] = self.O
		# advc: Print number of pegged river segments
		print "River map generated (" + str(riversPlaced) + " segments placed)"
		#at this point river should be in tolerance or close to it
		#riverMap is ready for use


	def siltifyLakes(self):
		lakeList = []
		onQueueMap = array('i')
		for y in range(mc.height):
			for x in range(mc.width):
				onQueueMap.append(0)
				i = GetIndex(x, y)
				if self.isLake(x, y):
					lakeList.append((x, y, 1))
					onQueueMap[i] = 1
		largestLength = len(lakeList)
		while len(lakeList) > 0:
			if len(lakeList) > largestLength:
				largestLength = len(lakeList)
			x, y, lakeSize = lakeList[0]
			del lakeList[0]
			i = GetIndex(x, y)
			onQueueMap[i] = 0
			if mc.RiverGenerator == 0: # advc: Flipped so that 0 is the PW2 river generator
				if lakeSize > mc.maxSiltPanSizePW2:
					continue
			else:
				if lakeSize > mc.maxSiltPanSizeSDK:
					continue
			lakeSize += 1
			lowestNeighborAlt = self.getLowestNeighborAltitude(x, y)
			self.averageHeightMap[i] = lowestNeighborAlt + 0.005
			for direction in range(1, 5):
				xx, yy = GetNeighbor(x, y, direction)
				ii = GetIndex(xx, yy)
				if ii >= 0 and self.isLake(xx, yy) and onQueueMap[ii] == 0:
					xx, yy = CoordsFromIndex(ii, mc.width) # advc.001
					lakeList.append((xx, yy, lakeSize))
					onQueueMap[ii] = 1


	def isLake(self, x, y):
		i = GetIndex(x, y)
		alt = self.averageHeightMap[i]
		if alt < 0.0:
			return False
		for direction in range(1, 5):
			xx, yy = GetNeighbor(x, y, direction)
			ii = GetIndex(xx, yy)
			if ii >= 0 and self.averageHeightMap[ii] < alt:
				return False
		return True


	def getLowestNeighborAltitude(self, x, y):
		lowest = 1.0
		for direction in range(1, 5):
			xx, yy = GetNeighbor(x, y, direction)
			ii = GetIndex(xx, yy)
			if ii >= 0 and self.averageHeightMap[ii] < lowest:
				lowest = self.averageHeightMap[ii]
		return lowest


	def createLakeDepressions(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		lakeList = []
		for y in range(mc.height):
			for x in range(mc.width):
				i = GetIndex(x, y)
				if self.averageHeightMap[i] > mc.minLakeAltitude:
					lakeList.append((x, y))
		lakeList = ShuffleList(lakeList)
		if mc.ClimateSystem == 0:
			numLakes = int(em.length * mc.numberOfLakesPerPlot3)
		else:
			numLakes = int(em.length * mc.numberOfLakesPerPlot2)
		for n in range(numLakes):
			x, y = lakeList[n]
			i = GetIndex(x, y)
			lowestAlt = self.getLowestNeighborAltitude(x, y)
			if lowestAlt >= 0.0:
				self.averageHeightMap[i] = lowestAlt - 0.001


rm = RiverMap()


class BonusPlacer: # advc (note): Disused; see addBonuses.
	def __init__(self):
		return


	def AddBonuses(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		gc = CyGlobalContext()
		CyMap().recalculateAreas()
		self.AssignBonusAreas()
		numBonuses = gc.getNumBonusInfos()
		#Create a list of map indices and shuffle them
		plotIndexList = []
		for i in range(em.length):
			plotIndexList.append(i)
		plotIndexList = ShuffleList(plotIndexList)
		#AIAndy - Check which placement orders are used, discard -1
		orderSet = {}
		for i in range(numBonuses):
			bonusInfo = gc.getBonusInfo(self.bonusList[i].eBonus)
			porder = bonusInfo.getPlacementOrder()
			if porder >= 0:
				orderSet[porder] = 1
		porderList = sorted(orderSet.keys())
		startAtIndex = 0
		for order in porderList:
			placementList = []
			for i in range(numBonuses):
				bonusInfo = gc.getBonusInfo(self.bonusList[i].eBonus)
				if bonusInfo.getPlacementOrder() == order:
					for n in range(self.bonusList[i].desiredBonusCount):
						placementList.append(self.bonusList[i].eBonus)
			if len(placementList) > 0:
				placementList = ShuffleList(placementList)
				for eBonus in placementList:
					startAtIndex = self.AddBonusType(eBonus, plotIndexList, startAtIndex)
		#now check to see that all resources have been placed at least once, this
		#pass ignoring area rules
		for i in range(numBonuses):
			bonus = self.bonusList[i]
			if bonus.currentBonusCount == 0 and bonus.desiredBonusCount > 0:
				startAtIndex = self.AddEmergencyBonus(bonus, False, plotIndexList, startAtIndex)
		#now check again to see that all resources have been placed at least once,
		#this time ignoring area rules and also class spacing
		for i in range(numBonuses):
			bonus = self.bonusList[i]
			if bonus.currentBonusCount == 0 and bonus.desiredBonusCount > 0:
				startAtIndex = self.AddEmergencyBonus(bonus, True, plotIndexList, startAtIndex)
		#now report resources that simply could not be placed
		for i in range(numBonuses):
			bonus = self.bonusList[i]
			bonusInfo = gc.getBonusInfo(bonus.eBonus)
			if bonus.currentBonusCount == 0 and bonus.desiredBonusCount > 0:
				print "No room at all found for %(bt)s!!!" % {"bt":bonusInfo.getType()}
			print "Placed %(cb)d, desired %(db)d for %(bt)s" % {"cb":bonus.currentBonusCount, "db":bonus.desiredBonusCount, "bt":bonusInfo.getType()}


	#AIAndy - Changed to start at the end of the last run in the plot list
	def AddBonusType(self, eBonus, plotIndexList, startAtIndex):
		#first get bonus/area link
		bonus = self.bonusList[self.bonusDict[eBonus]]
		if bonus.currentBonusCount >= bonus.desiredBonusCount:
			return False
		gc = CyGlobalContext()
		bonusInfo = gc.getBonusInfo(eBonus)
		bonusPlaced = False
		plotListLength = len(plotIndexList)
		lastI = 0
		#now add bonuses
		for i in range(startAtIndex, startAtIndex + plotListLength):
			index = 0
			lastI = i
			if i >= plotListLength:
				index = plotIndexList[i - plotListLength]
			else:
				index = plotIndexList[i]
			plot = CyMap().plotByIndex(index)
			x = plot.getX()
			y = plot.getY()
			if self.CanPlaceBonusAt(plot, eBonus, False, False):
				#place bonus
				plot.setBonusType(eBonus)
				bonusPlaced = True
				bonus.currentBonusCount += 1
				groupRange = bonusInfo.getGroupRange()
				#NEW CODE - Fuyu/LM
				#added/maxAdd: avoid grouping ALL the resources of a type together.
				#it's annoying to find 6 wines together and nowhere else on the map.
				added = 0
				if (mc.BonusMaxGroupSize == -1):
					maxAdd = (gc.getMap().getWorldSize() / 2) + 3
				elif (mc.BonusMaxGroupSize == 0):
					maxAdd = PRand.randint(1, gc.getGame().countCivPlayersEverAlive())
				else:
					maxAdd = PRand.randint(1, mc.BonusMaxGroupSize)
				for dx in range(-groupRange, groupRange + 1):
					for dy in range(-groupRange, groupRange + 1):
						#NEW CODE - Fuyu
						if(added >= maxAdd):
							break
						if bonus.currentBonusCount < bonus.desiredBonusCount:
							loopPlot = self.plotXY(x, y, dx, dy)
							if loopPlot != None:
								if loopPlot.getX() == -1:
									raise ValueError, "plotXY returns invalid plots plot= %(x)d, %(y)d" % {"x":x, "y":y}
								if self.CanPlaceBonusAt(loopPlot,eBonus,False,False):
									if PRand.randint(0, 99) < bonusInfo.getGroupRand():
										#place bonus
										loopPlot.setBonusType(eBonus)
										bonus.currentBonusCount += 1
										#NEW CODE - Fuyu
										added += 1
			if bonusPlaced:
				break
		lastI = (lastI + 1) % plotListLength
		return lastI


	#AIAndy - Changed to start at the end of the last run in the plot list and not shuffle an extra plot list
	def AddEmergencyBonus(self, bonus, ignoreClass, plotIndexList, startAtIndex):
		gc = CyGlobalContext()
		bonusInfo = gc.getBonusInfo(bonus.eBonus)
		plotListLength = len(plotIndexList)
		lastI = 0
		fFloodPlains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
		fOasis       = gc.getInfoTypeForString("FEATURE_OASIS")
		for i in range(startAtIndex, startAtIndex + plotListLength):
			index = 0
			lastI = i
			if i >= plotListLength:
				index = plotIndexList[i - plotListLength]
			else:
				index = plotIndexList[i]
			plot = CyMap().plotByIndex(index)
			x = plot.getX()
			y = plot.getY()
			featureEnum = plot.getFeatureType()
			requiredFeature = (featureEnum == fFloodPlains or featureEnum == fOasis)
			if ((ignoreClass and self.PlotCanHaveBonus(plot, bonus.eBonus, False, True)) or self.CanPlaceBonusAt(plot, bonus.eBonus, False, True)) and not requiredFeature:
				#temporarily remove any feature
				if featureEnum != FeatureTypes.NO_FEATURE:
					featureVariety = plot.getFeatureVariety()
					plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
				#place bonus
				plot.setBonusType(bonus.eBonus)
				bonus.currentBonusCount += 1
				#restore the feature if possible
				if featureEnum != FeatureTypes.NO_FEATURE:
					if bonusInfo == None or bonusInfo.isFeature(featureEnum):
						plot.setFeatureType(featureEnum, featureVariety)
				print "Emergency placement of 1 %(bt)s" % {"bt":bonusInfo.getType()}
				break
		lastI = (lastI + 1) % plotListLength
		return lastI


	def plotXY(self, x, y, dx, dy):
		#The one that civ uses will return junk so I have to make one that will not
		x = (x + dx) % mc.width
		y = y + dy
		if y < 0 or y > mc.height - 1:
			return None
		return CyMap().plot(x, y)


	def AssignBonusAreas(self):
		gc = CyGlobalContext()
		self.areas = CvMapGeneratorUtil.getAreas()
		self.bonusList = list()
		#Create and shuffle the bonus list and keep tally on one-area
		#bonuses and find the smallest min area requirement among those
		numUniqueBonuses = 0
		minLandAreaSize = -1
		numBonuses = gc.getNumBonusInfos()
		for i in range(numBonuses):
			bonus = BonusArea()
			bonus.eBonus = i
			self.bonusList.append(bonus)
			bonusInfo = gc.getBonusInfo(i)
			if bonusInfo.isOneArea():
				numUniqueBonuses += 1
				minAreaSize = bonusInfo.getMinAreaSize()
				if (minLandAreaSize == -1 or minLandAreaSize > minAreaSize) and minAreaSize > 0:
					minLandAreaSize = minAreaSize
		self.bonusList = ShuffleList(self.bonusList)
		self.bonusDict = [0] * numBonuses
		for i in range(numBonuses):
			eBonus = self.bonusList[i].eBonus
			self.bonusDict[eBonus] = i
			self.bonusList[i].desiredBonusCount = self.CalculateNumBonusesToAdd(eBonus)
			bonusInfo = gc.getBonusInfo(eBonus)
			if not bonusInfo.isOneArea():
				continue #Only assign areas to area bonuses
			areaSuitabilityList = list()
			for area in self.areas:
				if area.getNumTiles() >= minLandAreaSize:
					aS = AreaSuitability(area.getID())
					aS.suitability,aS.numPossible = self.CalculateAreaSuitability(area, eBonus)
					areaSuitabilityList.append(aS)
			#Calculate how many areas to assign (numUniqueBonuses will be > 0 if we get here)
			areasPerBonus = 1
			#Sort areaSuitabilityList best first
			areaSuitabilityList.sort(lambda x, y:cmp(x.numPossible, y.numPossible))
			areaSuitabilityList.reverse()
			#assign the best areas to this bonus
			for n in range(areasPerBonus):
				self.bonusList[i].areaList.append(areaSuitabilityList[n].areaID)
			#assign areas that have a high suitability also
			for n in range(areasPerBonus,len(areaSuitabilityList)):
				if areaSuitabilityList[n].suitability > 0.3:
					self.bonusList[i].areaList.append(areaSuitabilityList[n].areaID)


	def CanPlaceBonusAt(self, plot, eBonus, bIgnoreLatitude, bIgnoreArea):
		gc = CyGlobalContext()
		x = plot.getX()
		y = plot.getY()
		areaID = plot.getArea()
		if not self.PlotCanHaveBonus(plot, eBonus, bIgnoreLatitude, bIgnoreArea):
			return False
		for i in range(DirectionTypes.NUM_DIRECTION_TYPES):
			loopPlot = plotDirection(x, y, DirectionTypes(i))
			if loopPlot.getBonusType(TeamTypes.NO_TEAM) != BonusTypes.NO_BONUS and loopPlot.getBonusType(TeamTypes.NO_TEAM) != eBonus:
			   return False
		bonusInfo = gc.getBonusInfo(eBonus)
		classInfo = gc.getBonusClassInfo(bonusInfo.getBonusClassType())
		if plot.isWater():
			if (CyMap().getNumBonusesOnLand(eBonus) * 100) / (CyMap().getNumBonuses(eBonus) + 1) < bonusInfo.getMinLandPercent():
				return False
		#Make sure there are no bonuses of the same class (but a different type) nearby:
		if classInfo != None:
			try:
				iRange = classInfo.getUniqueRange()
			except:
				iRange = classInfo.getUniqueRange #<--attribute for vanilla
			iRange = max(0, int(iRange - (round(mc.BonusBonus) - 1)))
			for dx in range(-iRange, iRange + 1):
				for dy in range(-iRange, iRange + 1):
					loopPlot = self.plotXY(x, y, dx, dy)
					if loopPlot != None:
						if areaID == loopPlot.getArea():
							if plotDistance(x, y, loopPlot.getX(), loopPlot.getY()) <= iRange:
								eOtherBonus = loopPlot.getBonusType(TeamTypes.NO_TEAM)
								if eOtherBonus != BonusTypes.NO_BONUS:
									if gc.getBonusInfo(eOtherBonus).getBonusClassType() == bonusInfo.getBonusClassType():
										return False
		#Make sure there are no bonuses of the same type nearby:
		iRange = bonusInfo.getUniqueRange()
		iRange = max(0, int(iRange - (round(mc.BonusBonus) - 1)))
		for dx in range(-iRange, iRange + 1):
			for dy in range(-iRange, iRange + 1):
				loopPlot = self.plotXY(x, y, dx, dy)
				if loopPlot != None:
					if areaID == loopPlot.getArea():
						if plotDistance(x, y, loopPlot.getX(), loopPlot.getY()) <= iRange:
							eOtherBonus = loopPlot.getBonusType(TeamTypes.NO_TEAM)
							if eOtherBonus != BonusTypes.NO_BONUS:
								if eOtherBonus == eBonus:
									return False
		return True


	def PlotCanHaveBonus(self, plot, eBonus, bIgnoreLatitude, bIgnoreArea):
		#This function is like CvPlot::canHaveBonus but will ignore blocking features and checks for a valid area.
		if eBonus == BonusTypes.NO_BONUS:
			return True
		if plot.getBonusType(TeamTypes.NO_TEAM) != BonusTypes.NO_BONUS:
			return False
		if plot.isPeak():
			return False
		gc = CyGlobalContext()
		bonusInfo = gc.getBonusInfo(eBonus)
		#Here is the change from canHaveBonus. Forest does not block bonus
		featureForest  = gc.getInfoTypeForString("FEATURE_FOREST")
		requiresForest = bonusInfo.isFeature(featureForest)
		plotIsForest   = plot.getFeatureType() == featureForest
		#To avoid silk and spices on snow/tundra
		if plotIsForest and requiresForest:
			if not bonusInfo.isFeatureTerrain(plot.getTerrainType()):
				return False
		#now that bonuses that require forest are dealt with, count forest as no feature
		else:
			if plot.getFeatureType() != FeatureTypes.NO_FEATURE and not plotIsForest:
				if not bonusInfo.isFeature(plot.getFeatureType()):
					return False
				if not bonusInfo.isFeatureTerrain(plot.getTerrainType()):
					return False
			else:
				if not bonusInfo.isTerrain(plot.getTerrainType()):
					return False
		if plot.isFlatlands():
			if not bonusInfo.isFlatlands():
				return False
		elif plot.isHills():
			if not bonusInfo.isHills():
				return False
		if bonusInfo.isNoRiverSide():
			if plot.isRiverSide():
				return False
		if bonusInfo.getMinAreaSize() != -1:
			if plot.area().getNumTiles() < bonusInfo.getMinAreaSize():
				return False
		if not bIgnoreLatitude:
			if plot.getLatitude() > bonusInfo.getMaxLatitude():
				return False
			if plot.getLatitude() < bonusInfo.getMinLatitude():
				return False
		if not plot.isPotentialCityWork():
			return False
		if bonusInfo.isOneArea() and not bIgnoreArea:
			areaID = plot.getArea()
			areaFound = False
			i = self.bonusDict[eBonus]
			areaList = self.bonusList[i].areaList
			for n in range(len(areaList)):
				if areaList[n] == areaID:
					areaFound = True
					break
			if not areaFound:
				return False
		return True


	def CalculateNumBonusesToAdd(self, eBonus):
		#This is like the function in CvMapGenerator except it uses
		#self.PlotCanHaveBonus instead of CvPlot::canHaveBonus
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		gc = CyGlobalContext()
		bonusInfo = gc.getBonusInfo(eBonus)
		if bonusInfo.getPlacementOrder() < 0:
			return 0
		rand1 = PRand.randint(0, bonusInfo.getRandAppearance1())
		rand2 = PRand.randint(0, bonusInfo.getRandAppearance2())
		rand3 = PRand.randint(0, bonusInfo.getRandAppearance3())
		rand4 = PRand.randint(0, bonusInfo.getRandAppearance4())
		baseCount = bonusInfo.getConstAppearance() + rand1 + rand2 + rand3 + rand4
		bIgnoreLatitude = False
		bIgnoreArea     = True
		landTiles   = 0
		numPossible = 0
		if bonusInfo.getTilesPer() > 0:
			for i in range(em.length):
				plot = CyMap().plotByIndex(i)
				if self.PlotCanHaveBonus(plot, eBonus, bIgnoreLatitude, bIgnoreArea):
					numPossible += 1
			landTiles += numPossible / bonusInfo.getTilesPer()
		players = CyGame().countCivPlayersAlive() * bonusInfo.getPercentPerPlayer() / 100
		bonusCount = baseCount * (landTiles + players) / 100
		bonusCount = max(1, int(bonusCount * mc.BonusBonus))
		return bonusCount


	def GetUniqueBonusTypeCountInArea(self, area):
		gc = CyGlobalContext()
		areaID = area.getID()
		uniqueBonusCount = 0
		for i in range(len(self.bonusList)):
			areaList = self.bonusList[i].areaList
			bonusInfo = gc.getBonusInfo(self.bonusList[i].eBonus)
			if not bonusInfo.isOneArea():
				continue
			for n in range(len(areaList)):
				if areaList[n] == areaID:
					uniqueBonusCount += 1
					break
		return uniqueBonusCount


	def GetSameClassTypeCountInArea(self, area, eBonus):
		gc = CyGlobalContext()
		areaID = area.getID()
		uniqueBonusCount = 0
		bonusInfo = gc.getBonusInfo(eBonus)
		eClass = bonusInfo.getBonusClassType()
		if eClass == BonusClassTypes.NO_BONUSCLASS:
			return 0
		classInfo = gc.getBonusClassInfo(eClass)
		if classInfo == None:
			return 0
		try:
			uRange = classInfo.getUniqueRange()
		except:
			uRange = classInfo.getUniqueRange #<--vanilla Civ4
		uRange = max(0, int(uRange - (round(mc.BonusBonus) - 1)))
		for i in range(len(self.bonusList)):
			areaList = self.bonusList[i].areaList
			bonusInfo = gc.getBonusInfo(self.bonusList[i].eBonus)
			if not bonusInfo.isOneArea():
				continue
			if bonusInfo.getBonusClassType() != eClass:
				continue
			for n in range(len(areaList)):
				if areaList[n] == areaID:
					uniqueBonusCount += 1
					break
		#Same class types tend to really crowd out any bonus types that are placed later. A single cow can block
		#5 * 5 squares of pig territory for example. Probably shouldn't place them on the same area at all, but
		#sometimes it might be necessary.
		return uniqueBonusCount * uRange * uRange


	def CalculateAreaSuitability(self, area, eBonus):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		gc = CyGlobalContext()
		areaID = area.getID()
		uniqueTypesInArea    = self.GetUniqueBonusTypeCountInArea(area)
		sameClassTypesInArea = self.GetSameClassTypeCountInArea(area, eBonus)
		#Get the raw number of suitable tiles
		numPossible = 0
		for i in range(em.length):
			plot = CyMap().plotByIndex(i)
			if plot.getArea() == areaID:
				if self.PlotCanHaveBonus(plot, eBonus, False, True):
					numPossible += 1
		numPossible = numPossible / (uniqueTypesInArea + sameClassTypesInArea + 1)
		suitability = float(numPossible) / float(area.getNumTiles())
		return suitability, numPossible


class BonusArea:
	def __init__(self):
		self.eBonus = -1
		self.desiredBonusCount = -1
		self.currentBonusCount = 0
		self.areaList = list()


class AreaSuitability:
	def __init__(self, areaID):
		self.areaID = areaID
		self.suitability = 0
		self.numPossible = 0


bp = BonusPlacer()


class StartingPlotFinder:
	def __init__(self):
		return


	def CachePlotValue(self):
		self.inlandValueList  = []
		self.inlandFoodList   = []
		self.coastalValueList = []
		self.coastalFoodList  = []
		for y in range(mc.height):
			for x in range(mc.width):
				food, value = self.getPlotPotentialValueUncached(x, y, False)
				self.inlandValueList.append(value)
				self.inlandFoodList.append(food)
				food, value = self.getPlotPotentialValueUncached(x, y, True)
				self.coastalValueList.append(value)
				self.coastalFoodList.append(food)


	def SetStartingPlots(self):
		try:
			if mc.LandmassGenerator == 2:
				em = e2
			else:
				em = e3
			gc = CyGlobalContext()
			iPlayers = gc.getGame().countCivPlayersEverAlive()
			self.CachePlotValue()
			#Shuffle players so the same player doesn't always get the first pick.
			#lifted from Highlands.py that ships with Civ.
			player_list = []
			for plrCheckLoop in range(gc.getMAX_CIV_PLAYERS()):
				if CyGlobalContext().getPlayer(plrCheckLoop).isEverAlive():
					player_list.append(plrCheckLoop)
			shuffledPlayers = []
			for playerLoop in range(iPlayers):
				iChoosePlayer = PRand.randint(0, len(player_list) - 1)
				shuffledPlayers.append(player_list[iChoosePlayer])
				del player_list[iChoosePlayer]

			CyMap().recalculateAreas()
			areas = CvMapGeneratorUtil.getAreas()
			#get old/new world status
			isAreaOldWorld = self.setupOldWorldAreaList()
			#LM - Set up a map that merges Coast-linked landmasses so we can allow island starts while still ensuring adequate expansion room.
			regionMap = AreaMap(mc.width, mc.height, True, True)
			regionMap.defineAreas(isDeepWaterMatch)
			#LM - Set up a map that divides areas by Peaks so we can prevent starting locations from being walled-off in small pockets.
			''' # advc.030: Won't be needed
			if gc.getGame().getStartEra() < 3:
				self.peakMap = AreaMap(mc.width, mc.height, True, True)
				self.peakMap.defineAreas(isPeakWaterMatch)
			'''
			self.startingAreaList = list()
			'''
			if mc.SeaLevel == 0:
				if mc.OldWorldStarts:
					iWorldSizeFactor = 3
				else:
					iWorldSizeFactor = 5
			elif mc.SeaLevel == 1:
				if mc.OldWorldStarts:
					iWorldSizeFactor = 3.5
				else:
					iWorldSizeFactor = 6
			elif mc.SeaLevel == 2:
				if mc.OldWorldStarts:
					iWorldSizeFactor = 2.5
				else:
					iWorldSizeFactor = 4
			elif mc.SeaLevel == 3:
				if mc.OldWorldStarts:
					iWorldSizeFactor = 4
				else:
					iWorldSizeFactor = 7
			else:
				if mc.OldWorldStarts:
					iWorldSizeFactor = 2
				else:
					iWorldSizeFactor = 3
			iWorldSizeFactor *= gc.getMap().getWorldSize()
			'''
			# <advc> Less impact for the Old World Starts option; apart from that, pretty much as above.
			iWorldSizeFactor = math.sqrt(CyMap().getLandPlots()) / 1.67
			if mc.OldWorldStarts:
				iWorldSizeFactor *= 0.78
			# </advc>
			self.iMinIslandSize = 5 + int(round(iWorldSizeFactor))
			iMinRegionSize = self.iMinIslandSize * 4
			for i in range(len(areas)):
				if not isAreaOldWorld[i]:
					continue
				#areas[i].getNumTiles() >= self.iMinIslandSize:
				# advc: This is an AdvCiv DLL function. (Not crucial to call it.)
				if areas[i].getNumHabitableTiles() >= self.iMinIslandSize:
					iRegionSize = 0
					for pI in range(em.length):
						plot = CyMap().plotByIndex(pI)
						if plot.getArea() == areas[i].getID():
							iRegionSize = regionMap.getAreaByID(regionMap.data[pI]).size
							break
					if iRegionSize >= iMinRegionSize:
						startArea = StartingArea(areas[i].getID())
						# <advc>
						if mc.OldWorldStarts:
							print "Appending area of size " + str(areas[i].getNumTiles()) + " to startingAreaList"
						# </advc>
						self.startingAreaList.append(startArea)

			#Get the value of the whole old world
			oldWorldValue = 0
			for i in range(len(self.startingAreaList)):
				oldWorldValue += self.startingAreaList[i].rawValue
			#calulate value per player of old world
			oldWorldValuePerPlayer = oldWorldValue / len(shuffledPlayers)
			#Sort startingAreaList by rawValue
			self.startingAreaList.sort(lambda x, y: cmp(x.rawValue, y.rawValue))
			#Get rid of areas that have less value than oldWorldValuePerPlayer
			#as they are too small to put a player on, however leave at least
			#half as many continents as there are players, just in case the
			#continents are *all* quite small.
			#LM - max(1) is not necessary! Use max(0) in case it's already at or below the minimum number of areas allowed.
			numAreas = max(0, len(self.startingAreaList) - len(shuffledPlayers) / 2)
			for i in range(numAreas):
				if self.startingAreaList[0].rawValue < oldWorldValuePerPlayer:
					del self.startingAreaList[0]
				else:
					break #All remaining should be big enough
			#Recalculate the value of the whole old world
			oldWorldValue = 0
			for i in range(len(self.startingAreaList)):
				oldWorldValue += self.startingAreaList[i].rawValue
			#Recalulate value per player of old world so we are starting more accurately
			oldWorldValuePerPlayer = oldWorldValue / len(shuffledPlayers)
			assert oldWorldValuePerPlayer > 0 # advc
			#Record the ideal number of players for each continent
			for startingArea in self.startingAreaList:
				#LM - Store fractional values for accurate scaling below.
				startingArea.idealNumberOfPlayers = float(startingArea.rawValue) / float(max(1, oldWorldValuePerPlayer))
			#Now we want best first
			self.startingAreaList.reverse()
			print "number of starting areas is %(s)3d" % {"s":len(self.startingAreaList)}
			#LM - This iteration-based while loop is a complete mess. Not only is it slow and inefficient, but it
			#ONLY MODIFIES THE BEST/LARGEST LANDMASS'S PLAYER COUNT, no matter HOW far off it is in either direction!
			#You can EASILY end up with a super-crowded main landmass, or a nearly-deserted one, this way.
			#Player count assignments SHOULD SCALE PROPORTIONATELY!!!
			floatTotal = 0.0
			for startingArea in self.startingAreaList:
				floatTotal += startingArea.idealNumberOfPlayers
			fRatio = float(len(shuffledPlayers)) / floatTotal
			for startingArea in self.startingAreaList:
				startingArea.idealNumberOfPlayers *= fRatio
			#LM - Reallocate players as needed to fix any overloaded landmasses.
			iterations = len(self.startingAreaList)
			bSpaceAvailable = True
			while iterations > 0 and bSpaceAvailable:
				for startingArea in self.startingAreaList:
					difference = startingArea.idealNumberOfPlayers - float(len(startingArea.plotList))
					if difference > 0.0:
						searchTotal = 0.0
						for searchArea in self.startingAreaList:
							if searchArea.idealNumberOfPlayers < float(len(searchArea.plotList)):
								searchTotal += searchArea.idealNumberOfPlayers
						if searchTotal > 0.0:
							startingArea.idealNumberOfPlayers = float(len(startingArea.plotList))
							fRatio = (searchTotal + difference) / searchTotal
							for searchArea in self.startingAreaList:
								if searchArea.idealNumberOfPlayers < float(len(searchArea.plotList)):
									searchArea.idealNumberOfPlayers *= fRatio
						else:
							raise ValueError, "Not enough room on the map to place all players!"
							bSpaceAvailable = False
							break
				iterations -= 1
			#LM - Done with fractional values, finally.
			for startingArea in self.startingAreaList:
				startingArea.idealNumberOfPlayers = int(round(startingArea.idealNumberOfPlayers))
			#LM - Total player allocation should be pretty close to the correct number here. Smooth out any difference that's left.
			idealTotal = 0
			for startingArea in self.startingAreaList:
				idealTotal += startingArea.idealNumberOfPlayers
			if idealTotal < len(shuffledPlayers):
				iNum = len(shuffledPlayers) - idealTotal
				while iNum > 0:
					iEntry = iNum
					for startingArea in self.startingAreaList:
						if startingArea.idealNumberOfPlayers < len(startingArea.plotList):
							startingArea.idealNumberOfPlayers += 1
							iNum -= 1
							if iNum == 0:
								break
					if iNum == iEntry:
						raise ValueError, "Not enough room on the map to place all players!"
						break
			elif idealTotal > len(shuffledPlayers):
				iNum = idealTotal - len(shuffledPlayers)
				while iNum > 0:
					iEntry = iNum
					for startingArea in self.startingAreaList:
						if startingArea.idealNumberOfPlayers > 0:
							startingArea.idealNumberOfPlayers -= 1
							iNum -= 1
							if iNum == 0:
								break
					if iNum == iEntry:
						raise ValueError, "Not enough room on the map to place all players!"
						break
			#Assign players.
			for startingArea in self.startingAreaList:
				for i in range(startingArea.idealNumberOfPlayers):
					startingArea.playerList.append(shuffledPlayers[0])
					del shuffledPlayers[0]
				startingArea.FindStartingPlots()
			if len(shuffledPlayers) > 0:
				raise ValueError, "Some players not placed in starting plot finder!"
			#Now set up for normalization
			''' # advc: AdvCiv DLL handles normalization
			self.plotList = list()
			for startingArea in self.startingAreaList:
				for i in range(len(startingArea.plotList)):
					self.plotList.append(startingArea.plotList[i])
			#Remove bad features. (Jungle in the case of standard game)
			#also ensure minimum hills
			for i in range(len(self.plotList)):
				if not self.plotList[i].vacant:
					self.ensureMinimumHills(self.plotList[i].x, self.plotList[i].y)
			#find the best totalValue
			self.plotList.sort(lambda x, y:cmp(x.totalValue, y.totalValue))
			self.plotList.reverse()
			bestTotalValue = self.plotList[0].totalValue
			for i in range(len(self.plotList)):
				if not self.plotList[i].vacant:
					currentTotalValue = self.plotList[i].totalValue
					percentLacking = 1.0 - (float(currentTotalValue) / float(bestTotalValue))
					if percentLacking > 0:
						bonuses = min(5, int(percentLacking / 0.2))
						self.boostCityPlotValue(self.plotList[i].x, self.plotList[i].y, bonuses, self.plotList[i].isCoast())
			#add bonuses due to player difficulty settings
			self.addHandicapBonus()
			'''
		except Exception, e:
			# advc: Removed "due to a rarely occurring bug" - could be any error, and not necessarily that rare. Added info about the exception. That said, for debugging, it may be better not to catch (and re-raise) the exception here because this obscures the specific origin.
			errorPopUp("PerfectWorld's starting plot finder has failed; this map likely has unfair starting locations. You may wish to quit this game and generate a new map." + "\n\nAn exception of type " + e.__class__.__name__ + " occurred. Arguments:\n" + str(e.args))
			raise Exception, e


	def setupOldWorldAreaList(self):
		if mc.LandmassGenerator == 2:
			em = e2
		else:
			em = e3
		gc = CyGlobalContext()
		#get official areas and make corresponding lists that determines
		#old world vs. new and also the pre-settled value.
		areas = CvMapGeneratorUtil.getAreas()
		# <advc> Do this as late as possible (and don't do it when the Old World Starts option isn't used)
		if mc.OldWorldStarts:
			km.designateNewWorld() # </advc>
		areaOldWorld = list()
		for i in range(len(areas)):
			# <advc>
			if areas[i].isWater():
				areaOldWorld.append(False)
				continue
			if not mc.OldWorldStarts:
				areaOldWorld.append(True)
				continue
			# </advc>
			for pI in range(em.length):
				plot = CyMap().plotByIndex(pI)
				if plot.getArea() == areas[i].getID():
					# advc: Check both area id and region id
					if km.areaMap.data[pI] != km.newWorldAreaID and km.regionMap.data[pI] != km.newWorldRegionID:
						areaOldWorld.append(True)
						#print "Added to Old World: area of size " + str(km.areaMap.getAreaByID(km.areaMap.data[pI]).size) + " in region of size " + str(km.regionMap.getAreaByID(km.regionMap.data[pI]).size)
					else:
						areaOldWorld.append(False)
					break
		return areaOldWorld


	def getCityPotentialValue(self, x, y):
		gc = CyGlobalContext()
		numCityPlots = gc.getNUM_CITY_PLOTS()
		totalValue = 0
		totalFood  = 0
		start = CyMap().plot(x, y)
		if start.isWater():
			return -1, -1
		if start.isImpassable():
			return -1, -1

		#################################################
		## MongooseMod 3.5 BEGIN
		#################################################

		if start.isPeak():
			return -1, -1

		#################################################
		## MongooseMod 3.5 END
		#################################################

		#LM - Block invalid locations!
		terrainInfo = gc.getTerrainInfo(start.getTerrainType())
		if not terrainInfo.isFound() and (not terrainInfo.isFoundCoast() or not start.isCoastalLand()) and (not terrainInfo.isFoundFreshWater() or not start.isFreshWater()):
			return -1, -1
		featureEnum = start.getFeatureType()
		if featureEnum != FeatureTypes.NO_FEATURE:
			featureInfo = gc.getFeatureInfo(featureEnum)
			if featureInfo.isNoCity():
				return -1, -1
		#LM - Also block sucky locations unless there's a good feature present!
		base = terrainInfo.getYield(YieldTypes.YIELD_FOOD) + terrainInfo.getYield(YieldTypes.YIELD_PRODUCTION) + terrainInfo.getYield(YieldTypes.YIELD_COMMERCE)
		if featureEnum != FeatureTypes.NO_FEATURE:
			extra = featureInfo.getYieldChange(YieldTypes.YIELD_FOOD)
		else:
			extra = 0
		if base <= 0 and extra <= 0:
			return -1, -1

		cityPlotList = list()
		#The StartPlot class has a nifty function to determine salt water vs. fresh
		sPlot = StartPlot(x, y, 0)
		#noFoodPlots  = 0
		#lowFoodPlots = 0
		for i in range(numCityPlots):
			plot = plotCity(x, y, i)
			if not plot.isWater() and plot.getArea() != start.getArea():
				food, value = 0, 0
			elif plot.getX() == start.getX() and plot.getY() == start.getY():
				food, value = self.getCityPlotPotentialValueUncached(plot.getX(), plot.getY(), sPlot.isCoast())
			else:
				food, value = self.getPlotPotentialValue(plot.getX(), plot.getY(), sPlot.isCoast())
			totalFood += food
			#if food == 0:
			#	noFoodPlots  += 1
			#elif food == 1:
			#	lowFoodPlots += 1
			cPlot = CityPlot(food, value)
			cityPlotList.append(cPlot)
		#if noFoodPlots > 6 or lowFoodPlots + noFoodPlots > 12:
		#	return totalFood, 0
		usablePlots = totalFood / gc.getFOOD_CONSUMPTION_PER_POPULATION()
		cityPlotList.sort(lambda x, y:cmp(x.value, y.value))
		cityPlotList.reverse()
		#value is obviously limited to available food
		if usablePlots > numCityPlots:
			usablePlots = numCityPlots
		for i in range(usablePlots):
			cPlot = cityPlotList[i]
			totalValue += cPlot.value
		#LM - Removed redundant assignment.
		if sPlot.isCoast():
			totalValue = int(float(totalValue) * mc.CoastalCityValueBonus)
		#LM - Use isRiver, not isRiverSide!
		if start.isRiver():
			totalValue = int(float(totalValue) * mc.RiverCityValueBonus)
		#LM - Add small bonus for hill defense.
		if start.isHills():
			totalValue = int(float(totalValue) * mc.HillCityValueBonus)
		#LM - Add small bonus for starting on bonus.
		bonusEnum = start.getBonusType(TeamTypes.NO_TEAM)
		if bonusEnum != BonusTypes.NO_BONUS:
			bonusInfo = gc.getBonusInfo(bonusEnum)
			if bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_WONDER") or bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_RUSH") or bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_MODERN"):
				totalValue = int(float(totalValue) * mc.StrategicBonusCityValueBonus)
			else:
				totalValue = int(float(totalValue) * mc.OtherBonusCityValueBonus)
		# <advc> Extra avoidance for starts in high latitudes. A cradle of civilization shouldn't be placed in the tundra if it can be helped.
		if start.area().getNumTiles() - start.getLatitude() / 2 < 25 or start.getLatitude() > 60:
			totalValue /= 2 # </advc>
		return totalFood, totalValue


	def getPlotPotentialValue(self, x, y, coastalCity):
		i = GetIndex(x, y)
		#LM - This included an extension of the "ignore lakes" TRAIN WRECK below.
		#CODE ERASED.
		if coastalCity:
			value = self.coastalValueList[i]
			food  = self.coastalFoodList[i]
		else:
			value = self.inlandValueList[i]
			food  = self.inlandFoodList[i]
		return food, value


	def getPlotPotentialValueUncached(self, x, y, coastalCity):
		plot = CyMap().plot(x, y)
		sPlot = StartPlot(x, y, 0)
		gc = CyGlobalContext()
		#LM - Store highest era allowed for any of these things.
		if gc.getGame().getStartEra() < 5:
			eraLimit = 6
		else:
			eraLimit = 7
		#LM - Store most advanced route type that can be built within the allowed Era range.
		maxRoute = -1
		for n in range(gc.getNumRouteInfos()):
			for i in range(gc.getNumBuildInfos()):
				buildInfo = gc.getBuildInfo(i)
				if buildInfo.getRoute() == n:
					if buildInfo.getTechPrereq() == TechTypes.NO_TECH or gc.getTechInfo(buildInfo.getTechPrereq()).getEra() <= eraLimit:
						maxRoute = n
					break

		terrainEnum = plot.getTerrainType()
		terrainInfo = gc.getTerrainInfo(terrainEnum)
		featureEnum = plot.getFeatureType()
		featureInfo = gc.getFeatureInfo(featureEnum)

		#Get best bonus improvement score. Test tachnology era of bonus first, then test each improvement
		food       = plot.calculateBestNatureYield(YieldTypes.YIELD_FOOD,       TeamTypes.NO_TEAM)
		production = plot.calculateBestNatureYield(YieldTypes.YIELD_PRODUCTION, TeamTypes.NO_TEAM)
		commerce   = plot.calculateBestNatureYield(YieldTypes.YIELD_COMMERCE,   TeamTypes.NO_TEAM)
		#LM - Handle Plains-Floodplains (since it's a special case).
		#LM - Assume Lighthouse (since it's always one of the very first things a coastal city builds), and add in the VITAL extra food point from it.
		#But remember it doesn't apply on Sea Ice!
		if plot.isWater() and coastalCity and not plot.isImpassable():
			food += 1

		bonusEnum = plot.getBonusType(TeamTypes.NO_TEAM)
		bonusFood       = 0
		bonusProduction = 0
		bonusCommerce   = 0
		if bonusEnum != BonusTypes.NO_BONUS:
			bonusInfo = gc.getBonusInfo(bonusEnum)
			if bonusInfo.getTechReveal() == TechTypes.NO_TECH or gc.getTechInfo(bonusInfo.getTechReveal()).getEra() <= gc.getGame().getStartEra() + 1:
				food       += bonusInfo.getYieldChange(YieldTypes.YIELD_FOOD)
				production += bonusInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   += bonusInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)
			elif gc.getTechInfo(bonusInfo.getTechReveal()).getEra() <= eraLimit:
				bonusFood       += bonusInfo.getYieldChange(YieldTypes.YIELD_FOOD)
				bonusProduction += bonusInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
				bonusCommerce   += bonusInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)
			else:
				bonusEnum = BonusTypes.NO_BONUS

		improvementList = list()
		for n in range(gc.getNumBuildInfos()):
			#Test for improvement validity
			buildInfo = gc.getBuildInfo(n)
			impEnum = buildInfo.getImprovement()
			if impEnum == ImprovementTypes.NO_IMPROVEMENT:
				continue
			impInfo = gc.getImprovementInfo(impEnum)
			while impInfo.getImprovementUpgrade() != ImprovementTypes.NO_IMPROVEMENT:
				impEnum = impInfo.getImprovementUpgrade()
				impInfo = gc.getImprovementInfo(impEnum)

			#some mods use improvements for other things, so if there's no tech requirement we still don't want it factored in.
			if buildInfo.getTechPrereq() == TechTypes.NO_TECH or gc.getTechInfo(buildInfo.getTechPrereq()).getEra() > eraLimit:
				continue
			#LM - I'm not even going to block water tile improvements for non-coastal cities, b/c even if a player both DOESN'T have, and will NEVER have,
			#Workboat access to a non-coastal city's water tiles (VERY unlikely - start a war to get there if necessary!), we don't block land tiles that
			#are across a channel and might ultimately end up under enemy control... Plus an ally may come along and place Fishing Nets for him anyway.
			if plot.canHaveImprovement(impEnum, TeamTypes.NO_TEAM, True):
				impFood       = plot.calculateImprovementYieldChange(impEnum, YieldTypes.YIELD_FOOD,       PlayerTypes.NO_PLAYER, False)
				impProduction = plot.calculateImprovementYieldChange(impEnum, YieldTypes.YIELD_PRODUCTION, PlayerTypes.NO_PLAYER, False)
				impCommerce   = plot.calculateImprovementYieldChange(impEnum, YieldTypes.YIELD_COMMERCE,   PlayerTypes.NO_PLAYER, False)
				#That function will not find bonus yield changes for NO_PLAYER, much to my annoyance
				if bonusEnum != BonusTypes.NO_BONUS:
					impFood       += impInfo.getImprovementBonusYield(bonusEnum, YieldTypes.YIELD_FOOD)
					impProduction += impInfo.getImprovementBonusYield(bonusEnum, YieldTypes.YIELD_PRODUCTION)
					impCommerce   += impInfo.getImprovementBonusYield(bonusEnum, YieldTypes.YIELD_COMMERCE)
				#LM - Assume irrigation (since it's very easy to get everywhere once you have Civil Service), and add in any extra yields from it.
				#(bOptimal is false, so calculateImprovementYieldChange() didn't add anything.)
				impFood       += impInfo.getIrrigatedYieldChange(YieldTypes.YIELD_FOOD)
				impProduction += impInfo.getIrrigatedYieldChange(YieldTypes.YIELD_PRODUCTION)
				impCommerce   += impInfo.getIrrigatedYieldChange(YieldTypes.YIELD_COMMERCE)
				#LM - Add in extra yields from the most advanced route type that is unlocked up through the Era limit.
				#(bOptimal is false and these plots don't have any routes already on them, so calculateImprovementYieldChange() didn't add anything.)
				if maxRoute >= 0:
					impFood       += impInfo.getRouteYieldChanges(maxRoute, YieldTypes.YIELD_FOOD)
					impProduction += impInfo.getRouteYieldChanges(maxRoute, YieldTypes.YIELD_PRODUCTION)
					impCommerce   += impInfo.getRouteYieldChanges(maxRoute, YieldTypes.YIELD_COMMERCE)
				#LM - Undo later tech modifiers, and ALL civic modifiers, to the improvement, since calculateImprovementYieldChange()
				#adds them in when called with NO_PLAYER, regardless of the bOptimal parameter.
				for i in range(gc.getNumTechInfos()):
					if gc.getTechInfo(i).getEra() > eraLimit:
						impFood       -= impInfo.getTechYieldChanges(i, YieldTypes.YIELD_FOOD)
						impProduction -= impInfo.getTechYieldChanges(i, YieldTypes.YIELD_PRODUCTION)
						impCommerce   -= impInfo.getTechYieldChanges(i, YieldTypes.YIELD_COMMERCE)
				for i in range(gc.getNumCivicInfos()):
					civicInfo = gc.getCivicInfo(i)
					impFood       -= civicInfo.getImprovementYieldChanges(impEnum, YieldTypes.YIELD_FOOD)
					impProduction -= civicInfo.getImprovementYieldChanges(impEnum, YieldTypes.YIELD_PRODUCTION)
					impCommerce   -= civicInfo.getImprovementYieldChanges(impEnum, YieldTypes.YIELD_COMMERCE)
				#See if feature is removed, if so we must subtract the added yield from that feature
				bProceed = True
				if featureEnum != FeatureTypes.NO_FEATURE and buildInfo.isFeatureRemove(featureEnum):
					if buildInfo.getFeatureTech(featureEnum) == TechTypes.NO_TECH or gc.getTechInfo(buildInfo.getFeatureTech(featureEnum)).getEra() <= gc.getGame().getStartEra() + 2:
						#LM - Ceph's code was subtracting out the feature's extra river and hill yields EVEN IF THERE WAS NO RIVER OR HILL ON THE PLOT!!!
						#It was ALSO not restoring the TERRAIN'S extra river and hill yields afterward, which are used when no feature is present.
						#Wow, so many major bugs in this function...
						impFood       -= featureInfo.getYieldChange(YieldTypes.YIELD_FOOD)
						impProduction -= featureInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
						impCommerce   -= featureInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)
						if plot.isRiver():
							impFood       -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_FOOD)
							impProduction -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_PRODUCTION)
							impCommerce   -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_COMMERCE)
							impFood       += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_FOOD)
							impProduction += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_PRODUCTION)
							impCommerce   += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_COMMERCE)
						if plot.isHills():
							impFood       -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_FOOD)
							impProduction -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_PRODUCTION)
							impCommerce   -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_COMMERCE)
							impFood       += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_FOOD)
							impProduction += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_PRODUCTION)
							impCommerce   += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_COMMERCE)
					else:
						bProceed = False
				if bProceed:
					imp = Improvement(impEnum, impFood, impProduction, impCommerce, 0)
					improvementList.append(imp)
		for i in range(len(improvementList)):
			impFood       = improvementList[i].food       + food       + bonusFood
			impProduction = improvementList[i].production + production + bonusProduction
			impCommerce   = improvementList[i].commerce   + commerce   + bonusCommerce
			impValue = (impFood * mc.FoodValue) + (impProduction * mc.ProductionValue) + (impCommerce * mc.CommerceValue)
			#LM - Encourage Floodplains, Oases and early food resources here to differentiate them from tile improvements that add food!
			if food >= 3:
				impValue *= 2
			#LM - Encourage Forest-Plains-Hills and early production resources here to differentiate them from tile improvements that add production!
			if production >= 3:
				impValue *= 2
			#LM - Encourage Oases and early commerce resources here to differentiate them from tile improvements that add commerce!
			if commerce >= 3:
				impValue *= 2
			#LM - Discourage coastal water when dealing with a non-coastal city, BUT LEAVE LAKES ALONE!!!
			if not coastalCity and sPlot.isCoast():
				impValue /= 2
			#LM - Add small value for improvements with coughup chances.
			impInfo = gc.getImprovementInfo(improvementList[i].e)
			for n in range(gc.getNumBonusInfos()):
				if impInfo.getImprovementBonusDiscoverRand(n) > 0:
					impValue += (mc.ProductionValue / 2) + (mc.CommerceValue / 2)
					break
			#Food surplus makes the square much more valuable than if there is no food here.
			#LM - Another CRITICAL BUGFIX!!! This code was using "food", which is the base yield of the tile, rather than "impFood", which is the final value that actually MATTERS.
			#Since "food" is a constant from outside this loop, the result was value multiplication being always applied or never applied, regardless of the improvement under consideration.
			if impFood > gc.getFOOD_CONSUMPTION_PER_POPULATION():
				impValue *= 3
			elif impFood == gc.getFOOD_CONSUMPTION_PER_POPULATION():
				impValue *= 2
			#LM - "Commerce / 2" is my standard rule for yield balance
			elif impFood + impProduction + (impCommerce / 2) < 3:
				impValue = 0
			improvementList[i].value = impValue
		if len(improvementList) > 0:
			#sort all allowed improvement values to find the best
			improvementList.sort(lambda x, y:cmp(x.value, y.value))
			improvementList.reverse()
			bestImp = improvementList[0]
			#LM - And yet ANOTHER huge bug... I've lost count, lol. This code was ADDING bestImp's yields to the base yields, but bestImp already INCLUDED the base yields!!!
			#The result was a VERY messed up final value calculation below. None of this is necessary at all though; since the calculation is the same, just use bestImp's values directly.
			return bestImp.food, bestImp.value

		#Try to avoid included water food resources for non-coastal starts. It confuses the AI.
		#LM - Yeah, umm, WRONG! This is a TRAIN WRECK!!! It completely blocks lakes which have HUGE base values, and even then, coastal tiles can
		#be useful to non-coastal cities even WITHOUT any tile improvements or coastal buildings, especially with features or resources present.
		#CODE ERASED.

		#LM - Now we have to support the case where no valid improvements were found (even though it'll probably never happen, sigh).
		value = ((food + bonusFood) * mc.FoodValue) + ((production + bonusProduction) * mc.ProductionValue) + ((commerce + bonusCommerce) * mc.CommerceValue)
		if food >= 3:
			value *= 2
		if production >= 3:
			value *= 2
		if commerce >= 3:
			value *= 2
		if not coastalCity and sPlot.isCoast():
			value /= 2
		food += bonusFood
		if food > gc.getFOOD_CONSUMPTION_PER_POPULATION():
			value *= 3
		elif food == gc.getFOOD_CONSUMPTION_PER_POPULATION():
			value *= 2
		elif food + (production + bonusProduction) + ((commerce + bonusCommerce) / 2) < 3:
			#value = 0
			value = max(0, value) # advc (from Civ 4 Reimagined)
		return food, value


	#LM - We need a whole new version of the function specifically for city plots, because they have different rules for calculating yields (and no tile improvements either).
	def getCityPlotPotentialValueUncached(self, x, y, coastalCity):
		plot = CyMap().plot(x, y)
		gc = CyGlobalContext()
		if gc.getGame().getStartEra() < 5:
			eraLimit = 6
		else:
			eraLimit = 7

		terrainEnum = plot.getTerrainType()
		terrainInfo = gc.getTerrainInfo(terrainEnum)
		featureEnum = plot.getFeatureType()
		featureInfo = gc.getFeatureInfo(featureEnum)
		bonusEnum   = plot.getBonusType(TeamTypes.NO_TEAM)
		bonusInfo   = gc.getBonusInfo(bonusEnum)

		#LM - Get base value, then subtract out ALL feature and resource effects.
		food       = plot.calculateBestNatureYield(YieldTypes.YIELD_FOOD,       TeamTypes.NO_TEAM)
		production = plot.calculateBestNatureYield(YieldTypes.YIELD_PRODUCTION, TeamTypes.NO_TEAM)
		commerce   = plot.calculateBestNatureYield(YieldTypes.YIELD_COMMERCE,   TeamTypes.NO_TEAM)
		bonusFood       = 0
		bonusProduction = 0
		bonusCommerce   = 0
		if featureEnum != FeatureTypes.NO_FEATURE:
			food       -= featureInfo.getYieldChange(YieldTypes.YIELD_FOOD)
			production -= featureInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
			commerce   -= featureInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)
			if plot.isRiver():
				food       -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_FOOD)
				production -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   -= featureInfo.getRiverYieldChange(YieldTypes.YIELD_COMMERCE)
				food       += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_FOOD)
				production += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   += terrainInfo.getRiverYieldChange(YieldTypes.YIELD_COMMERCE)
			if plot.isHills():
				food       -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_FOOD)
				production -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   -= featureInfo.getHillsYieldChange(YieldTypes.YIELD_COMMERCE)
				food       += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_FOOD)
				production += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   += terrainInfo.getHillsYieldChange(YieldTypes.YIELD_COMMERCE)
		if bonusEnum != BonusTypes.NO_BONUS:
			food       -= bonusInfo.getYieldChange(YieldTypes.YIELD_FOOD)
			production -= bonusInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
			commerce   -= bonusInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)

		#LM - Apply city minimum effects, then add permanent features and visible resources back in on top.
		food       = max(food,       gc.getYieldInfo(YieldTypes.YIELD_FOOD).getMinCity())
		production = max(production, gc.getYieldInfo(YieldTypes.YIELD_PRODUCTION).getMinCity())
		commerce   += gc.getYieldInfo(YieldTypes.YIELD_COMMERCE).getMinCity()
		if bonusEnum != BonusTypes.NO_BONUS:
			if bonusInfo.getTechReveal() == TechTypes.NO_TECH or gc.getTechInfo(bonusInfo.getTechReveal()).getEra() <= gc.getGame().getStartEra() + 1:
				food       += bonusInfo.getYieldChange(YieldTypes.YIELD_FOOD)
				production += bonusInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
				commerce   += bonusInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)
			elif gc.getTechInfo(bonusInfo.getTechReveal()).getEra() <= eraLimit:
				bonusFood       += bonusInfo.getYieldChange(YieldTypes.YIELD_FOOD)
				bonusProduction += bonusInfo.getYieldChange(YieldTypes.YIELD_PRODUCTION)
				bonusCommerce   += bonusInfo.getYieldChange(YieldTypes.YIELD_COMMERCE)

		#LM - Now calculate tile value the same way as in getPlotPotentialValueUncached().
		value = ((food + bonusFood) * mc.FoodValue) + ((production + bonusProduction) * mc.ProductionValue) + ((commerce + bonusCommerce) * mc.CommerceValue)
		if food >= 3:
			value *= 2
		if production >= 3:
			value *= 2
		if commerce >= 3:
			value *= 2
		food += bonusFood
		if food > gc.getFOOD_CONSUMPTION_PER_POPULATION():
			value *= 3
		elif food == gc.getFOOD_CONSUMPTION_PER_POPULATION():
			value *= 2
		elif food + (production + bonusProduction) + ((commerce + bonusCommerce) / 2) < 3:
			value = 0
		return food, value


	def boostCityPlotValue(self, x, y, bonuses, isCoastalCity):
		mapGen = CyMapGenerator()
		food, value = self.getCityPotentialValue(x, y)
		gc = CyGlobalContext()
		numCityPlots = gc.getNUM_CITY_PLOTS()
		#Shuffle the bonus order so that different cities have different preferences for bonuses
		bonusList = list()
		numBonuses = gc.getNumBonusInfos()
		for i in range(numBonuses):
			bonusList.append(i)
		shuffledBonuses = list()
		for i in range(numBonuses):
			n = PRand.randint(0, len(bonusList) - 1)
			shuffledBonuses.append(bonusList[n])
			del bonusList[n]
		if len(shuffledBonuses) != numBonuses:
			raise ValueError, "Bad bonus shuffle. Learn 2 shuffle."
		bonusCount = 0
		#Do this process in 3 passes for each yield type
		yields = []
		yields.append(YieldTypes.YIELD_PRODUCTION)
		yields.append(YieldTypes.YIELD_COMMERCE)
		yields.append(YieldTypes.YIELD_FOOD)
		#NEW CODE - Fuyu
		allowBonusWonderClass = (PRand.random() < mc.allowWonderBonusChance)
		plotList = []
		for i in range(numCityPlots):
			plotList.append(plotCity(x, y, i))
		plotList = ShuffleList(plotList)
		for n in range(len(yields) * bonuses + 1):
			for plot in plotList:
				#NEW CODE - LM
				if bonusCount >= bonuses:
					return
				if plot.getX() == x and plot.getY() == y:
					continue
				if plot.isWater() and not isCoastalCity:
					continue
				if not plot.isWater() and CyMap().plot(x, y).getArea() != plot.getArea():
					continue
				if plot.getBonusType(TeamTypes.NO_TEAM) != BonusTypes.NO_BONUS:
					continue
				food, value = self.getCityPotentialValue(x, y)
				#NEW CODE - Fuyu
				currentYield = yields[(n + bonusCount) % (len(yields))]
				#switch to food if food is needed
				usablePlots = food / gc.getFOOD_CONSUMPTION_PER_POPULATION()
				if usablePlots <= numCityPlots / 2:
					currentYield = YieldTypes.YIELD_FOOD
				#temporarily remove any feature
				featureEnum = plot.getFeatureType()
				if featureEnum != FeatureTypes.NO_FEATURE:
					featureVariety = plot.getFeatureVariety()
					plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
				for b in range(numBonuses):
					bonusEnum = shuffledBonuses[b]
					bonusInfo = gc.getBonusInfo(bonusEnum)
					if not bonusInfo.isNormalize():
						continue
					if bonusInfo.getYieldChange(currentYield) < 1:
						continue
					#NEW CODE - Fuyu/LM
					if bonusInfo.getTechReveal() != TechTypes.NO_TECH and gc.getTechInfo(bonusInfo.getTechReveal()).getEra() > gc.getGame().getStartEra() + 1:
						continue
					if not bp.PlotCanHaveBonus(plot, bonusEnum, False, False):
						if not PRand.random() < mc.ignoreAreaRestrictionChance:
							continue
						if not bp.PlotCanHaveBonus(plot, bonusEnum, False, True):
							continue
					if bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_WONDER") or bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_RUSH") or bonusInfo.getBonusClassType() == gc.getInfoTypeForString("BONUSCLASS_MODERN"):
						if not allowBonusWonderClass:
							continue
						else:
							allowBonusWonderClass = False
					plot.setBonusType(bonusEnum)
					bonusCount += 1
					break
				#restore the feature if possible
				if featureEnum != FeatureTypes.NO_FEATURE:
					bonusInfo = gc.getBonusInfo(plot.getBonusType(TeamTypes.NO_TEAM))
					if bonusInfo == None or bonusInfo.isFeature(featureEnum):
						plot.setFeatureType(featureEnum, featureVariety)


	def ensureMinimumHills(self, x, y):
		gc = CyGlobalContext()
		hillsFound = 0
		peaksFound = 0
		badFeaturesFound = 0
		plotList = []
		for i in range(gc.getNUM_CITY_PLOTS()):
			plot = plotCity(x, y, i)
			featureInfo = gc.getFeatureInfo(plot.getFeatureType())
			if plot.getX() == x and plot.getY() == y:
				#remove bad feature on start but don't count it.
				if featureInfo != None:
					totalYield = 0
					for yi in range(YieldTypes.NUM_YIELD_TYPES):
						totalYield += featureInfo.getYieldChange(YieldTypes(yi))
					if totalYield <= 0:#bad feature
						plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
				continue
			if plot.getPlotType() == PlotTypes.PLOT_HILLS and CyMap().plot(x, y).getArea() == plot.getArea():
				hillsFound += 1
			if plot.getPlotType() == PlotTypes.PLOT_PEAK:
				peaksFound += 1
			if featureInfo != None:
				#now count the bad features
				totalYield = 0
				for yi in range(YieldTypes.NUM_YIELD_TYPES):
					totalYield += featureInfo.getYieldChange(YieldTypes(yi))
				if totalYield <= 0:#bad feature
					badFeaturesFound += 1
			if plot.isWater():
				continue
			if plot.getBonusType(TeamTypes.NO_TEAM) != BonusTypes.NO_BONUS:
				continue
			plotList.append(plot)
		plotList = ShuffleList(plotList)
		#ensure maximum number of peaks
		if peaksFound > mc.MaxPeaksInFC:
			for plot in plotList:
				if peaksFound == mc.MaxPeaksInFC:
					break
				if plot.getPlotType() == PlotTypes.PLOT_PEAK:
					plot.setPlotType(PlotTypes.PLOT_HILLS, True, True)
					if plot.getArea() == CyMap().plot(x, y).getArea():
						hillsFound += 1
					peaksFound -= 1
		#Ensure minimum number of hills
		hillsNeeded = mc.MinHillsInFC - hillsFound
		if hillsNeeded > 0:
			for plot in plotList:
				if hillsNeeded <= 0:
					break
				featureInfo = gc.getFeatureInfo(plot.getFeatureType())
				requiresFlatlands = (featureInfo != None and featureInfo.isRequiresFlatlands())
				bonusInfo = gc.getBonusInfo(plot.getBonusType(TeamTypes.NO_TEAM))
				if plot.getPlotType() != PlotTypes.PLOT_HILLS and plot.getArea() == CyMap().plot(x, y).getArea() and bonusInfo == None and not requiresFlatlands:
					plot.setPlotType(PlotTypes.PLOT_HILLS, True, True)
					hillsNeeded -= 1
			if hillsNeeded > 0:
				for plot in plotList:
					if plot.getPlotType() != PlotTypes.PLOT_HILLS and plot.getArea() == CyMap().plot(x, y).getArea():
						#if bonusInfo == None or not bonusInfo.isRequiresFlatlands():
						# advc.001: That function doesn't exist in the original BtS DLL. It might exist in MongooseMod, but, in the v3.2 standalone version, this was definitely a bug. Use isHills instead (like in the DLL).
						if bonusInfo is None or bonusInfo.isHills():
							plot.setPlotType(PlotTypes.PLOT_HILLS, True, True)
							hillsNeeded -= 1
							if requiresFlatlands:
								plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
		#ensure maximum number of bad features
		badFeaturesToRemove = badFeaturesFound - mc.MaxBadFeaturesInFC
		if badFeaturesToRemove > 0:
			#remove half from flatlands, the rest from hills
			badFeaturesToRemoveFromFlatlands = badFeaturesToRemove / 2 + badFeaturesToRemove % 2
			badFeaturesToRemove -= badFeaturesToRemoveFromFlatlands
			for plot in plotList:
				if badFeaturesToRemoveFromFlatlands <= 0 and badFeaturesToRemove <= 0:
					break
				featureEnum = plot.getFeatureType()
				featureInfo = gc.getFeatureInfo(featureEnum)
				bonusEnum = plot.getBonusType(TeamTypes.NO_TEAM)
				if featureInfo != None:
					totalYield = 0
					for yi in range(YieldTypes.NUM_YIELD_TYPES):
						totalYield += featureInfo.getYieldChange(YieldTypes(yi))
					if totalYield <= 0:#bad feature
						if plot.getPlotType() == PlotTypes.PLOT_LAND and badFeaturesToRemoveFromFlatlands > 0:
							badFeaturesToRemoveFromFlatlands -= 1
						if plot.getPlotType() == PlotTypes.PLOT_HILLS and badFeaturesToRemove > 0:
							badFeaturesToRemove -= 1
						plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)
						if (bonusEnum != BonusTypes.NO_BONUS and not bp.PlotCanHaveBonus(plot, bonusEnum, True, True)):
							badFeaturesToRemove += 1
							plot.setFeatureType(featureEnum, -1)
			#if there are not enough hills or flatlands, there will be leftovers
			badFeaturesToRemove += badFeaturesToRemoveFromFlatlands
			for plot in plotList:
				if badFeaturesToRemove <= 0:
					break
				featureInfo = gc.getFeatureInfo(plot.getFeatureType())
				if featureInfo != None:
					totalYield = 0
					for yi in range(YieldTypes.NUM_YIELD_TYPES):
						totalYield += featureInfo.getYieldChange(YieldTypes(yi))
					if totalYield <= 0:#bad feature
						badFeaturesToRemove -= 1
						plot.setFeatureType(FeatureTypes.NO_FEATURE, -1)


	def addHandicapBonus(self):
		gc = CyGlobalContext()
		for ePlayer in range(gc.getMAX_CIV_PLAYERS()):
			player = gc.getPlayer(ePlayer)
			if player.isEverAlive() and player.isHuman():
				eHandicap = player.getHandicapType()
				startPlot = player.getStartingPlot()
				sPlot = StartPlot(startPlot.getX(),startPlot.getY(), 0)
				if eHandicap == gc.getInfoTypeForString("HANDICAP_SETTLER"):
					if mc.SettlerBonus > 0:
						print "Human player at Settler difficulty, adding %d resources" % mc.SettlerBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.SettlerBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_CHIEFTAIN"):
					if mc.ChieftainBonus > 0:
						print "Human player at Chieftain difficulty, adding %d resources" % mc.ChieftainBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.ChieftainBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_WARLORD"):
					if mc.WarlordBonus > 0:
						print "Human player at Warlord difficulty, adding %d resources" % mc.WarlordBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.WarlordBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_NOBLE"):
					if mc.NobleBonus > 0:
						print "Human player at Noble difficulty, adding %d resources" % mc.NobleBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.NobleBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_PRINCE"):
					if mc.PrinceBonus > 0:
						print "Human player at Prince difficulty, adding %d resources" % mc.PrinceBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.PrinceBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_MONARCH"):
					if mc.MonarchBonus > 0:
						print "Human player at Monarch difficulty, adding %d resources" % mc.MonarchBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.MonarchBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_EMPEROR"):
					if mc.EmperorBonus > 0:
						print "Human player at Emperor difficulty, adding %d resources" % mc.EmperorBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.EmperorBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_IMMORTAL"):
					if mc.ImmortalBonus > 0:
						print "Human player at Immortal difficulty, adding %d resources" % mc.ImmortalBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.ImmortalBonus, sPlot.isCoast())
				elif eHandicap == gc.getInfoTypeForString("HANDICAP_DEITY"):
					if mc.DeityBonus > 0:
						print "Human player at Deity Difficulty, adding %d resources" % mc.DeityBonus
						self.boostCityPlotValue(startPlot.getX(), startPlot.getY(), mc.DeityBonus, sPlot.isCoast())


class CityPlot:
	def __init__(self, food, value):
		self.food  = food
		self.value = value


class Improvement:
	def __init__(self, e, food, production, commerce, value):
		self.e = e
		self.food       = food
		self.production = production
		self.commerce   = commerce
		self.value      = value


class StartingArea:
	def __init__(self, areaID):
		self.areaID = areaID
		self.plotList   = list()
		self.playerList = list()
		self.distanceTable = array('i')
		self.distTableOtherAreas = array('i') # advc
		self.rawValue = 0
		self.CalculatePlotList()
		self.idealNumberOfPlayers = 0


	def CalculatePlotList(self):
		gc = CyGlobalContext()
		for y in range(mc.height):
			for x in range(mc.width):
				plot = CyMap().plot(x, y)
				if plot.getArea() == self.areaID:
					food, value = sf.getCityPotentialValue(x, y)
					#don't place a city on top of a bonus
					#LM - Why completely rule out great tiles that could possibly be the only valid locations in their areas?!
					#I actually recommend a small BONUS to the value (no pun intended, lol), due to the protection from pillaging it affords.
					#This is not the right place to apply it, though!
					if plot.getBonusType(TeamTypes.NO_TEAM) != BonusTypes.NO_BONUS:
						continue

					#LM - Prevent starting locations from being walled-off in small pockets.
					# advc.030: No need; in AdvCiv, peaks always separate areas.
					'''
					# advc.001: Map unavailable in later eras (I think)
					if gc.getGame().getStartEra() < 3 and sf.peakMap.getAreaByID(sf.peakMap.data[GetIndex(x, y)]).size < sf.iMinIslandSize:
						value = 0
					'''
					#LM - Invalid locations are given a value of -1, which is blocked. Highly undesirable but technically valid locations are given a value of 0
					#which is also blocked, with any landmass overflows now handled above. I've left the values separate anyway though, in case they're ever used.
					if value > 0:
						startPlot = StartPlot(x, y, value)
						if plot.isWater():
							raise ValueError, "potential start plot is water!"
						self.plotList.append(startPlot)
		# <advc> Want to be able to divide by this length
		if len(self.plotList) <= 0:
			return # </advc>
		#Sort plots by local value
		self.plotList.sort(lambda x, y: cmp(x.localValue, y.localValue))
		#To save time and space let's get rid of some of the lesser plots
		#LM - Let's not. (You run a high risk of eliminating perfectly good low-value plots that are the only places to put cities in certain areas.)
		#LM - Hmm, apparently this is really important for masking out sucky regions. Instead or removing it, let's increase the cull percent from 2/3 to 3/4! ;)
		#cull = (len(self.plotList) * 3) / 4
		# <advc> Cull fewer tiles b/c start plots are getting placed too close to each other. If too few are culled, however, civs start in the middle of a continent too rarely.
		newWorldSubtr = 0
		# The more crowded the map, the fewer the tiles we can afford to rule out.
		if mc.OldWorldStarts:
			newWorldSubtr = 1
		civs = max(1, gc.getGame().countCivPlayersEverAlive())
		seaLevelAdj = (mc.SeaLevelFactor - 1) * 1.33
		cull = min(int(round(0.7 * len(self.plotList))), max(0, int(round(len(self.plotList) * (0.22  + (CyMap().getWorldSize() - newWorldSubtr + seaLevelAdj) / (2.0 * civs))))))
		print("cull ratio: %d percent of %d sites" % (int(100*cull/len(self.plotList)),len(self.plotList)))
		# </advc>
		for i in range(cull):
			del self.plotList[0]
		#You now should be able to eliminate more plots by sorting high to low and
		#having the best plot eat plots within 3 squares, then same for next, etc.
		self.plotList.reverse()
		# advc: Moved into subroutine
		self.ClearVicinity(3)
		print "Number of final plots in areaID = %(a)3d is %(p)5d" % {"a":self.areaID, "p":len(self.plotList)}
		# advc.021b: Moved up:
		for n in range(len(self.plotList)):
			self.rawValue += self.plotList[n].localValue
		# Moved the last third of this function's body into a new function FillDistanceTable

	# advc: Mostly cut from CalculatePlotList. Assumes that plotList is sorted by localValue in descending order
	def ClearVicinity(self, radius):
		numPlots = len(self.plotList)
		# <advc>
		protectedPlots = max(2, (1 + radius/10.0) * len(self.playerList))
		if numPlots <= protectedPlots:
			return # </advc>
		for n in range(numPlots):
			#At some point the length of plot list will be much shorter than at
			#the beginning of the loop, so it can never end normally
			if n >= len(self.plotList) - 1:
				break
			x = self.plotList[n].x
			y = self.plotList[n].y
			for yy in range(y - radius, y + radius + 1):
				for xx in range(x - radius, x + radius + 1):
					#LM - Easier to avoid the self-evaluation case here than down below.
					if xx == x and yy == y:
						continue
					# <advc> Clear a circular range, not square. That's better than LM's tweak below.
					if plotDistance(x, y, xx, yy) > radius:
						continue # </advc>
					#LM - Don't eat the outside corners! Cities there actually have less overlap (2) than the ones 4 tiles away in a cardinal line (3).
					#if abs(xx - x) == radius and abs(yy - y) == radius:
					#	continue
					#LM - Obey the mapscript wrap globals, don't ignore them!!!
					if mc.WrapX:
						xx = xx % mc.width
					elif xx < 0 or xx >= mc.width:
						continue
					if mc.WrapY:
						yy = yy % mc.height
					elif yy < 0 or yy >= mc.height:
						continue
					#LM - Search from n + 1, rather than n, to save time.
					for m in range(n + 1, len(self.plotList)):
						#LM - Just break when you find the target entry, it's a lot faster! Sheesh...
						if self.plotList[m].x == xx and self.plotList[m].y == yy:
							del self.plotList[m]
							break
					# <advc> Don't eliminate all our choices
					if len(self.plotList) <= protectedPlots:
						break
				if len(self.plotList) <= protectedPlots:
					break
			if len(self.plotList) <= protectedPlots:
				break
		print("%d/%d sites eliminated at dist=%d" % (numPlots-len(self.plotList),numPlots,radius))
		# </advc>


	# advc: Cut from CalculatePlotList
	def FillDistanceTable(self):
		gc = CyGlobalContext()
		#At this point we should have a list of the very best places
		#to build cities on this continent. Now we need a table with
		#the distance from each city to every other city
		#Create distance table
		for i in range(len(self.plotList) * len(self.plotList)):
			self.distanceTable.append(-1) #LM - I think he meant -1 instead of -11, lol :)
		# <advc>
		assignedStartingPlots = list()
		for i in range(gc.getGame().countCivPlayersEverAlive()):
			player = gc.getPlayer(i)
			startingPlot = player.getStartingPlot()
			if startingPlot and startingPlot.getX() >= 0 and startingPlot.getY() >= 0:
				assignedStartingPlots.append(startingPlot)
		for i in range(len(self.plotList) * len(assignedStartingPlots)):
			self.distTableOtherAreas.append(-1)
		bSingleCiv = (len(self.playerList) == 1)
		if bSingleCiv:
			print("Only one civ to be placed; ignoring distances within area")
		mmap = CyMap()
		# </advc>
		#Fill distance table
		for n in range(len(self.plotList)):
			#While were already looping lets calculate the raw value
			# advc: Moved up so that it remains in CalculatePlotList
			#self.rawValue += self.plotList[n].localValue
			avgDistance = 0
			for m in range(n, len(self.plotList)):
				nPlot = mmap.plot(self.plotList[n].x, self.plotList[n].y)
				mPlot = mmap.plot(self.plotList[m].x, self.plotList[m].y)
				mmap.resetPathDistance()
				distance = mmap.calculatePathDistance(nPlot, mPlot)
				#If path fails try reversing it
				self.distanceTable[n * len(self.plotList) + m] = distance
				self.distanceTable[m * len(self.plotList) + n] = distance
				if not bSingleCiv: # advc
					avgDistance += distance
			# <advc>
			for m in range(len(assignedStartingPlots)):
				nPlot = mmap.plot(self.plotList[n].x, self.plotList[n].y)
				mPlot = mmap.plot(assignedStartingPlots[m].getX(), assignedStartingPlots[m].getY())
				distance = plotDistance(nPlot.getX(), nPlot.getY(), mPlot.getX(), mPlot.getY())
				# Cap; don't need distance to be maximized, just large enough.
				if distance >= 13:
					distance = min(distance, 13)
				else:
					print("Start at %d/%d discouraged b/c too close to %d/%d; %d alternatives in plot list" % (nPlot.getX(),nPlot.getY(), mPlot.getX(),mPlot.getY(), len(self.plotList)-1))
				# To account for area boundary
				distance *= 2
				distance += 5
				self.distTableOtherAreas[m * len(self.plotList) + n] = distance
				avgDistance += distance
			# </advc>
			self.plotList[n].avgDistance = avgDistance


	def FindStartingPlots(self):
		gc = CyGlobalContext()
		numPlayers = len(self.playerList)
		if numPlayers <= 0:
			return
		# <advc> Eliminate sites in a range that increases successively
		for radius in range(4, 11):
			self.ClearVicinity(radius)
		self.FillDistanceTable() # Was previously already done in the constructor
		# Sometimes begin by making the plot with the best localValue a starting plot
		firstPlayerPlaced = False
		# Space tends to be too tight in the Old World; need to focus on maximizing distances. Coastal starts also make more sense when there is a New World to colonize.
		if not mc.OldWorldStarts and (numPlayers == 1 or PRand.randint(0, 100) < (numPlayers - 2) * 20):
			# Force an inland start from time to time
			for i in range(min(7, len(self.plotList))):
				if not self.plotList[i].isCoast() or PRand.randint(0, 100) < 15:
					print("First location placed with inland bias in area with %d players" % (numPlayers))
					self.plotList[i].vacant = False
					firstPlayerPlaced = True
					break
		if not firstPlayerPlaced: # </advc>
			avgDistanceList = list()
			for i in range(len(self.plotList)):
				avgDistanceList.append(self.plotList[i])
			#Make sure first guy starts on the end and not in the middle, otherwise if
			#there are two players one will start on the middle and the other on the end
			avgDistanceList.sort(lambda x, y:cmp(x.avgDistance, y.avgDistance))
			avgDistanceList.reverse()
			#First place players as far as possible away from each other
			#Place the first player
			avgDistanceList[0].vacant = False
		for i in range(1, numPlayers):
			distanceList = list()
			for n in range(len(self.plotList)):
				if self.plotList[n].vacant:
					minDistance = -1
					for m in range(len(self.plotList)):
						if not self.plotList[m].vacant:
							ii = n * len(self.plotList) + m
							distance = self.distanceTable[ii]
							if distance < minDistance or minDistance == -1:
								minDistance = distance
					# <advc>
					for m in range(len(self.distTableOtherAreas) // len(self.plotList)):
						ii = m * len(self.plotList) + n
						distance = self.distTableOtherAreas[ii]
						if minDistance == -1 or minDistance > distance:
							minDistance = distance
					# </advc>
					self.plotList[n].nearestStart = minDistance
					distanceList.append(self.plotList[n])
			#Find biggest nearestStart and place a start there
			distanceList.sort(lambda x, y:cmp(x.nearestStart, y.nearestStart))
			distanceList.reverse()
			# advc (comment): This raises an exception when no suitable plot is found. Caught by SetStartingPlots.
			distanceList[0].vacant = False
		self.CalculateStartingPlotValues()
		#Now place all starting positions
		n = 0
		for m in range(len(self.plotList)):
			if not self.plotList[m].vacant:
				sPlot = CyMap().plot(self.plotList[m].x, self.plotList[m].y)
				if sPlot.isWater():
					raise ValueError, "Start plot is water!"
				#sPlot.setImprovementType(gc.getInfoTypeForString("NO_IMPROVEMENT"))
				# advc.001:
				sPlot.setImprovementType(ImprovementTypes.NO_IMPROVEMENT)
				playerID = self.playerList[n]
				player = gc.getPlayer(playerID)
				sPlot.setStartingPlot(True)
				player.setStartingPlot(sPlot, True)
				# advc:
				print("%d/%d assigned as starting plot" % (sPlot.getX(),sPlot.getY()))
				n += 1


	def CalculateStartingPlotValues(self):
		numPlots = len(self.plotList)
		for n in range(numPlots):
			self.plotList[n].owner = -1
			self.plotList[n].totalValue = 0
		for n in range(numPlots):
			if self.plotList[n].vacant:
				continue
			#LM - Removed redundant assignment.
			self.plotList[n].numberOfOwnedCities = 0
			for m in range(numPlots):
				i = n * numPlots + m
				nDistance = self.distanceTable[i]
				if nDistance == -1:
					leastDistance = False
				else:
					leastDistance = True #Being optimistic, prove me wrong
				for p in range(numPlots):
					if p == n or self.plotList[p].vacant:
						continue
					ii = p * numPlots + m
					pDistance = self.distanceTable[ii]
					if pDistance > -1 and pDistance <= nDistance:
						leastDistance = False #Proven wrong
						break
				if leastDistance:
					self.plotList[n].totalValue += self.plotList[m].localValue
					self.plotList[n].numberOfOwnedCities += 1
					self.plotList[m].owner = self.plotList[n]
					self.plotList[m].distanceToOwner = nDistance


	def getDistance(self, x, y, dx, dy):
		xx = x - dx
		if abs(xx) > mc.width / 2:
			xx = mc.width - abs(xx)
		distance = max(abs(xx), abs(y - dy))
		return distance


class StartPlot:
	def __init__(self, x, y, localValue):
		self.x = x
		self.y = y
		self.localValue = localValue
		self.totalValue = 0
		self.numberOfOwnedCities = 0
		self.distanceToOwner = -1
		self.nearestStart = -1
		self.vacant = True
		self.owner = None
		self.avgDistance = 0


	def isCoast(self):
		plot = CyMap().plot(self.x, self.y)
		waterArea = plot.waterArea()
		if waterArea.isNone() or waterArea.isLake():
			return False
		return True


	def isRiverSide(self):
		plot = CyMap().plot(self.x, self.y)
		return plot.isRiverSide()


	def plot(self):
		return CyMap().plot(self.x, self.y)


	def copy(self):
		cp = StartPlot(self.x, self.y, self.localValue)
		cp.totalValue          = self.totalValue
		cp.numberOfOwnedCities = self.numberOfOwnedCities
		cp.distanceToOwner     = self.distanceToOwner
		cp.nearestStart        = self.nearestStart
		cp.vacant              = self.vacant
		cp.owner               = self.owner
		cp.avgDistance         = self.avgDistance
		return cp


	def __str__(self):
		linestring = "x=%(x)3d,y=%(y)3d,localValue=%(lv)6d,totalValue =%(tv)6d, nearestStart=%(ad)6d, coastalCity=%(cc)d" % \
		{"x":self.x,"y":self.y,"lv":self.localValue,"tv":self.totalValue,"ad":self.nearestStart,"cc":self.isCoast()}
		return linestring


sf = StartingPlotFinder()


###############################################################################
## Required DLL Tie-in Functions (Mapscript Template)
###############################################################################

def getDescription():
	# advc: First sentence taken from Perfect World 2. The description imo isn't the place for recounting the history of the map script.
	return "Random map that simulates earth-like plate tectonics, geostrophic and monsoon winds and rainfall. Customized for the AdvCiv mod."


def getWrapX():
	return mc.WrapX


def getWrapY():
	return mc.WrapY


def getNumCustomMapOptions():
	mc.initialize()
	return 3 # advc: was 8


def getCustomMapOptionName(argsList):
	optionID = argsList[0]
	'''
	if optionID == 0:
		return "Sea Level:"
	if optionID == 1:
		return "Landmasses:"
	if optionID == 2:
		return "Mountains:"
	if optionID == 3:
		return "Climate:"
	if optionID == 4:
		return "Rivers:"
	if optionID == 5:
		return "Pangaeas:"
	if optionID == 6:
		return "World Wrap:"
	if optionID == 7:
		return "Start:"
	'''
	# <advc> Reorder and use existing translations
	[optionID] = argsList
	option_names = {
		0:	"TXT_KEY_MAP_SCRIPT_LAND_SHAPE",
		1:	"Start", # Doesn't really need a translation ...
		2:	"TXT_KEY_MAP_WORLD_WRAP"
		}
	return unicode(CyTranslator().getText(option_names[optionID], ())) # </advc>


def getNumCustomMapOptionValues(argsList):
	optionID = argsList[0]
	# <advc>
	option_values = {
		0:	2,
		1:	2,
		2:	3
		}
	return option_values[optionID]
	# </advc>
	'''
	if optionID == 0:
		return 5
	if optionID == 1:
		return 3
	if optionID == 2:
		return 2
	if optionID == 3:
		return 2
	if optionID == 4:
		return 2
	if optionID == 5:
		return 2
	if optionID == 6:
		return 3
	if optionID == 7:
		return 2
	return 0
	'''

def getCustomMapOptionDescAt(argsList):
	# <advc>
	[iOption, iSelection] = argsList
	selection_names = {
		0:	{
			#0: "TXT_KEY_MAP_SCRIPT_NORMAL_CONTINENTS",
			#1: "TXT_KEY_MAP_SCRIPT_MASSIVE_CONTINENTS",
			# But they're not quite "massive" (and the Perlin continents aren't exactly "normal") ...
			0: "Perlin Noise",
			1: "Plate Tectonics",
			},
		1:	{
			0: "TXT_KEY_MAP_SCRIPT_START_ANYWHERE",
			#1: "TXT_KEY_MAP_SCRIPT_ALL_IN_OLD_WORLD"
			1: "Old World (unless Pangaea); -30% players recommended"
			},
		2:	{
			0: "TXT_KEY_MAP_WRAP_FLAT",
			1: "TXT_KEY_MAP_WRAP_CYLINDER",
			2: "TXT_KEY_MAP_WRAP_TOROID"
			}
		}
	translated_text = unicode(CyTranslator().getText(selection_names[iOption][iSelection], ()))
	return translated_text
	# </advc>
	'''
	optionID    = argsList[0]
	selectionID = argsList[1]
	if optionID == 0:
		if selectionID == 0:
			return "Normal"
		elif selectionID == 1:
			return "Low Tide"
		elif selectionID == 2:
			return "High Tide"
		elif selectionID == 3:
			return "Land Ho!"
		else:
			return "Water World"
	elif optionID == 1:
		if selectionID == 0:
			return "PerfectWorld 3"
		elif selectionID == 1:
			return "PerfectWorld 3 (Hex Grid)"
		else:
			return "PerfectWorld 2"
	elif optionID == 2:
		if selectionID == 0:
			return "Neighbor Slope"
		else:
			return "Absolute Height"
	elif optionID == 3:
		if selectionID == 0:
			return "PerfectWorld 3"
		else:
			return "PerfectWorld 2"
	elif optionID == 4:
		if selectionID == 0:
			return "Default SDK"
		else:
			return "PerfectWorld 2"
	elif optionID == 5:
		if selectionID == 0:
			return "Break"
		else:
			return "Allow"
	elif optionID == 6:
		if selectionID == 0:
			return "Cylindrical"
		elif selectionID == 1:
			return "Toroidal"
		else:
			return "Flat"
	elif optionID == 7:
		if selectionID == 0:
			return "Everywhere"
		else:
			return "Old World Only"
	return u""
	'''

# <advc> Make cylindrical the middle choice b/c that's what the standard map scripts do
def getCustomMapOptionDefault(argsList):
#	return 0
	[iOption] = argsList
	option_defaults = {
		0:	1, # And make the PW2 landmass generator the default
		1:	0,
		2:	1
		}
	return option_defaults[iOption] # </advc>


def isRandomCustomMapOption(argsList):
	return False


''' # advc: Re-enable all the normalization functions in the DLL. Extra rivers and lakes had already been re-enabled by v3.3.
#This doesn't work with my river system so it is disabled. Some civs
#might start without a river.
def normalizeAddRiver():
	return
def normalizeAddLakes():
	return
def normalizeAddGoodTerrain():
	return
def normalizeRemoveBadTerrain():
	return
def normalizeRemoveBadFeatures():
	return
def normalizeAddFoodBonuses():
	return
def normalizeAddExtras():
	return
def normalizeRemovePeaks():
	return
'''

def isAdvancedMap():
	return False

def isClimateMap():
	return False
# advc: Yes, we do use the standard sea level option.
#def isSeaLevelMap():
#	return False


def getTopLatitude():
	return mc.topLatitude # advc.001: was 90

def getBottomLatitude():
	return mc.bottomLatitude # advc.001: was -90

''' # advc: Use the defaults, which are smaller, combined with more arable land.
def getGridSize(argsList):
	grid_sizes = {
		WorldSizeTypes.WORLDSIZE_DUEL:					(12,  8),
		WorldSizeTypes.WORLDSIZE_TINY:					(15, 10),
		WorldSizeTypes.WORLDSIZE_SMALL:					(18, 12),
		WorldSizeTypes.WORLDSIZE_STANDARD:				(24, 16),
		WorldSizeTypes.WORLDSIZE_LARGE:					(30, 20),
		WorldSizeTypes.WORLDSIZE_HUGE:					(36, 24)
	}
	if (argsList[0] == -1): # (-1,) is passed to function on loads
			return []
	[eWorldSize] = argsList
	return grid_sizes[eWorldSize]
'''


def generatePlotTypes():
	print ""
	print "====================="
	print "Generating Plot Types"
	print "====================="
	gc = CyGlobalContext()
	map = gc.getMap()
	mc.width  = map.getGridWidth()
	mc.height = map.getGridHeight()
	#PRand.seed() # advc: Moved to beforeInit
	if mc.LandmassGenerator == 2:
		scaleMinMeteorSize() # advc: Moved into new function
		em = e2
		em.initialize(mc.hmWidth, mc.hmHeight, mc.WrapX, mc.WrapY)
		em.PerformTectonics()
		em.GenerateElevationMap()
		em.CombineMaps()
		em.CalculateSeaLevel()
		em.FillInLakes()
		em.AddWaterBands()
	else:
		em = e3
		if mc.ClimateSystem == 0:
			em.initialize(mc.width,   mc.height,   mc.WrapX, mc.WrapY)
		else:
			scaleMinMeteorSize() # advc: Moved into new function
			em.initialize(mc.hmWidth, mc.hmHeight, mc.WrapX, mc.WrapY)
		em.GenerateElevationMap()
		em.FillInLakes()
	if mc.maximumMeteorCount > 0: # advc
		pb.breakPangaeas()
	# <advc>
	if mc.LandmassGenerator == 2:
		centerMap(em.data, mc.hmWidth, mc.hmHeight, GetHmIndex)
	else:
		# (ElevationMap3 normally uses FloatMap.GetIndex, but the global function should be equivalent.)
		centerMap(em.data, em.width, em.height, GetIndex)
	# </advc>
	if mc.ClimateSystem == 0:
		c3.GenerateTemperatureMap()
		c3.GenerateRainfallMap()
	else:
		c2.CreateClimateMaps()
	if mc.LandmassGenerator == 2 or mc.ClimateSystem == 1:
		ShrinkMaps()
	tm.initialize()
	tm.GeneratePlotMap()
	tm.GenerateTerrainMap()
	rm.GenerateRiverMap()
	km.GenerateContinentMap()
	'''
	land   = 0.0
	flat   = 0.0
	snow   = 0.0
	tundra = 0.0
	desert = 0.0
	plains = 0.0
	grass  = 0.0
	for i in range(em.length):
		if tm.pData[i] != mc.WATER:
			land += 1.0
			if tm.pData[i] != mc.PEAK:
				flat += 1.0
				if tm.tData[i]   == mc.SNOW:
					snow   += 1.0
				elif tm.tData[i] == mc.TUNDRA:
					tundra += 1.0
				elif tm.tData[i] == mc.DESERT:
					desert += 1.0
				elif tm.tData[i] == mc.PLAINS:
					plains += 1.0
				elif tm.tData[i] == mc.GRASS:
					grass  += 1.0
	print("Land   Percentage = ", str(land   / float(em.length)))
	print("Land Count = ", str(land), "; Flat Count = ", str(flat))
	print("Snow   Percentage = ", str(snow   / flat))
	print("Tundra Percentage = ", str(tundra / flat))
	print("Desert Percentage = ", str(desert / flat))
	print("Plains Percentage = ", str(plains / flat))
	print("Grass  Percentage = ", str(grass  / flat))
	'''
	plotTypes = [PlotTypes.PLOT_OCEAN] * em.length
	for i in range(em.length):
		mapLoc = tm.pData[i]
		if mapLoc == mc.PEAK:
			plotTypes[i] = PlotTypes.PLOT_PEAK
		elif mapLoc == mc.HILLS:
			plotTypes[i] = PlotTypes.PLOT_HILLS
		elif mapLoc == mc.LAND:
			plotTypes[i] = PlotTypes.PLOT_LAND
	return plotTypes

# advc: Cut out of generatePlotTypes
def scaleMinMeteorSize():
	#return (1 + int(round(float(mc.hmWidth) / float(mc.width)))) * 3
	# advc: When using the PW 2 climate system, the PangaeaBreaker has to work with a map of dimensions hmWidth x hmHeight. Therefore, counterintuitively, the meteor size needs to be increased on small maps. That part is OK in the original code above. But we shouldn't discard the meteor size set previously.
	mc.minimumMeteorSize = int(math.ceil((mc.minimumMeteorSize * mc.hmWidth) / float(mc.width)))


def generateTerrainTypes():
	print "========================"
	print "Generating Terrain Types"
	print "========================"
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	gc = CyGlobalContext()
	iGrass  = gc.getInfoTypeForString("TERRAIN_GRASS")
	iPlains = gc.getInfoTypeForString("TERRAIN_PLAINS")
	iDesert = gc.getInfoTypeForString("TERRAIN_DESERT")
	iTundra = gc.getInfoTypeForString("TERRAIN_TUNDRA")
	iSnow   = gc.getInfoTypeForString("TERRAIN_SNOW")
	iCoast  = gc.getInfoTypeForString("TERRAIN_COAST")
	iOcean  = gc.getInfoTypeForString("TERRAIN_OCEAN")
	terrainTypes = [0] * em.length
	for i in range(em.length):
		if tm.tData[i] == mc.OCEAN:
			terrainTypes[i] = iOcean
		elif tm.tData[i] == mc.COAST:
			terrainTypes[i] = iCoast
		elif tm.tData[i] == mc.GRASS:
			terrainTypes[i] = iGrass
		elif tm.tData[i] == mc.PLAINS:
			terrainTypes[i] = iPlains
		elif tm.tData[i] == mc.TUNDRA:
			terrainTypes[i] = iTundra
		elif tm.tData[i] == mc.SNOW:
			terrainTypes[i] = iSnow
		elif tm.tData[i] == mc.DESERT:
			terrainTypes[i] = iDesert
	return terrainTypes


def placeRiversInPlot(x, y):
	gc = CyGlobalContext()
	pmap = gc.getMap()
	plot = pmap.plot(x, y)
	#NE
	ii = GetIndex(x, y + 1)
	if ii >= 0 and rm.riverMap[ii] == mc.S:
		plot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
	#SW
	ii = GetIndex(x - 1, y)
	if ii >= 0 and rm.riverMap[ii] == mc.E:
		plot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_EAST)
	#SE
	ii = GetIndex(x, y)
	if rm.riverMap[ii] == mc.N:
		plot.setWOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
	elif rm.riverMap[ii] == mc.W:
		plot.setNOfRiver(True, CardinalDirectionTypes.CARDINALDIRECTION_WEST)


'''
This function examines a lake area and removes ugly surrounding rivers. Any
river that is flowing away from the lake, or alongside the lake will be
removed. This function also returns a list of riverID's that flow into the
lake.
'''
def cleanUpLake(x, y):
	gc = CyGlobalContext()
	mmap = gc.getMap()
	riversIntoLake = list()
	plot = mmap.plot(x, y + 1) #North
	if plot != 0 and plot.isNOfRiver():
		plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x - 1, y) #West
	if plot != 0 and plot.isWOfRiver():
		plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x + 1, y) #East
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x, y - 1) #South
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x - 1, y + 1) #Northwest
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x + 1, y + 1) #Northeast
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot = mmap.plot(x - 1, y - 1) #Southhwest
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
			riversIntoLake.append(plot.getRiverID())
		else:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	#Southeast plot is not relevant
	return riversIntoLake


'''
This function replaces rivers to update the river crossings after a lake or
channel is placed at X,Y. There had been a long standing problem where water tiles
added after a river were causing graphical glitches and incorrect river rules
due to not updating the river crossings.
'''
def replaceRivers(x, y):
	gc = CyGlobalContext()
	mmap = gc.getMap()
	plot = mmap.plot(x, y + 1) #North
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH:
			#setting the river to what it already is will be ignored by the dll,
			#so it must be unset and then set again.
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setWOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
	plot = mmap.plot(x - 1, y) #West
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setNOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_EAST)
	plot = mmap.plot(x + 1, y) #East
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setNOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_WEST)
	plot = mmap.plot(x, y - 1) #South
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setWOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
	plot = mmap.plot(x - 1, y + 1) #Northwest
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_SOUTH:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setWOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_SOUTH)
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_EAST:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setNOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_EAST)
	plot = mmap.plot(x + 1, y + 1) #Northeast
	if plot != 0 and plot.isNOfRiver():
		if plot.getRiverWEDirection() == CardinalDirectionTypes.CARDINALDIRECTION_WEST:
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setNOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_WEST)
	plot = mmap.plot(x - 1, y - 1) #Southhwest
	if plot != 0 and plot.isWOfRiver():
		if plot.getRiverNSDirection() == CardinalDirectionTypes.CARDINALDIRECTION_NORTH:
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setWOfRiver(True,  CardinalDirectionTypes.CARDINALDIRECTION_NORTH)
	#Southeast plot is not relevant


'''
It looks bad to have a lake, fed by a river, sitting right next to the coast.
This function tries to minimize that occurance by replacing it with a
natural harbor, which looks much better.
'''
def makeHarbor(x, y, oceanMap):
	oceanID = oceanMap.getOceanID()
	i = oceanMap.getIndex(x, y)
	if oceanMap.data[i] != oceanID:
		return
	# <advc> Most tiles are near a coast; but shouldn't eliminate most lakes that are fed by rivers. And bays are rather too common.
	if PRand.randint(0, 1) != 0:
		return # </advc>
	#N
	ii = oceanMap.getIndex(x, y + 2)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		makeChannel(x, y + 1)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#S
	ii = oceanMap.getIndex(x, y - 2)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		makeChannel(x, y - 1)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#E
	ii = oceanMap.getIndex(x + 2, y)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		makeChannel(x + 1, y)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#W
	ii = oceanMap.getIndex(x - 2, y)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		makeChannel(x - 1, y)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#NW
	ii = oceanMap.getIndex(x - 1, y + 1)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		if PRand.randint(0, 1) == 0:
			makeChannel(x - 1, y)
		else:
			makeChannel(x, y + 1)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#SE
	ii = oceanMap.getIndex(x + 1, y - 1)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		if PRand.randint(0, 1) == 0:
			makeChannel(x + 1, y)
		else:
			makeChannel(x, y - 1)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#NE
	ii = oceanMap.getIndex(x + 1, y + 1)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		if PRand.randint(0, 1) == 0:
			makeChannel(x, y + 1)
		else:
			makeChannel(x + 1, y)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()
	#SW
	ii = oceanMap.getIndex(x - 1, y - 1)
	if ii >= 0 and oceanMap.getAreaByID(oceanMap.data[ii]).water and oceanMap.data[ii] != oceanID:
		if PRand.randint(0, 1) == 0:
			makeChannel(x, y - 1)
		else:
			makeChannel(x - 1, y)
		oceanMap.defineAreas(isWaterMatch)
		oceanID = oceanMap.getOceanID()


def makeChannel(x, y):
	gc = CyGlobalContext()
	mmap = gc.getMap()
	plot = mmap.plot(x, y)
	cleanUpLake(x, y)
	plot.setPlotType(PlotTypes.PLOT_OCEAN, False, False) # advc.opt: was True,True
	plot.setRiverID(-1)
	plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	replaceRivers(x, y)
	i = GetIndex(x, y)
	tm.pData[i] = mc.WATER
	tm.tData[i] = mc.COAST


def expandLake(x, y, riversIntoLake, oceanMap):
	class LakePlot:
		def __init__(self, x, y, altitude):
			self.x = x
			self.y = y
			self.altitude = altitude
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	gc = CyGlobalContext()
	mmap = gc.getMap()
	lakePlots = list()
	lakeNeighbors = list()
	i = oceanMap.getIndex(x, y)
	if tm.tData[i] == mc.DESERT:
		terrainModifier = mc.DesertLakeModifier
	else:
		terrainModifier = 1.0
	if mc.ClimateSystem == 0:
		lakeSize = max(mc.expandedLakeMinSize,
				int(rm.drainageMap[i] * mc.LakeSizePerDrainage3 * terrainModifier))
	else:
		lakeSize = max(mc.expandedLakeMinSize,
				int(rm.drainageMap[i] * mc.LakeSizePerDrainage2 * terrainModifier))
	start = LakePlot(x, y, em.data[i])
	lakeNeighbors.append(start)
	while lakeSize > 0 and len(lakeNeighbors) > 0:
		lakeNeighbors.sort(lambda x, y:cmp(x.altitude, y.altitude))
		currentLakePlot = lakeNeighbors[0]
		del lakeNeighbors[0]
		lakePlots.append(currentLakePlot)
		plot = mmap.plot(currentLakePlot.x, currentLakePlot.y)
		#if you are erasing a river to make a lake, make the lake smaller
		if plot.isNOfRiver() or plot.isWOfRiver():
			lakeSize -= 1
		makeChannel(currentLakePlot.x, currentLakePlot.y)
		#Add valid neighbors to lakeNeighbors
		for direction in range(1, 5):
			xx, yy = GetNeighbor(currentLakePlot.x, currentLakePlot.y, direction)
			ii = oceanMap.getIndex(xx, yy)
			if ii >= 0:
				#if this neighbor is in water area, then quit
				areaID = oceanMap.data[ii]
				if areaID == 0:
					raise ValueError, "areaID = 0 while generating lakes. This is a bug"
				for n in range(len(oceanMap.areaList)):
					if oceanMap.areaList[n].ID == areaID:
						if oceanMap.areaList[n].water:
							return
				xx, yy = CoordsFromIndex(ii, oceanMap.width) # advc.001
				if rm.riverMap[ii] != mc.L and not mmap.plot(xx, yy).isWater():
					lakeNeighbors.append(LakePlot(xx, yy, em.data[ii]))
		lakeSize -= 1

# <advc> Let the DLL place rivers even if the PM river generator is enabled (once the PM river generator has finished)
def addRivers():
	CyPythonMgr().allowDefaultImpl() # </advc>
	if mc.RiverGenerator != 0:
		return
	# <advc> Cut from addLakes
	''' # We no longer let the DLL place rivers first; no need to clear them.
	for y in range(mc.height):
		for x in range(mc.width):
			plot = CyMap().plot(x, y)
			plot.setRiverID(-1)
			plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
			plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	'''
	for y in range(mc.height):
		for x in range(mc.width):
			placeRiversInPlot(x, y) # </advc>


def addLakes():
	gc = CyGlobalContext()
	mmap = gc.getMap()

	# (advc: River generation code moved into addRivers.)
	oceanMap = AreaMap(mc.width, mc.height, True, True)
	oceanMap.defineAreas(isWaterMatch)
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			if rm.flowMap[i] == mc.L:
				riversIntoLake = cleanUpLake(x, y)
				plot = mmap.plot(x, y)
				if len(riversIntoLake) > 0:
					expandLake(x, y, riversIntoLake, oceanMap)
				else:
					#no lake here, but in that case there should be no rivers either
					plot.setRiverID(-1)
					plot.setNOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
					plot.setWOfRiver(False, CardinalDirectionTypes.NO_CARDINALDIRECTION)
	oceanMap.defineAreas(isWaterMatch)
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			makeHarbor(x, y, oceanMap)
	mmap.recalculateAreas(); # advc.opt: No longer done in makeChannel


def addFeatures():
	print "========================"
	print "Generating Feature Types"
	print "========================"
	gc = CyGlobalContext()
	mmap = gc.getMap()
	if mc.LandmassGenerator == 2:
		em = e2
	else:
		em = e3
	if mc.ClimateSystem == 0:
		cm = c3
	else:
		cm = c2
	fForest      = gc.getInfoTypeForString("FEATURE_FOREST")
	fJungle      = gc.getInfoTypeForString("FEATURE_JUNGLE")
	fFloodPlains = gc.getInfoTypeForString("FEATURE_FLOOD_PLAINS")
	fOasis       = gc.getInfoTypeForString("FEATURE_OASIS")
	FORESTLEAFY     = 0
	FORESTEVERGREEN = 1
	FORESTSNOWY     = 2

	#print "Forest"
	forestTiles  = []
	forestLength = 0
	coldTiles = [] # advc
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			# <advc>
			if tm.pData[i] == mc.WATER or tm.pData[i] == mc.PEAK:
				continue
			# Use global function for not-jungle checks
			if tm.tData[i] == mc.GRASS or tm.tData[i] == mc.PLAINS:
				if not canHaveJungle(cm.RainfallMap.data[i], tm.jungleRainfall, tm.tData[i], tm.pData[i], em.GetLatitudeForY(y), cm.TemperatureMap.data[i], tm.jungleTemp):
					forestTiles.append(cm.TemperatureMap.data[i])
					forestLength += 1
			elif tm.tData[i] == mc.TUNDRA:
				coldTiles.append(cm.TemperatureMap.data[i])
	treeLineTemp = FindValueFromPercent(coldTiles, len(coldTiles), mc.TreelinePercent, True)
	 # </advc>
	deciduousTemp = FindValueFromPercent(forestTiles, forestLength, mc.DeciduousPercent, True)

	#print "Oasis"
	oasisCandidates = [] # advc
	desertLength = 0
	for y in range(mc.height):
		for x in range(mc.width):
			i = GetIndex(x, y)
			if tm.tData[i] != mc.DESERT:
				continue
			desertLength += 1
			# advc: Moved into new global function
			if canHaveOasis(x, y, tm.tData, fOasis):
				oasisCandidates.append(cm.RainfallMap.data[i])
	# <advc>
	oasisRainfall = 1000
	if len(oasisCandidates) > 0:
		# The target frequency is supposed to apply to all desert tiles, but only certain tiles are eligible. I think PM had been making this adjustment later on through the min/max chance.
		oasisPercent = (mc.OasisPercent * desertLength) / float(len(oasisCandidates))
		# Was FindValueFromPercent, which has trouble with the distribution being almost uniform. (Meaning also that rainfall is actually a pretty meaningless criterion for placing oases.)
		oasisRainfall = FindThresholdFromPercent(oasisCandidates, len(oasisCandidates), oasisPercent, True)
	# </advc>
	createIce()
	for y in range(mc.height):
		lat = em.GetLatitudeForY(y)
		for x in range(mc.width):
			set = False
			i = GetIndex(x, y)
			plot = mmap.plot(x, y)
			#Jungle, Forest
			if (tm.tData[i] == mc.GRASS or tm.tData[i] == mc.PLAINS or tm.tData[i] == mc.TUNDRA) and tm.pData[i] != mc.PEAK:
				# advc: Jungle checks moved into global function
				if not set and canHaveJungle(cm.RainfallMap.data[i], tm.jungleRainfall, tm.tData[i], tm.pData[i], lat, cm.TemperatureMap.data[i], tm.jungleTemp) and PRand.random() < mc.MaxTreeChance:
					# <advc> Avoid placing jungle adjacent to desert
					desertScore = 0
					for dx in range(-1,2):
						for dy in range(-1,2):
							if dx == 0 and dy == 0:
								continue
							adjIndex = GetIndex(x + dx, y + dy)
							if adjIndex < 0 or adjIndex > len(tm.tData):
								continue
							if tm.tData[adjIndex] != mc.DESERT:
								continue
							desertScore += 1
							bOrth = (abs(dx + dy) % 2 != 0)
							if bOrth:
								desertScore += 1
					desertScoreLimit = 1
					if plot.isHills():
						desertScoreLimit += 1
					if desertScore > desertScoreLimit:
						# Also convert grassland to plains
						if tm.tData[i] == mc.GRASS:
							tm.tData[i] = mc.PLAINS
							# Terrain has already been set at this point; need to overwrite that.
							plot.setTerrainType(gc.getInfoTypeForString("TERRAIN_PLAINS"), False, False)
					else: # </advc>
						if setFeature(plot, fJungle, 0):
							set = True
				# <advc>
				if not set:
					if tm.tData[i] == mc.TUNDRA:
						if cm.TemperatureMap.data[i] < treeLineTemp:
							continue
						forestChance = mc.BorealForestChance
					else:
						forestChance = mc.TemperateForestChance # </advc>
					if cm.RainfallMap.data[i] >= tm.jungleRainfall * PRand.random() and PRand.random() < mc.MaxTreeChance * forestChance: # advc: Multiplication by ForestChance added
						if tm.tData[i] == mc.TUNDRA:
							if setFeature(plot, fForest, FORESTSNOWY):
								set = True
						elif cm.TemperatureMap.data[i] >= deciduousTemp:
							if setFeature(plot, fForest, FORESTLEAFY):
								set = True
						else:
							if setFeature(plot, fForest, FORESTEVERGREEN):
								set = True
			#Floodplains, Oasis
			if not set and tm.tData[i] == mc.DESERT:
				#if plot.isRiver(): # advc: Let setFeature (i.e. the DLL) check this
				if setFeature(plot, fFloodPlains, 0):
					set = True
				if not set and cm.RainfallMap.data[i] >= oasisRainfall:
					#if PRand.random() < mc.OasisMinChance + (((mc.OasisMaxChance - mc.OasisMinChance) * (cm.RainfallMap.data[i] - oasisRainfall)) / (tm.desertRainfall - oasisRainfall)):
					# advc: The rainfall ratio is dubious b/c there is very little rainfall on all desert tiles. I'm not sure that a (min/max) chance is needed at all. Let's try it w/o that. Surroundings check moved into new global function.
					if canHaveOasis(x, y, tm.tData, fOasis):
						if setFeature(plot, fOasis, 0):
							set = True


# advc: Make sure that the placement rules are consistent with the DLL.
# setFeatureType calls above redirected here.
def setFeature(plot, feature, variety):
	if not plot.canHaveFeature(feature):
		return False
	plot.setFeatureType(feature, variety)
	return True


def createIce():
	gc = CyGlobalContext()
	mmap = gc.getMap()
	featureIce = gc.getInfoTypeForString("FEATURE_ICE")
	if mc.ClimateSystem == 0:
		cm = c3
		iceTemp = 0.25
	else:
		cm = c2
		iceTemp = 0.4
	# advc: Adjust to top latitude
	iceTemp = iceTemp * mc.topLatitude / 90
	iceTemp *= 0.9 # advc: There's also a bit too much ice in general
	'''
	worldSize = gc.getMap().getWorldSize()
	if worldSize == 0:
		thickness = 3  #/ 8  = 0.375
	elif worldSize == 1:
		thickness = 4  #/ 10 = 0.4
	elif worldSize == 2:
		thickness = 5  #/ 12 = 0.4167
	elif worldSize == 3:
		thickness = 6  #/ 16 = 0.375
	elif worldSize == 4:
		thickness = 8  #/ 20 = 0.4
	elif worldSize == 5:
		thickness = 10 #/ 24 = 0.4167
	elif worldSize == 6:
		thickness = 11 #/ 28 = 0.393
	else:
		thickness = 14 #/ 36 = 0.389
	'''
	# advc: Simpler, and doesn't need to be adjusted to getGridSize. Divisor 10.0 would be (pretty much) equivalent to the above, but I don't want it to be as thick as that.
	thickness = int(round((mc.height / 12.5) * mc.topLatitude / 90))
	if mc.WrapY:
		iceChance    = 0.5
		iceReduction = 0.3 / (thickness - 1)
	else:
		iceChance    = 1.0
		iceReduction = 0.6 / (thickness - 1)
	for y in range(thickness * 2):
		for x in range(mc.width):
			i = GetIndex(x, y)
			plot = mmap.plot(x, y)
			if plot.isWater() and cm.TemperatureMap.data[i] < iceTemp and PRand.random() < iceChance:
				plot.setFeatureType(featureIce, 0)
		iceChance -= iceReduction
	if mc.WrapY:
		iceChance = 0.5
	else:
		iceChance = 1.0
	for y in range(mc.height - 1, (mc.height - 1) - (thickness * 2), -1):
		for x in range(mc.width):
			i = GetIndex(x, y)
			plot = mmap.plot(x, y)
			if plot.isWater() and cm.TemperatureMap.data[i] < iceTemp and PRand.random() < iceChance:
				plot.setFeatureType(featureIce, 0)
		iceChance -= iceReduction

# advc: The AdvCiv DLL can do this better - and much faster; the PM bonus placer seems to be almost as slow as generateTerrainTypes.
#def addBonuses():
#	bp.AddBonuses()


def assignStartingPlots():
	# <advc.027> Handle starting sites in findStartingArea - unless SPI is disabled.
	if CyGlobalContext().getDefineINT("ENABLE_STARTING_POSITION_ITERATION") <= 0:
		sf.SetStartingPlots()
	else:
		CyPythonMgr().allowDefaultImpl()


def findStartingArea(argsList):
	[playerID] = argsList
	player = CyGlobalContext().getPlayer(playerID)
	if CyGlobalContext().getDefineINT("ENABLE_STARTING_POSITION_ITERATION") <= 0:
		# Starting plots have already been computed in assignStartingPlots then
		CyPythonMgr().allowDefaultImpl()
		return -1
	if not mc.OldWorldStarts:
		# Would be nice to let SPI use the PM sites as its initial solution, but, if the PM sites are set in assignStartingPlots, then SPI won't call findStartingArea, and, once findStartingArea is called, SPI is already in the process of generating its own initial solution. Could be worked out perhaps ... Oh, well, leaving all the work to SPI at least saves time.
		CyPythonMgr().allowDefaultImpl()
		return -1
	plot = player.getStartingPlot()
	if not plot or plot.isNone(): # Don't run starting plot finder more than once(!)
		sf.SetStartingPlots()
	# Tell SPI to respect the starting areas chosen by PM. (One area per-player - however, SPI may still move players between starting areas; i.e. only the New-Old World split is handled by PM.)
	plot = player.getStartingPlot()
	if plot and not plot.isNone():
		return plot.getArea()
	CyPythonMgr().allowDefaultImpl()
	return -1
# </advc.027>

def beforeInit():
	PRand.seed() # advc: Moved from generatePlotTypes
	mc.initInGameOptions()


##############################################################################
## Version History (LunarMongoose)
##############################################################################
##
## 3.3 - Added a menu option to use Vanilla Civ4's SDK river generator by default
## instead of PerfectWorld 2's generator. Added a menu option to use absolute height
## instead of lowest-neighbor slope for setting Hills and Peaks. Wrote a new proximity
## calculation for determining which landmasses are added to the largest and
## second-largest continents to form the Old World and New World regions. Set Oases to
## only require Desert in all cardinal directions. Disabled meteors on Duel, Tiny, and
## Small regardless of Pangaea setting, since they tend to wipe out most of the land
## on the smaller map sizes (often leading to player spawning errors on Duel). Added a
## menu option to use 5 different Sea Level values.
##
## 3.2.1 - Changed Jungle temperature requirement from an absolute value to a global
## percent to avoid large amounts of Jungle on maps with a lot of land near the
## equator, and to avoid small amounts of Jungle on maps without much land near the
## equator. Increased minimum distance between Oases from 1 to 2 tiles.
##
## 3.2 - Added AIAndy's square grid evaluation, float division and geostrophic fixes,
## his bonus placement and starting location speed enhancements, and his PythonRandom
## multiplayer support. Added a menu option to continue using the old hex-grid-based
## Perlin Noise code if desired, since the previous PW3 landmass shapes are different
## and still fully viable. Merged in the remaining PW 2.0.8 functionality with a menu
## option to select the PW2 landmass generator if desired. Changed the rainfall
## thresholds from absolute values to global percents like the temperature thresholds,
## set them to ignore Peaks, and merged the climate system constants back together.
## Enforced the current map's x and y wrap settings in a number of places in the code,
## which fixes some bugs with -1 data values near the edges and should get rivers
## wrapping only when they're supposed to. Fixed natural harbor bug, and added shape
## randomization to natural harbor creation on diagonals. Changed sea ice to vary with
## map size instead of always being 4 tiles thick, and to require water temperature to
## be near freezing so the bands have some limited shape to them. Switched to PW2's
## oversized internal grid when using the PW3 LMG with the PW2 climate system so the
## latter works correctly. Changed the +/- 10% tolerances on elevation, rainfall and
## sea level thresholds to +/- 2%. Removed MeteorCompensationFactor since the system
## does indeed work best without it. (My apologies Ceph; you were right!) Made a
## number of additional code improvements.
##
## 3.1 - Fuyu's 2.0.6f bonus placement, starting location enhancement, minimum hill
## enforcement and bad feature removal code were added, along with his control
## variables. Reverted some more settings for use with vanilla that were still set for
## my mod. Added allowance in getPlotPotentialValue() for clearing features with
## negative food (ie Jungles), since it already accounted for cleared features with
## tile improvements that require it (only useful in mods). Added StartEra checks to
## verify the tech requirements are met for clearing features in both cases. Agreeing
## with Cephalo, I left the starting location production resource food override
## threshold at half the city plots being workable, rather than two-thirds. Changed
## the TechCityTrade requirement for resource valuation and placement to TechReveal
## since the former makes no sense: if a bonus is visible it enhances the tile, and if
## it isn't visible it doesn't enhance the tile, regardless of whether it can be
## harvested or traded with other cities. Added BonusMaxGroupSize option of -1 for
## setting Fuyu's clump limit based on WorldSize, clarified the description of what
## the 0 option there actually does, and fixed the random bounds. Added a minimum
## value to the StartEra checks to include all Classical resources, improvements and
## clearing abilities in the plot valuations. Changed allowWonderBonusChance to allow
## any strategic resource (not just Stone or Marble), and the city sweetener to allow
## non-strategic resources - both up through Classical (or later). Adjusted lake and
## river values again, and added separate controls for them for the two climate
## systems. Increased Desert slightly and Plains considerably in the PW2 system.
## Synchronized the PM3/PW2 code substantially more to make future updates easier.
## Scaled temperature from normal linearly down to zero in the top and bottom thirds
## of the map in the PW3 climate system, to get Tundra and Snow in the higher and
## lower latitudes as there should be. Lowered Tundra/Snow temperatures to compensate.
## Increased PW3 Grassland level slightly.
##
## 3.0 - Initial release of LM's Civ4 Port of Civ5's PW3_v2, using PW_2.06 as base.
## The PW2 HeightMap and ClimateMap have been replaced with their PW3 counterparts.
## PW2's high-altitude randomization was removed since it was causing 80-100%
## of land tiles to be Peaks regardless of settings. PW2's SmallMaps were removed
## since the new Perlin Noise landmass generator does not require an oversized map
## to avoid looking bad. The YToXRatio hex grid scale factor has been removed.
## PW2 control variables that are now unused have been removed, and the necessary
## PW3 ones have been added. Values have also been adjusted as needed or desired.
## MeteorCompensationFactor was added to try and help preserve total land percent
## when using Break Pangaeas. The Sea Level menu option has been enabled, and
## mc.SeaLevelFactor was added to support it. The Use menu option has been added,
## and a slightly-modified version of the PW2 ClimateMap was added back in, to
## support having a choice between the PW2 and PW3 climate systems. PW3's north
## and south attenuation were removed. PW2's code that forced Snow to be at higher
## elevation than Tundra, Tundra to be higher than everything else, and Desert to
## not be, well, something... was removed. Plains in the PW3 ClimateMap were
## set to have a null rainfall window and a relatively large temperature window,
## so that they form exclusively as a result of cold deserts; this helps create
## Great Plains type areas. RiverThreshold's dependence on PlainsPercent (via
## PlainsThreshold) was removed so that its value can be set reliably. Set Oases to
## require Desert in all surrounding tiles with no Oases present.
##

##############################################################################
## Version History (Cephalo)
##############################################################################
##
## 3v2 - Shrank the map sizes except for huge. Added a better way to adjust river
## lengths. Used the continent art styles in a more diverse way. Cleaned up the
## mountain ranges a bit.
##
## 3v1 - initial release! 11/24/2010
##
## 2.06 - Fixed a few bugs from my minimum hill/maximum bad feature function.
##
## 2.05 - Made maps of standard size and below a bit smaller. Changed the way I
## remove jungle to prevent excessive health problems. Tiles in FC on different
## continents have zero value. Tiles on different continents will not be boosted
## with resources or hills. Water tiles have zero value for non-coastal cities.
## Water tiles will not be boosted with resources for non-coastal cities, land
## tiles will be boosted instead. (lookout Sid's Sushi!)
##
## 2.04 - Changed many percent values to be a percent of land tiles rather than
## total map tiles for easier, more predictable adjustment. Ensured a minimum
## number of hills in a starting fat cross. Disabled the normalizeRemovePeaks
## function a replaced it with a maximum peaks in FC function. Added bonus
## resources to FC depending on player handicap. Added a value bonus for cities
## placed on river sides.
##
## 2.03 - Fixed an initialization problem related to Blue Marble. Added some
## enhanced error handling to help me track down some of the intermittant bugs
## that still remain.
##
## 2.02 - Fixed some problems with monsoons that were creating strange artifacts
## near the tropics. Added an exponential curve to heat loss due to altitude, so
## that jungles can appear more readily without crawling to inappropriate
## latitudes.
##
## 2.01 - Changed the way I handled a vanilla version difference. Added toroidal
## and flat map options. Made tree amount more easily adjustable. Added a variable to
## tune the level of resource bonuses. Changed the rules for fixing tundra/ice next
## to desert. Added altitude noise to the plate map to improve island chains. Added
## a variable to control heat loss due to high altitude. Implimented a new interleaved
## bonus placement scheme so that bonuses are placed individually in random order,
## rather than all of each bonus type at once. Brought back the meteor code from
## PerfectWorld 1 and eliminated the east/west continent divide.
##
## 2.0 - Rebuilt the landmass and climate model using the FaireWeather.py for
## Colonization map script engine. Improved the river system. Fixed some
## old bugs.
##
## 1.13 - Fixed a bug where starting on a goody hut would crash the game.
## Prevented start plots from being on mountain peaks. Changed an internal
## distance calculation from a straight line to a path distance, improving
## start locations somewhat. Created a new tuning variable called
## DesertLowTemp. Since deserts in civ are intended to be hot deserts, this
## variable will prevent deserts from appearing near the poles where the
## desert texture clashes horribly with the tundra texture.
##
## 1.12 - Found a small bug in the bonus placer that gave bonuses a minimum
## of zero, this is why duel size maps were having so much trouble.
##
## 1.11 - limited the features mixing with bonuses to forests only. This
## eliminates certain undesireable effects like floodplains being erased by
## or coinciding with oil or incense, or corn appearing in jungle.
##
## 1.10 - Wrapped all map constants into a class to avoid all those
## variables being loaded up when PW is not used. Also this makes it a
## little easier to change them programatically. Added two in-game options,
## New World Rules and Pangaea Rules. Added a tuning variable that allows
## bonuses with a tech requirement to co-exist with features, so that the
## absence of those features does not give away their location.
##
## 1.09 - Fixed a starting placement bug introduced in 1.07. Added a tuning
## variable to turn off 'New world' placement.
##
## 1.08 - Removed the hemispheres logic and replaced it with a simulated meteor
## shower to break up pangaeas. Added a tuning variable to allow pangaeas.
##
## 1.07 - Placing lakes and harbors after river placement was not updating river
## crossings. Resetting rivers after lake placement should solve this. Fixed a
## small discrepancy between Python randint and mapRand to make them behave the
## same way. Bonuses of the same bonus class, when forced to appear on the
## same continent, were sometimes crowding each other off the map. This was
## especially problematic on the smaller maps. I added some additional, less
## restrictive, passes to ensure that every resource has at least one placement
## unless the random factors decide that none should be placed. Starting plot
## normalization now will place food if a different bonus can not be used due
## to lack of food. Changed heightmap generation to more likely create a
## new world.
##
## 1.06 - Overhauled starting positions and resource placement to better
## suit the peculiarities of PerfectWorld
##
## 1.05 - Fixed the Mac bug and the multi-player bug.
##
## 1.04a - I had unfairly slandered getMapRand in my comments. I had stated
## that the period was shortened unnecessarily, which is not the case.
##
## 1.04 - Added and option to use the superior Python random number generator
## or the getMapRand that civ uses. Made the number of rivers generated tunable.
## Fixed a bug that prevented floodplains on river corners. Made floodplains
## in desert tunable.
##
## 1.03a - very minor change in hope of finding the source of a multi-player
## glitch.
##
## 1.03 - Improved lake generation. Added tuning variables to control some
## new features. Fixed some minor bugs involving the AreaMap filler
## and fixed the issue with oasis appearing on lakes. Maps will now report
## the random seed value that was used to create them, so they can be easily
## re-created for debugging purposes.
##
## 1.02 - Fixed a bug that miscalculated the random placing of deserts. This
## also necessitated a readjustment of the default settings.
##
## 1.01 - Added global tuning variables for easier customization. Fixed a few
## bugs that caused deserts to get out of control.
##
