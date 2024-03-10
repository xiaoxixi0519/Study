import os
# 注意放大查看图片的功能还没做
import pytz
import requests

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from werkzeug.exceptions import BadRequest

import oss2  # 导入阿里云OSS SDK

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

HOSTNAME = "127.0.0.1"
PORT = 3306
USERNAME = "root"
PASSWORD = "123456"
DATABASE = "yiyang"

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

db = SQLAlchemy(app)

access_key_id = 'LTAI5t7ESqGvfY2dWL1QParn'
access_key_secret = 'QVCUejyvokL7rCdAeDFvGxE5TqDfBu'

# 填写自己的 Bucket 名称和上传地址
bucket_name = 'my-yi-yang'
upload_path = 'pictures/'

# 创建 OSS 链接
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, 'http://oss-cn-shanghai.aliyuncs.com', bucket_name)


# 测试是否连接成功
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))
#         print(rs.fetchone())  # (1,)

# # 创建User类
# class User(db.Model):
#     # 创建user表
#     __tablename__ = "user"
#     # 增加表中字段
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # varchar, null=0
#     username = db.Column(db.String(100), nullable=False)
#     password = db.Column(db.String(100), nullable=False)


class Request(db.Model):
    __tablename__ = 'request'
    requestID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(255))
    serviceType = db.Column(db.String(255), nullable=False)
    actName = db.Column(db.String(255))
    recNumbers = db.Column(db.Integer)
    dateStart = db.Column(db.Date)
    timeStart = db.Column(db.Time)
    dateEnd = db.Column(db.Date)
    timeEnd = db.Column(db.Time)
    region = db.Column(db.String(255))
    location = db.Column(db.String(255))
    demPhone = db.Column(db.String(255))
    pay = db.Column(db.Float)
    comName = db.Column(db.String(255))
    comPhone = db.Column(db.String(255))
    relName = db.Column(db.String(255))
    relPhone = db.Column(db.String(255))
    actSupport = db.Column(db.String(255))
    request = db.Column(db.String(255))
    details = db.Column(db.String(255))
    updateTime = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Shanghai')))

    def to_dict(self):
        return {
            'serviceType': self.serviceType,
            'actName': self.actName,
            'recNumbers': self.recNumbers,
            'dateStart': self.dateStart.strftime('%Y-%m-%d'),
            'timeStart': self.timeStart.strftime('%H:%M:%S'),
            'dateEnd': self.dateStart.strftime('%Y-%m-%d'),
            'timeEnd': self.timeStart.strftime('%H:%M:%S'),
            'region': self.region,
            'location': self.location,
            'demPhone': self.demPhone,
            'pay': self.pay,
            'comName': self.comName,
            'comPhone': self.comPhone,
            'relName': self.relName,
            'relPhone': self.relPhone,
            'actSupport': self.actSupport,
            'request': self.request,
            'details': self.details,
            'updateTime': self.updateTime.strftime('%Y-%m-%d %H:%M:%S'),
        }


class Picture(db.Model):
    __tablename__ = 'pic'
    picID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(255))
    requestID = db.Column(db.Integer)
    picPath = db.Column(db.String(2048))
    usage = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'user'
    # userID = db.Column(db.Integer, primary_key=True, nullable=False)
    userID = db.Column(db.String(255), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(255))
    sex = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    identification = db.Column(db.String(255))
    birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    postcode = db.Column(db.String(255))
    region = db.Column(db.String(255))
    specialInfo = db.Column(db.String(255))
    demander = db.Column(db.Integer)
    receiver = db.Column(db.Integer)

    def __init__(self, name):
        self.userID = str(uuid.uuid4())
        self.name = name

    # default=datetime.now, onupdate=datetime.now


# user = User (username="法外狂徒张三",password='111111'
# sql: insert user(username,password) values('法外狂徒张三'，'111111');

with app.app_context():
    db.create_all()


