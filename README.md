# Qt_display
需求：  
1. 人流量统计标签模块（Qt的label类型）  
* init部分  
TCP连接evm的server（IP地址：192.168.101.100，端口号:8989）  
标签结果初始化为0  
创建timer  
timer连接函数  
启动timer(1秒）  
  
* timer链接函数  
非阻塞读tcp结果  
有结果则  
    获得锁  
    标签结果label+=1  
    释放锁  
启动timer(1秒)  
  
2. 人流量统计重置按钮  
* init部分  
创建按钮  
按钮连接函数  
  
* 按钮链接函数  
获得锁  
标签结果label = 0  
释放锁  
  
3. 人群计数结果标签模块  
* init部分  
TCP连接evm的server（IP地址：192.168.101.100，端口号:8989）  
标签结果初始化为-1  
创建timer  
timer连接函数  
启动timer（1秒）  
  
* timer链接函数  
非阻塞读tcp结果  
有结果则更新标签label = 结果  
启动timer（1秒）  

4. 人群计数结果曲线图  
* 曲线图展示人群计数结果。x轴为时间（单位：秒），保留10秒结果。y轴表示结果。