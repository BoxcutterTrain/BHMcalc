###################################################
#  ____  _    _ __  __           _      
# |  _ \| |  | |  \/  |         | |     
# | |_) | |__| | \  / | ___ __ _| | ___ 
# |  _ <|  __  | |\/| |/ __/ _` | |/ __|
# | |_) | |  | | |  | | (_| (_| | | (__ 
# |____/|_|  |_|_|  |_|\___\__,_|_|\___|
# v2.0
###################################################
# 2014 [)] Jorge I. Zuluaga, Viva la BHM!
###################################################
# Radiation and Plasma Environment around Binaries
# Inputs: 
# - Binary properties (binary.conf)
# - Stars properties (<star1>.conf,<star2>.conf)
# Outputs: 
# - Binary data (rot.data)
# - Html report (rot.html)
###################################################
from BHM import *
from BHM.BHMplot import *
from BHM.BHMstars import *
from BHM.BHMplanets import *
from BHM.BHMastro import *

###################################################
#CLI ARGUMENTS
###################################################
Usage=\
"""
Usage:
   python %s <sysdir> <module>.conf <qoverride>

   <sysdir>: Directory where the system configuration files lie

   <module>.conf (file): Configuration file for the module.

   <qoverride> (int 0/1): Override any existent object with the same hash.
"""%argv[0]

sys_dir,env_conf,qover=\
    readArgs(argv,
             ["str","str","int"],
             ["sys/template","hz.conf","0"],
             Usage=Usage)

###################################################
#LOAD PREVIOUS OBJECTS
###################################################
PRINTOUT("Loading other objects...")
#==================================================
#LOADING ROTATION
rot_conf="rotation.conf"
rot,rot_dir,rot_str,rot_hash,rot_liv,rot_stg=\
    signObject("rotation",sys_dir+"/"+rot_conf)
rot+=loadConf(rot_dir+"rotation.data")
tr,bin_rot1=interpMatrix(rot.star1_binrotevol)
tr,bin_rot2=interpMatrix(rot.star2_binrotevol)
#==================================================
#LOADING IHZ
ihz_conf="hz.conf"
ihz,ihz_dir,ihz_str,ihz_hash,ihz_liv,ihz_stg=\
    signObject("hz",sys_dir+"/"+ihz_conf)
ihz+=loadConf(ihz_dir+"hz.data")
#==================================================
#LOADING STAR 1
star1_conf="star1.conf"
star1,star1_dir,star1_str,star1_hash,star1_liv,star1_stg=\
    signObject("star",sys_dir+"/"+star1_conf)
star1+=loadConf(star1_dir+"star.data")
evoInterpFunctions(star1)
#==================================================
#LOADING STAR 2
star2_conf="star2.conf"
star2,star2_dir,star2_str,star2_hash,star2_liv,star2_stg=\
    signObject("star",sys_dir+"/"+star2_conf)
star2+=loadConf(star2_dir+"star.data")
evoInterpFunctions(star2)
#==================================================
#LOADING BINARY
binary_conf="binary.conf"
binary,binary_dir,binary_str,binary_hash,binary_liv,binary_stg=\
    signObject("binary",sys_dir+"/"+binary_conf)
binary+=loadConf(binary_dir+"binary.data")
#==================================================
#LOADING PLANET
planet_conf="planet.conf"
planet,planet_dir,planet_str,planet_hash,planet_liv,planet_stg=\
    signObject("planet",sys_dir+"/"+planet_conf)
planet+=loadConf(planet_dir+"planet.data")
tp,thermevol=interpMatrix(planet.thermevol)

###################################################
#LOAD ENV OBJECT
###################################################
env,env_str,env_hash,env_dir=\
    makeObject("interaction",sys_dir+"/"+env_conf,qover=qover)
env_webdir=WEB_DIR+env_dir
PRINTOUT("Object hash:%s"%env_hash)

###################################################
#CALCULATE ENVIRONMENTAL CONDITIONS
###################################################

