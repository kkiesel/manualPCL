#-- Common selection based on CRUZET 2015 Setup mp1553

import FWCore.ParameterSet.Config as cms
#from Configuration.AlCa.autoCond import *

process = cms.Process("Alignment")



process.options = cms.untracked.PSet(
    Rethrow = cms.untracked.vstring("ProductNotFound"), # do not accept this exception
    wantSummary = cms.untracked.bool(True)
    )

# initialize  MessageLogger
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.destinations = ['alignment']
process.MessageLogger.statistics = ['alignment']
process.MessageLogger.categories = ['Alignment']
process.MessageLogger.alignment = cms.untracked.PSet(
    DEBUG = cms.untracked.PSet(
        limit = cms.untracked.int32(-1)
        ),
    INFO = cms.untracked.PSet(
        limit = cms.untracked.int32(-1)
        ),
    WARNING = cms.untracked.PSet(
        limit = cms.untracked.int32(10)
        ),
    ERROR = cms.untracked.PSet(
        limit = cms.untracked.int32(-1)
        ),
    Alignment = cms.untracked.PSet(
        limit = cms.untracked.int32(-1),
        )
    )


process.MessageLogger.cerr.placeholder = cms.untracked.bool(True)
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )


#-- Magnetic field
process.load('Configuration.StandardSequences.MagneticField_cff')
#process.load("Configuration/StandardSequences/MagneticField_38T_cff") ## FOR 3.8T
#process.load("Configuration.StandardSequences.MagneticField_0T_cff")  ## FOR 0T

#-- Load geometry
process.load("Configuration.Geometry.GeometryRecoDB_cff")

#-- Global Tag
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.connect = "frontier://FrontierProd/CMS_CONDITIONS"
process.GlobalTag.globaltag = "${globalTag}"
process.GlobalTag.toGet.append(
    cms.PSet(
        connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS"),
        record = cms.string('TrackerAlignmentRcd'),
        tag = cms.string('TrackerAlignment_v17_offline'),
        )
    )

#-- initialize beam spot
process.load("RecoVertex.BeamSpotProducer.BeamSpot_cfi")

#-- Set APEs to ZERO
import CalibTracker.Configuration.Common.PoolDBESSource_cfi
process.conditionsInTrackerAlignmentErrorRcd = CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
    connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
    toGet = cms.VPSet(
        cms.PSet(
            record = cms.string('TrackerAlignmentErrorExtendedRcd'),
            tag = cms.string('TrackerIdealGeometryErrorsExtended210_mc')
            )
        )
    )
process.prefer_conditionsInTrackerAlignmentErrorRcd = cms.ESPrefer("PoolDBESSource", "conditionsInTrackerAlignmentErrorRcd")

## SiStrip BackPlane corrections
#process.conditionsInSiStripBackPlaneCorrectionRcd = CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
#     connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
#     toGet = cms.VPSet(
#         cms.PSet(
#             record = cms.string('SiStripBackPlaneCorrectionRcd'),
#             tag = cms.string('SiStripBackPlaneCorrection_deco_GR10_v4_offline'),
#             label = cms.untracked.string('deconvolution')
#             )
#         )
#      )

#process.prefer_conditionsInSiStripBackPlaneCorrectionRcd = cms.ESPrefer("PoolDBESSource", "conditionsInSiStripBackPlaneCorrectionRcd")

## SiStrip Lorentz Angle corrections
#process.conditionsInSiStripLorentzAngleRcd = CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
#     connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
#     toGet = cms.VPSet(
#         cms.PSet(
#             record = cms.string('SiStripLorentzAngleRcd'),
#             tag = cms.string('SiStripLorentzAngleDeco_v3_offline'),
#             label = cms.untracked.string('deconvolution')
#             )
#         )
#     )

#process.prefer_conditionsInSiStripLorentzAngleRcd = cms.ESPrefer("PoolDBESSource", "conditionsInSiStripLorentzAngleRcd")

#process.newPixelTemplates = CalibTracker.Configuration.Common.PoolDBESSource_cfi.poolDBESSource.clone(
#     toGet = cms.VPSet(
#         cms.PSet(
#            record = cms.string('SiPixelTemplateDBObjectRcd'),
#            connect = cms.untracked.string("sqlite_file:/afs/cern.ch/user/d/dkotlins/public/CMSSW/DB/310815/SiPixelTemplateDBObject_38T_2015_v3.db"),
#            tag = cms.string('SiPixelTemplateDBObject38Tv10')
#            )
#         )
#     )

#process.prefer_conditionsInSiPixelTemplateDBObjectRcd = cms.ESPrefer("PoolDBESSource", "newPixelTemplates")

#-- Load Local Alignment Object
#process.GlobalTag.toGet = cms.VPSet(
#    cms.PSet(record = cms.string("TrackerAlignmentRcd"),
#             tag = cms.string("Alignments"),
#             connect = cms.untracked.string("sqlite_file:/afs/cern.ch/cms/CAF/CMSALCA/ALCA_TRACKERALIGN2/HIP/cayou/CMSSW_7_4_6_patch5/src/Alignment/HIPAlignmentAlgorithm/hp1400/alignments_iter20.db")
#             )
#    )

