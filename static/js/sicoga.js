// ─── NAV
function nav(p) {
  document.querySelectorAll('.page').forEach(function(x){x.classList.remove('active');});
  document.querySelectorAll('.ni').forEach(function(x){x.classList.remove('active');});
  var pg = document.getElementById('page-'+p);
  if (pg) pg.classList.add('active');
  var ni = document.querySelector('.ni[data-p="'+p+'"]');
  if (ni) ni.classList.add('active');
  if (p==='disp' && !document.getElementById('dispTbl').hasChildNodes()) buildDisp();
  if (p==='proy-anual' && !document.getElementById('proyAnualTbl').hasChildNodes()) buildProyAnual();
}

// ─── WEEK CHART
(function(){
  var data=[{w:28,c:186},{w:29,c:214},{w:30,c:342,cur:1},{w:31,c:164},{w:32,c:394},
    {w:33,c:174},{w:34,c:0},{w:35,c:210},{w:36,c:0},{w:37,c:222},{w:38,c:0},{w:39,c:402},{w:40,c:186}];
  var mx=Math.max.apply(null,data.map(function(d){return d.c||1;}));
  var el=document.getElementById('wChart');
  data.forEach(function(d){
    var pct=d.c?Math.max(8,Math.round(d.c/mx*100)):8;
    var col=d.cur?'var(--am)':d.c?'var(--gn)':'var(--bdr2)';
    var w=document.createElement('div'); w.className='ww';
    w.innerHTML='<div class="wval">'+(d.c||'—')+'</div><div class="wb'+(d.cur?' cur':'')+'" style="height:'+pct+'%;background:'+col+'"></div><div class="wlbl">S'+d.w+'</div>';
    el.appendChild(w);
  });
})();

// ─── CORRAL MAP
(function(){
  var corrales=[
    {n:'C01',t:'vp',l:'CH087',c:214},{n:'C02',t:'oc',l:'CH089',c:196},
    {n:'C03',t:'vp',l:'CH091H',c:128},{n:'C04',t:'zp',l:'CH088',c:210},
    {n:'C05',t:'oc',l:'CH092',c:186},{n:'C06',t:'oc',l:'CH090H',c:174},
    {n:'C07',t:'li'},{n:'C08',t:'oc',l:'CH093',c:198},
    {n:'C09',t:'oc',l:'CH085',c:222},{n:'C10',t:'zp',l:'CH086H',c:164},
    {n:'C11',t:'oc',l:'CH094',c:220},{n:'C12',t:'li'},
    {n:'C13',t:'oc',l:'CH082',c:208},{n:'C14',t:'li'},
    {n:'C15',t:'oc',l:'CH084',c:194},{n:'C16',t:'li'},
    {n:'C17',t:'oc',l:'CH081',c:176},{n:'C18',t:'oc',l:'CH083',c:214},
  ];
  var cg=document.getElementById('corralMap');
  corrales.forEach(function(c){
    var el=document.createElement('div');
    el.className='cc '+c.t;
    el.innerHTML='<div class="cn">'+c.n+'</div><div class="ci">'+(c.l||'Libre')+(c.c?' · '+c.c:'')+'</div>';
    if(c.l) el.onclick=function(){nav('disp');};
    cg.appendChild(el);
  });
})();

// ─── DISPONIBILIDAD TABLE
var lotesData=[
  {l:'CH094',c:'C11',cab:220,dias:0,pi:250,pp:250,gdp:1.35,etapa:'F1',po:480,ini:'2025-07-21'},
  {l:'CH092',c:'C05',cab:186,dias:14,pi:265,pp:266,gdp:1.38,etapa:'F1',po:490,ini:'2025-07-07'},
  {l:'CH090H',c:'C06',cab:174,dias:28,pi:240,pp:242,gdp:1.22,etapa:'Transición',po:460,ini:'2025-06-23'},
  {l:'CH089',c:'C02',cab:196,dias:49,pi:270,pp:272,gdp:1.32,etapa:'F1',po:488,ini:'2025-06-02'},
  {l:'CH088',c:'C04',cab:210,dias:42,pi:290,pp:291,gdp:1.40,etapa:'F3 SSS',po:500,ini:'2025-06-09'},
  {l:'CH087',c:'C01',cab:214,dias:128,pi:252,pp:254,gdp:1.34,etapa:'F3 SZ',po:480,ini:'2025-03-14'},
  {l:'CH086H',c:'C10',cab:164,dias:32,pi:238,pp:239,gdp:1.25,etapa:'Zilpaterol',po:460,ini:'2025-04-16'},
  {l:'CH085',c:'C09',cab:222,dias:75,pi:275,pp:276,gdp:1.38,etapa:'F3 SSS',po:495,ini:'2025-05-07'},
];
var epill={'F1':'pill pb','Transición':'pill pa','F3 SSS':'pill pg','F3 SZ':'pill pp','Zilpaterol':'pill pp'};

