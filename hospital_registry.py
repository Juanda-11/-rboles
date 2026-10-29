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
  --navy: #253068;
  --blue: #5479fb;
  --orange: #ff7a45;
  --purple: #8e2391;
  --green: #00bfa5;
  --bg: #f6f8fc;
  --card: #ffffff;
  --line: #d7dcec;
  --text: #1f2547;
  --muted: #6b7399;
  --danger: #e53935;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
}
header {
  background: var(--navy);
  color: #fff;
  padding: 22px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
header h1 { margin: 0; font-size: 26px; }
header h1 span { color: var(--orange); }
header p { margin: 4px 0 0; color: #c5cdf5; font-size: 14px; }
.stats { display: flex; gap: 12px; flex-wrap: wrap; }
.stat {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 16px;
  min-width: 90px;
  text-align: center;
}
.stat b { display: block; font-size: 22px; }
.stat small { color: #c5cdf5; }
main {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  padding: 20px 32px 32px;
}
@media (max-width: 960px) {
  main { grid-template-columns: 1fr; padding: 16px; }
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px;
  margin-bottom: 16px;
  box-shadow: 0 4px 14px rgba(37, 48, 104, 0.06);
}
.card h2 {
  margin: 0 0 12px;
  font-size: 16px;
  color: var(--navy);
  border-left: 4px solid var(--orange);
  padding-left: 10px;
}
label { display: block; font-size: 12px; color: var(--muted); margin: 10px 0 4px; }
input, select {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text);
  background: #fff;
}
input:focus, select:focus { outline: 2px solid var(--blue); border-color: var(--blue); }
.row { display: flex; gap: 8px; }
.row > * { flex: 1; }
button {
  margin-top: 12px;
  padding: 10px 14px;
  border: 0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  background: var(--blue);
  width: 100%;
}
button:hover { filter: brightness(1.08); }
button.orange { background: var(--orange); }
button.purple { background: var(--purple); }
button.danger { background: var(--danger); }
button.green { background: var(--green); }
.toast {
  min-height: 22px;
  margin-top: 10px;
  font-size: 13px;
  font-weight: 600;
}
.toast.ok { color: #1b8f5a; }
.toast.error { color: var(--danger); }
.canvas {
  overflow: auto;
  background: #fbfcff;
  border: 1px dashed var(--line);
  border-radius: 12px;
  min-height: 380px;
}
.canvas svg { display: block; margin: 0 auto; }
.edge { stroke: #9aa5d6; stroke-width: 2; }
.edge.active { stroke: var(--orange); stroke-width: 3.5; }
.node circle {
  fill: #e6ecff;
  stroke: var(--blue);
  stroke-width: 2.5;
  cursor: pointer;
  transition: fill 0.2s;
}
.node.root circle { fill: #ffe4d6; stroke: var(--orange); }
.node.leaf circle { fill: #d6f7f0; stroke: var(--green); }
.node.active circle { fill: var(--orange); stroke: var(--navy); }
.node.found circle { fill: var(--green); stroke: var(--navy); }
.node text { font-size: 12px; font-weight: 700; fill: var(--navy); pointer-events: none; text-anchor: middle; }
.node.active text, .node.found text { fill: #fff; }
.legend { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 10px; font-size: 12px; color: var(--muted); }
.legend i { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; vertical-align: middle; border: 2px solid; }
.sequence { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; min-height: 34px; }
.chip {
  background: #e6ecff;
  color: var(--navy);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 600;
}
.chip.lit { background: var(--orange); color: #fff; }
.detail { font-size: 14px; line-height: 1.7; }
.detail b { color: var(--purple); }
.detail .empty { color: var(--muted); }
.traversals { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.traversals button { margin-top: 0; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Hospital <span>Patient Registry</span></h1>
    <p>Patients stored in a binary search tree and ordered by patient ID</p>
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
      <h2>Admit patient</h2>
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
      <h2>Search or discharge</h2>
      <label for="sid">Patient ID</label>
      <input id="sid" type="number" min="1" placeholder="e.g. 6050">
      <div class="row">
        <button id="searchBtn" class="orange">Search</button>
        <button id="deleteBtn" class="danger">Discharge</button>
      </div>
      <div id="toast" class="toast"></div>
    </section>
    <section class="card">
      <h2>Selected patient</h2>
      <div id="detail" class="detail"><span class="empty">Click a node or search an ID.</span></div>
    </section>
  </aside>
  <section>
    <div class="card">
      <h2>Registry tree</h2>
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
      <h2>Traversals</h2>
      <div class="traversals">
        <button class="purple" data-kind="in_order">In-order (sorted by ID)</button>
        <button class="purple" data-kind="pre_order">Pre-order</button>
        <button class="purple" data-kind="post_order">Post-order</button>
        <button class="purple" data-kind="level_order">Level-order (by depth)</button>
      </div>
      <div class="sequence" id="sequence"></div>
    </div>
  </section>
</main>
<script>
const NODE_RADIUS = 26;
const X_GAP = 70;
const Y_GAP = 90;
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
    canvas.innerHTML = '<p style="padding:24px;color:#6b7399">The registry is empty. Admit a patient to create the root.</p>';
    return;
  }
  const { nodes, count } = layout(state.tree);
  const edges = [];
  collectEdges(state.tree, edges);
  let maxDepth = 0;
  nodes.forEach((n) => { maxDepth = Math.max(maxDepth, Math.round((n.y - MARGIN) / Y_GAP)); });
  const width = MARGIN * 2 + Math.max(count - 1, 1) * X_GAP;
  const height = MARGIN * 2 + maxDepth * Y_GAP;
  const visitedSet = new Set(state.visited);
  let svg = '<svg width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '">';
  edges.forEach((e) => {
    const active = visitedSet.has(e.from.id) && visitedSet.has(e.to.id);
    svg += '<line class="edge' + (active ? " active" : "") + '" x1="' + e.from.x + '" y1="' + e.from.y + '" x2="' + e.to.x + '" y2="' + e.to.y + '"/>';
  });
  nodes.forEach((n) => {
    const classes = ["node"];
    if (n.id === state.tree.id) classes.push("root");
    else if (!n.left && !n.right) classes.push("leaf");
    if (visitedSet.has(n.id)) classes.push("active");
    if (state.found === n.id) classes.push("found");
    svg += '<g class="' + classes.join(" ") + '" data-id="' + n.id + '" transform="translate(' + n.x + "," + n.y + ')">';
    svg += '<circle r="' + NODE_RADIUS + '"/><text y="4">' + n.id + "</text></g>";
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
    "<b>ID:</b> " + patient.id + "<br><b>Name:</b> " + escapeHtml(patient.name) +
    "<br><b>Age:</b> " + patient.age + "<br><b>Diagnosis:</b> " + escapeHtml(patient.diagnosis) +
    (path ? "<br><b>Comparisons:</b> " + path.length + " (" + path.join(" &rarr; ") + ")" : "");
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
