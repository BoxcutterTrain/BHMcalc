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
# Stellar evolution routines
###################################################
from BHM import *
from BHM.BHMnum import *
from BHM.BHMboreas import pyBoreas

###################################################
#PACKAGES
###################################################

###################################################
#CONFIGURATION
###################################################
ZSVEC_DEF="ZSVEC_siblings"
NTIMES=100

###################################################
#MACROS
###################################################
RHO_COL=1
TEFF_COL=2
RAD_COL=3
LUM_COL=4

###################################################
#GLOBALS
###################################################
SMset=[]
Zset=[]
SMglob=dict2obj(dict())
ZSVEC_full=np.array([
        0.0001,0.0002,0.0004,0.0006,0.0008,
        0.0010,0.0020,0.0030,0.0040,0.0050,0.0060,0.0070,0.0080,0.0090,
        0.0100,0.0125,0.0150,0.0175,
        0.0200,0.0225,0.0250,0.0275,
        0.0300,0.0325,0.0350,0.0375,
        0.0400,0.0425,0.0450,0.0475,
        0.0500,0.0525,0.0550,0.0575,
        0.0600
        ])
ZSVEC_coarse=np.array([0.0001,0.0010,0.0050,0.0100,0.0152,0.0200,0.0300,0.0400,0.0500,0.0600])
ZSVEC_siblings=np.array([0.0100,0.0152,0.0200])
ZSVEC_solar=np.array([0.0152])

ROTAGE_STARS={r"Sun":dict(FeH=0.0,M=1.0,tau=4.56,Prot=25.4,up=5),
              r"Proxima":dict(FeH=+0.21,M=0.123,tau=6.0,Prot=83.5,up=10),
              r"Barnard":dict(FeH=-0.39,M=0.144,tau=10.0,Prot=130.4,up=-10),
              r"EK Dra":dict(FeH=0.00,M=1.06,tau=0.1,Prot=2.68,up=10),
              r"$\pi^1$ UMi":dict(FeH=0.00,M=1.03,tau=0.3,Prot=4.90,up=10),
              r"$\kappa^1$ Cet":dict(FeH=0.00,M=1.02,tau=0.65,Prot=9.21,up=10),
              r"$\beta$ Com":dict(FeH=0.00,M=1.10,tau=1.6,Prot=12.00,up=10),
              r"$\beta$ Hyi":dict(FeH=0.00,M=1.10,tau=6.7,Prot=28.00,up=10)
              }

###################################################
#ROUTINES
###################################################
def chooseZsvecSingle(Z):
    ZF=ZSVEC_full
    Z1=ZF[ZF<=Z][-1]
    Z2=ZF[ZF>Z][0]
    Zs=np.array([Z1,Z2])
    return Zs

def chooseZsvec(Z,zsdef=ZSVEC_DEF):
    #ZSs=["ZSVEC_siblings","ZSVEC_coarse","ZSVEC_full"]
    ZSs=["ZSVEC_siblings","ZSVEC_coarse"]
    qoutdef=False;qoutoth=False
    #if Z==ZSVEC_solar[0]:zsvec="ZSVEC_solar"
    if False:pass
    else:
        zsvec=zsdef
        for ZS in ZSs:
            exec("Zvec=%s[%s==Z]"%(ZS,ZS))
            if len(Zvec)>0:
                zsvec=ZS
                qoutdef=False
                break                
            exec("lzsvec=len(%s)"%(ZS))
            exec("lzgrea=len(%s[%s>Z])"%(ZS,ZS))
            if lzgrea==0 or lzgrea==lzsvec:
                if ZS==zsdef:
                    qoutdef=True
            else:
                qoutoth=True
                zsvecoth=ZS
    if qoutdef:
        if qoutoth:zsvec=zsvecoth
        else:
            PRINTERR("No isochrone found for Z = %.5f"%(Z))
            errorCode("DATA_ERROR")
    return zsvec

def PropertySet(Ms,age,prop,iiso):
    if age<0:return -1
    global SMset

    SMiso=SMset[iiso]
    age=np.log10(age*1E9)
    id=np.arange(0,SMiso.nAges)
    iage=id[SMiso.Ages==age]
    
    if len(iage):
        iage=iage[0]
        try:
            p=eval("SMiso.%sint[iage](Ms)"%prop)
        except:
            p=-1
    else:
        lages=id[SMiso.Ages<=age]
        gages=id[SMiso.Ages>age]

        try:
            iless=lages[-1]
            igreat=gages[0]
            t1=SMiso.Ages[iless]
            t2=SMiso.Ages[igreat]
            try:
                p1=eval("SMiso.%sint[iless](Ms)"%prop)
                p2=eval("SMiso.%sint[igreat](Ms)"%prop)
                p=p1+(p2-p1)/(t2-t1)*(age-t1)
            except:
                p=-1
        except:
            p=-1

    return p

def StellarPropertyNorm(prop,Z,Ms,tau,norm=True):
    val=StellarProperty(prop,Z,Ms,tau)
    if not norm:return val
    if prop=='Temperature':
        val=(val-SMglob.Tsun)+TSUN
    elif prop=='Radius':
        val=(val/SMglob.Rsun)
    elif prop=='Luminosity':
        val=(val/SMglob.Lsun)
    return val

