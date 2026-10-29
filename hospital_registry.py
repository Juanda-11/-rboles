import json
import threading
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 8000


class PatientNode:
    def __init__(self, patient_id, name, age, diagnosis):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.diagnosis = diagnosis
        self.left = None
        self.right = None

    def to_dict(self):
        return {
            "id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "diagnosis": self.diagnosis,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }


class PatientTree:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, patient_id, name, age, diagnosis):
        if self.root is None:
            self.root = PatientNode(patient_id, name, age, diagnosis)
            self.size += 1
            return True
        current = self.root
        while True:
            if patient_id == current.patient_id:
                return False
            if patient_id < current.patient_id:
                if current.left is None:
                    current.left = PatientNode(patient_id, name, age, diagnosis)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = PatientNode(patient_id, name, age, diagnosis)
                    break
                current = current.right
        self.size += 1
        return True

    def search(self, patient_id):
        path = []
        current = self.root
        while current is not None:
            path.append(current.patient_id)
            if patient_id == current.patient_id:
                return current, path
            current = current.left if patient_id < current.patient_id else current.right
        return None, path

    def delete(self, patient_id):
        removed = [False]

        def remove(node, key):
            if node is None:
                return None
            if key < node.patient_id:
                node.left = remove(node.left, key)
            elif key > node.patient_id:
                node.right = remove(node.right, key)
            else:
                removed[0] = True
                if node.left is None:
                    return node.right
                if node.right is None:
                    return node.left
                successor = node.right
                while successor.left is not None:
                    successor = successor.left
                node.patient_id = successor.patient_id
                node.name = successor.name
                node.age = successor.age
                node.diagnosis = successor.diagnosis
                node.right = remove(node.right, successor.patient_id)
            return node

        self.root = remove(self.root, patient_id)
        if removed[0]:
            self.size -= 1
        return removed[0]

    def height(self):
        def measure(node):
            if node is None:
                return 0
            return 1 + max(measure(node.left), measure(node.right))

        return measure(self.root)

    def in_order(self):
        result = []

        def visit(node):
            if node:
                visit(node.left)
                result.append(node.patient_id)
                visit(node.right)

        visit(self.root)
        return result

    def pre_order(self):
        result = []

        def visit(node):
            if node:
                result.append(node.patient_id)
                visit(node.left)
                visit(node.right)

        visit(self.root)
        return result

    def post_order(self):
        result = []

        def visit(node):
            if node:
                visit(node.left)
                visit(node.right)
                result.append(node.patient_id)

        visit(self.root)
        return result

    def level_order(self):
        result = []
        queue = deque([self.root] if self.root else [])
        while queue:
            node = queue.popleft()
            result.append(node.patient_id)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

    def minimum(self):
        current = self.root
        while current and current.left:
            current = current.left
        return current

    def maximum(self):
        current = self.root
        while current and current.right:
            current = current.right
        return current

    def snapshot(self):
        low = self.minimum()
        high = self.maximum()
        return {
            "tree": self.root.to_dict() if self.root else None,
            "size": self.size,
            "height": self.height(),
            "min": low.patient_id if low else None,
            "max": high.patient_id if high else None,
        }


registry = PatientTree()
lock = threading.Lock()

SEED_PATIENTS = [
    (5040, "Maria Fernandez", 34, "Migraine"),
    (3020, "Carlos Ramirez", 58, "Hypertension"),
    (7060, "Laura Gomez", 27, "Asthma"),
    (2010, "Andres Torres", 45, "Diabetes"),
    (4030, "Sofia Herrera", 19, "Allergy"),
    (6050, "Jorge Castillo", 63, "Arthritis"),
    (8070, "Valentina Ruiz", 41, "Anemia"),
    (1005, "Daniel Moreno", 52, "Gastritis"),
    (3500, "Camila Vargas", 30, "Bronchitis"),
]

for seed in SEED_PATIENTS:
    registry.insert(*seed)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hospital Patient Registry</title>
