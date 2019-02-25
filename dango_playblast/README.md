# 注意

bin里面的ffmpeg.exe是假的，因为真的太大传不上来。请移步官网下载ffmpeg.exe:
http://ffmpeg.org/download.html

### 运行方法
请将工具解压到某个位置后运行以下脚本：  
import sys  
sys.path.append(r"D:\dango_repo\maya_playblast")  
from dango_playblast import oct_playblast_main  
reload(oct_playblast_main)  
oct_playblast_main.main()  
请自行将上面的路径（D:\dango_repo\maya_playblast）换成自己的  