def StellarProperty(prop,Z,Ms,tau):
    global SMset
    num=len(SMset)
    ps=[]
    Zs=[]
    for i in xrange(0,num):
        Zi=Zset[i]
        exec "p=SMset[i].%s(Ms,tau)"%prop in globals(),locals()
        if p==-1:
            #print "Property '%s' calculated at Z = %f, Ms = %f, tau = %f is null"%(prop,Zi,Ms,tau)
            pass
        else:
            Zs+=[Zi]
            ps+=[p]
    try:
        func=interp1d(Zs,ps,kind='slinear')
        val=func(Z)
    except:
        #print "Metallicity Z = %f is out of range"%Z
        val=-1.2345
        #exit(1)
    return val

def loadIsochroneSet(Zs=ZSVEC_full,
                     verbose=False):
    global SMset,Zset
    Zset=Zs

    if verbose:print "Loading isochrone set..."
    iiso=0
    for Z in Zs:
        if verbose:print "\tLoading Isochrone for Z = %f..."%Z
        SMiso=dict2obj(dict())
        Stars='BHM/data/Stars/Isochrones/Padova-Z%.4f.dat'%Z
        Mmin=0.1
        Mmax=2.0
        try:
            data=np.loadtxt(Stars)
        except IOError:
            print "Error openning file '%s'"%Stars
            exit(1)
        ndata=data.shape[0]
        idata=np.arange(0,ndata)

        SMiso.Ages=[]
        ageold=data[0,1]
        for datum in data:
            age=datum[1]
            if age>ageold:
                SMiso.Ages+=[ageold]
                ageold=age
        SMiso.Ages+=[ageold]
        SMiso.nAges=len(SMiso.Ages)
        SMiso.Ages=np.array(SMiso.Ages)
        SMiso.tmin=10**SMiso.Ages[0]/1E9
        SMiso.tmax=10**SMiso.Ages[-1]/1E9
    
        SMiso.Msvec=[]
        SMiso.Mrvec=[]
        SMiso.Lsvec=[]
        SMiso.Rsvec=[]
        SMiso.Tsvec=[]
        SMiso.Mbolvec=[]
        SMiso.logLsvec=[]
        SMiso.loggsvec=[]
        SMiso.logTsvec=[]

        SMiso.Mrint=[]
        SMiso.Lsint=[]
        SMiso.Rsint=[]
        SMiso.Tsint=[]
        SMiso.Mbolint=[]
        SMiso.logLsint=[]
        SMiso.loggsint=[]
        SMiso.logTsint=[]

        Filters=['U','B','V','R','I','J','H','K']
        for filter in Filters:
            exec "SMiso.%svec=[]"%filter in globals(),locals()
            exec "SMiso.%sint=[]"%filter in globals(),locals()

        SMiso.Mmin=1E100
        SMiso.Mmax=0

        it=0
        for age in SMiso.Ages:
            ages=data[:,1]
            sages=ages==age
            ies=idata[sages]
            nies=ies.shape[0]
            masses=data[sages,2]
            nmass=masses.shape[0]
            imass=np.arange(0,nmass)
            bmass=masses>=Mmin
            iselbot=imass[bmass]
            tmass=masses<=Mmax
            iseltop=imass[tmass]
            
            ini=ies[0]+iselbot[0]
            end=ies[0]+iseltop[-1]
            
            Ms=data[ini:end,2]
            SMiso.Msvec+=[Ms]
            
            SMiso.Mrvec+=[data[ini:end,3]]
            SMiso.Mrint+=[interp1d(SMiso.Msvec[it],SMiso.Mrvec[it],kind='slinear')]

            SMiso.Lsvec+=[10**data[ini:end,4]]
            SMiso.Lsint+=[interp1d(SMiso.Msvec[it],SMiso.Lsvec[it],kind='slinear')]

            SMiso.logLsvec+=[data[ini:end,4]]
            SMiso.logLsint+=[interp1d(SMiso.Msvec[it],SMiso.logLsvec[it],kind='slinear')]

            SMiso.Tsvec+=[10**data[ini:end,5]]
            SMiso.Tsint+=[interp1d(SMiso.Msvec[it],SMiso.Tsvec[it],kind='slinear')]

            SMiso.logTsvec+=[data[ini:end,5]]
            SMiso.logTsint+=[interp1d(SMiso.Msvec[it],SMiso.logTsvec[it],kind='slinear')]

            SMiso.loggsvec+=[data[ini:end,6]]
            SMiso.loggsint+=[interp1d(SMiso.Msvec[it],SMiso.loggsvec[it],kind='slinear')]

            gs=10**data[ini:end,6]/100
            SMiso.Rsvec+=[np.sqrt(GCONST*(Ms*MSUN)/gs)/RSUN]
            SMiso.Rsint+=[interp1d(SMiso.Msvec[it],SMiso.Rsvec[it],kind='slinear')]

            SMiso.Mbolvec+=[data[ini:end,7]]
            SMiso.Mbolint+=[interp1d(SMiso.Msvec[it],SMiso.Mbolvec[it],kind='slinear')]

            col=8
            for filter in Filters:
                exec "SMiso.%svec+=[data[ini:end,%d]]"%(filter,col) in globals(),locals()
                exec "SMiso.%sint+=[interp1d(SMiso.Msvec[it],SMiso.%svec[it],kind='slinear')]"%(filter,
                                                                                     filter) in globals(),locals()
                col+=1

            SMiso.Mmin=min(SMiso.Mmin,min(Ms))
            SMiso.Mmax=max(SMiso.Mmax,max(Ms))
        
            it+=1

        SMset+=[SMiso]
        exec "SMset[iiso].Mactual=lambda M,t:PropertySet(M,t,'Mr',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Luminosity=lambda M,t:PropertySet(M,t,'Ls',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logLuminosity=lambda M,t:PropertySet(M,t,'logLs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Radius=lambda M,t:PropertySet(M,t,'Rs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logGravitation=lambda M,t:PropertySet(M,t,'loggs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Temperature=lambda M,t:PropertySet(M,t,'Ts',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logTemperature=lambda M,t:PropertySet(M,t,'logTs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Mbol=lambda M,t:PropertySet(M,t,'Mbol',%d)"%iiso in globals(),locals()
        for filter in Filters:
            exec "SMset[iiso].%s=lambda M,t:PropertySet(M,t,'%s',%d)"%(filter,
                                                                       filter,
                                                                       iiso) in globals(),locals()
        iiso+=1

    return iiso

