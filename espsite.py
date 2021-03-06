# cluster-dependent definitions
# espresso.py will make use of all "self" variables in config class
import os

class config:
    def __init__(self):
        self.scratch = os.path.dirname(os.getenv('LOCAL_SCRATCH'))
        u = os.getenv('USER')
        if self.scratch.find(u)<0:
            self.scratch = os.path.join(self.scratch,u)
        if not os.path.exists(self.scratch):
            self.scratch = '/tmp'
        self.submitdir = os.getenv('SLURM_SUBMIT_DIR')
        self.batch = self.submitdir!=None
        #we typically run batch jobs without openmp threads here
        if self.batch:
            os.putenv('OMP_NUM_THREADS','1')
        #check for batch
        if self.batch:
    	    #f = open('/home/vossj/suncat/specialpartitionsonly.txt', 'r')
    	    #usernames = [x.strip() for x in f.readlines()]
    	    usernames = []
    	    #f.close()
    	    if os.getenv('USER') in usernames:
    		try:
    		    partition = os.getenv('SLURM_JOB_PARTITION')
    		except:
    		    partition = ''
    		if not (partition in ('iric',)):
    		    import sys
    		    print >>sys.stderr, 'Please use the iric partition for your jobs by specifying\n-p iric         when submitting your jobs.'
    		    sys.exit(1)
            self.jobid = os.getenv('SLURM_JOBID')
            nodefile = self.submitdir+'/nodefile.'+self.jobid
            uniqnodefile = self.submitdir+'/uniqnodefile.'+self.jobid
            os.system('scontrol show hostnames $SLURM_JOB_NODELIST >'+uniqnodefile)
            taskspernode = os.getenv('SLURM_TASKS_PER_NODE')
            xtaskspernode = taskspernode.find('(')
            if xtaskspernode > -1:
        	taskspernode = taskspernode[:xtaskspernode]
            os.system("awk '{for(i=0;i<"+taskspernode+";i++)print}' "+uniqnodefile+" >"+nodefile)
            f = open(nodefile, 'r')
            procs = [x.strip() for x in f.readlines()]
            f.close()
            self.procs = procs

            nprocs = len(procs)
            self.nprocs = nprocs
            
            p = os.popen('wc -l <'+uniqnodefile, 'r')
            nnodes = p.readline().strip()
            p.close()
        
            self.perHostMpiExec = 'mpiexec -machinefile '+uniqnodefile+' -np '+nnodes
            self.perProcMpiExec = 'mpiexec -machinefile '+nodefile+' -np '+str(nprocs)+' -wdir %s %s'
            self.perSpecProcMpiExec = 'mpiexec -machinefile %s -np %d -wdir %s %s'

    def do_perProcMpiExec(self, workdir, program):
        return os.popen2(self.perProcMpiExec % (workdir, program))

    def do_perProcMpiExec_outputonly(self, workdir, program):
        return os.popen(self.perProcMpiExec % (workdir, program), 'r')

    def runonly_perProcMpiExec(self, workdir, program):
        os.system(self.perProcMpiExec % (workdir, program))

    def do_perSpecProcMpiExec(self, machinefile, nproc, workdir, program):
        return os.popen3(self.perSpecProcMpiExec % (machinefile, nproc, workdir, program))
