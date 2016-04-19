#include <cstring>
#include <cstdlib>


//基于索引表的细化细化算法
//功能：对图象进行细化
//参数：lpDIBBits：代表图象的一维数组
//      lWidth：图象高度
//      lHeight：图象宽度
//      无返回值
bool ThiningDIBSkeleton (unsigned char* lpDIBBits, int lWidth, int lHeight)
{	
	//循环变量
	long i;
	long j;
	long lLength;

	unsigned char deletemark[256] = {      // 这个即为前人据8领域总结的是否可以被删除的256种情况
		0,0,0,0,0,0,0,1,	0,0,1,1,0,0,1,1,
		0,0,0,0,0,0,0,0,	0,0,1,1,1,0,1,1,
		0,0,0,0,0,0,0,0,	1,0,0,0,1,0,1,1,
		0,0,0,0,0,0,0,0,	1,0,1,1,1,0,1,1,
		0,0,0,0,0,0,0,0,	0,0,0,0,0,0,0,0,
		0,0,0,0,0,0,0,0,	0,0,0,0,0,0,0,0,
		0,0,0,0,0,0,0,0,	1,0,0,0,1,0,1,1,
		1,0,0,0,0,0,0,0,	1,0,1,1,1,0,1,1,
		0,0,1,1,0,0,1,1,	0,0,0,1,0,0,1,1,
		0,0,0,0,0,0,0,0,	0,0,0,1,0,0,1,1,
		1,1,0,1,0,0,0,1,	0,0,0,0,0,0,0,0,
		1,1,0,1,0,0,0,1,	1,1,0,0,1,0,0,0,
		0,1,1,1,0,0,1,1,	0,0,0,1,0,0,1,1,
		0,0,0,0,0,0,0,0,	0,0,0,0,0,1,1,1,
		1,1,1,1,0,0,1,1,	1,1,0,0,1,1,0,0,
		1,1,1,1,0,0,1,1,	1,1,0,0,1,1,0,0
	};//索引表

	unsigned char p0, p1, p2, p3, p4, p5, p6, p7;
	unsigned char *pmid, *pmidtemp;    // pmid 用来指向二值图像  pmidtemp用来指向存放是否为边缘
	unsigned char sum;
	bool bStart = true;
	lLength = lWidth * lHeight;
	unsigned char *pTemp = new uchar[sizeof(unsigned char) * lWidth * lHeight]();  //动态创建数组 并且初始化
	
	//    P0 P1 P2
	//    P7    P3
	//    P6 P5 P4

	while(bStart)
	{
		bStart = false;

		//首先求边缘点
		pmid = (unsigned char *)lpDIBBits + lWidth + 1;
		memset(pTemp,  0, lLength);
		pmidtemp = (unsigned char *)pTemp + lWidth + 1; //  如果是边缘点 则将其设为1
		for(i = 1; i < lHeight -1; i++)     
		{
			for(j = 1; j < lWidth - 1; j++)
			{
				if( *pmid == 0)                   //是0 不是我们需要考虑的点
				{
					pmid++;
					pmidtemp++;
					continue;
				}
				p3 = *(pmid + 1);
				p2 = *(pmid + 1 - lWidth);
				p1 = *(pmid - lWidth);
				p0 = *(pmid - lWidth -1);
				p7 = *(pmid - 1);
				p6 = *(pmid + lWidth - 1);
				p5 = *(pmid + lWidth);
				p4 = *(pmid + lWidth + 1);				
				sum = p0 & p1 & p2 & p3 & p4 & p5 & p6 & p7;
				if(sum == 0)
				{
					*pmidtemp = 1;       // 这样周围8个都是1的时候  pmidtemp==1 表明是边缘     					
				}

				pmid++;
				pmidtemp++;
			}
			pmid++;
			pmid++;
			pmidtemp++;
			pmidtemp++;
		}
		
		//现在开始删除
		pmid = (unsigned char *)lpDIBBits + lWidth + 1;
		pmidtemp = (unsigned char *)pTemp + lWidth + 1;

		for(i = 1; i < lHeight -1; i++)   // 不考虑图像第一行 第一列 最后一行 最后一列
		{
			for(j = 1; j < lWidth - 1; j++)
			{
				if( *pmidtemp == 0)     //1表明是边缘 0--周围8个都是1 即为中间点暂不予考虑
				{
					pmid++;
					pmidtemp++;
					continue;
				}

				p3 = *(pmid + 1);
				p2 = *(pmid + 1 - lWidth);
				p1 = *(pmid - lWidth);
				p0 = *(pmid - lWidth -1);
				p7 = *(pmid - 1);
				p6 = *(pmid + lWidth - 1);
				p5 = *(pmid + lWidth);
				p4 = *(pmid + lWidth + 1);
				
				p1 *= 2;
				p2 *= 4;
				p3 *= 8;
				p4 *= 16;
				p5 *= 32;
				p6 *= 64;
				p7 *= 128;

				sum = p0 | p1 | p2 | p3 | p4 | p5 | p6 | p7;
			//	sum = p0 + p1 + p2 + p3 + p4 + p5 + p6 + p7;
				if(deletemark[sum] == 1)
				{
					*pmid = 0;
					bStart = true;      //  表明本次扫描进行了细化
				}
				pmid++;
				pmidtemp++;
			}

			pmid++;
			pmid++;
			pmidtemp++;
			pmidtemp++;
		}
	}
	delete []pTemp;
	return true;
}