#### START COMMENT ####

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#FLUXES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
LumFlux Data:
0:Time, 
1:LXUV1, 2:LXUV2, 3:LXUV,
4:ntLXUV1, 5:ntLXUV2, 6:ntLXUV,
7:ntLXUV/LXUV, 8:LXUV1/LXUV,
9:FXUVin, 10:FXUVout, 11:FXUVp,
12:ntFXUVin, 13:ntFXUVout, 14:ntFXUVp,
15:FXUVins, 16:FXUVouts, 17:FXUVeeqs,
18:PSWin, 19:FSWin, 20:PSWout, 21:FSWout, 22:PSWp, 23:FSWp
24:ntPSWin, 25:ntFSWin, 26:ntPSWout, 27:ntFSWout, 28:ntPSWp, 29:ntFSWp
30:PSWins, 31:FSWins, 32:PSWouts, 33:FSWouts, 34:PSWeeqs, 35:FSWeeqs
36:Rs,37:ntRs
"""

"""
Intflux Data:
0:Time
1:FXUVin, 2:FXUVout, 3:FXUVp,
4:ntFXUVin, 5:ntFXUVout, 6:ntFXUVp,
7:FXUVins, 8:FXUVouts, 9:FXUVeeqs,
10:PSWin, 11:FSWin, 12:PSWout, 13:FSWout, 14:PSWp, 15:FSWp
16:ntPSWin, 17:ntFSWin, 18:ntPSWout, 19:ntFSWout, 20:ntPSWp, 21:ntFSWp
22:PSWins, 23:FSWins, 24:PSWouts, 25:FSWouts, 26:PSWeeqs, 27:FSWeeqs
"""

ts=chopArray(star1.evotrack[:,0],env.tauini,rot.taums)
PRINTOUT("Calculating radiation and plasma fluxes between %.3f - %.3f Gyr"%(ts[0],ts[-1]))

env.lumflux=stack(37)
for t in ts:

    #ROTATIONAL AGES
    tau_rot1=bin_rot1[1](t)
    tau_rot2=bin_rot2[1](t)

    #CUMULATOR
    lumflux=[]

    #//////////////////////////////
    #LUMINOSITIES
    #//////////////////////////////
    #INSTANTANEOUS LUMINOSITIES
    L1=star1.Lfunc(t)
    L2=star2.Lfunc(t)

    #XUV LUMINOSITIES (TIDAL)
    LXUV1=starLXUV(L1,tau_rot1)
    LXUVs=starLXUV(L1,t)
    LXUV2=starLXUV(L2,tau_rot2)
    LXUV=LXUV1+LXUV2
    lumflux+=[LXUV1,LXUV2,LXUV]

    #XUV LUMINOSITIES (NO TIDAL)
    ntLXUV1=starLXUV(L1,t)
    ntLXUV2=starLXUV(L2,t)
    ntLXUV=ntLXUV1+ntLXUV2
    lumflux+=[ntLXUV1,ntLXUV2,ntLXUV]
    
    #CORRECTING FACTORS
    facnt=ntLXUV/LXUV
    facsn=LXUVs/LXUV
    lumflux+=[facnt,facsn]
    
    #//////////////////////////////
    #XUV FLUXES
    #//////////////////////////////
    pfluxbin=LXUV/(4*np.pi*(AU*1E2)**2)/PEL

    #%%%%%%%%%%%%%%%%%%%%
    #BINARY
    #%%%%%%%%%%%%%%%%%%%%
    #INNER EDGE
    r=ihz.linwd
    FXUVin=pfluxbin/r**2
    #OUTER EDGE
    r=ihz.loutwd
    FXUVout=pfluxbin/r**2
    #PLANET
    r=planet.aorb
    FXUVp=pfluxbin/r**2
    lumflux+=[FXUVin,FXUVout,FXUVp]

    #%%%%%%%%%%%%%%%%%%%%
    #BINARY (NO TIDAL)
    #%%%%%%%%%%%%%%%%%%%%
    #INNER EDGE
    ntFXUVin=facnt*FXUVin
    #OUTER EDGE
    ntFXUVout=facnt*FXUVout
    #PLANET
    ntFXUVp=facnt*FXUVp
    lumflux+=[ntFXUVin,ntFXUVout,ntFXUVp]

    #%%%%%%%%%%%%%%%%%%%%
    #SINGLE PRIMARY
    #%%%%%%%%%%%%%%%%%%%%
    #INNER EDGE
    r=star1.lins[0]
    FXUVins=facsn*pfluxbin/r**2
    #OUTER EDGE
    r=star1.louts[-1]
    FXUVouts=facsn*pfluxbin/r**2
    #EARTH-EQUIVALENT
    r=star1.lsun
    FXUVeeqs=facsn*pfluxbin/r**2
    lumflux+=[FXUVins,FXUVouts,FXUVeeqs]
    
    #//////////////////////////////
    #STELLAR WIND
    #//////////////////////////////

    #%%%%%%%%%%%%%%%%%%%%
    #BINARY
    #%%%%%%%%%%%%%%%%%%%%
    #INNER
    r=ihz.linwd
    PSWin,FSWin=binaryWind(r,
                           tau_rot1,star1.M,star1.Rfunc(t),
                           tau_rot2,star2.M,star2.Rfunc(t),
                           early=env.str_earlywind)
    #OUTER
    r=ihz.loutwd
    PSWout,FSWout=binaryWind(r,
                             tau_rot1,star1.M,star1.Rfunc(t),
                             tau_rot2,star2.M,star2.Rfunc(t),
                             early=env.str_earlywind)
    
    #PLANET
    r=planet.aorb
    PSWp,FSWp=binaryWind(r,
                         tau_rot1,star1.M,star1.Rfunc(t),
                         tau_rot2,star2.M,star2.Rfunc(t),
                         early=env.str_earlywind)
    lumflux+=[PSWin,FSWin/SWPEL,PSWout,FSWout/SWPEL,PSWp,FSWp/SWPEL]

    #%%%%%%%%%%%%%%%%%%%%
    #NO TIDAL
    #%%%%%%%%%%%%%%%%%%%%
    tau=t

    #INNER
    r=ihz.linwd
    ntPSWin,ntFSWin=binaryWind(r,
                               tau,star1.M,star1.Rfunc(t),
                               tau,star2.M,star2.Rfunc(t),
                               early=env.str_earlywind)
    #OUTER
    r=ihz.loutwd
    ntPSWout,ntFSWout=binaryWind(r,
                                 tau,star1.M,star1.Rfunc(t),
                                 tau,star2.M,star2.Rfunc(t),
                                 early=env.str_earlywind)
    
    #PLANET
    r=planet.aorb
    ntPSWp,ntFSWp=binaryWind(r,
                             tau,star1.M,star1.Rfunc(t),
                             tau,star2.M,star2.Rfunc(t),
                             early=env.str_earlywind)
    lumflux+=[ntPSWin,ntFSWin/SWPEL,ntPSWout,ntFSWout/SWPEL,ntPSWp,ntFSWp/SWPEL]

    #%%%%%%%%%%%%%%%%%%%%
    #SINGLE STAR
    #%%%%%%%%%%%%%%%%%%%%
    tau=t
    
    #INNER
    r=star1.lins[0]
    v,n=vnGreissmeier(r,tau,star1.M,star1.Rfunc(t),early=env.str_earlywind)
    PSWins,FSWins=n*v**2,n*v

    #OUTER
    r=star1.louts[-1]
    v,n=vnGreissmeier(r,tau,star1.M,star1.Rfunc(t),early=env.str_earlywind)
    PSWouts,FSWouts=n*v**2,n*v
    
    #LSUN
    r=star1.lsun
    v,n=vnGreissmeier(r,tau,star1.M,star1.Rfunc(t),early=env.str_earlywind)
    PSWeeqs,FSWeeqs=n*v**2,n*v
    
    lumflux+=[PSWins,FSWins/SWPEL,PSWouts,FSWouts/SWPEL,PSWeeqs,FSWeeqs/SWPEL]

    #//////////////////////////////
    #STANDOFF DISTANCE
    #//////////////////////////////
    Mdip=thermevol[9](t)
    Rs=StandoffDistance(Mdip*MDIPE,PSWp,planet.R*REARTH,
                        objref=env.str_refobj,nM=env.nM,nP=env.nP)
    ntRs=StandoffDistance(Mdip*MDIPE,ntPSWp,planet.R*REARTH,
                          objref=env.str_refobj,nM=env.nM,nP=env.nP)
    lumflux+=[Rs,ntRs]

    env.lumflux+=lumflux

env.lumflux=toStack(ts)|env.lumflux

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#CUMULATIVE FLUXES
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
PRINTOUT("Calculating cumulative fluxes...")

n=len(ts)
intflux=[]
for j in xrange(9,36):
    intflux+=\
        [[trapezoidalArray(ts,env.lumflux[:,j],i) for i in xrange(n)]]

#ADD TIME COLUMN
intflux=toStack(ts)|toStack(np.transpose(intflux))

#//////////////////////////////
#MASS-LOSS
#//////////////////////////////
facabs=GYR*SWPEL
PRINTOUT("Calculating Mass-Loss...")
#MASS-LOSS IN THE PLANET
influx=np.interp(env.tauref,ts,intflux[:,15])
Mlp=massLoss(planet.A,facabs*influx,mu=env.muatm,alpha=env.alpha)
Plp=surfacePressure(Mlp,planet.M,planet.R)
#print "No tidal:",influx,Mlp,Plp,planet.A

#NO TIDAL
influx=np.interp(env.tauref,ts,intflux[:,21])
ntMlp=massLoss(planet.A,facabs*influx,mu=env.muatm,alpha=env.alpha)
ntPlp=surfacePressure(ntMlp,planet.M,planet.R)

#MASS-LOSS IN AN ENSAMBLE OF PLANETS
Mps=np.logspace(np.log10(env.Mmin),np.log10(env.Mmax),30)

"""
Mass-Loss:
0:Time
1:Mlin,2:Plin,3:Mlout,4:Plout
5:ntMlin,6:ntPlin,7:ntMlout,8:ntPlout,
9:Mlins,10:Plins,11:Mlouts,12:Plouts,13:Mleeqs,14:Pleeqs
"""
massloss=stack(14)
#Mps=[planet.M]
for Mp in Mps:
    #SIMPLIFIED PROPERTIES OF PLANETS
    Rp=Mp**0.25
    Ap=4*PI*(Rp*REARTH)**2
    
    #MASS LOSS
    #BINARY
    influx=np.interp(env.tauref,ts,intflux[:,11])
    Mlin=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    Plin=surfacePressure(Mlin,Mp,Rp)
    #print "In:",influx,Mlin,Plin,Ap

    influx=np.interp(env.tauref,ts,intflux[:,13])
    Mlout=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    Plout=surfacePressure(Mlout,Mp,Rp)

    #print "Out:",influx,Mlout,Plout,Ap
    #exit(0)

    #BINARY NO TIDAL
    influx=np.interp(env.tauref,ts,intflux[:,17])
    ntMlin=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    ntPlin=surfacePressure(ntMlin,Mp,Rp)

    influx=np.interp(env.tauref,ts,intflux[:,19])
    ntMlout=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    ntPlout=surfacePressure(ntMlout,Mp,Rp)

    #SINGLE
    influx=np.interp(env.tauref,ts,intflux[:,23])
    Mlins=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    Plins=surfacePressure(Mlins,Mp,Rp)

    influx=np.interp(env.tauref,ts,intflux[:,25])
    Mlouts=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    Plouts=surfacePressure(Mlouts,Mp,Rp)

    influx=np.interp(env.tauref,ts,intflux[:,27])
    Mleeqs=massLoss(Ap,facabs*influx,mu=env.muatm,alpha=env.alpha)
    Pleeqs=surfacePressure(Mleeqs,Mp,Rp)

    massloss+=[Mlin,Plin,Mlout,Plout,
               ntMlin,ntPlin,ntMlout,ntPlout,
               Mlins,Plins,Mlouts,Plouts,Mleeqs,Pleeqs]

massloss=toStack(Mps)|massloss

###################################################
#STORE ENVIRONMENT EVOLUTION
###################################################
env.title="$M_1/M_{\\rm Sun}=$%.3f, $M_2/M_{\\rm Sun}$=%.3f, $a_{\\rm bin}$=%.3f AU, $e_{\\rm bin}$=%.2f, $P_{\\rm bin}$=%.3f d"%(star1.M,star2.M,binary.abin,binary.ebin,binary.Pbin)

PRINTERR("Storing rotational evolution data...")
f=open(env_dir+"interaction.data","w")

f.write("""\
from numpy import array
#TITLE
title=r"%s"