function getWeek(d){var f=new Date(d.getFullYear(),0,1);return Math.ceil(((d-f)/86400000+f.getDay()+1)/7);}
function addD(d,n){var r=new Date(d);r.setDate(r.getDate()+n);return r;}
function fmt(d){return d.toLocaleDateString('es-MX',{day:'2-digit',month:'short'});}
function fmtFull(d){return d.toLocaleDateString('es-MX',{day:'2-digit',month:'short',year:'numeric'});}

function buildDisp(){
  var tb=document.getElementById('dispTbl');
  lotesData.forEach(function(l){
    var ph=(l.pi+l.dias*l.gdp).toFixed(0);
    var dr=Math.ceil((l.po-l.pi)/l.gdp);
    var vd=addD(new Date(l.ini),dr);
    var sv=getWeek(vd);
    var r1=addD(new Date(l.ini),60);
    var pr=(l.pi+60*l.gdp).toFixed(0);
    var sexo=l.l.endsWith('HV')?'HV':l.l.endsWith('H')?'H':'M';
    tb.innerHTML+='<tr><td>'+l.c+'</td><td class="mn" style="color:var(--am)">'+l.l+'</td><td>'+sexo+'</td><td class="mn">'+l.cab+'</td><td class="mn">'+fmt(new Date(l.ini))+'</td><td class="mn">'+l.pi+' kg</td><td class="mn">'+l.dias+'</td><td class="mn">'+dr+'</td><td class="mn">'+ph+' kg</td><td class="mn">'+l.gdp+' kg/d</td><td class="mn">'+l.po+' kg</td><td class="mn">'+pr+' kg</td><td class="mn">60</td><td class="mn">'+fmt(r1)+'</td><td class="mn">'+l.pp+' kg</td><td><span class="'+(epill[l.etapa]||'pill pb')+'">'+l.etapa+'</span></td><td class="mn">S'+sv+'</td><td><span style="cursor:pointer;color:var(--bl);font-size:12px" onclick="nav(\'disp-alta\')">Alta →</span></td></tr>';
  });
}

// ─── PROYECCIÓN ANUAL
var proyData=[
  {s:28,f:'07 Jul',c:'C17',l:'CH081',sx:'M',inv:176},{s:29,f:'14 Jul',c:'C18',l:'CH083',sx:'M',inv:214},
  {s:30,f:'21 Jul',c:'C01',l:'CH087',sx:'M',inv:214},{s:30,f:'21 Jul',c:'C03',l:'CH091H',sx:'H',inv:128},
  {s:31,f:'28 Jul',c:'C10',l:'CH086H',sx:'H',inv:164},
  {s:32,f:'04 Ago',c:'C02',l:'CH089',sx:'M',inv:196},{s:32,f:'04 Ago',c:'C08',l:'CH093',sx:'M',inv:198},
  {s:33,f:'11 Ago',c:'C06',l:'CH090H',sx:'H',inv:174},
  {s:34,f:'18 Ago',c:null},{s:35,f:'25 Ago',c:'C04',l:'CH088',sx:'M',inv:210},
  {s:36,f:'01 Sep',c:null},{s:37,f:'08 Sep',c:'C09',l:'CH085',sx:'M',inv:222},
  {s:38,f:'15 Sep',c:null},{s:39,f:'22 Sep',c:'C15',l:'CH084',sx:'M',inv:194},
  {s:40,f:'29 Sep',c:'C05',l:'CH092',sx:'M',inv:186},
];
function buildProyAnual(){
  var tb=document.getElementById('proyAnualTbl');
  proyData.forEach(function(d){
    var sinSal=!d.c;
    tb.innerHTML+='<tr><td class="mn">Sem '+d.s+'</td><td class="mn">'+d.f+'</td><td>'+(d.c||'—')+'</td><td class="mn">'+(d.l||'—')+'</td><td>'+(d.sx||'—')+'</td><td class="mn">'+(d.inv||'0')+'</td><td>'+(sinSal?'<span class="pill pr">⚠ Planear compra</span>':'<span class="pill pg">OK</span>')+'</td></tr>';
  });
}