<style>
:root {
  --navy: #1e2a5e;
  --navy-2: #2c3b86;
  --blue: #4f6ef7;
  --blue-soft: #e8edff;
  --orange: #ff7a45;
  --orange-soft: #ffe9df;
  --purple: #8e2391;
  --green: #12b8a0;
  --green-soft: #d9f6f1;
  --bg: #f3f5fb;
  --card: #ffffff;
  --line: #e1e5f2;
  --text: #1f2547;
  --muted: #6f7799;
  --danger: #e5484d;
  --shadow: 0 10px 30px rgba(30, 42, 94, 0.08);
  --radius: 16px;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: "Inter", "Segoe UI", system-ui, -apple-system, Helvetica, Arial, sans-serif;
  background:
    radial-gradient(900px 400px at 100% -10%, #e3e9ff 0%, transparent 60%),
    radial-gradient(700px 400px at -10% 30%, #ffeee5 0%, transparent 55%),
    var(--bg);
  background-attachment: fixed;
  color: var(--text);
  min-height: 100vh;
}
header {
  background: linear-gradient(120deg, var(--navy) 0%, var(--navy-2) 60%, #4a3fa8 100%);
  color: #fff;
  padding: 26px 40px 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
  border-radius: 0 0 28px 28px;
  box-shadow: 0 12px 34px rgba(30, 42, 94, 0.25);
}
.brand { display: flex; align-items: center; gap: 16px; }
.logo {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.14);
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.25);
}
.logo svg { width: 30px; height: 30px; }
header h1 { margin: 0; font-size: 26px; letter-spacing: -0.3px; }
header h1 span { color: #ffb08a; }
header p { margin: 4px 0 0; color: #c9d1f7; font-size: 14px; }
.stats { display: flex; gap: 12px; flex-wrap: wrap; }
.stat {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 14px;
  padding: 10px 18px;
  min-width: 104px;
  text-align: center;
  backdrop-filter: blur(6px);
  transition: transform 0.2s;
}
.stat:hover { transform: translateY(-2px); }
.stat b { display: block; font-size: 24px; line-height: 1.2; }
.stat small { color: #c9d1f7; font-size: 12px; text-transform: uppercase; letter-spacing: 0.6px; }
main {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 24px;
  padding: 26px 40px 40px;
  max-width: 1500px;
  margin: 0 auto;
}
@media (max-width: 980px) {
  main { grid-template-columns: 1fr; padding: 18px; }
  header { padding: 22px 18px; }
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}
.card h2 {
  margin: 0 0 14px;
  font-size: 15px;
  color: var(--navy);
  display: flex;
  align-items: center;
  gap: 10px;
  text-transform: uppercase;
  letter-spacing: 0.7px;
}
.card h2 .dot {
  width: 28px;
  height: 28px;
  border-radius: 9px;
  display: grid;
  place-items: center;
  background: var(--orange-soft);
  color: var(--orange);
}
.card h2 .dot svg { width: 16px; height: 16px; }
.card h2 .dot.blue { background: var(--blue-soft); color: var(--blue); }
.card h2 .dot.green { background: var(--green-soft); color: var(--green); }
.card h2 .dot.purple { background: #f6e3f7; color: var(--purple); }
label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  margin: 12px 0 5px;
}
input {
  width: 100%;
  padding: 11px 13px;
  border: 1.5px solid var(--line);
  border-radius: 10px;
  font-size: 14px;
  font-family: inherit;
  color: var(--text);
  background: #fafbff;
  transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
}
input::placeholder { color: #a9b0cc; }
input:focus {
  outline: none;
  border-color: var(--blue);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(79, 110, 247, 0.15);
}
.row { display: flex; gap: 10px; }
.row > * { flex: 1; min-width: 0; }
button {
  margin-top: 14px;
  padding: 11px 16px;
  border: 0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, #5b79ff, #4160ee);
  width: 100%;
  box-shadow: 0 6px 14px rgba(79, 110, 247, 0.3);
  transition: transform 0.12s, box-shadow 0.12s, filter 0.12s;
}
button:hover { transform: translateY(-1px); filter: brightness(1.06); }
button:active { transform: translateY(1px); box-shadow: none; }
button:focus-visible { outline: 3px solid rgba(79, 110, 247, 0.4); outline-offset: 2px; }
button.orange { background: linear-gradient(135deg, #ff9566, #ff7a45); box-shadow: 0 6px 14px rgba(255, 122, 69, 0.3); }
button.danger { background: linear-gradient(135deg, #ef6a6e, #e5484d); box-shadow: 0 6px 14px rgba(229, 72, 77, 0.28); }
button.purple {
  background: #fff;
  color: var(--purple);
  border: 1.5px solid #e6c9e8;
  box-shadow: none;
  margin-top: 0;
}
button.purple:hover { background: #faf0fb; }
button.purple.on { background: var(--purple); color: #fff; border-color: var(--purple); }
.toast {
  margin-top: 12px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: all 0.25s;
}
.toast.ok, .toast.error { max-height: 80px; opacity: 1; padding: 10px 12px; }
.toast.ok { background: var(--green-soft); color: #0b7d6c; }
.toast.error { background: #fde8e9; color: #b3262b; }
.canvas {
  overflow: auto;
  background:
    linear-gradient(var(--line) 1px, transparent 1px) 0 0 / 100% 36px,
    linear-gradient(90deg, var(--line) 1px, transparent 1px) 0 0 / 36px 100%,
    #fbfcff;
  background-blend-mode: soft-light;
  border: 1px solid var(--line);
  border-radius: 14px;
  min-height: 420px;
  padding: 8px;
}
.canvas svg { display: block; margin: 0 auto; }
.empty-state {
  padding: 90px 24px;
  text-align: center;
  color: var(--muted);
}
.empty-state b { display: block; color: var(--navy); font-size: 18px; margin-bottom: 6px; }
.edge { stroke: #b4bde3; stroke-width: 2.5; fill: none; stroke-linecap: round; transition: stroke 0.3s; }
.edge.active { stroke: var(--orange); stroke-width: 4; }
.node circle {
  fill: var(--blue-soft);
  stroke: var(--blue);
  stroke-width: 3;
  cursor: pointer;
  filter: drop-shadow(0 4px 6px rgba(30, 42, 94, 0.18));
  transition: fill 0.25s, stroke 0.25s, r 0.2s;
}
.node:hover circle { r: 30; }
.node.root circle { fill: var(--orange-soft); stroke: var(--orange); }
.node.leaf circle { fill: var(--green-soft); stroke: var(--green); }
.node.active circle { fill: var(--orange); stroke: var(--navy); }
.node.found circle { fill: var(--green); stroke: var(--navy); }
.node text.id { font-size: 12px; font-weight: 800; fill: var(--navy); pointer-events: none; text-anchor: middle; }
.node text.who { font-size: 11px; font-weight: 600; fill: var(--muted); stroke: #fbfcff; stroke-width: 4px; paint-order: stroke; stroke-linejoin: round; pointer-events: none; text-anchor: middle; }
.node.active text.id, .node.found text.id { fill: #fff; }
.legend { display: flex; gap: 18px; flex-wrap: wrap; margin-top: 14px; font-size: 12px; color: var(--muted); font-weight: 600; }
.legend i { display: inline-block; width: 13px; height: 13px; border-radius: 50%; margin-right: 6px; vertical-align: -2px; border: 2.5px solid; }
.sequence { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 16px; min-height: 38px; }
.sequence .hint { color: var(--muted); font-size: 13px; }
.chip {
  background: var(--blue-soft);
  color: var(--navy);
  border-radius: 999px;
  padding: 5px 13px;
  font-size: 13px;
  font-weight: 700;
  transition: background 0.25s, color 0.25s, transform 0.25s;
}
.chip.lit { background: var(--orange); color: #fff; transform: scale(1.06); }
.detail { font-size: 14px; line-height: 1.5; }
.detail .name { font-size: 18px; font-weight: 800; color: var(--navy); margin-bottom: 10px; }
.detail dl { margin: 0; display: grid; grid-template-columns: 110px 1fr; gap: 8px 10px; }
.detail dt { color: var(--muted); font-weight: 600; font-size: 13px; }
.detail dd { margin: 0; font-weight: 600; }
.detail .path { margin-top: 12px; padding: 10px 12px; background: var(--orange-soft); border-radius: 10px; font-size: 13px; color: #a5441a; font-weight: 600; }
.detail .empty { color: var(--muted); }
.traversals { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
@media (max-width: 560px) { .traversals { grid-template-columns: 1fr; } }
footer { text-align: center; color: var(--muted); font-size: 12px; padding: 0 0 26px; }
</style>
</head>
<body>
<header>
  <div>
    <div class="brand">
      <div class="logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2.5"/><circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M11 7.3 7 16.7M13 7.3l4 9.4"/></svg>
      </div>
      <div>
        <h1>Hospital <span>Patient Registry</span></h1>
        <p>Patients stored in a binary search tree and ordered by patient ID</p>
      </div>
    </div>
  </div>
  <div class="stats">
    <div class="stat"><b id="statSize">0</b><small>Patients</small></div>
    <div class="stat"><b id="statHeight">0</b><small>Height</small></div>
    <div class="stat"><b id="statMin">-</b><small>Lowest ID</small></div>
    <div class="stat"><b id="statMax">-</b><small>Highest ID</small></div>
  </div>
</header>
<main>
  <aside>
    <section class="card">
      <h2><span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg></span>Admit patient</h2>
      <label for="pid">Patient ID</label>
      <input id="pid" type="number" min="1" placeholder="e.g. 4500">
      <label for="pname">Full name</label>
      <input id="pname" type="text" placeholder="e.g. Ana Lopez">
      <div class="row">
        <div>
          <label for="page">Age</label>
          <input id="page" type="number" min="0" max="120" placeholder="35">
        </div>
        <div>
          <label for="pdiag">Diagnosis</label>
          <input id="pdiag" type="text" placeholder="Flu">
        </div>
      </div>
      <button id="addBtn">Add to registry</button>
    </section>
    <section class="card">
      <h2><span class="dot blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></span>Search or discharge</h2>
      <label for="sid">Patient ID</label>
      <input id="sid" type="number" min="1" placeholder="e.g. 6050">
      <div class="row">
        <button id="searchBtn" class="orange">Search</button>
        <button id="deleteBtn" class="danger">Discharge</button>
      </div>
      <div id="toast" class="toast"></div>
    </section>
    <section class="card">
      <h2><span class="dot green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></span>Selected patient</h2>
      <div id="detail" class="detail"><span class="empty">Click a node or search an ID.</span></div>
    </section>
  </aside>
  <section>
    <div class="card">
      <h2><span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="19" r="2"/><path d="M11 7 7 17M13 7l4 10"/></svg></span>Registry tree</h2>
      <div class="canvas" id="canvas"></div>
      <div class="legend">
        <span><i style="background:#ffe4d6;border-color:#ff7a45"></i>Root</span>
        <span><i style="background:#e6ecff;border-color:#5479fb"></i>Internal node</span>
        <span><i style="background:#d6f7f0;border-color:#00bfa5"></i>Leaf</span>
        <span><i style="background:#ff7a45;border-color:#253068"></i>Visited</span>
        <span><i style="background:#00bfa5;border-color:#253068"></i>Found</span>
      </div>
    </div>
    <div class="card">
      <h2><span class="dot purple"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h12M12 6l6 6-6 6"/></svg></span>Traversals</h2>
      <div class="traversals">
        <button class="purple" data-kind="in_order">In-order (sorted by ID)</button>
        <button class="purple" data-kind="pre_order">Pre-order</button>
        <button class="purple" data-kind="post_order">Post-order</button>
        <button class="purple" data-kind="level_order">Level-order (by depth)</button>
      </div>
      <div class="sequence" id="sequence"><span class="hint">Choose a traversal to see the visiting order.</span></div>
    </div>
  </section>
</main>
<footer>Data Structures workshop &middot; Binary search tree case study</footer>
<script>
const NODE_RADIUS = 26;
const X_GAP = 76;
const Y_GAP = 100;
const MARGIN = 40;

const state = { tree: null, selected: null, visited: [], found: null, lit: -1 };

const $ = (id) => document.getElementById(id);

function toast(message, kind) {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast " + (kind || "");
}

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  return { ok: response.ok, data };
}

function layout(root) {
  const nodes = [];
  let counter = 0;
  function place(node, depth) {
    if (!node) return;
    place(node.left, depth + 1);
    node.x = MARGIN + counter * X_GAP;
    node.y = MARGIN + depth * Y_GAP;
    counter += 1;
    nodes.push(node);
    place(node.right, depth + 1);
  }
  place(root, 0);
  return { nodes, count: counter };
}

function collectEdges(node, edges) {
  if (!node) return;
  if (node.left) edges.push({ from: node, to: node.left });
  if (node.right) edges.push({ from: node, to: node.right });
  collectEdges(node.left, edges);
  collectEdges(node.right, edges);
}

function renderTree() {
  const canvas = $("canvas");
  if (!state.tree) {
    canvas.innerHTML = '<div class="empty-state"><b>The registry is empty</b>Admit a patient to create the root of the tree.</div>';
    return;
  }
  const { nodes, count } = layout(state.tree);
  const edges = [];
  collectEdges(state.tree, edges);
  let maxDepth = 0;
  nodes.forEach((n) => { maxDepth = Math.max(maxDepth, Math.round((n.y - MARGIN) / Y_GAP)); });
  const width = MARGIN * 2 + Math.max(count - 1, 1) * X_GAP;
  const height = MARGIN * 2 + maxDepth * Y_GAP + 20;
  const visitedSet = new Set(state.visited);
  let svg = '<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '">';
  edges.forEach((e) => {
    const active = visitedSet.has(e.from.id) && visitedSet.has(e.to.id);
    const midY = (e.from.y + e.to.y) / 2;
    svg += '<path class="edge' + (active ? " active" : "") + '" d="M' + e.from.x + " " + e.from.y + " C" + e.from.x + " " + midY + " " + e.to.x + " " + midY + " " + e.to.x + " " + e.to.y + '"/>';
  });
  nodes.forEach((n) => {
    const classes = ["node"];
    if (n.id === state.tree.id) classes.push("root");
    else if (!n.left && !n.right) classes.push("leaf");
    if (visitedSet.has(n.id)) classes.push("active");
    if (state.found === n.id) classes.push("found");
    svg += '<g class="' + classes.join(" ") + '" data-id="' + n.id + '" transform="translate(' + n.x + "," + n.y + ')">';
    svg += '<circle r="' + NODE_RADIUS + '"/><text class="id" y="4">' + n.id + '</text><text class="who" y="' + (NODE_RADIUS + 16) + '">' + escapeHtml(n.name.split(" ")[0]) + "</text></g>";
  });
  svg += "</svg>";
  canvas.innerHTML = svg;
  canvas.querySelectorAll(".node").forEach((el) => {
    el.addEventListener("click", () => selectPatient(Number(el.dataset.id)));
  });
}

function renderStats(data) {
  $("statSize").textContent = data.size;
  $("statHeight").textContent = data.height;
  $("statMin").textContent = data.min === null ? "-" : data.min;
  $("statMax").textContent = data.max === null ? "-" : data.max;
}

function renderDetail(patient, path) {
  const el = $("detail");
  if (!patient) {
    el.innerHTML = '<span class="empty">Click a node or search an ID.</span>';
    return;
  }
  el.innerHTML =
    '<div class="name">' + escapeHtml(patient.name) + "</div><dl>" +
    "<dt>Patient ID</dt><dd>" + patient.id + "</dd>" +
    "<dt>Age</dt><dd>" + patient.age + " years</dd>" +
    "<dt>Diagnosis</dt><dd>" + escapeHtml(patient.diagnosis) + "</dd></dl>" +
    (path ? '<div class="path">' + path.length + " comparisons: " + path.join(" &rarr; ") + "</div>" : "");
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function refresh() {
  const { data } = await api("/api/tree");
  state.tree = data.tree;
  renderStats(data);
  renderTree();
}

async function selectPatient(id) {
  const { ok, data } = await api("/api/search?id=" + id);
  state.visited = data.path || [];
  state.found = ok ? id : null;
  renderTree();
  renderDetail(ok ? data.patient : null, data.path);
  if (ok) toast("Patient " + id + " found after " + data.path.length + " comparisons.", "ok");
  return ok;
}

async function addPatient() {
  const payload = {
    id: $("pid").value,
    name: $("pname").value,
    age: $("page").value,
    diagnosis: $("pdiag").value,
  };
  const { ok, data } = await api("/api/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!ok) {
    toast(data.error, "error");
    return;
  }
  state.visited = [];
  state.found = null;
  await refresh();
  const id = Number(payload.id);
  await selectPatient(id);
  toast("Patient " + id + " admitted.", "ok");
  ["pid", "pname", "page", "pdiag"].forEach((field) => { $(field).value = ""; });
}

async function searchPatient() {
  const id = $("sid").value;
  if (id === "") {
    toast("Enter a patient ID to search.", "error");
    return;
  }
  const found = await selectPatient(Number(id));
  if (!found) toast("Patient " + id + " is not registered.", "error");
}

async function deletePatient() {
  const id = $("sid").value;
  if (id === "") {
    toast("Enter a patient ID to discharge.", "error");
    return;
  }
  const { ok, data } = await api("/api/patients/" + id, { method: "DELETE" });
  if (!ok) {
    toast(data.error, "error");
    return;
  }
  state.visited = [];
  state.found = null;
  renderDetail(null);
  await refresh();
  toast("Patient " + id + " discharged.", "ok");
}

async function runTraversal(kind) {
  const { data } = await api("/api/traversal?kind=" + kind);
  const box = $("sequence");
  box.innerHTML = "";
  document.querySelectorAll("[data-kind]").forEach((btn) => {
    btn.classList.toggle("on", btn.dataset.kind === kind);
  });
  state.found = null;
  state.visited = [];
  renderTree();
  data.sequence.forEach((id, index) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = id;
    box.appendChild(chip);
    setTimeout(() => {
      state.visited = data.sequence.slice(0, index + 1);
      renderTree();
      chip.classList.add("lit");
    }, index * 350);
  });
}

$("addBtn").addEventListener("click", addPatient);
$("searchBtn").addEventListener("click", searchPatient);
$("deleteBtn").addEventListener("click", deletePatient);
document.querySelectorAll("[data-kind]").forEach((btn) => {
  btn.addEventListener("click", () => runTraversal(btn.dataset.kind));
});
refresh();
</script>
</body>
</html>
"""


class RegistryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def send_payload(self, status, body, content_type="application/json"):
        payload = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path == "/":
            self.send_payload(200, PAGE.encode("utf-8"), "text/html")
        elif url.path == "/api/tree":
            with lock:
                self.send_payload(200, registry.snapshot())
        elif url.path == "/api/search":
            try:
                patient_id = int(query.get("id", [""])[0])
            except ValueError:
                self.send_payload(400, {"error": "Patient ID must be a number.", "path": []})
                return
            with lock:
                node, path = registry.search(patient_id)
            if node is None:
                self.send_payload(404, {"error": "Patient not found.", "path": path})
            else:
                patient = {"id": node.patient_id, "name": node.name, "age": node.age, "diagnosis": node.diagnosis}
                self.send_payload(200, {"patient": patient, "path": path})
        elif url.path == "/api/traversal":
            kind = query.get("kind", ["in_order"])[0]
            if kind not in ("in_order", "pre_order", "post_order", "level_order"):
                self.send_payload(400, {"error": "Unknown traversal."})
                return
            with lock:
                sequence = getattr(registry, kind)()
            self.send_payload(200, {"sequence": sequence})
        else:
            self.send_payload(404, {"error": "Not found."})

    def do_POST(self):
        if urlparse(self.path).path != "/api/patients":
            self.send_payload(404, {"error": "Not found."})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            patient_id = int(data.get("id"))
            age = int(data.get("age"))
        except (ValueError, TypeError):
            self.send_payload(400, {"error": "ID and age must be valid numbers."})
            return
        name = str(data.get("name", "")).strip()
        diagnosis = str(data.get("diagnosis", "")).strip()
        if patient_id <= 0 or not name or not diagnosis or not 0 <= age <= 120:
            self.send_payload(400, {"error": "Fill in every field with valid values."})
            return
        with lock:
            created = registry.insert(patient_id, name, age, diagnosis)
        if not created:
            self.send_payload(409, {"error": "Patient ID " + str(patient_id) + " already exists."})
            return
        self.send_payload(201, {"ok": True})

    def do_DELETE(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "patients"]:
            self.send_payload(404, {"error": "Not found."})
            return
        try:
            patient_id = int(parts[2])
        except ValueError:
            self.send_payload(400, {"error": "Patient ID must be a number."})
            return
        with lock:
            removed = registry.delete(patient_id)
        if not removed:
            self.send_payload(404, {"error": "Patient " + str(patient_id) + " is not registered."})
            return
        self.send_payload(200, {"ok": True})


def main():
    server = ThreadingHTTPServer((HOST, PORT), RegistryHandler)
    url = "http://" + HOST + ":" + str(PORT)
    print("Hospital Patient Registry running at " + url)
    print("Press Ctrl+C to stop.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
