# pd-signal
监控多个pandalive主播的直播状态，并发送开播、下播提醒消息的Telegram Bot。  

根据此项目修改而来 https://github.com/juzeon/dd-signal ，使用安装请前往查看原项目   

这个分支为需要使用Cookie登录的版本   
先看普通版介绍：https://github.com/nbtu/pd-signal/  

普通版：不需要账号登录，轮询每个主播的主要检测是否开播，使用API较频繁容易被封。  

Cookie登录版：需要获取Cookie填入index.js的第255行，登录后一次获取能100个主播信息，大大地减少的请求数量，避免IP被封。     
获取到数据后查询主播也变成在本地进行，循环间隔可以任意设置小数值，加快检测推送。     