def StellarRadius(Ms,gs):
    from numpy import sqrt
    Rs=sqrt(GCONST*Ms*MSUN/gs)/RSUN
    return Rs

def StellarGTRL(Z,M,t):
    logg=StellarProperty('logGravitation',Z,M,t)
    g=10**logg/100
    R=StellarRadius(M,g)
    logT=StellarProperty('logTemperature',Z,M,t)
    T=10**logT
    logL=StellarProperty('logLuminosity',Z,M,t)
    L=10**logL
    if logg==-1.2345:g=-1
    if logT==-1.2345:T=-1
    if logL==-1.2345:L=-1
    return g,T,R,L

def minmaxRadius(Z,M,tmin=TAU_MIN,tmax=1.0):
    Rmin=1E100
    Rmax=0.0
    for t in np.linspace(tmin,tmax,20):
        g,T,R,L=StellarGTRL(Z,M,t)
        if R>Rmax:Rmax=R
        if R<Rmin:Rmin=R
    return Rmin,Rmax

def XYfromZ(Z):
    """
    See: http://stev.oapd.inaf.it/cgi-bin/cmd
    """
    Y=0.2485+1.78*Z
    X=1-Y-Z
    return X,Y

XSUN,YSUN=XYfromZ(ZSUN)
    
#METALLICITY FROM Z
def FeH2Z(FeH,X=0.75,A=1.0):
    """
    Values at sun.txt
    
    Examples:
    print FeH2Z(-0.5,X=0.75,A=0.9)
    print FeH2Z(-0.5,X=0.70,A=1.0)
    print FeH2Z(-0.5,X=0.75,A=1.0)
    print FeH2Z(-0.5,X=0.70,A=0.9)
    """
    """
    Wikipedia
    XSun=0.7110
    ZSun=0.0149
    YSun=0.2741
    """
    Z=ZSUN*(X/XSUN)*10**(A*FeH)
    return Z

#CALCULATE Z FROM METALLICITY
def ZfromFHe(FeH):
    """
    Example:
    print ZfromFHe(-0.55)
    print ZfromFHe(-0.40)
    """
    Xvec=np.linspace(0.700,0.739,100)
    Avec=np.linspace(0.9,1.0,100)
    Zvals=[]
    for X in Xvec:
        for A in Avec:
            Zvals+=[FeH2Z(FeH,X=X,A=A)]
    Z=np.mean(Zvals)
    dZ=np.std(Zvals)
    return Z,dZ

def FeHfromZ(Z):
    func=lambda FeH:ZfromFHe(FeH)[0]-Z
    FeH=newton(func,0)
    return FeH

def evoFunctions(evodata):
    ts=evodata[:,0]
    logrho_func=interp1d(np.log10(ts),
                      np.log10(evodata[:,RHO_COL]),
                      kind='slinear')
    Teff_func=interp1d(np.log10(ts),
                       evodata[:,TEFF_COL],
                       kind='slinear')
    logR_func=interp1d(np.log10(ts),
                    np.log10(evodata[:,RAD_COL]),
                    kind='slinear')
    logL_func=interp1d(np.log10(ts),
                       np.log10(evodata[:,LUM_COL]),
                       kind='slinear')
    return logrho_func,Teff_func,logR_func,logL_func

def evoInterpFunctions(star):
    evodata=star.evotrack
    funcs=evoFunctions(evodata)
    star.__dict__['gfunc']=lambda t:10**funcs[0](np.log10(t))
    star.__dict__['Tfunc']=lambda t:funcs[1](np.log10(t))
    star.__dict__['Rfunc']=lambda t:10**funcs[2](np.log10(t))
    star.__dict__['Lfunc']=lambda t:10**funcs[3](np.log10(t))
    rmoi=star.RMoI
    star.__dict__['Ifunc']=interp1d(rmoi[:,0],rmoi[:,3],kind='slinear')
    star.__dict__['dIdtfunc']=interp1d(rmoi[:,0],rmoi[:,4],kind='slinear')

