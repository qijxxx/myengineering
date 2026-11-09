import webview
import sys
import os
import base64
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


def resource_path(relative_path):
    """兼容直接运行与 PyInstaller --onefile 打包后的资源路径。"""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def inline_offline_libraries(html):
    """把本地 JS 依赖直接嵌入 HTML，运行时不再访问 CDN。"""
    libraries = [
        (
            '<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js">\n  </script>',
            "vendor/xlsx.full.min.js",
        ),
        (
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js">\n  </script>',
            "vendor/jspdf.umd.min.js",
        ),
        (
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js">\n  </script>',
            "vendor/html2canvas.min.js",
        ),
    ]

    for tag, relative_file in libraries:
        file_path = resource_path(relative_file)
        if not file_path.exists():
            raise FileNotFoundError(
                f"缺少离线依赖文件：{relative_file}\n"
                "请确认 vendor 文件夹已准备好，并在打包时使用 --add-data。"
            )
        js_code = file_path.read_text(encoding="utf-8")
        html = html.replace(tag, f"<script>\n{js_code}\n</script>")

    return html


class FileApi:
    """用 tkinter 的 Windows 文件对话框处理导入/保存，绕开 pywebview 文件弹窗兼容问题。"""

    @staticmethod
    def _make_hidden_root():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.update()
        return root

    def choose_student_file(self):
        root = self._make_hidden_root()
        try:
            path = filedialog.askopenfilename(
                parent=root,
                title="选择学生数据文件",
                filetypes=[
                    ("Excel / CSV 文件", "*.xlsx *.xls *.csv"),
                    ("Excel 工作簿", "*.xlsx *.xls"),
                    ("CSV 文件", "*.csv"),
                    ("所有文件", "*.*"),
                ],
            )
        finally:
            root.destroy()

        if not path:
            return None

        file_path = Path(path)
        return {
            "name": file_path.name,
            "data": base64.b64encode(file_path.read_bytes()).decode("ascii"),
        }

    def save_base64_file(self, data, default_name, file_type):
        suffix = Path(default_name).suffix.lower()

        if suffix == ".xlsx":
            filetypes = [("Excel 工作簿", "*.xlsx"), ("所有文件", "*.*")]
            default_ext = ".xlsx"
        elif suffix == ".pdf":
            filetypes = [("PDF 文件", "*.pdf"), ("所有文件", "*.*")]
            default_ext = ".pdf"
        else:
            filetypes = [("所有文件", "*.*")]
            default_ext = suffix or ""

        root = self._make_hidden_root()
        try:
            path = filedialog.asksaveasfilename(
                parent=root,
                title="保存文件",
                initialfile=default_name,
                defaultextension=default_ext,
                filetypes=filetypes,
            )
        finally:
            root.destroy()

        if not path:
            return False

        Path(path).write_bytes(base64.b64decode(data))
        return True