// ─── ALTA LOTE CALC
function recalc(){
  var pi=parseFloat(document.getElementById('fPI').value)||250;
  var po=parseFloat(document.getElementById('fPO').value)||480;
  var gdp=parseFloat(document.getElementById('fGDP').value)||1.35;
  var cab=parseInt(document.getElementById('fCab').value)||220;
  var fs=document.getElementById('fFech').value;
  var ini=fs?new Date(fs):new Date();
  var dias=Math.ceil((po-pi)/gdp);
  var hoy=new Date();
  var dt=Math.max(0,Math.floor((hoy-ini)/86400000));
  var ph=(pi+dt*gdp).toFixed(1);
  var pr=(pi+60*gdp).toFixed(0);
  var vd=addD(ini,dias); var sv=getWeek(vd);
  var r1=addD(ini,60),r2=addD(ini,120);
  var r3=pi<290?addD(ini,180):null;
  var tf=addD(ini,35),zd=addD(vd,-35);
  document.getElementById('pDias').textContent=dias+' días';
  document.getElementById('pPhoy').textContent=ph+' kg';
  document.getElementById('pRango').textContent=pr+' kg (al día 60)';
  document.getElementById('pFV').textContent=fmtFull(vd);
  document.getElementById('pSV').textContent='Semana '+sv;
  document.getElementById('pR1').textContent=fmtFull(r1);
  document.getElementById('pR2').textContent=fmtFull(r2);
  document.getElementById('pR3').textContent=r3?fmtFull(r3):'No aplica (peso ≥290 kg)';
  document.getElementById('pFT').textContent=fmtFull(tf);
  document.getElementById('pZilp').textContent=fmtFull(zd);
  document.getElementById('pKilos').textContent=(po*cab).toLocaleString()+' kg';
  var etapas=[
    {t:'F1 sin melaza',s:fmt(ini)+' → '+fmt(addD(ini,21))+' · 21 días',done:dt>=21},
    {t:'Transición F1→F3',s:fmt(addD(ini,21))+' → '+fmt(tf)+' · 14 días',done:dt>=35},
    {t:'F3 SSS — Engorda',s:fmt(tf)+' → '+fmt(zd),done:hoy>zd},
    {t:'F3 SZ + Zilpaterol (35 días)',s:fmt(zd)+' → '+fmt(vd),done:hoy>vd},
    {t:'Venta proyectada',s:fmt(vd)+' · Semana '+sv,done:false,act:true},
  ];
  document.getElementById('etapasTL').innerHTML=etapas.map(function(e,i){
    return '<div class="tli '+(e.done?'done':e.act?'act':'pend')+'"><div class="tll"><div class="tld"></div>'+(i<etapas.length-1?'<div class="tlln"></div>':'')+'</div><div class="tlc"><div class="tlt">'+e.t+'</div><div class="tls">'+e.s+'</div></div></div>';
  }).join('');
}
recalc();
['fPI','fPO','fGDP','fCab','fFech'].forEach(function(id){
  var el=document.getElementById(id);
  if(el) el.addEventListener('input',recalc);
});

