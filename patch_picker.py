import io

p = r"C:\Users\1\Documents\deepseek-harness\default-workspace\publish\quiz.html"
s = io.open(p, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. CSS
css = '''
/* ---- 抽人 ---- */
.picker{display:flex;align-items:center;gap:10px;margin:0 0 14px;background:var(--panel);
  border:1px solid var(--bd);border-radius:12px;padding:8px 10px}
.reel{flex:1;min-width:0;height:54px;overflow:hidden;position:relative;border-radius:9px;
  background:var(--bg);border:1px solid var(--bd)}
.strip{position:absolute;left:0;right:0;top:0;will-change:transform}
.strip>div{height:54px;line-height:54px;text-align:center;font-size:22px;letter-spacing:.04em;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 14px;color:var(--fg)}
.strip>div.win{color:var(--ac);font-weight:700}
.reel.spin .strip{filter:blur(.5px)}
.reel.won{border-color:var(--ac);box-shadow:0 0 0 3px color-mix(in srgb,var(--ac) 18%,transparent)}
#pickBtn{white-space:nowrap}
.pickNote{font-size:12px;color:var(--mut);text-align:center;margin:-6px 0 14px}
#rWho{list-style:none;padding:0;margin:16px 0 0}
#rWho li{display:flex;justify-content:space-between;gap:12px;border-bottom:1px dashed var(--bd);padding:6px 2px;font-size:13.5px}
#rWho li b{font-weight:600}
'''
s = s.replace("</style>", css + "</style>", 1)

# ---------------------------------------------------------------- 2. HTML
html = '''    <div class="picker">
      <div class="reel" id="reel"><div class="strip" id="strip"><div>点「抽人」开始</div></div></div>
      <button id="pickBtn">🎲 抽人</button>
      <label class="chk" style="font-size:12px;color:var(--mut);display:inline-flex;align-items:center;gap:5px;white-space:nowrap">
        <input type="checkbox" id="autoPick"> 每题自动抽
      </label>
    </div>
    <div class="pickNote" id="pickNote"></div>

'''
s = s.replace('    <div class="prompt" id="qPrompt"></div>', html + '    <div class="prompt" id="qPrompt"></div>', 1)

s = s.replace('    <ul class="miss" id="rWrong"></ul>', '    <ul class="miss" id="rWrong"></ul>\n    <ul id="rWho"></ul>', 1)

# ---------------------------------------------------------------- 3. JS：抽人逻辑
js = r'''
/* ---------- 抽人（点名） ---------- */
const ROSTER_KEY = 'prh.roster';
const PICK_KEY = 'prh.pickcount';
let currentStudent = null;
let spinning = false;

function roster() {
  try { return JSON.parse(localStorage.getItem(ROSTER_KEY) || '[]') || []; } catch (e) { return []; }
}
function pickCounts() {
  try { return JSON.parse(localStorage.getItem(PICK_KEY) || '{}') || {}; } catch (e) { return {}; }
}
function saveCounts(c) { try { localStorage.setItem(PICK_KEY, JSON.stringify(c)); } catch (e) {} }
function autoPickOn() { return localStorage.getItem('prh.autopick') === '1'; }

/* 公平抽取：只从“被抽次数最少”的人里选，全班轮完一遍才会重复 */
function nextStudent() {
  const names = roster();
  if (!names.length) return null;
  const c = pickCounts();
  const min = Math.min.apply(null, names.map(function (n) { return c[n] || 0; }));
  const pool = names.filter(function (n) { return (c[n] || 0) === min; });
  const pick = pool[Math.floor(Math.random() * pool.length)];
  c[pick] = (c[pick] || 0) + 1;
  saveCounts(c);
  return pick;
}

function setReel(items, offset) {
  const strip = $('strip');
  strip.innerHTML = '';
  items.forEach(function (n, i) {
    const d = document.createElement('div');
    d.textContent = n;
    if (offset === i) d.className = 'win';
    strip.appendChild(d);
  });
  strip.style.transform = 'translateY(' + (-(offset || 0) * 54) + 'px)';
}

/* 老虎机式滚动：先快后慢，稳稳停在目标名字上 */
function spinPick() {
  if (spinning) return Promise.resolve(currentStudent);
  const target = nextStudent();
  if (!target) {
    toast('先去首页贴学生名单');  // 没有名单时的提示
    $('pickNote').textContent = '还没有名单：回到首页「课堂：贴一份学生名单」。';
    return Promise.resolve(null);
  }
  const names = roster();
  const items = [];
  const N = 26;
  for (let i = 0; i < N; i++) items.push(names[Math.floor(Math.random() * names.length)]);
  items.push(target);

  spinning = true;
  $('reel').classList.add('spin');
  $('reel').classList.remove('won');
  $('pickBtn').disabled = true;
  setReel(items, -1);

  const total = (items.length - 1) * 54;
  const t0 = performance.now();
  const dur = 1500;
  const ease = function (t) { return 1 - Math.pow(1 - t, 4); };
  const strip = $('strip');
  let done = false;

  function finish() {
    if (done) return;
    done = true;
    clearInterval(timer);
    strip.style.transform = 'translateY(' + (-total) + 'px)';
    const last = strip.lastElementChild;
    if (last) last.className = 'win';
    $('reel').classList.remove('spin');
    $('reel').classList.add('won');
    $('pickBtn').disabled = false;
    spinning = false;
    currentStudent = target;
    $('pickNote').textContent = '请 ' + target + ' 回答';
    if (navigator.vibrate) try { navigator.vibrate(30); } catch (e) {}
  }

  const timer = setInterval(function () {
    const p = Math.min(1, (performance.now() - t0) / dur);
    strip.style.transform = 'translateY(' + (-total * ease(p)) + 'px)';
    if (p >= 1) finish();
  }, 16);
  setTimeout(finish, dur + 400);   // 定时器被节流时兜底

  return new Promise(function (resolve) {
    const wait = setInterval(function () {
      if (done) { clearInterval(wait); resolve(target); }
    }, 40);
  });
}
'''

anchor = "/* ---------- 事件 ---------- */"
assert anchor in s
s = s.replace(anchor, js + "\n" + anchor, 1)

# ---------------------------------------------------------------- 4. 每题自动抽 + 记录学生成绩
old = """  if (item.type === 'listen2zh') speak(item.term.zh);
  else if (item.type === 'zh2py' && autoSpeakOn()) speak(item.term.zh);"""
new = """  if (item.type === 'listen2zh') speak(item.term.zh);
  else if (item.type === 'zh2py' && autoSpeakOn()) speak(item.term.zh);

  currentStudent = null;
  $('pickNote').textContent = '';
  if (autoPickOn()) setTimeout(function () { if (!currentStudent) spinPick(); }, 280);"""
assert old in s
s = s.replace(old, new, 1)

old = """  const ok = chosen === item.correct;
  q.answered = true;
  if (ok) { q.score++; bump(item.term.zh, true); }"""
new = """  const ok = chosen === item.correct;
  q.answered = true;
  if (ok) { q.score++; bump(item.term.zh, true); }
  if (currentStudent) {
    if (!q.scores) q.scores = {};
    const sc = q.scores[currentStudent] || (q.scores[currentStudent] = { r: 0, w: 0 });
    if (ok) sc.r++; else sc.w++;
  }"""
assert old in s
s = s.replace(old, new, 1)

old = """  $('onlyWrong').disabled = q.wrong.length === 0;"""
new = """  $('onlyWrong').disabled = q.wrong.length === 0;

  const who = $('rWho');
  who.innerHTML = '';
  if (q.scores) {
    Object.keys(q.scores).forEach(function (name) {
      const sc = q.scores[name];
      const li = document.createElement('li');
      const l = document.createElement('b'); l.textContent = name;
      const r = document.createElement('span'); r.textContent = sc.r + ' 对 / ' + sc.w + ' 错';
      li.appendChild(l); li.appendChild(r);
      who.appendChild(li);
    });
  }"""
assert old in s
s = s.replace(old, new, 1)

# ---------------------------------------------------------------- 5. 事件与暴露
old = """$('qNext').addEventListener('click', nextQuestion);"""
new = """$('pickBtn').addEventListener('click', function () { spinPick(); });
$('autoPick').addEventListener('change', function () {
  try { localStorage.setItem('prh.autopick', $('autoPick').checked ? '1' : '0'); } catch (e) {}
});
$('autoPick').checked = autoPickOn();
$('qNext').addEventListener('click', nextQuestion);"""
assert old in s
s = s.replace(old, new, 1)

old = """    if (/^[1-4]$/.test(e.key)) { e.preventDefault(); answer(Number(e.key) - 1); }
    else if (e.key === 'Enter') { e.preventDefault(); if (q && q.answered) nextQuestion(); }"""
new = """    if (/^[1-4]$/.test(e.key)) { e.preventDefault(); answer(Number(e.key) - 1); }
    else if (e.key === 'Enter') { e.preventDefault(); if (q && q.answered) nextQuestion(); }
    else if (e.key === 'p' || e.key === 'P') { e.preventDefault(); spinPick(); }"""
assert old in s
s = s.replace(old, new, 1)

old = """  card: function () { return { i: cardIdx, flipped: flipped, term: order[cardIdx] }; }
};"""
new = """  card: function () { return { i: cardIdx, flipped: flipped, term: order[cardIdx] }; },
  roster: roster,
  setRoster: function (list) { try { localStorage.setItem(ROSTER_KEY, JSON.stringify(list)); localStorage.removeItem(PICK_KEY); } catch (e) {} },
  nextStudent: nextStudent,
  spin: spinPick,
  student: function () { return currentStudent; }
};"""
assert old in s
s = s.replace(old, new, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("quiz patched")