###################################################
#TEST
###################################################
if __name__=="__main__":
    num=loadIsochroneSet(Zs=ZSVEC_siblings,verbose=True)

    Ms=1.0
    tau=TAGE
    Z=0.0152
    
    Ls=StellarProperty('Luminosity',Z,Ms,tau)
    Lslog=10**StellarProperty('logLuminosity',Z,Ms,tau)
    print "Ls (normal) = %e"%Ls
    print "Ls (log-interp) = %e"%Lslog
    
    Rs=StellarProperty('Radius',Z,Ms,tau)
    loggs=StellarProperty('logGravitation',Z,Ms,tau)
    gs=10**loggs/100
    Rslog=np.sqrt(GCONST*Ms*MSUN/gs)/RSUN
    print "Rs (normal) = %e"%Rs
    print "Rs (log-interp g) = %e"%Rslog
    
    Ts=StellarProperty('Temperature',Z,Ms,tau)
    Tslog=10**StellarProperty('logTemperature',Z,Ms,tau)
    print "Ts (normal) = %e"%Ts
    print "Ts (log-interp) = %e"%Tslog

def Seff2014(Teff,crits=['recent venus'],Tsun=TSUN,Mp='1.0'):
    """
    Kopparapu et al., 2014
    """
    
    if Teff<2600:Teff=2600.0
    if Teff>7200:Teff=7200.0
    Tst=Teff-Tsun

    Seffs=[]
    for crit in crits:
        if crit=="runaway greenhouse":
            if Mp=='1.0':
                S=1.107
                a=1.332E-4;b=1.58E-8;c=-8.308E-12;d=-1.931E-15
            if Mp=='5.0':
                S=1.188
                a=1.433E-4;b=1.707E-8;c=-8.968E-12;d=-2.048E-15
            if Mp=='0.1':
                S=0.99
                a=1.209E-4;b=1.404E-8;c=-7.418E-12;d=-1.713E-15
        elif crit=="moist greenhouse":
            S=1.0146
            #SAME AS 2013
            a=8.1884E-5;b=1.9394E-9;c=-4.3618E-12;d=-6.8260E-16
        elif crit=="recent venus":
            #ALL MASSES ARE EQUARL
            S=1.776
            a=2.136E-4;b=2.533E-8;c=-1.332E-11;d=-3.097E-15
        elif crit=="maximum greenhouse":
            S=0.356
            a=6.171E-5;b=1.698E-9;c=-3.198E-12;d=-5.575E-16
        elif crit=="early mars":
            S=0.32
            a=5.547E-5;b=1.526E-9;c=-2.874E-12;d=-5.011E-16
        else:
            S=a=b=c=d=Tst=-1
        Seffs+=[S+a*Tst+b*Tst**2+c*Tst**3+d*Tst**4]
        
    if len(Seffs)==1:return Seffs[0]
    else:return Seffs

def HZ(Ls,Teff,lin='recent venus',lout='early mars',Seff=Seff2014):
    """
    Habitable Zone limits by Kopparapu et al. (2013)
    Ls: In solar Units
    Teff: In K
    """
    if Ls<0 or Teff<0:
        raise Exception("Negative value in stellar properties")
    Seffin,Seffout=Seff(Teff,crits=[lin,lout])
    Seffsun=1.0
    lin=(Ls/Seffin)**0.5
    lout=(Ls/Seffout)**0.5
    aHZ=(Ls/Seffsun)**0.5
    return lin,aHZ,lout

"""
Taken from Claret & Gimenez (1989, 1990)
ZAMS values
"""
STELLAR_MOI=np.array([
        [0.020,0.230**1],
        [0.600,0.378**2],
        [0.800,0.323**2],
        [1.000,0.277**2],
        [1.122,0.248**2],
        [1.259,0.224**2],
        ])
def stellarMoI(M,type="Regression"):
    """
    #type=Regression,Upper,Lower
    plt.figure()
    plt.plot(STELLAR_MOI[:,0],sqrt(STELLAR_MOI[:,1]))
    plt.savefig("moi.png")
    print sqrt(stellarMoI(1.5))
    exit(0)
    """    
    #Regression Coefficients (calculated at May.7/2013)
    a=-1.577705e-01
    b=2.339366e-01
    
    #Lower limit
    MoIlow=0.076729 #Claret & Gimenez (1989)

    #Upper limit
    MoIup=0.25 #Leconte et al. (2011)
    
    #type="Upper"
    if type=="Regression":
        MoI=a*M+b
    elif type=="Upper":
        MoI=MoIup
    else:
        MoI=MoIlow

    if M>STELLAR_MOI[-1,0]:
        MoI=STELLAR_MOI[-1,-1]

    return MoI

def dissipationTime(M,R,L):
    #Zahn (2008) DISSIPATION TIME
    tdiss=3.48*((M*MSUN*(R*RSUN)**2)/(L*LSUN))**(1./3)    
    return tdiss

def Flux(q,Ls1=1.0,Ls2=1.0,rc1=0.1,rc2=0.1,D=1.0,qsgn=1):
    R1=np.sqrt(D**2+rc1**2+2*D*rc1*np.sin(q))
    R2=np.sqrt(D**2+rc2**2-2*D*rc2*np.sin(q))
    F=qsgn*(Ls1/R1**2+Ls2/R2**2)
    return F

