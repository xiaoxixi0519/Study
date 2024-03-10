#
# from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# import mysql.connector
# from sqlalchemy.sql import text
# import io
#
# app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
#
# HOSTNAME = "127.0.0.1"
# PORT = 3306
# USERNAME = "root"
# PASSWORD = "123456"
# DATABASE = "photo"
#
#
# def save_image_to_database(name, data):
#     connection = mysql.connector.connect(
#         host='127.0.0.1',
#         user='root',
#         password='123456',
#         database='photo'
#     )
#
#     cursor = connection.cursor()
#     query = 'INSERT INTO images (name, data) VALUES (%s, %s)'
#     cursor.execute(query, (name, data))
#     connection.commit()
#
#     cursor.close()
#     connection.close()
#
#
# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     name = file.filename
#     data = file.read().getbuffer()  # 使用getbuffer()方法获取文件内容的二进制表示形式
#
#     save_image_to_database(name, data)
#
#     return jsonify({'message': 'Upload successful'})
#
#
# @app.route('/view/<int:image_id>', methods=['GET'])
# def view(image_id):
#     connection = mysql.connector.connect(
#         host='127.0.0.1',
#         user='root',
#         password='123456',
#         database='photo'
#     )
#
#     cursor = connection.cursor()
#     query = 'SELECT name, data FROM images WHERE id = %s'
#     cursor.execute(query, (image_id,))
#     result = cursor.fetchone()
#
#     if result is None:
#         return jsonify({'message': 'Image not found'})
#
#     name, data = result
#
#     cursor.close()
#     connection.close()
#
#     return jsonify({'name': name, 'data': data})
#
#
# if __name__ == '__main__':
#     app.run()


from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os

app = Flask(__name__)
CORS(app)

# MySQL数据库配置
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '123456',
    'db': 'photo',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 修改处理图片上传的 API
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # 获取上传的文件列表
        files = request.files.getlist('file')

        # 连接 MySQL 数据库
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            for file in files:
                # 读取文件内容
                file_content = file.read()

                # 将文件内容插入数据库
                cursor.execute("INSERT INTO images (image_data) VALUES (%s)", (file_content,))
                connection.commit()

        return jsonify({'status': 'success', 'message': 'Images uploaded successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})




# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_mysqldb import MySQL
# import os
# from werkzeug.utils import secure_filename
#
# app = Flask(__name__)
# CORS(app)
#
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'photo'
#
#
# mysql = MySQL(app)
#
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#
# def allowed_file(filename):
#     # 添加文件类型检查，确保上传的是图片
#     allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
#
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'})
#
#     file = request.files['file']
#
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'})
#
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)
#
#         # 在这里将文件路径保存到数据库中
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO images (path) VALUES (%s)", (file_path,))
#         mysql.connection.commit()
#         cur.close()
#
#         return jsonify({'message': 'File uploaded successfully'})
#
#
#


# 处理图片上传的API
# @app.route('/upload', methods=['POST'])
# def upload():
#     try:
#         # 获取上传的文件
#         file = request.files['file']
#
#         # 连接MySQL数据库
#         connection = pymysql.connect(**db_config)
#
#         with connection.cursor() as cursor:
#             # 读取文件内容
#             file_content = file.read()
#
#             # 将文件内容插入数据库
#             cursor.execute("INSERT INTO images (image_data) VALUES (%s)", (file_content,))
#             connection.commit()
#
#         return jsonify({'status': 'success', 'message': 'Image uploaded successfully'})
#
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
