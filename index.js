const args = require('minimist')(process.argv.slice(2));
const urlParse = require('url-parse');
const fs=require('fs');
const path=require('path');
const nodeGlobalProxy = require("node-global-proxy").default;
const $ = require('./includes');
const dbm = require('./dbm');
const FormData = require('form-data');
const jsonfile = require('jsonfile');
const axios = require('axios');
const helpText = `
参数：
  --interval <IntervalBySec> - 可选，每次访问API间隔的秒数，默认为60
  --token <TelegramBotToken> - 必选，Telegram Bot Token
  --proxy <HTTPProxy> - 可选，以 http:// 开头的代理
  --pass <password> - 可选，默认 kbjba，用于管理黑白名单
`;
//检测的检测
const interval = 2;

//获取列表的间隔
const maininterval = args.interval ? args.interval : 60;
if (!$.isInt(interval)) {
    console.log(helpText);
    process.exit(-1);
}
const token = args.token;
if (!token) {
    console.log(helpText);
    process.exit(-1);
}
const pass = args.pass ? args.pass : "kbjba" ;
$.bot.token = token;
const proxy = args.proxy;
if (proxy) {
    let proxyUrlObj = urlParse(proxy, true);
    if (proxyUrlObj.protocol != 'http:') {
        console.log('--proxy 只支持HTTP PROXY');
        process.exit(-1);
    }
    nodeGlobalProxy.setConfig(proxy);
    nodeGlobalProxy.start();
    // $.bot.options.request = {
    //     proxy: proxy
    // };
    // $.axios.defaults.proxy = {
    //     host: proxyUrlObj.hostname,
    //     port: proxyUrlObj.port
    // };

}
let whitelist = dbm.getListBystatus("whitelist");
let blacklist = dbm.getListBystatus("blacklist");
console.log(whitelist);
console.log(blacklist);
const botRegister = require('./bot-register')(whitelist, blacklist, pass);

botRegister();
$.bot.startPolling();
let vtbs = dbm.getVtbs();
$.emitter.on('updateVtbs', () => {
    vtbs=dbm.getVtbs();
    console.log('Reloaded Vtbs.');
});
console.log('dd-signal 已启动！');
async function notifySubscriberChats(vtb){
    console.log('Let\'s notify subscribers about '+vtb.mid);
    let head;
    if (vtb.liveStatus !== null && vtb.liveStatus !== undefined) {
        const sourceZone = 9; //源时区，韩+9;
        const targetZone = 8; //目标时区，中+8;
        //将标准时间格式转换成时间戳
        const nowTime = new Date(vtb.liveStatus);
        const chineseTime = nowTime - (sourceZone*60*60*1000)  + (targetZone*60*60*1000) ;
        const startTime = new Date(chineseTime).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
        let type = "";
        // 检查 vtb.title 是否包含特定字符，并相应地追加到 type
        if (vtb.title.includes("🎥")) {
            type += "🎥录像";
        }
        if (vtb.title.includes("💰")) {
            type += "💰粉丝房";
        }
        let online = '';
        let offline = '';
        
        const cleanedTitle = vtb.title.replace(/[\[\].\-_()]/g, '');
        const message = '`' + vtb.username + '`' + '(`' + vtb.usernick + '`)\n';
        const link =  ' [' + cleanedTitle + '](https://5721004.xyz/player/pandalive.html?url=' + vtb.mid + ')\n' ;
        online  += '🟢  ' + message + link + '~';
        offline += '🔴  ' + message + '~';
        
        head='`'+vtb.mid+'` '+(vtb.liveStatus?'开播啦！'+ type +'\n开播时间：'+ startTime +'\n\n'+ online :'下播了。\n\n'+offline);
    } else {
        console.error('vtb.liveStatus 不存在或为 null/undefined');
    }
    
    let watches=dbm.getWatchByMid(vtb.mid);
    for(let [index,watch] of watches.entries()){
        console.log(watch.chatid);
		const options = {
            parse_mode:'Markdown',
            disable_web_page_preview:true,
            reply_markup: {
                inline_keyboard: [
                    [
                        { text: '在线主播', callback_data: 'online' },
                        { text: '监控列表', callback_data: 'list' }
                    ]
                ]
            }
        };
        await $.bot.sendMessage(watch.chatid,head,options);
        if(index%20==0 && index!=0){
            await $.sleep(1000);
        }
    }
}