NCALLS=0
def AverageFlux(d,**args):
    global NCALLS
    args['D']=d
    intFlux=lambda x:Flux(x,**args)
    F=integrate(intFlux,0.0,2*PI)[0]/(2*PI)
    NCALLS+=1
    return F

def HZbin(q,Ls1,Ls2,Teffbin,abin,
          Seff=Seff2014,
          crits=['recent venus','early mars'],
          eeq=False):
    global NCALLS

    rc2=abin/(q+1)
    rc1=q*rc2
    args=dict(Ls1=Ls1,Ls2=Ls2,rc1=rc1,rc2=rc2)

    #EFFECTIVE FLUXES
    Seffin,Seffout=Seff(Teffbin,crits=crits)

    #INNER LIMIT
    AF=lambda x:AverageFlux(x,**args)-Seffin
    #lin=newton(AF,1.0)
    lin=brentq(AF,1.0E-3,100.0)
    limits=lin,

    #OUTER LIMIT
    AF=lambda x:AverageFlux(x,**args)-Seffout
    #lout=newton(AF,1.0)
    lout=brentq(AF,1.0E-3,100.0)
    limits+=lout,

    if eeq:
        #EARTH EQUIVALENT
        AF=lambda x:AverageFlux(x,**args)-1.0
        #aeeq=newton(AF,1.0)
        aeeq=brentq(AF,1.0E-3,100.0)
        limits+=aeeq,

    return limits

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#STELLAR WIND
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def vn1AUeq(t):
    """
    Velocity and density 1 AU equivalent for main sequence stars.  G07.

    Parameter:
    t: secs

    Return:
    Velocity v at 1 AU: m/s
    Number density n at 1 AU: m^{-3}
    """
    vo=3971*KILO #m/s
    no=1.04E11 #m^{-3}
    tau=2.56E7*YEAR #secs
    betav=-0.43
    betan=-1.86

    ft=(1+t/tau)
    v=vo*ft**betav #Eq. 6
    n=no*ft**betan #Eq. 7
    return v,n

def EqTcorona(Tc,M=1.0,t=1.0):
    """
    Equation to compute corona temperature, G07
    """
    vref,nref=vn1AUeq(t*GIGA*YEAR)
    v=VParker(1.0,M,Tc)
    et=v-vref
    return et

def EqParker(vn,dn=1.0):
    """
    Parker Equation.  G07.
    """
    ep=np.log(vn**2.0)-vn**2.0+4*np.log(dn)+4/dn-3 #Eq.3
    return ep

def VParker(d,M,Tc):
    """
    Velocity of a Parker stellar wind. G07.
    
    Parameters:
    M: Stellar mass (solar masses)
    Tc: Corona temperature (K)
    d: Distance (AU)
    """
    M=M*MSUN
    d=d*AU
    m=MP
    
    vc=np.sqrt(KB*Tc/m) #Eq.4
    dc=m*GCONST*M/(4*KB*Tc) #Eq.5
    
    dn=d/dc
    
    if abs(dn-1)<1E-3:
        vn=1
    elif dn>1:
        vn=brentq(EqParker,1.001,10,args=(dn,))
    else:
        vn=brentq(EqParker,0.0001,0.9998,args=(dn,))
    return vn*vc

def Tcorona(t,M):
    """
    Temperature of Corona, G07
    """
    Tc=newton(EqTcorona,1E6,args=(M,t))
    return Tc

def vnGreissmeier(d,t,M,R,verbose=False,early='constant'):
    """
    Velocity and number density computed from Greissmeier model at G07
    
    Parameters:
    d: distance in AU
    t: time in Gyrs
    M: Mass in Msun
    R: Radius in Msun

    Return:
    v: Velocity in m/s
    n: Number density in m^{-3}
    """
    if verbose:
        print "Computing stellar wind properties at t=%e:Ms=%e Msun,Rs = %e Rsun,d=%e AU"%(t,M,R,d)

    #IF TIME IS EARLY THAN 0.7 ASSUME A CONTANT WIND
    if t<0.7 and early=='constant':
        if verbose:print "\tSATURATION!"
        t=0.7

    #REFERENCE VELOCITY AND DENSITY
    vref,nref=vn1AUeq(t*GIGA*YEAR)
    if verbose:print "\tvref,nref = %e m/s,%e m^-3"%(vref,nref)

    #SOLAR MASS LOSS RATE AT t
    dMsun=4*np.pi*AU**2*nref*vref*MP #Eq. 10
    if verbose:print "\tSolar mass loss: %e kg/s"%dMsun

    #SCALED STELLAR MASS LOSS RATE AT t
    dMstar=scaleProp(R,dMsun,2.0) # Eq.11
    if verbose:print "\tStellar mass loss: %e kg/s (%e Mdot,sun)"%(dMstar,dMstar/dMsun)

    #CORONAL TEMPERATURE AT t (ISOTHERMAL MODEL)
    Tc=Tcorona(t,M)
    if verbose:print "\tTc=%e MK"%(Tc/1E6)

    #RADIAL VELOCITY
    vr=VParker(d,M,Tc)
    if verbose:print "\tvr = %e m/s"%(vr)

    #NUMBER DENSITY
    n=dMstar/(4*np.pi*(d*AU)**2*vr*MP)

    #EFFECTIVE VELOCITY
    vkep=np.sqrt(GCONST*M*MSUN/(d*AU))
    if verbose:print "\tvkep = %e m/s"%(vkep)
    v=np.sqrt(vr**2+vkep**2)
    if verbose:print "\tn = %e m^-3"%(n)
    if verbose:print "\tv = %e m/s"%(v)

    return v,n

