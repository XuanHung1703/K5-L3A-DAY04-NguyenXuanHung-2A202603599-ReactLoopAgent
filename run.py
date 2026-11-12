import argparse
import io
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

sys.dont_write_bytecode = True
from agent import run_agent
from providers import Provider
from status_tools import StatusTools
from bonus.tools import BonusTools

ROOT = Path(__file__).resolve().parent
UI_PAGE = r'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Status Agent · Lab 04</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:#172925;background:#f5f7f5;font-synthesis:none}*{box-sizing:border-box}body{margin:0}button,textarea,select{font:inherit}button{cursor:pointer}.shell{max-width:1440px;margin:auto;padding:0 44px}.topbar{height:74px;background:#fff;border-bottom:1px solid #e3eae5;display:flex;align-items:center}.topinner{width:100%;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;align-items:center;gap:12px;font-weight:750;font-size:15px;letter-spacing:-.02em}.logo{width:32px;height:32px;border-radius:10px;background:#1d705b;color:#fff;display:grid;place-items:center;font-weight:800}.tag{color:#688079;background:#f0f5f1;border:1px solid #e0ebe3;padding:6px 10px;border-radius:8px;font-size:11px;font-weight:700;letter-spacing:.05em}.hero{padding:55px 0 28px}.eyebrow{color:#2b8065;font-size:11px;font-weight:800;letter-spacing:.15em;text-transform:uppercase;display:flex;align-items:center;gap:8px}.eyebrow:before{content:'';width:7px;height:7px;background:#3c9c78;border-radius:50%}h1{font-size:clamp(30px,4vw,43px);letter-spacing:-.045em;margin:12px 0 10px;line-height:1.1}h1 span{color:#268264}.subtitle{font-size:14px;color:#71817b;margin:0;line-height:1.6}.grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(360px,.95fr);gap:24px;align-items:start}.card{background:#fff;border:1px solid #e2eae4;border-radius:16px;box-shadow:0 3px 20px rgba(30,62,46,.035)}.cardpad{padding:25px}.card-title{display:flex;align-items:flex-start;gap:12px;margin-bottom:25px}.icon{width:38px;height:38px;border-radius:12px;background:#e9f5ee;color:#258665;display:grid;place-items:center;flex:none}.icon svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.8}.title{font-size:15px;font-weight:750;margin:0 0 4px}.desc{margin:0;font-size:12px;color:#91a098;line-height:1.5}.label{display:flex;align-items:center;justify-content:space-between;font-size:12px;font-weight:750;margin-bottom:9px}.label .sub{font-weight:500;color:#9ba8a1}textarea{display:block;width:100%;height:140px;resize:vertical;border:1px solid #dce6de;border-radius:11px;padding:14px;background:#fbfcfb;color:#21352e;outline:none;font-size:13px;line-height:1.7}textarea:focus,select:focus{border-color:#4a9f7c;box-shadow:0 0 0 3px #e1f4e8}textarea::placeholder{color:#b3bdb7}.counter{text-align:right;color:#a5b2aa;font-size:11px;margin-top:7px}.samples{margin:23px 0}.sample-label{font-size:11px;color:#98a89e;font-weight:750;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px}.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{border:1px solid #e0e9e2;background:#fff;color:#5a7166;border-radius:8px;font-size:11px;padding:8px 10px;text-align:left}.chip:hover{border-color:#76b99b;color:#247556;background:#f6fbf8}.divider{height:1px;background:#eef2ef;margin:22px 0}.settings{display:grid;grid-template-columns:1fr 1fr;gap:14px}.field label{font-size:11px;font-weight:750;display:block;margin-bottom:8px}.field select,.config{width:100%;height:42px;border:1px solid #e0e8e2;border-radius:9px;padding:0 12px;background:#fff;color:#425a4c;font-size:12px}.config{display:flex;align-items:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.hint{font-size:11px;color:#98a79e;line-height:1.55;margin:12px 0 0}.submit{width:100%;border:0;background:#1e755a;color:white;border-radius:10px;height:47px;font-weight:750;font-size:13px;margin-top:23px;box-shadow:0 5px 12px #1e755a25}.submit:hover{background:#165f48}.submit:disabled{opacity:.6;cursor:wait}.under{font-size:11px;text-align:center;color:#a2afa7;margin:12px 0 0}.right{display:grid;gap:18px}.result-card{min-height:352px;display:flex;flex-direction:column}.result-head{padding:22px 24px;border-bottom:1px solid #eef2ef;display:flex;justify-content:space-between;align-items:center}.head-left{display:flex;align-items:center;gap:9px;font-size:14px;font-weight:750}.head-left svg{width:17px;height:17px;fill:none;stroke:#328e6d;stroke-width:1.8}.badge{border-radius:20px;background:#f0f5f1;color:#83948a;font-size:10px;font-weight:700;padding:6px 9px}.badge.done{background:#e7f6eb;color:#27805f}.badge.error{background:#fff1ec;color:#b45c43}.result-body{flex:1;padding:24px;overflow-wrap:anywhere}.empty{min-height:250px;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center}.empty-icon{height:62px;width:62px;border-radius:20px;background:#f0f7f1;display:grid;place-items:center;color:#82b99a;margin-bottom:16px}.empty-icon svg{width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.5}.empty strong{font-size:13px}.empty p{color:#a0afa5;font-size:12px;line-height:1.6;max-width:240px}.answer{white-space:pre-wrap;font-size:13px;line-height:1.75;color:#364a3e}.notice{background:#f2f8f3;border:1px solid #e2efe5;border-radius:12px;padding:15px 17px;display:flex;gap:11px;color:#52725f;font-size:11px;line-height:1.6}.notice strong{display:block;color:#347054;font-size:11px;margin-bottom:2px}.trace-card{overflow:hidden}.trace-toggle{width:100%;padding:19px 22px;background:#fff;border:0;display:flex;align-items:center;justify-content:space-between;text-align:left}.trace-title{font-size:13px;font-weight:750;color:#243d30}.trace-sub{font-size:11px;color:#a1afa5;margin-top:4px}.chevron{color:#90a497;transition:transform .2s}.trace-toggle[aria-expanded=true] .chevron{transform:rotate(180deg)}.trace-content{padding:0 22px 20px;display:none}.trace-content.open{display:block}.trace-empty{font-size:12px;color:#9eaca2;margin:3px 0}.event{border-top:1px solid #edf1ed;padding:13px 0}.event-top{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:700;color:#365c47}.step{background:#eef6ef;color:#468065;padding:3px 7px;border-radius:6px;font-size:10px}.event pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:240px;overflow:auto;background:#f7faf7;border-radius:8px;padding:11px;font-size:10px;line-height:1.6;color:#536c5d}.footer{margin:32px 0;color:#a8b6ac;font-size:11px;display:flex;justify-content:space-between;gap:12px}.loading{color:#668575;font-size:13px}.spinner{display:inline-block;width:15px;height:15px;border:2px solid #c9e5d1;border-top-color:#278363;border-radius:50%;vertical-align:-3px;margin-right:8px;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}@media(max-width:800px){.shell{padding:0 20px}.hero{padding:36px 0 24px}.grid{grid-template-columns:1fr}.result-card{min-height:270px}.empty{min-height:170px}.footer{display:block}.footer span{display:block;margin:5px 0}}@media(max-width:420px){.tag{display:none}.settings{grid-template-columns:1fr}.cardpad{padding:20px}}
.lab-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:12px}.lab-btn{border:1px solid #dce9df;background:#f9fcfa;color:#35664e;border-radius:9px;min-height:40px;font-weight:700;font-size:11px;padding:9px;line-height:1.35}.lab-btn:hover{background:#eaf5ed;border-color:#a8cfb6}.lab-btn:disabled{opacity:.5;cursor:wait}.case-select{width:100%;height:40px;border:1px solid #e0e8e2;border-radius:9px;background:white;padding:0 10px;color:#425a4c;font-size:12px}.tools-title{font-size:13px;font-weight:750;margin:0 0 5px}.tools-copy{font-size:11px;line-height:1.6;color:#90a096;margin:0 0 13px}.out-pre{background:#f7faf7;border:1px solid #eaf0eb;border-radius:9px;padding:13px;font-size:11px;line-height:1.55;color:#405d4c;white-space:pre-wrap;overflow-wrap:anywhere;max-height:360px;overflow:auto}.score-card{padding:15px;border:1px solid #e5eee6;background:#f7fbf7;border-radius:10px;margin-bottom:14px}.score-card strong{font-size:21px;color:#1f7557}.score-card span{font-size:11px;color:#7d9284;display:block;margin-top:3px}
.tool-input{width:100%;height:40px;border:1px solid #e0e8e2;border-radius:9px;background:white;padding:0 10px;color:#425a4c;font-size:12px;outline:none}.tool-input:focus{border-color:#4a9f7c;box-shadow:0 0 0 3px #e1f4e8}
</style>
</head>
<body>
<header class="topbar"><div class="shell topinner"><div class="brand"><span class="logo">S</span> Status Agent <span style="color:#c5d3c9;font-weight:400">/</span> <span style="color:#8c9d92;font-weight:500">Lab 04</span></div><span class="tag">STATUS INVESTIGATION</span></div></header>
<main class="shell"><section class="hero"><div class="eyebrow">PHÒNG THỰC HÀNH · DAY 04</div><h1>Kiểm thử <span>Status Agent.</span></h1><p class="subtitle">Đặt câu hỏi, theo dõi các bước gọi tool và kiểm tra bằng chứng của agent.</p></section>
<div class="grid"><section class="card cardpad"><div class="card-title"><span class="icon"><svg viewBox="0 0 24 24"><path d="M4 5h16v12H9l-5 3z"/><path d="M8 9h8M8 12h5"/></svg></span><div><h2 class="title">Câu hỏi điều tra</h2><p class="desc">Bắt đầu với một câu hỏi về GitHub hoặc Cloudflare.</p></div></div>
<form id="form"><div class="label"><label for="question">Bạn muốn kiểm tra điều gì?</label><span class="sub">Bắt buộc</span></div><textarea id="question" maxlength="4000" placeholder="Ví dụ: GitHub Actions hiện có sự cố không? Hãy kiểm tra incident gần đây." required></textarea><div class="counter"><span id="count">0</span> / 4000</div>
<div class="samples"><div class="sample-label">THỬ VỚI CÂU HỎI GỢI Ý</div><div class="chips"><button class="chip" type="button" data-q="GitHub Actions hiện có sự cố không? Hãy kiểm tra incident gần đây.">↗ &nbsp;GitHub Actions</button><button class="chip" type="button" data-q="Cloudflare có incident liên quan cache purge không?">↗ &nbsp;Cloudflare Cache Purge</button><button class="chip" type="button" data-q="Kiểm tra các incident gần đây của GitHub và Cloudflare.">↗ &nbsp;So sánh hai dịch vụ</button></div></div>
<div class="divider"></div><div class="settings"><div class="field"><label for="mode">Nguồn dữ liệu</label><select id="mode"><option value="snapshot">Snapshot · Dữ liệu có sẵn</option><option value="live">Live · Dữ liệu trực tiếp</option></select></div><div class="field"><label>Cấu hình model</label><div class="config" id="config">Đang tải cấu hình...</div></div></div><p class="hint" id="mode-hint">Snapshot là dữ liệu lưu sẵn, không phản ánh trạng thái hiện tại.</p><button class="submit" id="submit" type="submit">Chạy agent &nbsp; →</button><p class="under">Agent gọi model và có thể sử dụng nhiều lượt API.</p></form>
<div class="divider"></div><h3 class="tools-title">Khám phá status tools</h3><p class="tools-copy">Chạy trực tiếp các tool của đề. Với snapshot, không cần API key.</p>
<div class="settings"><div class="field"><label for="tool-provider">Provider</label><select id="tool-provider"><option value="github">GitHub</option><option value="cloudflare">Cloudflare</option></select></div><div class="field"><label for="component">Component (không bắt buộc)</label><input class="tool-input" id="component" maxlength="200" placeholder="Ví dụ: Actions"></div></div>
<button class="lab-btn action" id="get-status" type="button" style="width:100%;margin-top:10px">get_status</button>
<div class="field" style="margin-top:14px"><label for="incident-id">Incident ID</label><input class="tool-input" id="incident-id" maxlength="200" placeholder="Ví dụ: wp49bp8bqo6c"></div><button class="lab-btn action" id="get-incident" type="button" style="width:100%;margin-top:10px">get_incident_details</button>
<div class="divider"></div><h3 class="tools-title">Kiểm thử &amp; đánh giá</h3><p class="tools-copy">Chạy kiểm thử offline hoặc đánh giá agent theo các case của đề.</p>
<button class="lab-btn action" id="unit" type="button" style="width:100%">Chạy unit test</button>
<div class="label" style="margin-top:18px"><label for="case">Chọn case eval</label><span class="sub">Bài chính</span></div><select class="case-select" id="case"></select>
<div class="lab-actions"><button class="lab-btn action" id="eval-one" type="button">Chạy eval một case</button><button class="lab-btn action" id="eval-all" type="button">Chạy eval 22 case</button></div>
<p class="hint">Eval gọi model cho agent và judge, có thể tốn quota. Kết quả chạy trên giao diện chỉ hiển thị, không lưu file.</p>
<div class="lab-actions"><button class="lab-btn action" id="before" type="button">Xem eval trước</button><button class="lab-btn action" id="after" type="button">Xem eval sau</button></div><button class="lab-btn action" id="trace-case" type="button" style="width:100%;margin-top:9px">Xem trace case đã chọn</button><p class="hint" id="case-hint">Chọn case, sau đó xem eval trước hoặc eval sau để xem trace.</p></section>
<div class="right"><section class="card result-card"><div class="result-head"><div class="head-left"><svg viewBox="0 0 24 24"><path d="M4 4h16v16H4zM8 9h8M8 13h8M8 17h5"/></svg> Kết quả kiểm thử</div><span class="badge" id="status">CHƯA CHẠY</span></div><div class="result-body" id="result" aria-live="polite"><div class="empty"><div class="empty-icon"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4M8 11h6M11 8v6"/></svg></div><strong>Kết quả sẽ xuất hiện tại đây</strong><p>Nhập câu hỏi và chạy kiểm tra để xem agent phản hồi.</p></div></div></section>
<div class="notice"><span style="font-size:16px">ⓘ</span><div><strong>Hiểu đúng dữ liệu</strong>Agent sử dụng tool và dữ liệu status; hãy kiểm tra nguồn và thời điểm snapshot trước khi kết luận.</div></div>
<section class="card trace-card"><button type="button" id="trace-toggle" class="trace-toggle" aria-expanded="false"><div><div class="trace-title">Các bước thực hiện <span id="trace-count" style="color:#8da396;font-weight:500"></span></div><div class="trace-sub">Xem tool, tham số và dữ liệu trả về</div></div><span class="chevron">⌄</span></button><div class="trace-content" id="trace-content"><p class="trace-empty">Chưa có bước nào được ghi nhận.</p></div></section></div></div><footer class="footer"><span>STATUS AGENT &nbsp; / &nbsp; LAB 04</span><span>Chạy cục bộ trên máy của bạn</span></footer></main>
<script>
const $=id=>document.getElementById(id), question=$('question'), result=$('result'), status=$('status'), trace=$('trace-content');
const actionButtons=[...document.querySelectorAll('.action'),$('submit')]; let lastCases=[];
question.addEventListener('input',()=>{$('count').textContent=question.value.length});
document.querySelectorAll('[data-q]').forEach(button=>button.addEventListener('click',()=>{question.value=button.dataset.q;question.dispatchEvent(new Event('input'));question.focus()}));
for(const [prefix,count] of [['E',6],['A',8],['H',8]])for(let i=1;i<=count;i++){const o=document.createElement('option');o.value=prefix+i;o.textContent=prefix+i;$('case').append(o)}
$('case').value='E2';
$('mode').addEventListener('change',e=>{$('mode-hint').textContent=e.target.value==='live'?'Live gọi status API thật và cần kết nối Internet.':'Snapshot là dữ liệu lưu sẵn, không phản ánh trạng thái hiện tại.'});
$('trace-toggle').addEventListener('click',()=>{const open=$('trace-toggle').getAttribute('aria-expanded')!=='true';$('trace-toggle').setAttribute('aria-expanded',String(open));trace.classList.toggle('open',open)});
fetch('/api/config').then(r=>r.json()).then(c=>{$('config').textContent=[c.provider,c.model].filter(Boolean).join(' · ')||'Chưa cấu hình'}).catch(()=>{$('config').textContent='Không đọc được cấu hình'});
function setStatus(text,type=''){status.textContent=text;status.className='badge '+type}
function appendText(text,cls='answer'){const el=document.createElement(cls==='out-pre'?'pre':'div');el.className=cls;el.textContent=text;result.append(el);return el}
function showTrace(items){trace.replaceChildren();$('trace-count').textContent=items.length?`· ${items.length} bước`:'';if(!items.length){const p=document.createElement('p');p.className='trace-empty';p.textContent='Không có bước nào được ghi nhận.';trace.append(p);return}items.forEach(item=>{const box=document.createElement('div');box.className='event';const top=document.createElement('div');top.className='event-top';const step=document.createElement('span');step.className='step';step.textContent='BƯỚC '+(item.step??'—');const name=document.createElement('span');name.textContent=item.name||item.event||'Sự kiện';top.append(step,name);const pre=document.createElement('pre');pre.textContent=JSON.stringify(item,null,2);box.append(top,pre);trace.append(box)})}
function showEval(report,selectedCount){result.replaceChildren();const summary=report.summary||{};const cases=report.cases||[];lastCases=cases;const count=selectedCount||cases.length;const score=summary.score_0_100;const card=document.createElement('div');card.className='score-card';const strong=document.createElement('strong');strong.textContent=score===null||score===undefined?'Chưa có điểm tổng':`${score} / 100`;const sub=document.createElement('span');sub.textContent=`Đã chấm ${summary.scored_cases??0} / ${count} case · Điểm judge chỉ mang tính tham khảo`;card.append(strong,sub);result.append(card);let lines=cases.map(c=>`${c.id}: ${c.grade?.score??'chưa chấm'} / 100 — ${c.grade?.reason||''}${c.result?.error?' · '+c.result.error:''}`).join('\n\n');if(cases.length===1&&cases[0].result?.answer)lines+='\n\nCâu trả lời agent:\n'+cases[0].result.answer;appendText(lines||'Không có case nào.','out-pre');showTrace(cases.length===1?(cases[0].result?.trace||[]):[]);setStatus(score===null||cases.length<count?'CHƯA HOÀN TẤT':'HOÀN THÀNH',score===null||cases.length<count?'error':'done')}
async function showReport(name){actionButtons.forEach(x=>x.disabled=true);setStatus('ĐANG TẢI');try{const response=await fetch('/api/report/'+name);const data=await response.json();if(!response.ok)throw Error(data.error||'Không đọc được kết quả.');showEval(data,data.summary?.total_cases)}catch(e){result.replaceChildren();appendText(e.message);setStatus('CÓ LỖI','error')}finally{actionButtons.forEach(x=>x.disabled=false)}}
$('before').addEventListener('click',()=>showReport('before'));$('after').addEventListener('click',()=>showReport('after'));
$('trace-case').addEventListener('click',()=>{const selected=lastCases.find(c=>c.id===$('case').value);if(!selected){$('case-hint').textContent='Chưa có dữ liệu cho case này. Hãy xem eval trước hoặc eval sau.';return}showTrace(Array.isArray(selected.result?.trace)?selected.result.trace:[]);$('trace-toggle').setAttribute('aria-expanded','true');trace.classList.add('open');$('case-hint').textContent='Đang xem trace của '+selected.id+'.';trace.scrollIntoView({behavior:'smooth',block:'nearest'})});
function renderJob(out){result.replaceChildren();if(out.kind==='agent'){const data=out.data;appendText(data.answer||(data.status==='max_steps'?'Agent đã hết số bước trước khi trả lời.':data.error||'Agent không trả về câu trả lời.'));setStatus(data.status==='completed'?'HOÀN THÀNH':data.status==='max_steps'?'HẾT SỐ BƯỚC':'CÓ LỖI',data.status==='completed'?'done':'error');showTrace(Array.isArray(data.trace)?data.trace:[])}else if(out.kind==='tool'){appendText('Kết quả '+out.name);appendText(JSON.stringify(out.data,null,2),'out-pre');setStatus(out.data?.ok===false?'CÓ LỖI':'HOÀN THÀNH',out.data?.ok===false?'error':'done')}else if(out.kind==='unit'){appendText(out.ok?'Unit test: thành công':'Unit test: có lỗi');appendText(out.output||'Không có đầu ra.','out-pre');setStatus(out.ok?'HOÀN THÀNH':'CÓ LỖI',out.ok?'done':'error')}else if(out.kind==='eval'){showEval(out,out.selected_count)}}
async function startJob(payload,label){actionButtons.forEach(x=>x.disabled=true);setStatus('ĐANG CHẠY');result.replaceChildren();const loading=document.createElement('p');loading.className='loading';const spin=document.createElement('span');spin.className='spinner';const message=document.createElement('span');message.textContent=label+'...';loading.append(spin,message);result.append(loading);lastCases=[];showTrace([]);try{const response=await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw Error(data.error||'Không thể bắt đầu.');while(true){await new Promise(resolve=>setTimeout(resolve,1000));const res=await fetch('/api/job?id='+encodeURIComponent(data.id));const job=await res.json();if(!res.ok)throw Error(job.error||'Không tìm thấy lượt chạy.');if(job.state==='done'){renderJob(job.result);break}if(job.state==='error')throw Error(job.error||'Không thể hoàn tất.');message.textContent=job.total?`${label}: ${job.completed}/${job.total} · đang chạy ${job.current}`:label+'...'}}catch(e){result.replaceChildren();appendText(e.message||'Không thể kết nối tới server.');setStatus('CÓ LỖI','error')}finally{actionButtons.forEach(x=>x.disabled=false)}}
$('form').addEventListener('submit',e=>{e.preventDefault();const text=question.value.trim();if(text)startJob({action:'agent',question:text,mode:$('mode').value},'Agent đang xử lý')});
$('get-status').addEventListener('click',()=>startJob({action:'get_status',provider:$('tool-provider').value,component:$('component').value,mode:$('mode').value},'Đang chạy get_status'));
$('get-incident').addEventListener('click',()=>{const id=$('incident-id').value.trim();if(!id){$('incident-id').focus();$('incident-id').setCustomValidity('Nhập incident ID trước khi chạy.');$('incident-id').reportValidity();return}startJob({action:'get_incident_details',provider:$('tool-provider').value,incident_id:id,mode:$('mode').value},'Đang chạy get_incident_details')});
$('incident-id').addEventListener('input',()=>$('incident-id').setCustomValidity(''));
$('unit').addEventListener('click',()=>startJob({action:'unit'},'Đang chạy unit test'));
$('eval-one').addEventListener('click',()=>startJob({action:'eval_one',case:$('case').value},'Đang chạy eval'));
$('eval-all').addEventListener('click',()=>startJob({action:'eval_all'},'Đang chạy eval 22 case'));
</script>
</body>
</html>
'''
LOCK = threading.Lock()
JOB = {'id': '', 'state': 'idle'}


def run(question, mode, provider_name, model, max_steps, fail=False, bonus=False):
    provider = Provider(provider_name, model)
    tools = BonusTools(mode) if bonus else StatusTools(mode, fail=fail)
    return run_agent(question, provider, tools, max_steps=max_steps)


def configured_values():
    values = {}
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:].strip()
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return {'provider': values.get('PROVIDER') or os.getenv('PROVIDER', 'openai'),
            'model': values.get('MODEL') or os.getenv('MODEL', '')}


def update_job(job_id, **values):
    with LOCK:
        if JOB['id'] == job_id:
            JOB.update(values)


def perform_job(job_id, data):
    try:
        action = data['action']
        if action == 'agent':
            config = configured_values()
            result = run(data['question'], data['mode'], config['provider'], config['model'], 6)
            update_job(job_id, state='done', result={'kind': 'agent', 'data': result})
        elif action in ('get_status', 'get_incident_details'):
            arguments = {'provider': data['provider']}
            if action == 'get_status':
                arguments['component'] = data['component']
            else:
                arguments['incident_id'] = data['incident_id']
            result = StatusTools(data['mode']).execute(action, arguments)
            update_job(job_id, state='done', result={'kind': 'tool', 'name': action, 'data': result})
        elif action == 'unit':
            env = os.environ.copy()
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            proc = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                                  cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
            update_job(job_id, state='done', result={'kind': 'unit', 'ok': proc.returncode == 0,
                                                    'output': (proc.stdout + proc.stderr)[-30000:]})
        else:
            eval_path = str(ROOT / 'evals')
            if eval_path not in sys.path:
                sys.path.insert(0, eval_path)
            from evals.run_evals import run_case
            from grading import summarize
            cases = json.loads((ROOT / 'evals' / 'cases.json').read_text(encoding='utf-8'))
            selected = cases if action == 'eval_all' else [c for c in cases if c['id'] == data['case']]
            if not selected:
                raise ValueError('Không tìm thấy case.')
            config = configured_values()
            args = SimpleNamespace(provider=config['provider'], model=config['model'],
                                   judge_provider=config['provider'], judge_model=config['model'],
                                   max_steps=8, bonus=False)
            results = []
            for case in selected:
                update_job(job_id, current=case['id'], completed=len(results), total=len(selected))
                item = run_case(case, args)
                results.append(item)
                if item.get('grade', {}).get('score') is None:
                    break
            summary = summarize(results)
            update_job(job_id, state='done', result={'kind': 'eval', 'cases': results, 'summary': summary,
                                                    'selected_count': len(selected), 'config': config})
    except Exception:
        update_job(job_id, state='error', error='Không thể hoàn tất. Kiểm tra cấu hình, kết nối và quota.')


class UIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.valid_host():
            return self.send_json(403, {'error': 'Địa chỉ không hợp lệ.'})
        url = urlsplit(self.path)
        if url.path == '/':
            body = UI_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
        elif url.path == '/api/config':
            self.send_json(200, configured_values())
        elif url.path == '/api/job':
            requested = parse_qs(url.query).get('id', [''])[0]
            with LOCK:
                state = dict(JOB) if requested and requested == JOB['id'] else None
            self.send_json(200, state) if state else self.send_json(404, {'error': 'Không tìm thấy lượt chạy.'})
        elif url.path in ('/api/report/before', '/api/report/after'):
            name = 'eval_before.json' if url.path.endswith('/before') else 'eval_after.json'
            try:
                report = json.loads((ROOT / name).read_text(encoding='utf-8'))
                self.send_json(200, report)
            except (OSError, ValueError):
                self.send_json(404, {'error': f'Không đọc được {name}.'})
        else:
            self.send_json(404, {'error': 'Không tìm thấy trang.'})

    def do_POST(self):
        if not self.valid_host() or self.path != '/api/start':
            return self.send_json(403, {'error': 'Yêu cầu không hợp lệ.'})
        origin = self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
            return self.send_json(403, {'error': 'Nguồn yêu cầu không hợp lệ.'})
        if self.headers.get_content_type() != 'application/json':
            return self.send_json(415, {'error': 'Cần gửi dữ liệu JSON.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 16384:
                raise ValueError()
            data = json.loads(self.rfile.read(length))
            action = data.get('action')
            if action not in ('agent', 'unit', 'eval_one', 'eval_all', 'get_status', 'get_incident_details'):
                raise ValueError()
            if action == 'agent':
                question = data.get('question')
                if not isinstance(question, str) or not 1 <= len(question.strip()) <= 4000 or data.get('mode') not in ('snapshot', 'live'):
                    raise ValueError()
                data['question'] = question.strip()
            if action == 'eval_one':
                valid = {f'E{i}' for i in range(1, 7)} | {f'A{i}' for i in range(1, 9)} | {f'H{i}' for i in range(1, 9)}
                if data.get('case') not in valid:
                    raise ValueError()
            if action in ('get_status', 'get_incident_details'):
                if data.get('provider') not in ('github', 'cloudflare') or data.get('mode') not in ('snapshot', 'live'):
                    raise ValueError()
                key = 'component' if action == 'get_status' else 'incident_id'
                value = data.get(key, '')
                if not isinstance(value, str) or len(value) > 200 or (key == 'incident_id' and not value.strip()):
                    raise ValueError()
                data[key] = value.strip()
        except (TypeError, ValueError, AttributeError, json.JSONDecodeError):
            return self.send_json(400, {'error': 'Kiểm tra dữ liệu đầu vào.'})
        with LOCK:
            if JOB['state'] == 'running':
                return self.send_json(409, {'error': 'Đang có một lượt chạy khác.'})
            job_id = secrets.token_urlsafe(18)
            JOB.clear()
            JOB.update({'id': job_id, 'state': 'running', 'current': '', 'completed': 0, 'total': 0})
        threading.Thread(target=perform_job, args=(job_id, data), daemon=True).start()
        self.send_json(202, {'id': job_id})


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description='Chạy status agent hoặc mở giao diện kiểm thử')
    parser.add_argument('question', nargs='?', help='Câu hỏi cho agent; bỏ trống để mở giao diện')
    parser.add_argument('--bonus', action='store_true', help='Dùng bộ tools bonus')
    parser.add_argument('--mode', choices=['snapshot', 'live'], default='snapshot')
    parser.add_argument('--provider', choices=['openai', 'gemini', 'anthropic', 'openrouter'], default=os.getenv('PROVIDER', 'openai'))
    parser.add_argument('--model', default=os.getenv('MODEL'))
    parser.add_argument('--max-steps', type=int, default=6)
    parser.add_argument('--port', type=int, default=8765, help='Cổng giao diện trên localhost')
    args = parser.parse_args()
    if args.max_steps < 1:
        parser.error('--max-steps phải >= 1')
    if args.question is None:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), UIHandler)
        url = f'http://127.0.0.1:{server.server_port}'
        print(f'Open {url}', flush=True)
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    try:
        result = run(args.question, args.mode, args.provider, args.model, args.max_steps, bonus=args.bonus)
    except (ValueError, RuntimeError, NotImplementedError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'completed' else 1


if __name__ == '__main__':
    sys.exit(main())