// ─── CIERRE
var cData={
  'CH083':{cab:214,cabI:220,mu:6,fc:'2025-03-14',fci:'2025-07-25',kR:55330,cC:2486850,kV:60242,pvK:52,alK:234800,alC:914720,mC:38200,hC:342400,gdpR:1.34,conv:7.42,mort:2.73},
  'CH078H':{cab:186,cabI:192,mu:6,fc:'2025-02-10',fci:'2025-06-30',kR:44928,cC:2067688,kV:50886,pvK:48,alK:192600,alC:763182,mC:32100,hC:317250,gdpR:1.24,conv:7.81,mort:3.13},
  'CH071':{cab:198,cabI:202,mu:4,fc:'2025-01-05',fci:'2025-05-20',kR:49290,cC:2218050,kV:55836,pvK:50,alK:216000,alC:842400,mC:29600,hC:334125,gdpR:1.38,conv:7.20,mort:1.98}
};
function updCierre(){
  var k=document.getElementById('cLote').value;
  var d=cData[k]; if(!d) return;
  var dc=Math.round((new Date(d.fci)-new Date(d.fc))/86400000);
  var daB=dc*d.cabI, daN=daB-d.mu*Math.round(dc*0.4);
  var ing=d.kV*d.pvK, ct=d.cC+d.alC+d.mC+d.hC;
  var util=ing-ct, mg=((util/ing)*100).toFixed(1), cpk=(ct/d.kV).toFixed(2);
  document.getElementById('cBlocks').innerHTML=
    '<div class="cblk"><div class="cbt">Compra y recibo</div>'+
      '<div class="cbr"><span class="ck">Cab. compradas</span><span class="cv">'+d.cabI+'</span></div>'+
      '<div class="cbr"><span class="ck">Cab. recibidas</span><span class="cv">'+d.cab+'</span></div>'+
      '<div class="cbr"><span class="ck">Kilos recepción</span><span class="cv">'+d.kR.toLocaleString()+'</span></div>'+
      '<div class="cbr"><span class="ck">Costo compra</span><span class="cv">$'+d.cC.toLocaleString()+'</span></div>'+
      '<div class="cbr"><span class="ck">Muertos</span><span class="cv" style="color:var(--rd)">'+d.mu+' ('+d.mort+'%)</span></div>'+
    '</div>'+
    '<div class="cblk"><div class="cbt">Días animal</div>'+
      '<div class="cbr"><span class="ck">Días calendario</span><span class="cv">'+dc+'</span></div>'+
      '<div class="cbr"><span class="ck">D-A base</span><span class="cv">'+daB.toLocaleString()+'</span></div>'+
      '<div class="cbr"><span class="ck">Desc. x muertes</span><span class="cv" style="color:var(--rd)">−'+(daB-daN).toLocaleString()+'</span></div>'+
      '<div class="cbr"><span class="ck">D-A netos</span><span class="cv" style="color:var(--gn)">'+daN.toLocaleString()+'</span></div>'+
    '</div>'+
    '<div class="cblk"><div class="cbt">Venta</div>'+
      '<div class="cbr"><span class="ck">Kilos vendidos</span><span class="cv">'+d.kV.toLocaleString()+'</span></div>'+
      '<div class="cbr"><span class="ck">Precio/kg</span><span class="cv">$'+d.pvK+'</span></div>'+
      '<div class="cbr"><span class="ck">Ingreso total</span><span class="cv" style="color:var(--gn)">$'+ing.toLocaleString()+'</span></div>'+
    '</div>';
  document.getElementById('cTbl').innerHTML=[
    ['Compra del ganado',d.cabI+' cab','$'+(d.cC/d.cabI).toFixed(0)+'/cab','$'+d.cC.toLocaleString()],
    ['Alimentación',d.alK.toLocaleString()+' kg','$'+(d.alC/d.alK).toFixed(2)+'/kg','$'+d.alC.toLocaleString()],
    ['Medicación',d.cab+' cab','$'+(d.mC/d.cab).toFixed(0)+'/cab','$'+d.mC.toLocaleString()],
    ['Costo hotel',daN.toLocaleString()+' d-a','$12.50/d-a','$'+d.hC.toLocaleString()],
    ['<strong>COSTO TOTAL</strong>','','','<strong>$'+ct.toLocaleString()+'</strong>'],
    ['<strong style="color:var(--gn)">UTILIDAD</strong>','','','<strong style="color:var(--gn)">$'+util.toLocaleString()+'</strong>'],
  ].map(function(r){return '<tr>'+r.map(function(c){return '<td class="mn">'+c+'</td>';}).join('')+'</tr>';}).join('');
  document.getElementById('cInd').innerHTML=[
    {l:'GDP Real',v:d.gdpR+' kg/d',cl:'var(--bl)'},
    {l:'Conversión',v:d.conv.toFixed(2),cl:'var(--am)'},
    {l:'Costo/kg prod.',v:'$'+cpk,cl:'var(--txb)'},
    {l:'Margen %',v:mg+'%',cl:parseFloat(mg)>=18?'var(--gn)':'var(--am)'},
  ].map(function(i){return '<div style="text-align:center"><div style="font-size:22px;font-family:var(--mono);font-weight:700;color:'+i.cl+'">'+i.v+'</div><div style="font-size:10.5px;color:var(--txd);margin-top:4px;text-transform:uppercase;letter-spacing:.6px">'+i.l+'</div></div>';}).join('');
}
updCierre();

// ─── TAB SWITCH
// ─── IA DASHBOARD ────────────────────────────────────────────────────────────
// Contexto comprimido: ~250 tokens de entrada por llamada
// Respuesta limitada a 180 tokens → costo por consulta ~0.001 USD con Claude Haiku
function buildContext() {
  return [
    "Rancho Chamizal · Sem 30 · 21 Jul 2025",
    "Inventario: 2847 cab (2527 corrales + 320 potreros)",
    "Venta sem30: 342 cab (CH087 M 214 + CH091H H 128) · 94,640 kg · Rastro Norteño",
    "Lotes activos: 22 · GDP prom real: 1.28 kg/d · Conversión: 7.42 · Mort: 0.82%",
    "Semanas sin salida: S34, S36, S38 · Corrales libres: C07 C12 C14 C16",
    "Reimplantes pendientes sem30: CH083 C03, CH092 C05, CH090H C06",
    "Zilpaterol activos: CH087 (35d ✓) CH091H (32d) · Entra: CH088 (23jul)",
    "Transiciones sem30: CH088 F3→F3+Zilp, CH090H FT→F3",
  ].join(". ");
}

