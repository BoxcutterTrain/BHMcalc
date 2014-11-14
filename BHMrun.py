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
# Master running script
###################################################
from BHM import *

###################################################
#CLI ARGUMENTS
###################################################
Usage=\
"""
Usage:
   python %s <script>.py <sysdir> <module>.conf <qoverride>

   <script>.py: Script to run

   <systdir>: Directory where the system configuration files lie

   <module>.conf (file): Configuration file for the module.

   <qoverride> (int 0/1): Override any existent moduleect with the same hash.
"""%argv[0]

script,sys_dir,module_conf,qover=\
    readArgs(argv,
             ["str","str","str","int"],
             ["BHMstar.py","sys/template","star1.conf","0"],
             Usage=Usage)

###################################################
#PRELIMINARY VERIFICATIONS
###################################################
module_file="%s/%s"%(sys_dir,module_conf)
if not FILEEXISTS(module_file):
    PRINTERR("File '%s' does not exist."%module_file)
    errorCode("FILE_ERROR")
PRINTERR("Error Output:")

###################################################
#RUN MODULE
###################################################
PRINTOUT("System Directory: %s"%sys_dir)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#HASH MODULE
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
module_type=module_conf
module_type=module_type.replace(".conf","")
module_type=module_type.replace("1","")
module_type=module_type.replace("2","")
module,module_dir,module_str,module_hash,module_liv,module_stg=\
    signObject(module_type,sys_dir+"/"+module_conf)
PRINTOUT("Module type: %s"%module_type)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#CHECK-OUT MODULES ON WHICH IT DEPENDS
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
for depmod in OBJECT_PIPE[module_type]:

    #========================================
    #HASHING OBJECTS
    #========================================
    depmod_conf="%s.conf"%depmod
    depmod_type=depmod
    depmod_type=depmod_type.replace("1","")
    depmod_type=depmod_type.replace("2","")
    depmod,depmod_dir,depmod_str,depmod_hash,depmod_liv,depmod_stg=\
        signObject(depmod_type,sys_dir+"/"+depmod_conf)

    #========================================
    #HASHING OBJECTS
    #========================================
    if depmod_stg<10 or qover==2:
        PRINTOUT("Forcing %s"%depmod_type);
        System("python BHMrun.py BHM%s.py %s %s %d"%(depmod_type,sys_dir,depmod_conf,qover),out=False)
    else:PRINTOUT("%s ready."%depmod_type);
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#EXECUTING MODULE
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if module_stg<10 or qover>=1:
    PRINTOUT("Forcing %s"%module_type);
    System("python BHM%s.py %s %s %d"%(module_type,sys_dir,module_conf,qover),out=False)
else:PRINTOUT("%s ready."%module_type);
print "--sig--\n%s"%module_hash
