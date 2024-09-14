# pd-signal
监控多个pandalive主播的直播状态，并发送开播、下播提醒消息的Telegram Bot。  

根据此项目修改而来 https://github.com/juzeon/dd-signal ，使用安装请前往查看原项目   

这个分支为需要使用Cookie登录的版本   
先看普通版介绍：https://github.com/nbtu/pd-signal/  

普通版：不需要账号登录，轮询每个主播的主要检测是否开播，使用API较频繁容易被封。  

Cookie登录版：需要获取Cookie填入index.js的第255行，登录后一次获取能100个主播信息，大大地减少的请求数量，避免IP被封。     
获取到数据后查询主播也变成在本地进行，循环间隔可以任意设置小数值，加快检测推送。    

bot-register.js 53行和63行     
有个设置必须关注频道才能关注,改一下自己的，把机器人拉进频道   
(私密频道可以转发一条频道信息到给 @getidsbot 获取频道id，-100开头的那个)  
如果仅仅自己使用可以填自己的id，也可以设置白名单（优先级更高）   