magnetOn = ${magneticFieldOn}
cosmics = ${cosmics}
#-- AlignmentTrackSelector
import Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi
if not cosmics:
    if magnetOn:
        process.HighPuritySelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
            applyBasicCuts = True,
            #filter = True,
            src = 'ALCARECOTkAlMinBias',
            trackQualities = ["highPurity"],
            pMin = 4. #for 3.8T Collisions
            )
    else:
        process.HighPuritySelector = Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi.AlignmentTrackSelector.clone(
            applyBasicCuts = True,
            #filter = True,
            src = 'ALCARECOTkAlMinBias',
            trackQualities = ["highPurity"],
            pMin = 4.9, #for 0T Collisions
            pMax = 5.1, #for 0T Collisions
            )

process.load("Alignment.CommonAlignmentProducer.AlignmentTrackSelector_cfi")
process.AlignmentTrackSelector.src = 'HitFilteredTracks' # adjust to input file
process.AlignmentTrackSelector.applyBasicCuts = True
if magnetOn:
    if cosmics:
        process.AlignmentTrackSelector.pMin = 4. #for 3.8T Collisions
    else:
        process.AlignmentTrackSelector.pMin = 8. #for 3.8T Collisions
    process.AlignmentTrackSelector.ptMin = 1.0 #for 3.8T Collisions
else:
    process.AlignmentTrackSelector.pMin = 4.9  #for 0T Collisions
    process.AlignmentTrackSelector.pMax = 5.1 #for 0T Collisions
    process.AlignmentTrackSelector.ptMin = 0. #for 0T Collisions
process.AlignmentTrackSelector.etaMin = -999.
process.AlignmentTrackSelector.etaMax = 999.
process.AlignmentTrackSelector.nHitMin = 8
process.AlignmentTrackSelector.nHitMin2D = 2
process.AlignmentTrackSelector.chi2nMax = 9999.
if cosmics:
    process.AlignmentTrackSelector.applyMultiplicityFilter = True
else:
    process.AlignmentTrackSelector.applyMultiplicityFilter = False
process.AlignmentTrackSelector.maxMultiplicity = 1
process.AlignmentTrackSelector.applyNHighestPt = False
process.AlignmentTrackSelector.nHighestPt = 1
process.AlignmentTrackSelector.seedOnlyFrom = 0
process.AlignmentTrackSelector.applyIsolationCut = False
process.AlignmentTrackSelector.minHitIsolation = 0.8
process.AlignmentTrackSelector.applyChargeCheck = False
if cosmics:
    process.AlignmentTrackSelector.minHitChargeStrip = 50.
else:
    process.AlignmentTrackSelector.minHitChargeStrip = 30.
#Special option for PCL
process.AlignmentTrackSelector.minHitsPerSubDet.inPIXEL = 2


#-- new track hit filter
# TrackerTrackHitFilter takes as input the tracks/trajectories coming out from TrackRefitter1
process.load("RecoTracker.FinalTrackSelectors.TrackerTrackHitFilter_cff")
process.TrackerTrackHitFilter.src = 'TrackRefitter1'
process.TrackerTrackHitFilter.useTrajectories= True  # this is needed only if you require some selections; but it will work even if you don't ask for them
process.TrackerTrackHitFilter.minimumHits = 8
process.TrackerTrackHitFilter.replaceWithInactiveHits = True
process.TrackerTrackHitFilter.rejectBadStoNHits = True
process.TrackerTrackHitFilter.commands = cms.vstring("keep PXB","keep PXE","keep TIB","keep TID","keep TOB","keep TEC")#,"drop TID stereo","drop TEC stereo")
process.TrackerTrackHitFilter.stripAllInvalidHits = False
process.TrackerTrackHitFilter.StoNcommands = cms.vstring("ALL 12.0")
process.TrackerTrackHitFilter.rejectLowAngleHits = True
if cosmics:
    process.TrackerTrackHitFilter.TrackAngleCut = 0.35# in rads, starting from the module surface; .35 for cosmcics ok, .17 for collision tracks
else:
    process.TrackerTrackHitFilter.TrackAngleCut = 0.17# in rads, starting from the module surface; .35 for cosmcics ok, .17 for collision tracks
process.TrackerTrackHitFilter.usePixelQualityFlag = True #False

#-- TrackFitter
import RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cff
process.HitFilteredTracks = RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cff.ctfWithMaterialTracks.clone(
           src = 'TrackerTrackHitFilter',
        TrajectoryInEvent = True,
        TTRHBuilder = 'WithAngleAndTemplate', #should already be default
        NavigationSchool = cms.string('')
)