(async function rotate() {
    await main();
    let data;

    try {
        data = await new Promise((resolve, reject) => {
            fs.readFile('json.json', 'utf8', (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        });
    } catch (err) {
        console.error('Failed to read json.json:', err);
        return; // 如果读取文件失败，停止执行
    }
    
    if (!data.trim()) {
        console.error('File is empty or contains only whitespace');
        return; // 如果文件为空或仅包含空白字符，停止执行
    }
    
    let jsonData;

    try {
        // 解析 JSON 数据
        jsonData = JSON.parse(data);
    } catch (err) {
        console.error('Failed to parse JSON:', err);
        return; // 如果解析失败，停止执行
    }

    if (!jsonData || !jsonData.list) {
        console.error('Invalid jsonData format');
        return; // 如果 jsonData 格式无效，停止执行
    }

    const processVtb = async (vtb) => {
        process.stdout.write('Checking ' + vtb.mid + '：');

        try {
            // 查找 userId 的信息
            const response = jsonData.list.find(item => item.userId === vtb.mid);

            if (response) {
                // 处理成功响应
                const mediaData = response;
                const startTime = mediaData.startTime || "";
                const otitle = mediaData.title || "";
                const userNick = mediaData.userNick || "";

                const liveType = mediaData.liveType === "rec" ? "🎥|" : "";
                const isPw = mediaData.isPw ? "🔒|" : "";
                const isAdult = mediaData.isAdult ? "🔞|" : "";
                const type = mediaData.type === "fan" ? "💰|" : "";
                const title = liveType + type + isPw + isAdult + otitle;

                if (userNick !== vtb.usernick) {
                    dbm.updateVtbColumn('usernick', userNick, vtb.mid);
                    vtb.usernick = userNick;
                }
                if (title !== vtb.title) {
                    dbm.updateVtbColumn('title', title, vtb.mid);
                    vtb.title = title;
                }

                if (startTime !== vtb.liveStatus) {
                    dbm.updateVtbColumn('liveStatus', startTime, vtb.mid);
                    vtb.liveStatus = startTime;
                    notifySubscriberChats(vtb);
                }

                console.log('online');
            } else {
                console.log('offline');
                const startTime = "";
                if (startTime !== vtb.liveStatus) {
                    dbm.updateVtbColumn('liveStatus', startTime, vtb.mid);
                    vtb.liveStatus = startTime;
                    notifySubscriberChats(vtb);
                }
            }
        } catch (error) {
            // 处理 jsonData 获取错误
            console.error(`Error while checking ${vtb.mid}:`, error.message);
        } finally {
            await new Promise(resolve => setTimeout(resolve, interval * 1000));
        }
    };

    const chunkSize = 3;

    for (let i = 0; i < vtbs.length; i += chunkSize) {
        const chunk = vtbs.slice(i, i + chunkSize);
        await Promise.all(chunk.map(vtb => processVtb(vtb)));
    }

    console.log(vtbs.length);

    if (vtbs.length < 30) {
        console.log('wait!');
        await new Promise(resolve => setTimeout(resolve, maininterval * 1000));
    }

    setImmediate(rotate);
})();

async function fetchJson(offset, limit, cookie) {
    try {
        const response = await axios.get('https://api.pandalive.co.kr/v1/live', {
            params: {
                offset,
                limit,
                orderBy: 'hot',
                onlyNewBj: 'N'
            },
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'cookie': cookie
            },
            timeout: 5000 // 设置超时时间为5秒
        });
        
        return response.data;
    } catch (error) {
        console.error('Failed to fetch data:', error.message);
        return null;
    }
}

// 主要函数
async function main() {
    ////////////////////////修改cookie////////////修改cookie//////////////////修改cookie///////////////////////
    const cookie="Your Cookie"; 
    const batchSize = 96; // 一次获取的数据量

    // 获取第一页的JSON数据
    let json = await fetchJson(0, batchSize, cookie);
    if (!json || !json.result) {
        console.error('获取列表失败');
        return; // 直接跳过整个函数的执行
    }

    console.log(`------${new Date()}------`);
    const total = json.page.total;
    console.log(`在线主播:${total} | 获取前96主播`);

    // 如果在线主播数超过96，则获取额外的页面并合并JSON数据
    if (total > batchSize) {
        let remaining = total - batchSize;
        let page = 2;
        while (remaining > 0) {
            console.log(` | 获取第${page}页`);
            const offset = (page - 1) * batchSize;
            const limit = Math.min(batchSize, remaining); // 确保不超过剩余数据量
            const json2 = await fetchJson(offset, limit, cookie);
            if (json2 && json2.list) {
                console.log(`获取第${page}页成功`);
                json.list = [...json.list, ...json2.list.filter(item => !json.list.find(existing => existing.code === item.code))];
                remaining -= batchSize;
                page++;
            } else {
                console.error(`获取第${page}页失败`);
                break;
            }
        }
    }

    // 将结果写入JSON文件
    try {
        await jsonfile.writeFile('json.json', json, { spaces: 2 });
        console.log('JSON文件写入成功');
        
    } catch (error) {
        console.error('写入JSON文件失败:', error);
    }
}