"""
Compare with:
MacGregor & Brenner, 1991
http://articles.adsabs.harvard.edu//full/1991ApJ...376..204M/0000211.000.html
"""
VSUN,NSUN=vnGreissmeier(1.0,TAGE,1.0,1.0)
SWPEL=NSUN*VSUN
MDOTSUN=4*PI*(1*AU)**2*MP*SWPEL
#print "Solar mass loss: %e kg/s"%(MDOTSUN/MSUN*YEAR)
#Period-ram pressure relationship (Griessmeier, 2006):
#Mdot v = ko P^{-3.3}
KO=(MDOTSUN*VSUN)*(PSUN**3.3)
def Prot(t,**pars):
    """
    Stellar Rotational Period
    Consistent with stellar wind model
    """
    Ms=pars['Ms']
    Rs=pars['Rs']

    #Properties of the Solar Wind
    v,n=vnGreissmeier(1.0,t,Ms,Rs)

    #Mass Loss
    Mdot=4*PI*(1*AU)**2*MP*n*v

    #Period from the scaling law
    P=(Mdot*v/KO)**(-1/3.3)

    #print "Ms, t (Gyr), P (day)= ",Ms,t,P/DAY
    return P

def maxPeriod(M,R):
    """
    Maximum period of rotation before disruption
    """
    Wmax=(GCONST*M*MSUN/(R*RSUN)**3)**0.5
    Pmax=2*PI/Wmax
    return Pmax/DAY

def tidalAcceleration(Mtarg,Rtarg,Ltarg,MoItarg,
                      Mfield,abin,e,n,Omega,
                      verbose=False):
    """
    Tidal acceleration on star Mtarg,Rtarg,Ltarg (in solar units) due
    to body Mfield when body is rotating with angular velocity Omega
    in an orbit with semimajor axis abin (AU), eccentricity e and mean
    angular velocity n (same units as Omega)
    
    Returns angular velocity 
    """
    if verbose:print "*"*50
    if verbose:print "HUT"
    if verbose:print "R=%e,L=%e"%(Rtarg,Ltarg)
    if verbose:print "abin:",abin

    Rtarg=Rtarg*1.0
    #Eccentricity function
    f2=1+(15./2.)*e**2+(45./8.)*e**4+(5./16.)*e**6
    f5=1+3*e**2+(3./8.)*e**4
    if verbose:print "f1,f5:",f2,f5

    #Maximum rotational rate
    Omega_min=n*f2/((1-e**2)**1.5*f5)

    #Zahn (2008) DISSIPATION TIME
    tdiss=3.48*((Mtarg*MSUN*(Rtarg*RSUN)**2)/(Ltarg*LSUN))**(1./3)
    kdiss=1/tdiss

    if verbose:print "tdiss:",tdiss
    if verbose:print "n,Omega:",n,Omega
    if verbose:print "e:",e

    #Radius of gyration
    rg2=MoItarg**2
    if verbose:print "Radius of Gyration:",rg2

    #Angular acceleration
    angacc=kdiss/rg2*(Mfield/Mtarg)**2*((Rtarg*RSUN)/(abin*AU))**6*(n/(1-e**2)**6)*(f2-(1-e**2)**1.5*f5*Omega/n)
    if verbose:print "Factors:",Omega/n,f2/((1-e**2)**1.5*f5)
    if verbose:print "Acc:",angacc

    return angacc

def theoProt(t,x):
    a=x[0]
    b=x[1]
    c=x[2]
    y=a*t**b+c
    return y

def dtheoProt(t,x):
    a=x[0]
    b=x[1]
    c=x[2]
    y=a*b*t**(b-1)
    return y
    
def tfromProt(P,x):
    a=x[0]
    b=x[1]
    c=x[2]
    if P-c>0:
        t=((P-c)/a)**(1./b)
    else:
        t=0
    return t

def totalAcceleration(t,star,starf,binary,verbose=False,qreturn=False):
    if verbose:print "Time:",t
    acc_tid=tidalAcceleration(star.M,star.Rfunc(t),
                              star.Lfunc(t),star.MoI,
                              starf.M,
                              binary.abin,binary.ebin,
                              binary.nbin/DAY,star.W,
                              verbose=verbose)
    if verbose:print "Tidal acceleration:",acc_tid
    tau_rot=tfromProt(star.P/DAY,star.protfit)
    dProtdt=dtheoProt(tau_rot,star.protfit)*DAY/GYR
    acc_ML=-2*np.pi/star.P**2*dProtdt
    if verbose:print "Mass-loss acceleration:",acc_ML
    acc=acc_tid+acc_ML
    if qreturn:
        return acc_tid,acc_ML,acc
    else:
        return acc

