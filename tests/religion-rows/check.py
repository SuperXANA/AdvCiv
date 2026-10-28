#!/usr/bin/env python3
"""Execute the actual marked summary-row block with instrumented UI dependencies."""
from pathlib import Path
import textwrap,sys
root=Path(__file__).resolve().parents[2]
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/'Python/Screens/CvReligionScreen.py'
s=source.read_text();a=s.index('\t\t\t# Minor Religions do not have Temples, Monastaries, or Missionaries',s.index('\t\t\t# number of cities'))
b=s.index('\t\t\t# XANA: 06-27-2026 Unique Civics and Religions',a)
block=textwrap.dedent(s[a:b])
class Constants:
 def __getattr__(self,n):return n
class Info:
 def __init__(self,minor):self.minor=minor
 def isMinorOrganization(self):return self.minor
class Context:
 def getReligionInfo(self,i):return Info(i==1)
 def getGame(self):return self
 def getReligionGameTurnFounded(self,i):return -1 if i in self.unfounded else 1
class Screen:
 def __init__(self):self.labels=[]
 def setLabelAt(self,name,area,text,justify,x,y,*args):self.labels.append((text,x,y))
class Subject:pass
gc=Context()
def check(religions,unfounded=()):
 gc.unfounded=unfounded
 subject=Subject();subject.RELIGIONS=religions
 for k,v in dict(Y_INFLUENCE=100,LEFT_EDGE_TEXT=5,DZ=0,X_RELIGION_START=100,DX_RELIGION=50,szTemples='Temples',szMonastaries='Monasteries',szMissionaries='Missionaries').items():setattr(subject,k,v)
 screen=Screen();env=dict(self=subject,screen=screen,gc=gc,szArea='Area',CvUtil=Constants(),FontTypes=Constants(),WidgetTypes=Constants(),iTemple={0:10,1:99,2:20},iMonastery={0:11,1:99,2:21},iMissionaries_Active={0:12,1:99,2:22},iMissionaries_Construct={0:13,1:99,2:23})
 # Model the preceding loop's stale variable for the original-source negative control.
 if religions:env['iRel']=religions[-1]
 exec(block,env)
 major=[r for r in religions if r!=1]
 expected=[]
 if major:
  for label,y,values in [('Temples',140,{0:'10',2:'20'}),('Monasteries',160,{0:'11',2:'21'}),('Missionaries',180,{0:'12 [13]',2:'22 [23]'})]:
   expected.append((label,5,y))
   for col,r in enumerate(religions):
    if r!=1 and r not in unfounded:expected.append((values[r],100+50*col,y))
 assert screen.labels==expected,(religions,screen.labels,expected)
for religions in [[0,2,1],[1,0,2],[0,1,2],[1],[0],[2],[]]:
 check(religions);check(religions,[2]);check(religions,[0,2])
print('PASS: actual marked rows; mixed/reordered/minor-only/empty sets, founded filters, counts and fixed column positions. Python 3/UI stubs; engine untested.')
