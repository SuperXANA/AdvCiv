#include <cassert>
#include <cstdio>
#include <cstddef>
#include "CvMemoryManager.h"
struct Item { static int live; Item(){++live;} ~Item(){--live;} };
int Item::live=0;
Item** makeRows(int rows, int columns, int pattern=0) {
    Item** p=new Item*[rows];
    for(int row=0;row<rows;++row)
        p[row]=(pattern!=0 && row%2==pattern-1)?NULL:new Item[columns];
    return p;
}
Item** owned=NULL;
int pointerCalls=0, countCalls=0;
Item**& owner(){++pointerCalls;return owned;}
int rowCount(){++countCalls;return 3;}
int main() {
    int cases=0;
    for(int rows=0;rows<=6;++rows)
    for(int columns=0;columns<=4;++columns)
    for(int pattern=0;pattern<=2;++pattern) {
        Item** p=makeRows(rows,columns,pattern);
        SAFE_DELETE_2D_ARRAY(p,rows);
        assert(p==NULL && Item::live==0);
        SAFE_DELETE_2D_ARRAY(p,rows);
        assert(p==NULL && Item::live==0);++cases;
    }
    {
        Item** p=makeRows(3,2);int i=3;
        SAFE_DELETE_2D_ARRAY(p,i);
        assert(i==3 && p==NULL && Item::live==0);++cases;
    }
    {
        Item** i=makeRows(3,2);
        SAFE_DELETE_2D_ARRAY(i,3);
        assert(i==NULL && Item::live==0);++cases;
    }
    {
        Item** groups[2]={makeRows(2,3),makeRows(3,2)};
        int counts[2]={2,3};int i=1;
        SAFE_DELETE_2D_ARRAY(groups[i],counts[i]);
        assert(i==1 && groups[0]!=NULL && groups[1]==NULL && Item::live==6);
        SAFE_DELETE_2D_ARRAY(groups[0],counts[0]);
        assert(groups[0]==NULL && Item::live==0);++cases;
    }
    {
        owned=makeRows(3,2);pointerCalls=countCalls=0;
        SAFE_DELETE_2D_ARRAY(owner(),rowCount());
        assert(owned==NULL && pointerCalls==1 && countCalls==1 && Item::live==0);++cases;
    }
    {
        pointerCalls=countCalls=0;
        SAFE_DELETE_2D_ARRAY(owner(),rowCount());
        assert(owned==NULL && pointerCalls==1 && countCalls==1 && Item::live==0);++cases;
    }
    {
        Item** p=makeRows(3,2);int rows=3;
        SAFE_DELETE_2D_ARRAY(p,rows++);
        assert(rows==4 && p==NULL && Item::live==0);++cases;
    }
    {
        Item** p=makeRows(2,1);bool other=false;
        if(true) SAFE_DELETE_2D_ARRAY(p,2); else other=true;
        assert(p==NULL && !other && Item::live==0);++cases;
    }
    {
        struct Holder { Item** rows; } h;h.rows=makeRows(2,3);
        SAFE_DELETE_2D_ARRAY(h.rows,2);
        assert(h.rows==NULL && Item::live==0);++cases;
    }
    {
        int** p=new int*[2];p[0]=new int[1];p[1]=NULL;
        SAFE_DELETE_2D_ARRAY(p,static_cast<std::size_t>(2));
        assert(p==NULL);++cases;
    }
    {
        double** p=new double*[1];p[0]=new double[4];
        SAFE_DELETE_2D_ARRAY(p,1);
        assert(p==NULL);++cases;
    }
    std::printf("%d deletion/lifetime/argument cases passed\n",cases);
}
