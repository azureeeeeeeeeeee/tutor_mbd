from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import jwt

# inisiasi aplikasi flask
app = Flask(__name__)

# konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'perpustakaan'

# inisiasi mysql
mysql = MySQL(app)


"""
POST -> Ngirim data (nambahin data baru di db)
GET -> ngambil data
PUT/PATCH -> update data yang udah ada
DELETE -> ngehapus data yang udah ada
"""





@app.route('/auth/register', methods=['POST'])
def register():
    # tabel user -> username, password
    data = request.json # ambil data dari request body
    print(data)

    username = data.get('username')
    password = data.get('password')

    # bikin procedure yang ada transaction
    """
        CREATE PROCEDURE register(
            IN username VARCHAR(255),
            IN password VARCHAR(255)
        )
        BEGIN
            START TRANSACTION;

            INSERT INTO users (username, password) VALUES (%s, %s);

            COMMIT;
        END
    """

    # query = "CALL register(%s, %s)"

    query = "INSERT INTO users (username, password) VALUES (%s, %s)"

    cursor = mysql.connection.cursor()
    
    cursor.execute(query, (username, password))
    mysql.connection.commit()

    cursor.close()

    return jsonify({'message': 'trest'})


"""
    - input username & password ke api
    - api bakal verifikasi username sama password yang kita input, sama nggak sama yang ada di db
    - kalo sama, generate jwt
    - kalo beda, kasih response 'kredential yang diinput beda sama yang ada di db'
"""
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json

    username = data.get('username')
    password = data.get('password')

    # SELECT col1, col2, col3 jangan SELECT *
    query = "SELECT id, username, password FROM users WHERE username = %s AND password = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, (username, password))

    user = cursor.fetchone()
    cursor.close()

    # []
    # print(user) -> [id, username, password]

    if not user:
        return jsonify({'message': 'User tidak ditemukan'})
    
    token = jwt.encode({'id': user[0]}, 'ijat_nt', algorithm='HS256')

    print(token)

    return jsonify({'message': 'login beryhasil', 'token': token})

"""
    /tambahbuku
    /hapusbuku
    /updatebuku

    /buku POST, DELETE, PUT/PATCH
"""

@app.route('/buku', methods=['POST'])
def books():
    data = request.json

    judul = data.get('judul')
    penulis = data.get('penulis')
    
    query = "INSERT INTO buku (judul, penulis) VALUES (%s, %s)"

    cursor = mysql.connection.cursor()
    cursor.execute(query, (judul, penulis))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': f'buku {judul} berhasil ditambahkan'})

# /buku/:id -> /buku/3 -> id: 3 
@app.route('/buku/<int:id>', methods=['DELETE', 'PUT'])
def book(id):
    if request.method == 'DELETE':
        query = "DELETE FROM buku WHERE id = %s"

        cursor = mysql.connection.cursor()
        cursor.execute(query, (id, ))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': f'Buku dengan id {id} berhasil dihapus'})

"""
    - taro token jwt di request body
    - decode jwt yang ada di request body untuk dapat informasi user
    - ngelakuin insert pake data id user
"""



# /pinjam/buku/5
"""
    "token": token
"""
@app.route('/pinjam/buku/<int:id>', methods=['POST'])
def pinjam(id):
    data = request.json

    token = data.get('token')
    user = jwt.decode(token, 'ijat_nt', algorithms=['HS256'])

    # print(user) -> {id: id_user}
    print(user)

    query = "INSERT INTO pinjam (id_user, id_buku) VALUES (%s, %s)"
    cursor = mysql.connection.cursor()
    cursor.execute(query, (user['id'], id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': 'peminjaman berhasil'})



if __name__ == '__main__':
    app.run(debug=True)

















# login -> token
# endpoint pembayaran -> kasih token di request body
# decode token untuk dapat informasi user (id user)