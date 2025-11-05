# app.py
# Flask-SocketIO realtime chat board with irreversible delete
# Run: python app.py

from flask import Flask, request, g, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import sqlite3
from datetime import datetime
import os

DB_PATH = "chat.db"

app = Flask(__name__)
# set secret key from env if available
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecret')
socketio = SocketIO(app, cors_allowed_origins="*")

# --- DB ---
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    db.commit()
    db.close()


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# --- HTML ---
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Shared Board</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
  <style>
    body {font-family: system-ui, sans-serif; background:#f7fafc; margin:0; padding:0;}
    .container {max-width:800px; margin:30px auto; background:white; padding:16px; border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.1);}
    h1 {margin-bottom:10px;}
    #messages {border:1px solid #ddd; border-radius:6px; padding:8px; height:60vh; overflow:auto;}
    .msg {padding:8px; border-bottom:1px solid #f0f0f0; position:relative;}
    .meta {font-size:12px; color:#777;}
    button.delete {position:absolute; top:8px; right:8px; background:#ef4444; border:none; color:white; padding:4px 8px; border-radius:4px; cursor:pointer;}
    button.delete:hover {background:#dc2626;}
    form {display:flex; margin-top:10px; gap:8px;}
    input[type=text] {flex:1; padding:10px; border-radius:6px; border:1px solid #ccc;}
    button {padding:10px 14px; background:#2563eb; color:white; border:none; border-radius:6px;}
  </style>
</head>
<body>
  <div class="container">
    <h1>Shared Message Board</h1>
    <div id="messages"></div>

    <form id="form" onsubmit="return false;">
      <input id="text" placeholder="Nhập tin nhắn...">
      <button id="send">Gửi</button>
    </form>
  </div>

<script>
const socket = io();

function escapeHtml(s){
  return s.replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function addMessage(msg){
  const box = document.getElementById('messages');
  const div = document.createElement('div');
  div.className='msg';
  div.id = 'msg-'+msg.id;
  const date = new Date(msg.created_at).toLocaleString();
  div.innerHTML = `
    <div class="meta">${date}</div>
    <div>${escapeHtml(msg.text)}</div>
    <button class="delete" onclick="deleteMessage(${msg.id})">Xóa</button>
  `;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function deleteMessage(id){
  if (!confirm("Bạn có chắc muốn xóa tin nhắn này không? Hành động không thể hoàn tác.")) return;
  fetch('/messages/'+id, {method:'DELETE'}).then(r=>{
    if(!r.ok) alert("Không thể xóa.");
  });
}

// tải lịch sử
fetch('/messages').then(r=>r.json()).then(list=>{
  list.forEach(addMessage);
});

// realtime
socket.on('new_message', msg=>addMessage(msg));
socket.on('delete_message', data=>{
  const el = document.getElementById('msg-'+data.id);
  if (el) el.remove();
});

// gửi
document.getElementById('send').onclick = ()=>{
  const text = document.getElementById('text').value.trim();
  if(!text) return;
  socket.emit('send_message', {text});
  document.getElementById('text').value='';
};
</script>
</body>
</html>
"""

# --- Routes ---
@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/messages", methods=["GET"])
def get_messages():
    db = get_db()
    rows = db.execute("SELECT * FROM messages ORDER BY id ASC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/messages/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
    db.commit()
    # thông báo cho tất cả client xoá
    socketio.emit("delete_message", {"id": msg_id}, broadcast=True)
    return "", 204

# --- SocketIO ---
@socketio.on('send_message')
def send_message(data):
    text = data.get("text", "").strip()
    if not text: return
    now = datetime.utcnow().isoformat() + "Z"
    db = get_db()
    cur = db.execute("INSERT INTO messages (text, created_at) VALUES (?,?)",(text,now))
    db.commit()
    msg = {"id":cur.lastrowid,"text":text,"created_at":now}
    emit("new_message", msg, broadcast=True)

if __name__ == "__main__":
    if not os.path.exists(DB_PATH): init_db()
    print("Server running on 0.0.0.0:8080")
    socketio.run(app, host="0.0.0.0", port=8080)

