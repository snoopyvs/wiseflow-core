from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Ini adalah route utama yang akan menampilkan halaman dashboard/map
    return render_template('index.html')

if __name__ == '__main__':
    # Menjalankan server Flask dalam mode debug
    app.run(debug=True, port=5000)