var preguntas = {
  resumen: "En máximo 4 viñetas cortas: qué pasa esta semana en el rancho (ventas, reimplantes, transiciones, Zilpaterol). Sin introducción.",
  riesgos: "Lista los 3 principales riesgos operativos de las próximas 4 semanas basándote en los datos. Máximo 3 líneas por riesgo.",
  compra: "Con base en las semanas sin salida (S34, S36, S38) y los corrales libres (C07,C12,C14,C16), ¿cuándo conviene comprar ganado y cuántas cabezas aproximadamente? Respuesta directa, máximo 80 palabras.",
  rentabilidad: "Con GDP real 1.28 vs proy 1.35 y conversión 7.42: ¿qué impacto tiene eso en la rentabilidad de los lotes activos? Respuesta concreta, máximo 80 palabras.",
};

function showLoading() {
  document.getElementById('ai-response-area').innerHTML =
    '<div style="display:flex;align-items:center;gap:10px;padding:16px 0;color:var(--txd);font-size:12.5px">' +
    '<div style="width:16px;height:16px;border:2px solid var(--pud);border-top-color:var(--pu);border-radius:50%;animation:spin .8s linear infinite"></div>' +
    'Analizando datos del rancho...</div>';
  if (!document.getElementById('ai-spin-style')) {
    var s = document.createElement('style');
    s.id = 'ai-spin-style';
    s.textContent = '@keyframes spin{to{transform:rotate(360deg)}}';
    document.head.appendChild(s);
  }
}

function renderResponse(text, tokens) {
  var html = '<div style="font-size:13px;line-height:1.7;color:var(--tx)">' +
    text.replace(/\n/g, '<br>').replace(/^[•·-] /gm, '<span style="color:var(--pu)">▸</span> ') +
    '</div>';
  document.getElementById('ai-response-area').innerHTML = html;
  var info = document.getElementById('ai-token-info');
  info.style.display = 'block';
  info.textContent = '~' + tokens + ' tokens · costo estimado: $0.001 USD · modelo: claude-haiku-4-5';
}

function renderError(msg) {
  document.getElementById('ai-response-area').innerHTML =
    '<div style="color:var(--rd);font-size:12.5px;padding:12px 0">⚠️ ' + msg + '</div>';
}

async function callAI(pregunta) {
  showLoading();
  var ctx = buildContext();
  var userMsg = "DATOS DEL RANCHO: " + ctx + "\n\nPREGUNTA: " + pregunta;
  try {
    var resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 220,
        system: "Eres el asistente de gestión ganadera del Rancho Chamizal. Responde en español, de forma directa y concisa, solo con la información solicitada. Sin saludos ni despedidas.",
        messages: [{ role: "user", content: userMsg }]
      })
    });
    var data = await resp.json();
    if (data.content && data.content[0]) {
      var totalTk = (data.usage ? data.usage.input_tokens + data.usage.output_tokens : 320);
      renderResponse(data.content[0].text, totalTk);
    } else {
      renderError("Sin respuesta del modelo. " + (data.error ? data.error.message : ''));
    }
  } catch(e) {
    renderError("Error de conexión: " + e.message);
  }
}

function askAI(tipo) {
  document.getElementById('ai-input-area').style.display = 'none';
  if (tipo === 'libre') {
    document.getElementById('ai-input-area').style.display = 'flex';
    document.getElementById('ai-custom-q').focus();
    document.getElementById('ai-response-area').innerHTML =
      '<div style="color:var(--txd);font-size:12.5px;padding:8px 0">Escribe tu pregunta y presiona Enviar.</div>';
    return;
  }
  callAI(preguntas[tipo]);
}

function askAICustom() {
  var q = document.getElementById('ai-custom-q').value.trim();
  if (!q) return;
  document.getElementById('ai-input-area').style.display = 'none';
  callAI(q);
}

document.getElementById('ai-custom-q') && document.getElementById('ai-custom-q').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') askAICustom();
});

function swTab(el){
  el.closest('.tabs').querySelectorAll('.tab').forEach(function(t){t.classList.remove('active');});
  el.classList.add('active');
}