@app.route('/select/part', methods=['POST'])
def select_part():
    if request.method == 'POST':
        data = request.get_json()
        service_type = data.get('currentServiceType')
        print(service_type)
        # 假设你想根据serviceType查询数据库中的相关记录
        requests = Request.query.filter_by(serviceType=service_type).all()
        print(requests)
        # 将查询结果转换为字典列表
        # results = [r.to_dict() for r in requests]
        results = [
            {
                'requestID': r.requestID,
                'userID': r.userID,
                **r.to_dict()
            } for r in requests
        ]
        print(results)
    # 假设您已经有了 results 列表
    final_results = []  # 创建一个新的列表来存储最终结果

    for result in results:
        # 根据requestID查询pic表中的所有图片
        pics = Picture.query.filter_by(requestID=result['requestID']).all()
        # 提取图片的URL或其他标识符
        images = [pic.picPath for pic in pics]
        print(images)

        # 将图片信息添加到当前结果字典中
        result_with_images = {**result, 'image': images}
        # 将带有图片信息的结果字典添加到最终结果列表中
        final_results.append(result_with_images)

    print(final_results)
    return jsonify(final_results)


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('nickName')

        if not name:
            raise BadRequest('Name is required.')

        # Check if a user with the same name already exists
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            # Return a response indicating the user already exists, but don't raise an error
            return jsonify({'message': 'User with this name already exists'}), 200

        # Create new user if name is unique
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'userID': str(new_user.userID), 'name': new_user.name}), 201
    except BadRequest as e:
        db.session.rollback()
        return jsonify({'error': str(e.description)}), 400
    except Exception as e:
        db.session.rollback()
        print(e)  # Print exception information for debugging
        return jsonify({'error': 'Something went wrong'}), 500


@app.route('/login', methods=['POST'])
def login():
    # 微信小程序的 AppID 和 AppSecret
    app_id = 'wxba2a7cb8dd5be653'
    app_secret = 'da4b0a4a7d27bdd00ad9aa9916767a37'

    # 从请求中获取 code
    code = request.json.get('code')
    name = request.get('nickName')
    print(code)
    if not code:
        return jsonify({'error': 'Missing code'}), 400
    # 向微信服务器发送请求以获取 openId 和 sessionKey
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={code}&grant_type=authorization_code'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to get user info from WeChat server'}), 500
    data = response.json()
    if 'errcode' in data:
        return jsonify({'error': data['errmsg']}), 400
    open_id = data['openid']
    session_key = data['session_key']
    # 查找或创建用户
    user_info = get_or_create_user(open_id)
    print(user_info)
    # 返回用户信息
    return jsonify({
        'userInfo': {
            '_id': user_info.userID,
            'nickName': user_info.name
        },
        'openid': open_id
    })


def get_or_create_user(open_id):
    user = User.query.filter_by(userID=open_id).first()
    if not user:
        user = User(name='Default Name')  # 使用默认名称或其他逻辑创建用户
        user.userID = open_id
        db.session.add(user)
        db.session.commit()
    return user


@app.route('/request/upload', methods=['POST'])
def upload_image():
    file = request.files.get('file')
    if file:
        filename = secure_filename(file.filename)
        oss_path = 'pictures/' + filename
        # 假设你已经创建并配置了bucket对象
        bucket.put_object(oss_path, file.stream)
        image_url = f"http://{bucket_name}.oss-cn-shanghai.aliyuncs.com/{oss_path}"
        return jsonify({'url': image_url}), 200
    else:
        return jsonify({'error': 'No file uploaded'}), 400

    #     # 创建Pic实例并保存图片URL到数据库
    #     new_pic = Picture(picPath=image_url)
    #     db.session.add(new_pic)
    #     try:
    #         db.session.commit()
    #         return jsonify({'url': image_url}), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({'error': str(e)}), 500
    #
    # return jsonify({'error': 'No file uploaded'}), 400


