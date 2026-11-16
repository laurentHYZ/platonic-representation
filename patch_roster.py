import io

# ---------------------------------------------------------------- index.html
p = r"C:\Users\1\Documents\deepseek-harness\default-workspace\publish\index.html"
s = io.open(p, encoding="utf-8").read()

anchor = '  <div id="doc"></div>'
assert anchor in s

block = '''  <details class="cls" id="cls">
    <summary>课堂：贴一份学生名单 <span class="pill" id="clsCount">0 人</span></summary>
    <p class="cls-note">一行一个名字，也可以用逗号、顿号、空格分隔。名单只存在这台电脑的浏览器里，测验页会读同一份。</p>
    <textarea id="clsInput" rows="6" spellcheck="false" placeholder="张三
李四
王五"></textarea>
    <div class="cls-row">
      <button id="clsSave" class="primary">保存名单</button>
      <button id="clsClear" class="ghost">清空</button>
      <a class="cls-go" href="quiz.html">去抽人 →</a>
    </div>
  </details>

'''
s = s.replace(anchor, block + anchor, 1)

css = '''
.cls{margin:0 0 1.6em;border:1px solid var(--bd);border-radius:12px;background:var(--panel);padding:0 16px}
.cls summary{cursor:pointer;padding:12px 0;font-size:14px;color:var(--fg);list-style:none;display:flex;align-items:center;gap:10px}
.cls summary::-webkit-details-marker{display:none}
.cls summary::before{content:"▸";color:var(--ac);font-size:12px;transition:transform .15s}
.cls[open] summary::before{transform:rotate(90deg)}
.cls .pill{font-size:11.5px;color:var(--bg);background:var(--ac);border-radius:999px;padding:1px 9px}
.cls-note{font-size:12.5px;color:var(--mut);margin:.2em 0 .7em;line-height:1.8}
#clsInput{width:100%;box-sizing:border-box;font:14px/1.7 ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--fg);background:var(--bg);border:1px solid var(--bd);border-radius:9px;padding:10px 12px;resize:vertical}
#clsInput:focus{outline:2px solid color-mix(in srgb,var(--ac) 45%,transparent);outline-offset:1px;border-color:var(--ac)}
.cls-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 0 14px}
.cls-go{margin-left:auto;font-size:13px;color:var(--ac);text-decoration:none;border-bottom:1px solid currentColor}
'''
s = s.replace("</style>", css + "</style>", 1)

script = '''
<script>
(function () {
  var KEY = 'prh.roster';
  var $ = function (id) { return document.getElementById(id); };
  function parse(raw) {
    var parts = raw.split(/[\\n\\r,，、;；\\t]+/);
    var out = [], seen = {};
    parts.forEach(function (x) {
      var n = x.trim().replace(/\\s+/g, ' ');
      if (n && !seen[n]) { seen[n] = 1; out.push(n); }
    });
    return out;
  }
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || '[]') || []; } catch (e) { return []; } }
  function save(list) {
    try {
      localStorage.setItem(KEY, JSON.stringify(list));
      localStorage.removeItem('prh.pickcount');
    } catch (e) {}
  }
  function render() {
    var list = load();
    $('clsCount').textContent = list.length + ' 人';
    if (list.length) {
      $('clsInput').value = list.join('\\n');
      $('cls').open = true;
    }
  }
  $('clsSave').addEventListener('click', function () {
    var list = parse($('clsInput').value);
    save(list);
    $('clsInput').value = list.join('\\n');
    $('clsCount').textContent = list.length + ' 人';
    $('clsCount').animate
      ? $('clsCount').animate([{ transform: 'scale(1.25)' }, { transform: 'scale(1)' }], { duration: 220 })
      : null;
    document.getElementById('clsSave').textContent = list.length ? '已保存 ' + list.length + ' 人' : '名单是空的';
    setTimeout(function () { document.getElementById('clsSave').textContent = '保存名单'; }, 1400);
  });
  $('clsClear').addEventListener('click', function () {
    $('clsInput').value = '';
    save([]);
    $('clsCount').textContent = '0 人';
    $('clsInput').focus();
  });
  render();
})();
</script>
'''
s = s.replace("</body>", script + "</body>", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("index patched")
