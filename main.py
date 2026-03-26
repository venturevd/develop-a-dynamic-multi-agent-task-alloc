import argparse,json,sys,atexit
sys.path.insert(0,'/home/kingjames/agents/artifacts')
from agent_representation_broker.agent_broker import AgentBroker
class DynamicAllocator(AgentBroker):
    def __init__(s,state_file=None):super().__init__();s.fb={};s.cw,s.ww,s.pw=1.0,0.5,0.3;s.state_file=state_file;state_file and (s._load(),atexit.register(s._save))
    def _load(s):
        try:
            with open(s.state_file) as f: d=json.load(f); s.agents=d.get('agents',{}); s.tasks=d.get('tasks',{}); s.fb=d.get('feedback',{})
        except: pass
    def _save(s):
        if s.state_file:
            with open(s.state_file,'w') as f: json.dump({'agents':s.agents,'tasks':s.tasks,'feedback':s.fb},f,indent=2)
    def submit_task(s,t,r,p=1):
        if t in s.tasks:return 0
        s.tasks[t]={'requirements':r,'assigned_agents':[],'priority':p};s._a(t);return 1
    def _a(s,t):
        tsk=s.tasks[t]
        if tsk.get('a'):return
        c=[(s._sc(a,t),a)for a,ag in s.agents.items()if all(x in ag['capabilities']for x in tsk['requirements'])]
        if c:
            c.sort(reverse=True);b=c[0][1];tsk['a']=b
            if b not in tsk['assigned_agents']:tsk['assigned_agents'].append(b)
            if t not in s.agents[b]['tasks']:s.agents[b]['tasks'].append(t)
    def _sc(s,a,t):
        ag,tsk=s.agents[a],s.tasks[t];w=1.0/(1+len(ag['tasks']));pf=s.fb.get(a,{}).get(t,2.5)/5.0
        return (s.cw+w*s.ww+pf*s.pw)*tsk['priority']
    def rebalance(s):
        for a in s.agents.values():a['tasks']=[]
        for t in s.tasks.values():t['a']=None
        for tid in sorted(s.tasks,key=lambda x:s.tasks[x]['priority'],reverse=True):s._a(tid)
    def feedback(s,a,t,r):
        if a not in s.agents or t not in s.tasks or not(1<=r<=5):return 0
        s.fb.setdefault(a,{})[t]=r;return 1
    def status(s):
        return{'agents':len(s.agents),'tasks':len(s.tasks),'assigned':sum(1 for t in s.tasks.values()if t.get('a'))}
def main():
    p=argparse.ArgumentParser(description='Dynamic Multi-Agent Task Allocation System',epilog='Ex: %(prog)s --persist state.json -a a1 -c python,api -T t1 -r python,api -S')
    p.add_argument('-a','--agent');p.add_argument('-c','--cap',default='');p.add_argument('-T','--task');p.add_argument('-r','--req',default='');p.add_argument('-p','--pri',type=int,default=1);p.add_argument('--persist',metavar='FILE',help='Save/load state');p.add_argument('-R','--rebalance',action='store_true');p.add_argument('-S','--status',action='store_true');p.add_argument('-j','--json',action='store_true');p.add_argument('-f','--feedback',nargs=3,metavar=('A','T','R'))
    args=p.parse_args();b=DynamicAllocator(state_file=args.persist)
    if args.agent:
        if not b.register_agent(args.agent,args.cap.split(',')if args.cap else[]):sys.exit(1)
        print(f"Agent '{args.agent}' registered")
    if args.task:
        if not b.submit_task(args.task,args.req.split(',')if args.req else[],args.pri):sys.exit(1)
        print(f"Task '{args.task}' -> {b.tasks[args.task].get('a','unassigned')}")
    if args.rebalance:b.rebalance();print("Rebalanced")
    if args.feedback:
        a,t,r=args.feedback;(not b.feedback(a,t,float(r)))and sys.exit(1);print(f"Feedback: {a}->{t}={r}")
    if args.status:
        s=b.status();print(json.dumps(s,indent=2)if args.json else f"Agents: {s['agents']}\nTasks: {s['tasks']}\nAssignments: {s['assigned']}/{s['tasks']}")
if __name__=="__main__":main()