def main():
    # 将您的完整HTML代码粘贴在下方三引号之间
    html = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
  <title>当涂县乌溪初级中学阳光分班</title>
  <script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js">
  </script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js">
  </script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js">
  </script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Segoe UI', Roboto, system-ui, sans-serif;
    }
    body {
      background: #eef2f6;
      padding: 20px;
      display: flex;
      justify-content: center;
    }
    .container {
      width: 100%;
      max-width: 1500px;
      background: #fff;
      border-radius: 24px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
      padding: 25px 30px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    h1 {
      font-size: 2.4rem;
      color: #0a3144;
      text-align: center;
      font-weight: 650;
      border-bottom: 4px solid #1e7e83;
      padding-bottom: 14px;
    }
    .panel {
      background: #f5f9fc;
      border-radius: 16px;
      padding: 15px 20px;
      border: 1px solid #d0dde8;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 18px;
    }
    .group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    label {
      font-weight: 600;
      color: #1e3b4f;
    }
    input,
    select,
    button {
      padding: 9px 16px;
      border-radius: 10px;
      border: 1px solid #cbd5e1;
      font-size: 0.95rem;
      outline: none;
    }
    button {
      background: #1e7e83;
      color: #fff;
      border: none;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
    }
    button:hover {
      background: #135c60;
    }
    button.secondary {
      background: #4b5563;
    }
    button.danger {
      background: #b91c1c;
    }
    .action-hint {
      font-size: 1.5rem;
      font-weight: 700;
      color: #b45309;
      text-align: center;
      min-height: 52px;
      padding: 12px;
      background: #fef3c7;
      border-radius: 12px;
      margin: 5px 0;
      border: 2px dashed #f59e0b;
    }
    .log-box {
      display: none;
    }
    .data-table {
      max-height: 300px;
      overflow: auto;
      border: 1px solid #ccc;
      border-radius: 12px;
      margin: 5px 0;
    }
    table.data-preview {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8rem;
    }
    table.data-preview th,
    table.data-preview td {
      border: 1px solid #b9c7d6;
      padding: 4px 3px;
      text-align: center;
    }
    table.data-preview th {
      background: #e4edf5;
      font-weight: 700;
      position: sticky;
      top: 0;
    }
    .classrooms {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-top: 8px;
      align-items: center;
      justify-content: center;
      min-height: 200px;
    }
    .class-card {
      background: #fff;
      border-radius: 16px;
      border: 2px solid #cfdde9;
      padding: 12px;
      box-shadow: 0 6px 14px rgba(0, 0, 0, 0.04);
      max-height: none;
      overflow-y: auto;
      transition: all 0.5s ease;
      scroll-margin-top: 20px;
      width: 100%;
      max-width: 100%;
    }
    .class-card.active-class {
      border-color: #f59e0b !important;
      box-shadow: 0 0 28px rgba(245, 158, 11, 0.55) !important;
      transform: scale(1.03);
      z-index: 10;
      background: #fffef5;
    }
    .class-card.visible-class {
      border-color: #1e7e83 !important;
      box-shadow: 0 0 18px rgba(30, 126, 131, 0.35) !important;
      transform: scale(1.02);
      z-index: 5;
      background: #f8fffe;
    }
    .class-card h3 {
      color: #0b3b5c;
      border-bottom: 2px solid #1e7e83;
      margin-bottom: 8px;
      font-size: 1rem;
    }
    .student-list {
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      padding: 4px 0;
    }
    .student-tag {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 7px 12px;
      border-radius: 22px;
      font-size: 0.85rem;
      font-weight: 500;
      transition: all 0.4s ease;
      white-space: nowrap;
      border: 2px solid transparent;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }
    .student-tag.male {
      background: #dbeafe;
      border-color: #3b82f6;
      color: #1e3a5f;
    }
    .student-tag.male .gender-icon {
      color: #2563eb;
      font-size: 1.1rem;
    }
    .student-tag.female {
      background: #fce7f3;
      border-color: #ec4899;
      color: #5c1a3a;
    }
    .student-tag.female .gender-icon {
      color: #db2777;
      font-size: 1.1rem;
    }
    .student-tag.highlight {
      background: #fde047 !important;
      border-color: #f59e0b !important;
      font-weight: 700;
      font-size: 1rem;
      transform: scale(1.18);
      box-shadow: 0 0 20px rgba(245, 158, 11, 0.7);
      animation: pulse 0.45s infinite;
      z-index: 20;
    }
    @keyframes pulse {
      0% {
        background: #fde047;
        transform: scale(1.18);
      }
      50% {
        background: #fbbf24;
        transform: scale(1.25);
      }
      100% {
        background: #fde047;
        transform: scale(1.18);
      }
    }
    .multi-container {
      display: flex;
      gap: 20px;
      margin: 8px 0;
    }
    .multi-box {
      flex: 1;
      background: #f9fdf9;
      border-radius: 12px;
      padding: 10px;
      border: 1px solid #b9d6bc;
      max-height: 250px;
      overflow: auto;
      font-size: 0.85rem;
    }
    .multi-box h3 {
      margin-bottom: 6px;
      color: #1e4a2e;
    }
    .multi-item {
      margin: 4px 0;
    }
    .stats-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin-top: 10px;
    }
    .stats-table th,
    .stats-table td {
      border: 1px solid #b9c7d6;
      padding: 7px;
      text-align: center;
    }
    .stats-table th {
      background: #e4edf5;
    }
    .hidden {
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>当涂县乌溪初级中学阳光分班</h1>

    <div class="panel">
      <div class="group"><label>班级数量</label><input type="number" id="classCount" min="2" max="25" value="4"
          style="width:80px"></div>
      <button id="downloadTemplateBtn">📥 下载模板</button>
      <button id="importBtn">📂 导入学生数据</button>
      <input type="file" id="fileInput" accept=".xlsx,.xls,.csv" hidden>
      <button id="clearAllBtn" class="danger">🗑️ 清除所有数据</button>
    </div>

    <div style="display:flex; gap:20px; align-items:center;">
      <span>👨 男生:<span id="maleCount">0</span> 👩 女生:<span id="femaleCount">0</span> 👥 总计:<span
        id="totalCount">0</span></span>
    </div>

    <div class="data-table" id="dataPreviewContainer">
      <table class="data-preview" id="dataPreviewTable">
        <thead></thead><tbody></tbody>
      </table>
    </div>

    <div class="panel" style="justify-content:space-between;">
      <div><strong>📋 多胞胎/重名近似操作</strong></div>
      <button id="markTwinsBtn">👯 设为多胞胎</button>
      <button id="markSimilarBtn">📛 设为重名近似</button>
      <button id="cancelGroupBtn" class="secondary">❌ 取消选中组</button>
    </div>

    <div class="multi-container" id="multiInfoArea">
      <div class="multi-box" id="twinsBox">
        <h3>多胞胎组</h3>
        <div id="twinsContent"></div>
      </div>
      <div class="multi-box" id="similarBox">
        <h3>重名近似组</h3>
        <div id="similarContent"></div>
      </div>
    </div>

    <div id="actionHint" class="action-hint">🎯 准备就绪，请导入数据并开始分班</div>
    <button id="startBtn" style="font-size:1.1rem; padding:12px 28px;">🎲 开始阳光分班</button>
    <div class="log-box" id="logPanel">[操作日志] 就绪。</div>

    <div class="classrooms" id="classroomsContainer"></div>

    <div style="display:flex; gap:12px; flex-wrap:wrap;">
      <button id="toggleStatsBtn">📊 显示/隐藏统计表</button>
      <button id="exportExcelBtn">📗 导出分班Excel</button>
      <button id="exportPdfBtn">📄 导出分班PDF</button>
      <button id="exportLogBtn" class="secondary">📋 导出操作日志(PDF)</button>
    </div>

    <table id="statsTable" class="stats-table hidden">
      <thead></thead><tbody></tbody>
    </table>
  </div>

  <script>
    (() => {
      let students = [];
      let twinsGroups = [];
      let similarGroups = [];
      let classrooms = [];
      let logEntries = [];
      let isAllocating = false;

      const actionHint = document.getElementById('actionHint');

      function log(msg) {
        const t = new Date().toLocaleTimeString();
        logEntries.push(`[${t}] ${msg}`);
        const panel = document.getElementById('logPanel');
        if (panel) {
          panel.textContent = logEntries.join('\n');
          panel.scrollTop = panel.scrollHeight;
        }
      }

      function parseNum(v) { if (v === null || v === undefined || v === '') return 0; let n = Number(String(v).trim());
        return isNaN(n) ? 0 : n; }

      function parseGender(raw) { if (!raw) return '男'; let s = String(raw).trim(); return (s === '女' || s === '0' || s
          .toLowerCase() === 'f') ? '女' : '男'; }

      function calcTotal(s) { return parseNum(s.语文) + parseNum(s.数学) + parseNum(s.英语); }

      function getClassCount() { let v = parseInt(document.getElementById('classCount').value) || 4; return Math.min(25,
          Math.max(2, v)); }

      function renderDataPreview() {
        const thead = document.querySelector('#dataPreviewTable thead');
        const tbody = document.querySelector('#dataPreviewTable tbody');
        thead.innerHTML = '';
        tbody.innerHTML = '';
        if (!students.length) return;
        thead.innerHTML =
          '<tr><th><input type="checkbox" id="selectAll"></th><th>报名号</th><th>姓名</th><th>性别</th><th>身份证</th><th>生源</th><th>语文</th><th>数学</th><th>英语</th><th>总分</th><th>数学附加分</th><th>多胞胎</th><th>重名近似</th></tr>';
        students.forEach((s, idx) => {
          const row = tbody.insertRow();
          row.innerHTML = `<td><input type="checkbox" class="student-check" data-index="${idx}"></td>
            <td>${s.报名号||''}</td><td>${s.姓名||''}</td><td>${s.性别}</td><td>${s.身份证||''}</td><td>${s.生源||''}</td>
            <td>${s.语文}</td><td>${s.数学}</td><td>${s.英语}</td><td>${s.总分}</td><td>${s.数学附加分}</td>
            <td>${s.多胞胎原始||''}</td><td>${s.重名近似原始||''}</td>`;
        });
        document.getElementById('selectAll').addEventListener('change', e => {
          document.querySelectorAll('.student-check').forEach(cb => cb.checked = e.target.checked);
        });
      }

      function getCheckedIndices() {
        return Array.from(document.querySelectorAll('.student-check:checked')).map(cb => parseInt(cb.dataset.index));
      }

      function updateCounts() {
        const m = students.filter(s => s.性别 === '男').length,
          f = students.filter(s => s.性别 === '女').length;
        document.getElementById('maleCount').textContent = m;
        document.getElementById('femaleCount').textContent = f;
        document.getElementById('totalCount').textContent = students.length;
      }

      function showMultiInfo() {
        const twinsContent = document.getElementById('twinsContent');
        const similarContent = document.getElementById('similarContent');
        twinsContent.innerHTML = '';
        similarContent.innerHTML = '';
        if (twinsGroups.length === 0) twinsContent.innerHTML = '<div class="multi-item">无</div>';
        else twinsGroups.forEach((g, i) => {
          const div = document.createElement('div');
          div.className = 'multi-item';
          div.innerHTML =
            `<strong>组${i+1}:</strong> ${g.map(idx => `${students[idx].报名号||idx} ${students[idx].姓名}(${students[idx].性别})`).join('， ')}`;
          twinsContent.appendChild(div);
        });
        if (similarGroups.length === 0) similarContent.innerHTML = '<div class="multi-item">无</div>';
        else similarGroups.forEach((g, i) => {
          const div = document.createElement('div');
          div.className = 'multi-item';
          div.innerHTML =
            `<strong>组${i+1}:</strong> ${g.map(idx => `${students[idx].报名号||idx} ${students[idx].姓名}(${students[idx].性别})`).join('， ')}`;
          similarContent.appendChild(div);
        });
      }

      function renderClassrooms(highlightUid = null, targetClassIndex = null, visibleClassIndices = null) {
        const container = document.getElementById('classroomsContainer');
        container.innerHTML = '';
        const cnt = getClassCount();
        if (!classrooms.length || classrooms.length !== cnt) {
          classrooms = Array.from({ length: cnt }, () => []);
        }
        // 确定需要显示的班级索引集合
        let showSet = null;
        if (isAllocating && visibleClassIndices && visibleClassIndices.length > 0) {
          showSet = new Set(visibleClassIndices);
        }
        classrooms.forEach((cls, idx) => {
          // 如果设置了可见班级集合，且当前班级不在集合中，则跳过渲染
          if (showSet && !showSet.has(idx)) return;
          const card = document.createElement('div');
          card.className = 'class-card';
          if (isAllocating && targetClassIndex !== null && idx === targetClassIndex && highlightUid) {
            card.classList.add('active-class');
          } else if (isAllocating && showSet && showSet.has(idx) && !(targetClassIndex !== null && idx ===
              targetClassIndex)) {
            card.classList.add('visible-class');
          }
          card.setAttribute('data-class-index', idx);
          card.innerHTML = `<h3>${idx+1}班 (${cls.length}人)</h3><ul class="student-list"></ul>`;
          const ul = card.querySelector('ul');
          cls.forEach(s => {
            const li = document.createElement('li');
            li.style.listStyle = 'none';
            const isMale = s.性别 === '男';
            const icon = isMale ? '👦' : '👩';
            const genderClass = isMale ? 'male' : 'female';
            li.innerHTML =
              `<span class="student-tag ${genderClass}"><span class="gender-icon">${icon}</span> ${s.姓名} ${s.总分}</span>`;
            if (highlightUid && s._uid === highlightUid) {
              li.querySelector('.student-tag').classList.add('highlight');
            }
            ul.appendChild(li);
          });
          container.appendChild(card);
        });
        if (isAllocating && targetClassIndex !== null && highlightUid && showSet && showSet.has(targetClassIndex)) {
          setTimeout(() => {
            const targetCard = container.querySelector(`[data-class-index="${targetClassIndex}"]`);
            if (targetCard) {
              targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
              targetCard.scrollLeft = targetCard.scrollWidth;
            }
          }, 80);
        }
      }

      function updateStats() {
        const thead = document.querySelector('#statsTable thead'),
          tbody = document.querySelector('#statsTable tbody');
        thead.innerHTML = '';
        tbody.innerHTML = '';
        if (!classrooms.length) return;
        thead.innerHTML =
          '<tr><th>班级</th><th>总人数</th><th>男生</th><th>女生</th><th>总分均分</th><th>前80%总分均分</th><th>语文均分</th><th>前80%语文</th><th>数学均分</th><th>前80%数学</th><th>英语均分</th><th>前80%英语</th></tr>';
        const allStudents = classrooms.flat();
        const sortedAll = [...allStudents].sort((a, b) => b.总分 - a.总分);
        const gradeTop80Count = Math.ceil(allStudents.length * 0.8);
        const gradeTop80 = sortedAll.slice(0, gradeTop80Count);
        const gAvg = (arr, field) => arr.reduce((a, s) => a + parseNum(s[field]), 0) / arr.length || 0;
        let tStu = 0,
          tM = 0,
          tF = 0,
          tSc = 0,
          tCh = 0,
          tMa = 0,
          tEn = 0,
          tSc80 = 0,
          tCh80 = 0,
          tMa80 = 0,
          tEn80 = 0;
        classrooms.forEach((cls, i) => {
          const n = cls.length,
            m = cls.filter(s => s.性别 === '男').length,
            f = n - m;
          const sortedCls = [...cls].sort((a, b) => b.总分 - a.总分);
          const top80 = sortedCls.slice(0, Math.ceil(n * 0.8));
          const avg = (arr, field) => arr.reduce((a, s) => a + parseNum(s[field]), 0) / arr.length || 0;
          tStu += n;
          tM += m;
          tF += f;
          tSc += cls.reduce((a, s) => a + s.总分, 0);
          tCh += cls.reduce((a, s) => a + parseNum(s.语文), 0);
          tMa += cls.reduce((a, s) => a + parseNum(s.数学), 0);
          tEn += cls.reduce((a, s) => a + parseNum(s.英语), 0);
          tSc80 += top80.reduce((a, s) => a + s.总分, 0);
          tCh80 += top80.reduce((a, s) => a + parseNum(s.语文), 0);
          tMa80 += top80.reduce((a, s) => a + parseNum(s.数学), 0);
          tEn80 += top80.reduce((a, s) => a + parseNum(s.英语), 0);
          tbody.innerHTML +=
            `<tr><td>${i+1}班</td><td>${n}</td><td>${m}</td><td>${f}</td><td>${avg(cls,'总分').toFixed(2)}</td><td>${avg(top80,'总分').toFixed(2)}</td><td>${avg(cls,'语文').toFixed(2)}</td><td>${avg(top80,'语文').toFixed(2)}</td><td>${avg(cls,'数学').toFixed(2)}</td><td>${avg(top80,'数学').toFixed(2)}</td><td>${avg(cls,'英语').toFixed(2)}</td><td>${avg(top80,'英语').toFixed(2)}</td></tr>`;
        });
        tbody.innerHTML +=
          `<tr style="font-weight:bold"><td>年级</td><td>${tStu}</td><td>${tM}</td><td>${tF}</td><td>${(tSc/tStu).toFixed(2)}</td><td>${gAvg(gradeTop80,'总分').toFixed(2)}</td><td>${(tCh/tStu).toFixed(2)}</td><td>${gAvg(gradeTop80,'语文').toFixed(2)}</td><td>${(tMa/tStu).toFixed(2)}</td><td>${gAvg(gradeTop80,'数学').toFixed(2)}</td><td>${(tEn/tStu).toFixed(2)}</td><td>${gAvg(gradeTop80,'英语').toFixed(2)}</td></tr>`;
      }

      function compareDesc(a, b) {
        if (a.总分 !== b.总分) return b.总分 - a.总分;
        if (parseNum(a.数学附加分) !== parseNum(b.数学附加分)) return parseNum(b.数学附加分) - parseNum(a.数学附加分);
        if (parseNum(a.语文) !== parseNum(b.语文)) return parseNum(b.语文) - parseNum(a.语文);
        if (parseNum(a.数学) !== parseNum(b.数学)) return parseNum(b.数学) - parseNum(a.数学);
        return parseNum(b.英语) - parseNum(a.英语);
      }

      function groupConsecutive(sorted, classCnt) {
        const groups = [];
        for (let i = 0; i < sorted.length; i += classCnt) groups.push(sorted.slice(i, i + classCnt));
        return groups;
      }

      async function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

      function findBestSwapCandidate(targetClassIdx, incoming, excludeUids) {
        const cls = classrooms[targetClassIdx];
        const sorted = [...cls].sort(compareDesc);
        const top10Uids = new Set(sorted.slice(0, 10).map(s => s._uid));
        let best = null,
          minDiff = Infinity;
        for (let i = 0; i < cls.length; i++) {
          const s = cls[i];
          if (excludeUids.has(s._uid) || top10Uids.has(s._uid)) continue;
          const diff = Math.abs(s.总分 - incoming.总分);
          if (diff < minDiff) { minDiff = diff;
            best = { student: s, index: i }; }
        }
        return best;
      }

      function swapValid(clsA, idxA, clsB, idxB, classCnt) {
        const a = clsA[idxA],
          b = clsB[idxB];
        const newA = [...clsA];
        newA[idxA] = b;
        const newB = [...clsB];
        newB[idxB] = a;
        for (let g of twinsGroups) {
          const group = g.map(i => students[i]);
          for (let cls of [newA, newB]) {
            const present = group.filter(s => cls.includes(s));
            if (present.length > 0 && present.length < group.length) return false;
          }
          for (let k = 0; k < classCnt; k++) {
            if (k === classrooms.indexOf(clsA) || k === classrooms.indexOf(clsB)) continue;
            const other = classrooms[k];
            const presentOther = group.filter(s => other.includes(s));
            if (presentOther.length > 0 && presentOther.length < group.length) return false;
          }
        }
        for (let g of similarGroups) {
          const group = g.map(i => students[i]);
          for (let cls of [newA, newB]) {
            if (group.filter(s => cls.includes(s)).length > 1) return false;
          }
        }
        return true;
      }

      async function enforceConstraints(classCnt) {
        actionHint.textContent = '⚙️ 正在调整多胞胎/重名近似约束...';
        for (let g of twinsGroups) {
          const group = g.map(i => students[i]);
          const classes = group.map(s => classrooms.findIndex(cls => cls.includes(s)));
          if (new Set(classes).size === 1) continue;
          const sortedGroup = [...group].sort((a, b) => b.总分 - a.总分);
          const target = sortedGroup[0];
          const targetClass = classrooms.findIndex(cls => cls.includes(target));
          for (let stu of sortedGroup.slice(1)) {
            const srcClass = classrooms.findIndex(cls => cls.includes(stu));
            if (srcClass === targetClass) continue;
            const cand = findBestSwapCandidate(targetClass, stu, new Set(group.map(s => s._uid)));
            if (cand && swapValid(classrooms[srcClass], classrooms[srcClass].indexOf(stu), classrooms[targetClass], cand
                .index, classCnt)) {
              [classrooms[srcClass][classrooms[srcClass].indexOf(stu)], classrooms[targetClass][cand.index]] = [
                classrooms[targetClass][cand.index], classrooms[srcClass][classrooms[srcClass].indexOf(stu)]
              ];
              actionHint.textContent =
                `🔄 多胞胎调整：${stu.姓名}(${stu.性别},${stu.总分}) → ${targetClass+1}班，换出${cand.student.姓名}`;
              log(`多胞胎调整：${stu.姓名} -> ${targetClass+1}班，换出${cand.student.姓名}`);
              renderClassrooms(stu._uid, targetClass, [srcClass, targetClass]);
              await delay(800);
            }
          }
        }
        for (let g of similarGroups) {
          const group = g.map(i => students[i]);
          const classCounts = new Map();
          group.forEach(s => {
            const ci = classrooms.findIndex(cls => cls.includes(s));
            classCounts.set(ci, (classCounts.get(ci) || 0) + 1);
          });
          for (let [ci, cnt] of classCounts) {
            if (cnt > 1) {
              const same = group.filter(s => classrooms[ci].includes(s)).sort((a, b) => a.总分 - b.总分);
              const toMove = same[0];
              let minClass = -1,
                minSize = Infinity;
              for (let i = 0; i < classCnt; i++) {
                if (i === ci) continue;
                if (group.some(s => classrooms[i].includes(s))) continue;
                if (classrooms[i].length < minSize) { minSize = classrooms[i].length;
                  minClass = i; }
              }
              if (minClass !== -1) {
                const cand = findBestSwapCandidate(minClass, toMove, new Set(group.map(s => s._uid)));
                if (cand && swapValid(classrooms[ci], classrooms[ci].indexOf(toMove), classrooms[minClass], cand.index,
                    classCnt)) {
                  [classrooms[ci][classrooms[ci].indexOf(toMove)], classrooms[minClass][cand.index]] = [classrooms[
                    minClass][cand.index], classrooms[ci][classrooms[ci].indexOf(toMove)]];
                  actionHint.textContent =
                    `🔄 重名近似调整：${toMove.姓名}(${toMove.性别},${toMove.总分}) → ${minClass+1}班，换出${cand.student.姓名}`;
                  log(`重名近似调整：${toMove.姓名} -> ${minClass+1}班，换出${cand.student.姓名}`);
                  renderClassrooms(toMove._uid, minClass, [ci, minClass]);
                  await delay(800);
                }
              }
            }
          }
        }
        actionHint.textContent = '';
      }

      function evaluatePair(i, j) {
        const A = classrooms[i],
          B = classrooms[j];
        const mA = A.filter(s => s.性别 === '男').length,
          mB = B.filter(s => s.性别 === '男').length;
        const tDiff = Math.abs(A.length - B.length);
        const mDiff = Math.abs(mA - mB);
        const fDiff = Math.abs((A.length - mA) - (B.length - mB));
        const topA = [...A].sort((a, b) => b.总分 - a.总分).slice(0, Math.ceil(A.length * 0.8));
        const topB = [...B].sort((a, b) => b.总分 - a.总分).slice(0, Math.ceil(B.length * 0.8));
        const avgA = topA.reduce((a, s) => a + s.总分, 0) / topA.length || 0,
          avgB = topB.reduce((a, s) => a + s.总分, 0) / topB.length || 0;
        let penalty = 0;
        if (tDiff > 2) penalty += 1000;
        if (mDiff > 1) penalty += 1000;
        if (fDiff > 1) penalty += 1000;
        return penalty + tDiff * 15 + mDiff * 20 + fDiff * 20 + Math.abs(avgA - avgB) * 12;
      }

      async function balanceClasses(classCnt) {
        actionHint.textContent = '⚖️ 开始均衡优化...';
        for (let iter = 0; iter < 500; iter++) {
          let improved = false;
          for (let i = 0; i < classCnt; i++) {
            for (let j = i + 1; j < classCnt; j++) {
              const A = classrooms[i],
                B = classrooms[j];
              const topA = new Set(A.slice(0, 10).map(s => s._uid)),
                topB = new Set(B.slice(0, 10).map(s => s._uid));
              for (let a = 0; a < A.length; a++) {
                for (let b = 0; b < B.length; b++) {
                  if (topA.has(A[a]._uid) || topB.has(B[b]._uid)) continue;
                  if (!swapValid(A, a, B, b, classCnt)) continue;
                  const before = evaluatePair(i, j);
                  [A[a], B[b]] = [B[b], A[a]];
                  const after = evaluatePair(i, j);
                  if (after < before - 0.001) {
                    improved = true;
                    actionHint.textContent = `🔁 优化交换：${A[a].姓名} ↔ ${B[b].姓名}`;
                    renderClassrooms(null, null, [i, j]);
                    await delay(200);
                  } else [A[a], B[b]] = [B[b], A[a]];
                }
              }
            }
          }
          if (!improved) break;
        }
        actionHint.textContent = '';
      }

      async function allocate() {
        if (students.length === 0) { alert('请先导入数据'); return; }
        const classCnt = getClassCount();
        document.getElementById('classCount').value = classCnt;
        isAllocating = true;
        log(`开始分班，班级数：${classCnt}，学生数：${students.length}`);
        classrooms = Array.from({ length: classCnt }, () => []);

        const males = students.filter(s => s.性别 === '男').sort(compareDesc);
        const females = students.filter(s => s.性别 === '女').sort(compareDesc);
        const maleGroups = groupConsecutive(males, classCnt);
        const femaleGroups = groupConsecutive(females, classCnt);

        async function processGroup(group, gender) {
          let arr = [...group];
          for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]]; }
          if (arr.length === classCnt) {
            for (let idx = 0; idx < arr.length; idx++) {
              const stu = arr[idx];
              classrooms[idx].push(stu);
              actionHint.textContent = `🎯 派位${stu.姓名}(${stu.性别},${stu.总分}) → ${idx+1}班`;
              log(`派位${stu.姓名}(${stu.性别},${stu.总分}) -> ${idx+1}班`);
              renderClassrooms(stu._uid, idx, [idx]);
              await delay(900);
            }
          } else {
            for (let i = 0; i < arr.length; i++) {
              const target = i % classCnt;
              classrooms[target].push(arr[i]);
              actionHint.textContent = `🎯 派位${arr[i].姓名}(${arr[i].性别},${arr[i].总分}) → ${target+1}班`;
              log(`派位${arr[i].姓名}(${arr[i].性别},${arr[i].总分}) -> ${target+1}班`);
              renderClassrooms(arr[i]._uid, target, [target]);
              await delay(850);
            }
          }
        }

        for (let g of maleGroups) await processGroup(g, '男');
        for (let g of femaleGroups) await processGroup(g, '女');

        classrooms.forEach(cls => cls.sort((a, b) => {
          if (a.性别 === b.性别) return compareDesc(a, b);
          return a.性别 === '男' ? -1 : 1;
        }));
        renderClassrooms();
        await enforceConstraints(classCnt);
        await balanceClasses(classCnt);
        isAllocating = false;
        renderClassrooms();
        updateStats();
        actionHint.textContent = '✅ 分班完成！';
        log("分班完成！");
      }

      document.getElementById('classCount').addEventListener('change', function() {
        const cnt = getClassCount();
        this.value = cnt;
        classrooms = Array.from({ length: cnt }, () => []);
        renderClassrooms();
        updateStats();
        log(`班级数量变更为${cnt}，分班区域已重置。`);
      });

      document.getElementById('importBtn').addEventListener('click', async () => {
        try {
          const picked = await window.pywebview.api.choose_student_file();
          if (!picked) return;

          const binary = atob(picked.data);
          const data = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) data[i] = binary.charCodeAt(i);

        const wb = XLSX.read(data);
        const sheet = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 });
        if (rows.length < 2) return;
        students = rows.slice(1).map(row => ({
          报名号: row[0],
          姓名: row[1],
          性别: parseGender(row[2]),
          身份证: row[3],
          生源: row[4],
          语文: parseNum(row[5]),
          数学: parseNum(row[6]),
          英语: parseNum(row[7]),
          总分: row[8] ? parseNum(row[8]) : calcTotal({ 语文: row[5], 数学: row[6], 英语: row[7] }),
          数学附加分: parseNum(row[9]),
          多胞胎原始: row[10],
          重名近似原始: row[11],
          _uid: Math.random().toString(36)
        }));
        students.forEach(s => { if (!s.总分) s.总分 = calcTotal(s); });
        twinsGroups = [];
        similarGroups = [];
        const twinMap = new Map(),
          simMap = new Map();
        students.forEach((s, i) => {
          let tv = parseInt(s.多胞胎原始);
          if (!isNaN(tv) && tv > 0) { if (!twinMap.has(tv)) twinMap.set(tv, []);
            twinMap.get(tv).push(i); }
          let sv = parseInt(s.重名近似原始);
          if (!isNaN(sv) && sv > 0) { if (!simMap.has(sv)) simMap.set(sv, []);
            simMap.get(sv).push(i); }
        });
        twinsGroups = Array.from(twinMap.values()).filter(g => g.length >= 2);
        similarGroups = Array.from(simMap.values()).filter(g => g.length >= 2);
        renderDataPreview();
        updateCounts();
        showMultiInfo();
        log(`导入${students.length}名学生，多胞胎${twinsGroups.length}组，重名近似${similarGroups.length}组`);
        } catch (err) {
          console.error(err);
          alert('导入失败：' + (err && err.message ? err.message : err));
        }
      });

      document.getElementById('markTwinsBtn').addEventListener('click', () => {
        const sel = getCheckedIndices();
        if (sel.length < 2) { alert('请至少勾选2名学生'); return; }
        twinsGroups.push([...sel]);
        showMultiInfo();
        log(`新增多胞胎组: ${sel.map(i=>students[i].姓名).join(',')}`);
      });
      document.getElementById('markSimilarBtn').addEventListener('click', () => {
        const sel = getCheckedIndices();
        if (sel.length < 2) { alert('请至少勾选2名学生'); return; }
        similarGroups.push([...sel]);
        showMultiInfo();
        log(`新增重名近似组: ${sel.map(i=>students[i].姓名).join(',')}`);
      });
      document.getElementById('cancelGroupBtn').addEventListener('click', () => {
        const sel = getCheckedIndices();
        if (sel.length === 0) { alert('请勾选要取消组中的学生'); return; }
        twinsGroups = twinsGroups.filter(g => !g.some(i => sel.includes(i)));
        similarGroups = similarGroups.filter(g => !g.some(i => sel.includes(i)));
        showMultiInfo();
        log('已取消包含选中学生的组');
      });

      document.getElementById('startBtn').addEventListener('click', allocate);
      document.getElementById('clearAllBtn').addEventListener('click', () => {
        students = [];
        twinsGroups = [];
        similarGroups = [];
        classrooms = [];
        logEntries = [];
        isAllocating = false;
        document.getElementById('fileInput').value = '';
        renderDataPreview();
        updateCounts();
        showMultiInfo();
        renderClassrooms();
        updateStats();
        document.getElementById('logPanel').textContent = '[操作日志] 已清除。';
        actionHint.textContent = '🎯 准备就绪，请导入数据并开始分班';
        log('所有数据已重置');
      });
      document.getElementById('toggleStatsBtn').addEventListener('click', () => document.getElementById('statsTable')
        .classList.toggle('hidden'));
      document.getElementById('downloadTemplateBtn').addEventListener('click', async () => {
        try {
          const wb = XLSX.utils.book_new();
          XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([
            ['报名号', '姓名', '性别', '身份证', '生源', '语文', '数学', '英语', '总分', '数学附加分', '多胞胎',
              '重名近似'
            ]
          ]), "模板");
          const data = XLSX.write(wb, { bookType: 'xlsx', type: 'base64' });
          await window.pywebview.api.save_base64_file(
            data, "学生导入模板.xlsx", "Excel 工作簿 (*.xlsx)"
          );
        } catch (err) {
          console.error(err);
          alert('下载模板失败：' + (err && err.message ? err.message : err));
        }
      });

      document.getElementById('exportExcelBtn').addEventListener('click', async () => {
        if (!classrooms.length) return alert('无分班结果');
        const title = "当涂县乌溪初级中学阳光分班";
        const header = ['报名号', '姓名', '性别', '身份证', '生源', '语文', '数学', '英语', '总分', '数学附加分', '新班级',
          '序号'
        ];
        const out = [
          [title], header
        ];
        classrooms.forEach((cls, idx) => cls.forEach((s, i) => out.push([s.报名号, s.姓名, s.性别, s.身份证, s.生源, s.语文,
          s.数学, s.英语, s.总分, s.数学附加分, `${idx+1}班`, i + 1
        ])));
        const ws = XLSX.utils.aoa_to_sheet(out);
        ws['!merges'] = [{ s: { r: 0, c: 0 }, e: { r: 0, c: header.length - 1 } }];
        const range = XLSX.utils.decode_range(ws['!ref']);
        for (let R = range.s.r; R <= range.e.r; R++) {
          for (let C = range.s.c; C <= range.e.c; C++) {
            const addr = XLSX.utils.encode_cell({ r: R, c: C });
            if (!ws[addr]) continue;
            if (!ws[addr].s) ws[addr].s = {};
            ws[addr].s.alignment = { horizontal: 'center', vertical: 'center' };
          }
        }
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "分班结果");
        const data = XLSX.write(wb, { bookType: 'xlsx', type: 'base64' });
        await window.pywebview.api.save_base64_file(
          data, `${title}.xlsx`, "Excel 工作簿 (*.xlsx)"
        );
      });

      async function exportPDF() {
        if (!classrooms.length) return alert('无分班结果');
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        const today = new Date().toLocaleDateString('zh-CN');
        const title = "当涂县乌溪初级中学阳光分班";
        for (let i = 0; i < classrooms.length; i++) {
          if (i > 0) doc.addPage();
          const cls = classrooms[i];
          const div = document.createElement('div');
          div.style.position = 'absolute';
          div.style.left = '-9999px';
          div.style.width = '190mm';
          div.innerHTML = `<div style="font-family: SimSun, serif; padding: 10px; text-align:center; border: 2px solid #333; border-radius: 4px;">
            <h2 style="text-align:center; margin:5px 0; font-size:16px;">${title}</h2>
            <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:8px;">
              <span>${i+1}班</span><span>班主任签名：____________</span><span>日期：${today}</span>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:10px; font-family:SimSun; text-align:center; border:1px solid #000;">
              <tr style="border:1px solid #000;"><th style="border:1px solid #000;">报名号</th><th style="border:1px solid #000;">姓名</th><th style="border:1px solid #000;">性别</th><th style="border:1px solid #000;">身份证</th><th style="border:1px solid #000;">生源</th><th style="border:1px solid #000;">语文</th><th style="border:1px solid #000;">数学</th><th style="border:1px solid #000;">英语</th><th style="border:1px solid #000;">总分</th><th style="border:1px solid #000;">数学附加分</th><th style="border:1px solid #000;">新班级</th><th style="border:1px solid #000;">序号</th></tr>
              ${cls.map((s, idx) => `<tr style="border:1px solid #000;"><td style="border:1px solid #000;">${s.报名号||''}</td><td style="border:1px solid #000;">${s.姓名}</td><td style="border:1px solid #000;">${s.性别}</td><td style="border:1px solid #000;">${s.身份证||''}</td><td style="border:1px solid #000;">${s.生源||''}</td><td style="border:1px solid #000;">${s.语文}</td><td style="border:1px solid #000;">${s.数学}</td><td style="border:1px solid #000;">${s.英语}</td><td style="border:1px solid #000;">${s.总分}</td><td style="border:1px solid #000;">${s.数学附加分}</td><td style="border:1px solid #000;">${i+1}班</td><td style="border:1px solid #000;">${idx+1}</td></tr>`).join('')}
            </table>
          </div>`;
          document.body.appendChild(div);
          const canvas = await html2canvas(div, { scale: 2, useCORS: true, allowTaint: true });
          document.body.removeChild(div);
          const imgData = canvas.toDataURL('image/png');
          const pageWidth = doc.internal.pageSize.getWidth();
          const pageHeight = doc.internal.pageSize.getHeight();
          doc.addImage(imgData, 'PNG', 0, 0, pageWidth, pageHeight, undefined, 'FAST');
        }
        const pdfData = doc.output('datauristring').split(',')[1];
        await window.pywebview.api.save_base64_file(
          pdfData, `${title}.pdf`, "PDF 文件 (*.pdf)"
        );
      }
      document.getElementById('exportPdfBtn').addEventListener('click', exportPDF);

      document.getElementById('exportLogBtn').addEventListener('click', async () => {
        if (logEntries.length === 0) return alert('无日志');
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF('p', 'mm', 'a4');
        const title = "当涂县乌溪初级中学阳光分班 - 操作日志";
        const today = new Date().toLocaleDateString('zh-CN');
        const div = document.createElement('div');
        div.style.position = 'absolute';
        div.style.left = '-9999px';
        div.style.width = '180mm';
        div.style.padding = '10mm';
        div.style.fontFamily = 'SimSun, serif';
        div.innerHTML = `<div style="font-family: SimSun, serif; padding: 10px; border: 2px solid #333;">
          <h2 style="text-align:center; font-size:14px;">${title}</h2>
          <p style="text-align:right; font-size:10px;">导出日期：${today}</p>
          <hr style="margin:6px 0;">
          <div style="font-size:9px; line-height:1.6; white-space:pre-wrap;">${logEntries.join('\n')}</div>
        </div>`;
        document.body.appendChild(div);
        const canvas = await html2canvas(div, { scale: 2, useCORS: true, allowTaint: true });
        document.body.removeChild(div);
        const imgData = canvas.toDataURL('image/png');
        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const imgHeight = (canvas.height * pageWidth) / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;
        doc.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
        heightLeft -= pageHeight;
        while (heightLeft > 0) {
          position = -(imgHeight - heightLeft);
          doc.addPage();
          doc.addImage(imgData, 'PNG', 0, position, pageWidth, imgHeight);
          heightLeft -= pageHeight;
        }
        const pdfData = doc.output('datauristring').split(',')[1];
        await window.pywebview.api.save_base64_file(
          pdfData, '操作日志.pdf', "PDF 文件 (*.pdf)"
        );
      });

      classrooms = Array.from({ length: getClassCount() }, () => []);
      renderDataPreview();
      updateCounts();
      showMultiInfo();
      renderClassrooms();
      updateStats();
    })();
  </script>
</body>
</html>
"""

    # 将 Excel / PDF 相关 JS 库改为本地嵌入，保证离线运行
    html = inline_offline_libraries(html)

    # pywebview 默认会阻止网页触发的文件下载。
    # 本程序的“下载模板 / 导出 Excel / 导出 PDF”等功能需要开启它。
    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.settings["ALLOW_FILE_URLS"] = True

    # 创建窗口
    api = FileApi()
    window = webview.create_window(
        title="当涂县乌溪初级中学阳光分班",
        html=html,
        js_api=api,
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    webview.start(debug=os.environ.get("SUNSHINE_DEBUG") == "1")

if __name__ == "__main__":
    main()