def rotationalAcceleration(Omega,t,params):
    star=params['star']
    starf=params['starf']
    binary=params['binary']
    taudisk=params['taudisk']
    Kw=params['Kw']
    wsat=params['wsat']

    t=t/GYR
    if t>star.taums:t=star.taums
    M=star.M
    R=star.Rfunc(t)

    if t<taudisk:
        dOdt_cont=0.0
        dOdt_wind=0.0
    else:
        I=star.Ifunc(t)
        #========================================
        #CONTRACTION ACCELERATION
        #========================================
        if t>12:dOdt_cont=0.0
        else:
            dOdt_cont=-Omega*star.dIdtfunc(t)/I/GYR
        #print star.Ifunc(t)*MSUN*RSUN**2,star.dIdtfunc(t)*MSUN*RSUN**2/GYR,Omega,dOdt_cont

        #========================================
        #WIND BREAKING
        #========================================
        facw=R**0.5/M**0.5
        if Omega<=(wsat*OMEGASUN):
            dJdtw=-Kw*Omega**3*facw
        else:
            dJdtw=-Kw*Omega*(wsat*OMEGASUN)**2*facw

        dOdt_wind=dJdtw/(I*MSUN*RSUN**2)

    #========================================
    #TIDAL ACCELERATION
    #========================================
    if starf is None:
        dOdt_tide=0.0
    else:
        dOdt_tide=tidalAcceleration(M,R,
                                    star.Lfunc(t),star.MoI,
                                    starf.M,
                                    binary.abin,binary.ebin,
                                    binary.nbin/DAY,Omega,
                                    verbose=False)
        #print t,M,R,star.MoI,binary.abin,binary.ebin
        #print dOdt_cont,dOdt_wind,dOdt_tide
        #raw_input()

    #========================================
    #TOTAL ACCELERATION
    #========================================
    dOdt=dOdt_tide+dOdt_cont+dOdt_wind

    #print "t,w = ",t,Omega
    #print "dOdt = ",dOdt
    return dOdt

def starLXUV(Ls,t):
    """
    Stellar XUV Luminosity
    Ls in LSUN and t in Gyrs
    """
    #==================================================
    #CRITICAL TIME: Scalo 2007, Khodachenko 2009 Fig.1
    #==================================================
    taui=2.03E15*(Ls*1.8)**(-0.65)/(1E9*YEAR)

    #==================================================
    #X-RAY LUMINOSITY --kilsykova et Lammer 2012
    #==================================================
    if t<=taui:
        LX=6.3E-4*(Ls*LSUN*1E7)
    else:
        LX=1.8928E28*t**(-1.34)

    #==================================================
    #EUV LUMINOSITY
    #==================================================
    LEUV=10**(4.8+0.86*np.log10(LX))
    LXUV=(LX+LEUV) #/(Ls*4E33)
    LXUV=LX #/(Ls*4E33)
    return LXUV

#XUV Present Earth Level in erg cm^-2 s^-1
PEL=starLXUV(1.0,TAGE)/(4*PI*(1*AU*1E2)**2)
#XUV IN SI
PELSI=PEL*(1E-7/(1E-2))

def binaryWind(a,tau1,M1,R1,tau2,M2,R2,early='constant'):
    v1,n1=vnGreissmeier(a,tau1,M1,R1,early=early)
    if tau2>0:
        v2,n2=vnGreissmeier(a,tau2,M2,R2,early=early)
    else:v2=n2=0
    Psw=n1*v1**2+n2*v2**2
    Fsw=n1*v1+n2*v2
    return Psw,Fsw

def starLuminosity(R,T):
    L=R**2*(T/TSUN)**4
    return L

def starDistance(L,V,BCV):
    """
    Estimate stellar distance
    """
    MV=MBOLSUN-2.5*np.log10(L)-BCV
    d=10**((V-MV)/5+1)
    return d

def starProt(vsini,i,R):
    if vsini>0:
        Prot=2*np.pi*R*(RSUN/1E3)/(vsini/np.sin(i*DEG))/DAY
    else:
        PRINTOUT("Trying to calculate rotational period o a star without rotation '%e,%e'."%(vsini,R))
        errorCode("DATA_ERROR")
    return Prot

def bolometricCorrection(Teff):
    """
    Torres (2010), 2010AJ....140.1158T
    Flower (1996), 1996ApJ...469..355F
    """
    #Torres (2010), Flower (1996)
    a=[-0.190537291496456E+05,-0.370510203809015E+05,-0.118115450538963E+06]
    b=[+0.155144866764412E+05,+0.385672629965804E+05,+0.137145973583929E+06]
    c=[-0.421278819301717E+04,-0.150651486316025E+05,-0.636233812100225E+05]
    d=[+0.381476328422343E+03,+0.261724637119416E+04,+0.147412923562646E+05]
    e=[+0.000000000000000E+00,-0.170623810323864E+03,-0.170587278406872E+04]
    f=[+0.000000000000000E+00,+0.000000000000000E+00,+0.788731721804990E+02]
    logTeff=np.log10(Teff)
    if logTeff<3.70:i=0
    elif logTeff<3.90:i=1
    else:i=2
    BCV=a[i]+b[i]*logTeff+c[i]*logTeff**2+d[i]*logTeff**3+e[i]*logTeff**4+f[i]*logTeff**5
    return BCV

def mainSequenceDuration(Ms):
    """
    Handbook of Space Astronomy and Astrophysics
    Zombeck
    """
    logM=np.log10(Ms)
    Tms=array([[0.36,8.62,0.56],
               [0.26,8.93,0.64],
               [0.17,9.24,0.78],
               [0.08,9.60,0.98],
               [-0.02,9.83,1.00],
               [-0.11,10.28,1.00]])
    if logM<Tms[-1,0] or logM>Tms[0,0]:logTms=13*Ms**(-2.5)
    else:logTms=np.interp(logM,Tms[::-1,0],Tms[::-1,1])
    return logTms

