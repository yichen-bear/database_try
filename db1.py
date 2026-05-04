from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

DB_NAME = "menu.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        description TEXT,
        available INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    conn.close()

# 取得資料庫連線
def get_db():
    return sqlite3.connect(DB_NAME)

# API：取得所有菜單
@app.route("/api/menu", methods=["GET"])
def get_menu():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    rows = cursor.fetchall()
    conn.close()

    menu = []
    for row in rows:
        menu.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": row[3],
            "description": row[4],
            "available": row[5]
        })

    return jsonify(menu)

# API：新增菜單
@app.route("/api/menu", methods=["POST"])
def add_item():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO menu (name, category, price, description)
    VALUES (?, ?, ?, ?)
    """, (data["name"], data["category"], data["price"], data["description"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "新增成功"})

# API：刪除
@app.route("/api/menu/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "刪除成功"})

# 前端頁面
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>嘿嘿嘿</title>
</head>
<body>
    <h1>🍜 菜單管理</h1>

    <h2>新增菜色</h2>
    名稱: <input id="name"><br>
    分類: <input id="category"><br>
    價格: <input id="price" type="number"><br>
    描述: <input id="description"><br>
    <button onclick="addItem()">新增</button>

    <h2>菜單列表</h2>
    <ul id="menu"></ul>

<script>
async function loadMenu() {
    const res = await fetch('/api/menu');
    const data = await res.json();

    const menu = document.getElementById('menu');
    menu.innerHTML = "";

    data.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `${item.name} (${item.category}) - $${item.price}
        <button onclick="deleteItem(${item.id})">刪除</button>`;
        menu.appendChild(li);
    });
}

async function addItem() {
    const name = document.getElementById('name').value;
    const category = document.getElementById('category').value;
    const price = document.getElementById('price').value;
    const description = document.getElementById('description').value;

    await fetch('/api/menu', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, category, price, description })
    });

    loadMenu();
}

async function deleteItem(id) {
    await fetch('/api/menu/' + id, { method: 'DELETE' });
    loadMenu();
}

loadMenu();
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# 啟動
if __name__ == "__main__":
    init_db()
    app.run(debug=True)