@app.route('/request/submit', methods=['POST'])
def submit_request():
    if request.method == 'POST':
        data = request.get_json()
        new_request = Request(
            serviceType=data.get('currentServiceType') or None,
            actName=data.get('actName') or None,
            recNumbers=data.get('recNumbers') or None,
            dateStart=data.get('dateStart') or None,
            timeStart=data.get('timeStart') or None,
            dateEnd=data.get('dateEnd') or None,
            timeEnd=data.get('timeEnd') or None,
            region=','.join(data.get('region')) if data.get('region') else None,
            location=data.get('location') or None,
            demPhone=data.get('demPhone') or None,
            pay=data.get('pay') or None,
            comName=data.get('comName') or None,
            comPhone=data.get('comPhone') or None,
            relName=data.get('relName') or None,
            relPhone=data.get('relPhone') or None,
            actSupport=','.join(data.get('actSupport')) if data.get('actSupport') else None,
            request=data.get('request') or None,
            details=data.get('details') or None,
            updateTime=datetime.now(pytz.timezone('Asia/Shanghai'))
        )

        db.session.add(new_request)
        db.session.flush()
        print('flush')
        pic_urls = data.get('pics', [])
        print(pic_urls)
        for url in pic_urls:
            new_pic = Picture(picPath=url, requestID=new_request.requestID)
            db.session.add(new_pic)

        try:
            print("commit successful")
            db.session.commit()
            print("requestID: " + str(new_request.requestID))
            return jsonify({'message': '提交成功', 'requestId': new_request.requestID}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        # try:
        #     db.session.commit()
        #     print("commit successful")
        # except Exception as e:
        #     db.session.rollback()
        #     print(e)  # 或使用更详细的日志记录方法
        #     return jsonify({'error': str(e)}), 500
        #
        # print("requestID: " + str(new_request.requestID))
        # return jsonify({'message': '提交成功', 'requestId': new_request.requestID}), 200


@app.route('/request/details/<int:request_id>', methods=['GET'])
def get_request_details(request_id):
    request = Request.query.get(request_id)
    if request:
        # 假设Request模型有一个to_dict方法将对象转换为字典
        return jsonify(request.to_dict()), 200
    else:
        return jsonify({'error': 'Request not found'}), 404


#
# @app.route('/user/add')
# def add_user(uname,pword):
#     # 1.创建ORM对象
#     user = User(username=uname, password=pword)
#     # 2．将ORM对象添加到db.session中
#     db.session.add(user)
#     # 3．将db.session中的改变同步到数据库中
#     db.session.commit()
#     return "用户创建成功!"
#
#
# @app.route('/user/query')
# def query_user():
#     # 1. get查找:根据主键查找
#     # user = User.query.get(1)
#     # print(f"{user.id} : {user.username}-{user.password}")
#     # 2.filter_by查找
#     # Query:类数组
#     # users = User.query.filter_by(username="法外狂徒张三")
#     # for user in users:
#     #     print(user.username)
#     # return "数据查找成功!"
#
#     users = db.session.query(User).all()
#     data = []
#     for user in users:
#         data.append({
#             'id': user.id,
#             'username': user.username,
#             'password': user.password
#         })
#     return json.dumps(data, ensure_ascii=False)
#
#
# @app.route('/user/update')
# # def update_user():
# #     user = User.query.filter_by(username="法外狂徒张三").first()
# #     user.password = "222222"
# #     db.session.commit()
# #     return "数据修改成功!"
#
# def update_user(uname,pword):
#     user = User.query.filter_by(username=uname).first()
#     print("sfd=")
#     user.password = pword
#     print("ok")
#     db.session.commit()
#     return "数据修改成功!"
#
#
# @app.route('/user/delete')
# def delete_user(uname,pword):
#     # 1，查找
#     user = User.query.filter_by(username=uname,password=pword).first()
#     # 2.从db.session中删除
#     db.session.delete(user)
#     # 3．将db.session中的修改，同步到数据库中
#     db.session.commit()
#     return "数据删除成功!"
#
# # def delete_user():
# #     # 1，查找
# #     user = User.query.filter_by(username="小美").first()
# #     # 2.从db.session中删除
# #     db.session.delete(user)
# #     # 3．将db.session中的修改，同步到数据库中
# #     db.session.commit()
# #     return "数据删除成功!"
#
#     #删除多行
#     # users = User.query.filter(User.username == '小李').all()
#     # for user in users:
#     #     db.session.delete(user)
#     #     db.session.commit()
#
#
# @app.route('/user/score',methods=['POST'])
# def score():
#     # p_goodsname = json.loads(request.values.get("goodsname"))
#     p_goodsname = request.values.get("goodsname")
#     p_goodpword = request.values.get("goodpword")
#     print(p_goodsname)
#     print(p_goodpword)
#     way=request.values.get("way")
#     print(way)
#
#     if (way == '0'):
#         print("0000")
#         add_user(p_goodsname,p_goodpword)
#
#     elif (way == '1'):
#         print("adfsd")
#         update_user(p_goodsname,p_goodpword)
#
#     elif (way == '2'):
#         delete_user(p_goodsname,p_goodpword)
#
#     return json.dumps(p_goodsname, ensure_ascii=False)  # aftersort为需要回传的数据

if __name__ == '__main__':
    app.run(debug=True, port=5000)