def convectiveTurnoverTime(Teff):
    """
    Fit of Convective Turnover Time to Teff (Gunn et al.,1998)
    Taken from Cranmer & Saar (2011)
    """
    tauc = 314.241*np.exp(-Teff/1952.5)*np.exp(-(Teff/6250.)**18.)+0.002
    return tauc

TAUCSUN=convectiveTurnoverTime(5770.2)
WSATSUN=30.0

def starRX(Ro,regime='middle'):
    """
    Lbol: Bolometric Luminosity
    Ro: Rossby number
    From Wright et al. (2013)
    """
    if regime=='middle':
        Rosat=0.13
        RXsat=10**(-3.13)
    elif regime=='high':
        Rosat=0.13+2*0.02
        RXsat=10**(-3.13+2*0.08)
    else:
        Rosat=0.13-2*0.02
        RXsat=10**(-3.13-2*0.08)
        
    if Ro<Rosat:
        RX=RXsat
    else:
        RX=RXsat*(Ro/Rosat)**(-2.70)
    return RX

def starLXEUV(LX):
    """
    LEUV=10**(4.8+0.86*np.log10(LX))
    LXEUV=LX+LEUV
    """
    LXEUV=LX
    return LXEUV

def findTrack(model,Z,M,verbose=False):
    modeldir=DATA_DIR+"Stars/EvoTracks/%s"%model

    if verbose:
        PRINTOUT("Looking for closest track to Z = %.5f and M = %.2f in model '%s'..."%\
                     (Z,M,model))
    if not DIREXISTS(modeldir):
        PRINTERR("Model '%s' not found."%modeldir)
        exit(0)

    #FIND THE CLOSEST Z
    Zdirs=listDirectory(modeldir,"Z*")
    Zvals=np.array([])
    for Zdir in Zdirs:
        matches=re.search("/Z(.+)",Zdir)
        Zval=float(matches.group(1))
        Zvals=np.append([Zval],Zvals)

    dlogZ=np.abs(np.log10(Z)-np.log10(Zvals))
    iZ=dlogZ.argmin()
    Zfind=Zvals[iZ]
    dZfind=dlogZ[iZ]/abs(np.log10(Z))
    Zdir=modeldir+"/Z%.2e"%Zfind
    if verbose:
        PRINTOUT("Closest metallicity in model: Z = %.5f (closeness %.1e)."%(Zfind,dZfind))
        
    #FIND THE CLOSEST M
    Mdirs=listDirectory(Zdir,"M_*")
    Mvals=np.array([])
    for Mdir in Mdirs:
        matches=re.search("/M_(.+)\.dat",Mdir)
        Mval=float(matches.group(1))
        Mvals=np.append([Mval],Mvals)

    dM=np.abs(M-Mvals)
    iM=dM.argmin()
    Mfind=Mvals[iM]
    dMfind=dM[iM]/M
    if verbose:
        PRINTOUT("Closest mass in model: M = %.2f (closeness %.1e)."%(Mfind,dMfind))

    #TRACK LOADING ROUTINE
    track=loadConf(modeldir+"/track.py")
    
    #READ EVOLUTIONARY TRACK
    try:
        tfile=Zdir+"/M_%.2f.dat"%Mfind
        datatrack=track.getTrack(Zfind,Mfind,tfile)
    except:
        tfile=Zdir+"/M_%.3f.dat"%Mfind
        datatrack=track.getTrack(Zfind,Mfind,tfile)

    return [Zfind,dZfind,Mfind,dMfind],datatrack

def trackFunctions(track):
    trackfunc=dict()
    ts=track["qt_fun"](track["qt"])
    g=track["qg_fun"](track["qg"])
    T=track["qT_fun"](track["qT"])
    R=track["qR_fun"](track["qR"])
    L=track["qL_fun"](track["qL"])
    trackfunc["g"]=interp1d(ts,g,kind='slinear')
    trackfunc["T"]=interp1d(ts,T,kind='slinear')
    trackfunc["R"]=interp1d(ts,R,kind='slinear')
    trackfunc["L"]=interp1d(ts,L,kind='slinear')
    return dict2obj(trackfunc)
        
if __name__=="__main__":
    from matplotlib import pyplot as plt


    print RXSUN
    print RXSUN*LSUN*1E7/(4*PI*(AU*1E2)**2)

    Ros=np.logspace(np.log10(1E-3),np.log10(1E1),50)
    RXs_mid=np.array([starRX(Ro) for Ro in Ros])
    RXs_hig=np.array([starRX(Ro,regime='high') for Ro in Ros])
    RXs_low=np.array([starRX(Ro,regime='low') for Ro in Ros])
    fig=plt.figure()
    plt.plot(Ros,RXs_mid)
    plt.plot(Ros,RXs_low)
    plt.plot(Ros,RXs_hig)
    plt.plot([2.0],[RXSUN],'o',color='y',markersize=10)
    plt.xscale("log")
    plt.yscale("log")
    plt.savefig("tests/RosRX.png")