#PLANETARY MASS-LOSS
Mlp=%.17e #kg
Plp=%.17e #bars
ntMlp=%.17e #kg
ntPlp=%.17e #bars

#LUMFLUX
lumflux=%s

#INTEGRATED FLUXES
intflux=%s

#MASS LOSS
massloss=%s

"""%(env.title,
     Mlp,Plp,ntMlp,ntPlp,
     array2str(env.lumflux),
     array2str(intflux),
     array2str(massloss)
     ))
f.close()

#### END COMMENT ####

###################################################
#GENERATE PLOTS
###################################################
PRINTERR("Creating plots...")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#XUV FLUX ABSOLUTE
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"flux-XUV-absolute",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")
rot=\
loadConf("%s"+"rotation.conf")+\
loadConf("%s"+"rotation.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.1,0.1,0.8,0.8])

ts=env.lumflux[:,0]
#AREAS
ax.fill_between(ts,env.lumflux[:,9],env.lumflux[:,10],color='g',alpha=0.3)
ax.fill_between(ts,env.lumflux[:,12],env.lumflux[:,13],color='r',alpha=0.3)
ax.fill_between(ts,env.lumflux[:,15],env.lumflux[:,16],color='k',alpha=0.2)
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

#PLANET
ax.plot(ts,env.lumflux[:,11],'k-',label=r'Planet $a_{\\rm p}$=%%.2f AU'%%planet.aorb)
ax.plot(ts,env.lumflux[:,14],'k--',label='Planet (no tidal)')
ax.plot(ts,env.lumflux[:,17],'k:',label='Earth-analogue single primary')

ax.set_yscale("log")
ax.set_xlim((env.tauini,rot.taums))

ax.set_title(env.title,position=(0.5,1.02),fontsize=12)
ax.legend(loc='upper right',prop=dict(size=10))

ax.set_xlabel(r"$\\tau$ (Gyr)")
ax.set_ylabel(r"$F_{\\rm XUV}$ (PEL)")
"""%(env_dir,env_dir,
     planet_dir,planet_dir,
     rot_dir,rot_dir
     ),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#SW FLUX ABSOLUTE
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"flux-SW-absolute",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")
rot=\
loadConf("%s"+"rotation.conf")+\
loadConf("%s"+"rotation.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.1,0.1,0.8,0.8])

ts=env.lumflux[:,0]

#AREAS
ax.fill_between(ts,env.lumflux[:,19],env.lumflux[:,21],color='g',alpha=0.3,label='Tidal')
ax.fill_between(ts,env.lumflux[:,25],env.lumflux[:,27],color='r',alpha=0.3,label='No tidal')
ax.fill_between(ts,env.lumflux[:,31],env.lumflux[:,33],color='k',alpha=0.2,label='Single Primary')
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

ax.plot(ts,env.lumflux[:,23],'k-',label=r'Planet $a_{\\rm p}$=%%.2f AU'%%planet.aorb)
ax.plot(ts,env.lumflux[:,29],'k--',label='Planet (no tidal)')
ax.plot(ts,env.lumflux[:,35],'k:',label='Earth-analogue single primary')

ax.set_yscale("log")
ax.set_xlim((env.tauini,rot.taums))

ax.set_title(env.title,position=(0.5,1.02),fontsize=12)
ax.legend(loc='upper right',prop=dict(size=10))
ax.set_xlabel(r"$\\tau$ (Gyr)")
ax.set_ylabel(r"$F_{\\rm SW}$ (PEL)")
"""%(env_dir,env_dir,
     planet_dir,planet_dir,
     rot_dir,rot_dir
     ),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#INTEGRATED FXUV
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"int-XUV-absolute",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")
rot=\
loadConf("%s"+"rotation.conf")+\
loadConf("%s"+"rotation.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.14,0.1,0.80,0.8])

ts=env.intflux[:,0]

#RANGES
facabs=GYR*PELSI
arrs=[facabs*env.intflux[:,1],facabs*env.intflux[:,2]]
ax.fill_between(ts,facabs*env.intflux[:,1],facabs*env.intflux[:,2],color='g',alpha=0.3,label='Tidal')
arrs+=[facabs*env.intflux[:,4],facabs*env.intflux[:,8]]
ax.fill_between(ts,facabs*env.intflux[:,4],facabs*env.intflux[:,5],color='r',alpha=0.3,label='No tidal')
arrs+=[facabs*env.intflux[:,7],facabs*env.intflux[:,8]]
ax.fill_between(ts,facabs*env.intflux[:,7],facabs*env.intflux[:,8],color='k',alpha=0.2,label='Single Primary')
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

#PLANET
arrs+=[facabs*env.intflux[:,3],facabs*env.intflux[:,6]]
ax.plot(ts,facabs*env.intflux[:,3],'k-',label=r'Planet $a_{\\rm p}$=%%.2f AU'%%planet.aorb)
ax.plot(ts,facabs*env.intflux[:,6],'k--',label='Planet (no tidal)')
ax.plot(ts,facabs*env.intflux[:,9],'k:',label='Earth-analogue single primary')

ymin,ymean,ymax=minmeanmaxArrays(arrs)
expscl=int(np.log10(ymax))
scl=10**expscl

ax.set_yscale("log")
ax.set_title(env.title,position=(0.5,1.02),fontsize=12)
ax.legend(loc='lower right',prop=dict(size=10))
ax.set_xlabel(r"$\\tau$ (Gyr)")
ax.set_ylabel(r"$\int_{%%.2f\,{\\rm Gyr}}^{\\tau} F_{\\rm XUV}(t)\,dt$ (${\\rm j/m}^2$)"%%(env.tauini))
# \\times 10^{%%d}\,
# yt=ax.get_yticks()
# yl=[]
# for y in yt:
#     iy=np.log10(y/scl) 
#     if iy==0:yl+=["$1$"]
#     else:yl+=["$10^{%%d}$"%%(iy)]
# ax.set_yticklabels(yl)

ax.set_ylim((max(ymin,ymean/10),ymax))
ax.set_xlim((env.tauini,rot.taums))
"""%(env_dir,env_dir,
     planet_dir,planet_dir,
     rot_dir,rot_dir
     ),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#INTEGRATED SW
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"int-SW-absolute",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")
rot=\
loadConf("%s"+"rotation.conf")+\
loadConf("%s"+"rotation.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.14,0.1,0.80,0.8])

ts=env.intflux[:,0]
facabs=GYR*SWPEL

#RANGES
arrs=[facabs*env.intflux[:,11],facabs*env.intflux[:,13]]
ax.fill_between(ts,facabs*env.intflux[:,11],facabs*env.intflux[:,13],color='g',alpha=0.3,label='Tidal')
arrs+=[facabs*env.intflux[:,17],facabs*env.intflux[:,19]]
ax.fill_between(ts,facabs*env.intflux[:,17],facabs*env.intflux[:,19],color='r',alpha=0.3,label='No tidal')
arrs+=[facabs*env.intflux[:,23],facabs*env.intflux[:,25]]
ax.fill_between(ts,facabs*env.intflux[:,23],facabs*env.intflux[:,25],color='k',alpha=0.2,label='Single Primary')
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

#PLANET
arrs+=[facabs*env.intflux[:,15],facabs*env.intflux[:,21]]
ax.plot(ts,facabs*env.intflux[:,15],'k-',label=r'Planet $a_{\\rm p}$=%%.2f AU'%%planet.aorb)
ax.plot(ts,facabs*env.intflux[:,21],'k--',label='Planet (no tidal)')
ax.plot(ts,facabs*env.intflux[:,27],'k:',label='Earth-analogue single primary')

ymin,ymean,ymax=minmeanmaxArrays(arrs)
expscl=int(np.log10(ymax))
scl=10**expscl

ax.set_yscale("log")
ax.set_title(env.title,position=(0.5,1.02),fontsize=12)
ax.legend(loc='lower right',prop=dict(size=10))
ax.set_xlabel(r"$\\tau$ (Gyr)")
ax.set_ylabel(r"$\int_{%%.2f\,{\\rm Gyr}}^{\\tau} F_{\\rm SW}(t)\,dt$ (${\\rm ions/m}^2$)"%%(env.tauini))
# $\\times 10^{%%d}\,
# yt=ax.get_yticks()
# yl=[]
# for y in yt:
#     iy=np.log10(y/scl) 
#     if iy==0:yl+=["$1$"]
#     else:yl+=["$10^{%%d}$"%%(iy)]
# ax.set_yticklabels(yl)

ax.set_ylim((max(ymin,ymean/10),ymax))
ax.set_xlim((env.tauini,rot.taums))
"""%(env_dir,env_dir,
     planet_dir,planet_dir,
     rot_dir,rot_dir
     ),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#STANDOFF DISTANCE
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"standoff-distance",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.1,0.1,0.8,0.8])

ts=env.lumflux[:,0]

ax.plot(ts,env.lumflux[:,36],'k-',label='Tidal')
ax.plot(ts,env.lumflux[:,37],'k--',label='No Tidal')

ax.text(0.05,0.05,planet.orbit,transform=ax.transAxes)
ax.set_title(env.title,position=(0.5,1.02),fontsize=12)
ax.legend(loc='lower right',prop=dict(size=10))
ax.set_xlabel(r"$\\tau$ (Gyr)")
ax.set_ylabel(r"$R_{\\rm S}/R_{\\rm p}$")

#ymin,ymean,ymax=minmeanmaxArrays(arrs)
#ax.set_xlim((max(ymin,ymean/10),ymax))
"""%(env_dir,env_dir,
     planet_dir,planet_dir),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#MASS-LOSS (BARS)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"mass-loss-absolute",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.1,0.1,0.8,0.8])

Mps=env.massloss[:,0]
ax.fill_between(Mps,env.massloss[:,2],env.massloss[:,4],color='g',alpha=0.3)
ax.fill_between(Mps,env.massloss[:,6],env.massloss[:,8],color='r',alpha=0.3)
ax.fill_between(Mps,env.massloss[:,10],env.massloss[:,12],color='k',alpha=0.3)
ax.plot(Mps,env.massloss[:,14],'k:',label="Earth-analogue single primary")
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

#PLANET
ax.plot([planet.M],[env.Plp],'o',color='b',markeredgecolor='none',label=r"Planet, $a_{\\rm orb}$=%%.2f"%%(planet.aorb))
ax.plot([planet.M],[env.ntPlp],'s',color='r',markeredgecolor='none',label="Planet (No tidal)")

ax.set_title(env.title,position=(0.5,1.02),fontsize=12)

ax.set_xlabel(r"$M_{\\rm p}/M_{\\rm Earth}$")
ax.set_ylabel(r"$P_{\\rm loss}$ (bars)")

pmass=[MGANYMEDE,MMERCURY,MMARS,MVENUS]
pnames=["Ganymede","Mercury","Mars","Venus"]
for Mp,name in zip(pmass,pnames):
    fp=Mp/MEARTH
    fpt=(np.log10(fp)+2)/3.0-0.01
    plt.axvline(fp,color='b')
    plt.text(fpt,0.02,name,
             rotation=90,
             horizontalalignment='right',
             verticalalignment='bottom',
             #bbox=dict(fc='w',ec='none'),
             transform=plt.gca().transAxes)

ax.legend(loc='lower right',prop=dict(size=10))
ax.set_xscale("log")
ax.set_yscale("log")
"""%(env_dir,env_dir,
     planet_dir,planet_dir),
           watermarkpos='outer')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#MASS-LOSS (RELATIVE)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
plotFigure(env_dir,"mass-loss-relative",\
"""
from BHM.BHMstars import *
env=\
loadConf("%s"+"interaction.conf")+\
loadConf("%s"+"interaction.data")
planet=\
loadConf("%s"+"planet.conf")+\
loadConf("%s"+"planet.data")

fig=plt.figure(figsize=(8,6))
ax=fig.add_axes([0.1,0.1,0.8,0.8])

Mps=env.massloss[:,0]
ax.fill_between(Mps,env.massloss[:,1]/MEARTH/Mps,env.massloss[:,3]/MEARTH/Mps,color='g',alpha=0.3)
ax.fill_between(Mps,env.massloss[:,5]/MEARTH/Mps,env.massloss[:,7]/MEARTH/Mps,color='r',alpha=0.3)
ax.fill_between(Mps,env.massloss[:,9]/MEARTH/Mps,env.massloss[:,11]/MEARTH/Mps,color='k',alpha=0.3)
ax.plot(Mps,env.massloss[:,13]/MEARTH/Mps,'k:',label="Earth-analogue single primary")
ax.plot([0],[0],color='g',alpha=0.3,linewidth=10,label='Tidal')
ax.plot([0],[0],color='r',alpha=0.3,linewidth=10,label='No Tidal')
ax.plot([0],[0],color='k',alpha=0.3,linewidth=10,label='Single Primary')

#PLANET
ax.plot([planet.M],[env.Mlp/MEARTH/planet.M],'o',color='b',markeredgecolor='none',label=r"Planet, $a_{\\rm orb}$=%%.2f"%%(planet.aorb))
ax.plot([planet.M],[env.ntMlp/MEARTH/planet.M],'s',color='r',markeredgecolor='none',label="Planet (No tidal)")

ax.set_title(env.title,position=(0.5,1.02),fontsize=12)

ax.set_xlabel(r"$M_{\\rm p}/M_{\\rm Earth}$")
ax.set_ylabel(r"$M_{\\rm loss}/M_{\\rm Earth}$")

pmass=[MGANYMEDE,MMERCURY,MMARS,MVENUS]
pnames=["Ganymede","Mercury","Mars","Venus"]
for Mp,name in zip(pmass,pnames):
    fp=Mp/MEARTH
    fpt=(np.log10(fp)+2)/3.0-0.01
    plt.axvline(fp,color='b')
    plt.text(fpt,0.02,name,
             rotation=90,
             horizontalalignment='right',
             verticalalignment='bottom',
             #bbox=dict(fc='w',ec='none'),
             transform=plt.gca().transAxes)

ax.legend(loc='upper right',prop=dict(size=10))
ax.set_xscale("log")
ax.set_yscale("log")
"""%(env_dir,env_dir,
     planet_dir,planet_dir),
           watermarkpos='outer')

###################################################
#GENERATE FULL REPORT
###################################################
PRINTERR("Creating html report...")

fh=open(env_dir+"interaction.html","w")
fh.write("""\
<head>
  <link rel="stylesheet" type="text/css" href="%s/web/BHM.css">
</head>
<h2>Binary-Planet Interaction</h2>
<center>
  <a target="_blank" href="%s/flux-XUV-absolute.png">
    <img width=60%% src="%s/flux-XUV-absolute.png">
  </a>
  <br/>
  <i>Evolution of XUV flux</i>
  (
  <a target="_blank" href="%s/flux-XUV-absolute.png.txt">data</a>|
  <a target="_blank" href="%s/web/replot.php?plot=flux-XUV-absolute.py">replot</a>
  )
</center>
<h3>XUV Flux</h3>
<table>
  <tr><td>
      <a href="%s/flux-XUV-absolute.png" target="_blank">
	<img width=100%% src="%s/flux-XUV-absolute.png">
      </a>
      <br/>
      <i>XUV Flux (absolute)</i>
	(
	<a href="%s/flux-XUV-absolute.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=flux-XUV-absolute.py" target="_blank">replot</a>
	)
  </td></tr>
  <tr><td>
      <a href="%s/int-XUV-absolute.png" target="_blank">
	<img width=100%% src="%s/int-XUV-absolute.png">
      </a>
      <br/>
      <i>Integrated XUV Flux (absolute)</i>
	(
	<a href="%s/int-XUV-absolute.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=int-XUV-absolute.py" target="_blank">replot</a>
	)
  </td></tr>
</table>
<h3>Stellar Wind Flux</h3>
<table>
  <tr><td>
      <a href="%s/flux-SW-absolute.png" target="_blank">
	<img width=100%% src="%s/flux-SW-absolute.png">
      </a>
      <br/>
      <i>SW Flux (absolute)</i>
	(
	<a href="%s/flux-SW-absolute.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=flux-SW-absolute.py" target="_blank">replot</a>
	)
  </td></tr>
  <tr><td>
      <a href="%s/int-SW-absolute.png" target="_blank">
	<img width=100%% src="%s/int-SW-absolute.png">
      </a>
      <br/>
      <i>Integrated SW Flux (absolute)</i>
	(
	<a href="%s/int-SW-absolute.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=int-SW-absolute.py" target="_blank">replot</a>
	)
  </td></tr>
</table>
<h3>Standoff distance</h3>
<table>
  <tr><td>
      <a href="%s/standoff-distance.png" target="_blank">
	<img width=100%% src="%s/standoff-distance.png">
      </a>
      <br/>
      <i>Standoff Distance</i>
	(
	<a href="%s/standoff-distance.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=standoff-distance.py" target="_blank">replot</a>
	)
  </td></tr>
</table>
<h3>Mass-loss</h3>
<table>
  <tr><td>M<sub>loss,planet</sub> (Tidal, kg):</td><td>%.3f</td></tr>
  <tr><td>P<sub>loss,planet</sub> (Tidal, bars):</td><td>%.3f</td></tr>
  <tr><td>M<sub>loss,planet</sub> (No tidal, kg):</td><td>%.3f</td></tr>
  <tr><td>P<sub>loss,planet</sub> (No tidal, bars):</td><td>%.3f</td></tr>
  <tr><td>
      <a href="%s/mass-loss-absolute.png" target="_blank">
	<img width=100%% src="%s/mass-loss-absolute.png">
      </a>
      <br/>
      <i>Mass-loss (absolute)</i>
	(
	<a href="%s/mass-loss-absolute.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=mass-loss-absolute.py" target="_blank">replot</a>
	)
  </td></tr>
  <tr><td>
      <a href="%s/mass-loss-relative.png" target="_blank">
	<img width=100%% src="%s/mass-loss-relative.png">
      </a>
      <br/>
      <i>Mass-loss (absolute)</i>
	(
	<a href="%s/mass-loss-relative.png.txt" target="_blank">data</a>|
	<a href="%s/web/replot.php?plot=mass-loss-relative.py" target="_blank">replot</a>
	)
  </td></tr>
</table>
"""%(WEB_DIR,env_webdir,env_webdir,env_webdir,WEB_DIR,#FLUX XUV ABSOLUTE (INTRO)
     env_webdir,env_webdir,env_webdir,WEB_DIR,#FLUX XUV ABSOLUTE
     env_webdir,env_webdir,env_webdir,WEB_DIR,#INT XUV ABSOLUTE
     env_webdir,env_webdir,env_webdir,WEB_DIR,#FLUX SW ABSOLUTE
     env_webdir,env_webdir,env_webdir,WEB_DIR,#INT SW ABSOLUTE
     env_webdir,env_webdir,env_webdir,WEB_DIR,#STANDOFF DISTANCE
     Mlp,Plp,ntMlp,ntPlp,
     env_webdir,env_webdir,env_webdir,WEB_DIR,#MASS-LOSS ABSOLUTE
     env_webdir,env_webdir,env_webdir,WEB_DIR#MASS-LOSS RELATIVE
     ))
fh.close()

###################################################
#CLOSE OBJECT
###################################################
closeObject(env_dir)