#-- Alignment producer
process.load("Alignment.CommonAlignmentProducer.TrackerAlignmentProducerForPCL_cff")
process.AlignmentProducer.ParameterBuilder.Selector = cms.PSet(
    alignParams = cms.vstring(
        'TrackerTPBHalfBarrel,111111',
        'TrackerTPEHalfCylinder,111111',

        'TrackerTIBHalfBarrel,ffffff',
        'TrackerTOBHalfBarrel,ffffff',
        'TrackerTIDEndcap,ffffff',
        'TrackerTECEndcap,ffffff'
        )
    )

process.AlignmentProducer.doMisalignmentScenario = False #True


process.AlignmentProducer.checkDbAlignmentValidity = False
process.AlignmentProducer.applyDbAlignment = True
process.AlignmentProducer.tjTkAssociationMapTag = 'TrackRefitter2'

process.AlignmentProducer.algoConfig = process.MillePedeAlignmentAlgorithm
process.AlignmentProducer.algoConfig.mode = 'pede'
process.AlignmentProducer.algoConfig.mergeBinaryFiles = [${mergeBinaryFiles}]
process.AlignmentProducer.algoConfig.binaryFile = ''
if magnetOn:
    process.AlignmentProducer.algoConfig.TrajectoryFactory = cms.PSet(
          process.BrokenLinesTrajectoryFactory #for 3.8T Collisions
          )

else:
    process.AlignmentProducer.algoConfig.TrajectoryFactory = cms.PSet(
          process.BrokenLinesBzeroTrajectoryFactory #for 0T Collisions
          )
    process.AlignmentProducer.algoConfig.TrajectoryFactory.MomentumEstimate = 5 #for 0T Collisions

process.AlignmentProducer.algoConfig.pedeSteerer.pedeCommand = 'pede'
process.AlignmentProducer.algoConfig.pedeSteerer.method = 'inversion  5  0.8'
process.AlignmentProducer.algoConfig.pedeSteerer.options = cms.vstring(
    #'regularisation 1.0 0.05', # non-stated pre-sigma 50 mrad or 500 mum
     'entries 500',
     'chisqcut  30.0  4.5', #,
     'threads 1 1' #,
     #'outlierdownweighting 3','dwfractioncut 0.1'
     #'outlierdownweighting 5','dwfractioncut 0.2'
    )
process.AlignmentProducer.algoConfig.minNumHits = 10



#-- TrackRefitter
if not cosmics:
    process.load("RecoTracker.TrackProducer.TrackRefitters_cff")
    process.TrackRefitter1 = RecoTracker.TrackProducer.TrackRefitter_cfi.TrackRefitter.clone(
        src ='HighPuritySelector',#'ALCARECOTkAlMinBias',
        NavigationSchool = cms.string(''),
        TrajectoryInEvent = True,
        TTRHBuilder = "WithAngleAndTemplate" #default
        )
else:
    process.load("RecoTracker.TrackProducer.TrackRefitters_cff")
    process.TrackRefitter1 = RecoTracker.TrackProducer.TrackRefitter_cfi.TrackRefitter.clone(
        src ='ALCARECOTkAlCosmicsCTF0T',#'ALCARECOTkAlMinBias',
        NavigationSchool = cms.string(''),
        TrajectoryInEvent = True,
        TTRHBuilder = "WithAngleAndTemplate" #default
        )
process.TrackRefitter2 = process.TrackRefitter1.clone(
    src = 'AlignmentTrackSelector',
#    TTRHBuilder = 'WithTrackAngle'
    )

process.source = cms.Source("PoolSource",
    secondaryFileNames = cms.untracked.vstring(),
    fileNames = cms.untracked.vstring(
            [${input}],
    ),
)
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

#process.dump = cms.EDAnalyzer("EventContentAnalyzer")
#process.p  = cms.Path(process.dump)

if not cosmics:
    process.p = cms.Path(process.HighPuritySelector
                 *process.offlineBeamSpot
                     *process.TrackRefitter1
                     *process.TrackerTrackHitFilter
                     *process.HitFilteredTracks
                     *process.AlignmentTrackSelector
                     *process.TrackRefitter2
                     *process.AlignmentProducer
                     )
else:
    process.p = cms.Path(process.offlineBeamSpot
                     *process.TrackRefitter1
                     *process.TrackerTrackHitFilter
                     *process.HitFilteredTracks
                     *process.AlignmentTrackSelector
                     *process.TrackRefitter2
                     *process.AlignmentProducer
                     )

process.AlignmentProducer.saveToDB = True
from CondCore.DBCommon.CondDBSetup_cfi import *
process.PoolDBOutputService = cms.Service(
        "PoolDBOutputService",
            CondDBSetup,
            connect = cms.string('sqlite_file:TkAlignment.db'),
            toPut = cms.VPSet(cms.PSet(
                record = cms.string('TrackerAlignmentRcd'),
                tag = cms.string('testTag')
            )#,
                              #     #                  cms.PSet(
                              #     #  record = cms.string('TrackerAlignmentErrorRcd'),
                              #     #  tag = cms.string('testTagAPE') # needed is saveApeToDB = True
                              #     #)
                                                     )
            )




# MPS needs next line as placeholder for pede _cfg.py:
#MILLEPEDEBLOCK
