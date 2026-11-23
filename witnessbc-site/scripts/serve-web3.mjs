import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..','dist','deploy');
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.svg':'image/svg+xml','.xml':'application/xml','.txt':'text/plain; charset=utf-8'};
const port=Number(process.env.PORT||8091);
http.createServer((req,res)=>{
 try{
  const url=new URL(req.url||'/', 'http://127.0.0.1');
  let relative=decodeURIComponent(url.pathname);
  if(relative==='/'||relative==='')relative='/index.html';
  else if(/^\/[a-z-]+(?:\/[a-z-]+)*$/.test(relative))relative+='.html';
  if(relative.includes('..')||!/^\/[a-zA-Z0-9._/-]+$/.test(relative)){res.writeHead(400);return res.end('Invalid path');}
  const dest=path.resolve(root,'.'+relative);
  if(!dest.startsWith(root+path.sep)){res.writeHead(403);return res.end('Forbidden');}
  if(!fs.existsSync(dest)||!fs.statSync(dest).isFile()){res.writeHead(404);return res.end('Not Found');}
  res.writeHead(200,{'content-type':types[path.extname(dest)]||'application/octet-stream','cache-control':'no-cache'});
  fs.createReadStream(dest).pipe(res);
 }catch{res.writeHead(500);res.end('Server error');}
}).listen(port,'127.0.0.1',()=>console.log('Witness Web3 clean URL test server on '+port));
