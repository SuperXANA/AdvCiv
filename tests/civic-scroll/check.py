#!/usr/bin/env python3
"""Run actual Python 2-compatible screen methods under Python 3 with UI stubs."""
from pathlib import Path
import textwrap
import sys
root = Path(__file__).resolve().parents[2]
source_path = Path(sys.argv[1]) if len(sys.argv)>1 else root/'Python/Screens/CvCivicsScreen.py'
lines = source_path.read_text().splitlines()
def method(name):
    start = next(i for i,l in enumerate(lines) if l.startswith('\tdef '+name+'('))
    end = next((i for i in range(start+1,len(lines)) if lines[i].startswith('\tdef ')),len(lines))
    return '\n'.join(l[1:] if l.startswith('\t') else l for l in lines[start:end]).rstrip()
class Constants:
    def __getattr__(self, name): return name
class Civic:
    def __init__(self, option, name): self.option,self.name=option,name
    def getCivicOptionType(self): return self.option
    def getDescription(self): return self.name
    def getButton(self): return self.name+'.dds'
class Player:
    def __init__(self, allowed): self.allowed=set(allowed)
    def isAllowedCivic(self, civic): return civic in self.allowed
class GlobalContext:
    civics=[Civic(0,'A'),Civic(0,'B'),Civic(0,'C'),Civic(1,'D')]
    players=[Player([0,2,3]),Player([1])]
    def getNumCivicOptionInfos(self): return 2
    def getNumCivicInfos(self): return len(self.civics)
    def getCivicInfo(self,i): return self.civics[i]
    def getCivicOptionInfo(self,i): return Civic(i,'Option'+str(i))
    def getPlayer(self,i): return self.players[i]
class Art:
    def getInterfaceArtInfo(self,name): return self
    def getPath(self): return 'highlight.dds'
class Screen:
    def __init__(self): self.widgets={}; self.deleted=[]; self.panels=[]
    def addPanel(self,*args): pass
    def setLabel(self,*args): pass
    def deleteWidget(self,parent):
        self.deleted.append(parent)
        self.widgets={k:v for k,v in self.widgets.items() if v[0]!=parent}
    def addScrollPanel(self,parent,title,x,y,w,h,style):
        assert h>0
        self.panels.append(parent)
    def setActivation(self,*args): pass
    def addCheckBoxGFCAt(self,parent,name,texture,highlight,x,y,*rest):
        assert parent in self.panels and y>0
        self.widgets[name]=(parent,y)
    def setLabelAt(self,name,parent,label,justify,x,y,*rest):
        self.widgets[name]=(parent,y)
gc=GlobalContext()
env=dict(gc=gc,ArtFileMgr=Art(),**{n:Constants() for n in ['CvUtil','PanelStyles','FontTypes','WidgetTypes','ActivationTypes','ButtonStyles']})
exec('class Subject:\n'+textwrap.indent(method('isCivicVisible')+'\n'+method('drawAllButtons'),'    '),env)
subject=env['Subject']()
for key,value in dict(HEADINGS_WIDTH=200,CIVIC_LIST_PANEL_WIDTH=200,HEADINGS_SPACING=5,HEADINGS_TOP=70,HEADINGS_BOTTOM=280,AREA_NAME='Area',SCROLL_PANEL_NAME='Scroll',HEADER_HEIGHT=40,TEXT_MARGIN=15,BUTTON_SIZE=24,iActivePlayer=0).items():
    setattr(subject,key,value)
screen=Screen(); refreshed=[]
subject.getScreen=lambda:screen
subject.getCivicsButtonName=lambda i:'Button'+str(i)
subject.getCivicsTextName=lambda i:'Text'+str(i)
subject.drawCivicOptionButtons=lambda i:refreshed.append(i)
subject.drawAllButtons()
assert screen.widgets=={'Button0':('Scroll0',30),'Text0':('Scroll0',30),'Button2':('Scroll0',60),'Text2':('Scroll0',60),'Button3':('Scroll1',30),'Text3':('Scroll1',30)}
assert refreshed==[0,1]
subject.iActivePlayer=1; subject.drawAllButtons()
assert screen.widgets=={'Button1':('Scroll0',30),'Text1':('Scroll0',30)}
subject.iActivePlayer=0; gc.players[0]=Player([]); subject.drawAllButtons()
assert screen.widgets=={} and screen.deleted==['Scroll0','Scroll1']*3
print('PASS: actual draw/visibility methods; filtered rows, matching coordinates, independent columns, player-switch and empty redraw. Engine UI stubbed.')
