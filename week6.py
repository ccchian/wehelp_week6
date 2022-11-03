from flask import Flask,request,render_template,redirect,session,url_for
import mysql.connector

app = Flask(__name__,
    static_folder="static",
    static_url_path="/")

#設定 session 密鑰
app.secret_key='ThisIsAKey'

# mysql.connector 引入方式
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345678",
  database="test"
)
# index.route -> index.html
@app.route('/')
def index():
    return render_template("index.html")

#index.html -> signup.route
@app.route('/signup',methods=['POST'])
def signup():
    #取得物件，連到member
    #拿取form中叫做xxx的值，但是使用get可以避免字典型態form找不到key時發生錯誤。
    name = request.form['name']
    user = request.form.get('username')
    pwd = request.form.get('password')
    
    #execute()-執行  rowcount()-資料筆數 commit()-提交資料到資料庫
    mycursor = mydb.cursor()
    sql='SELECT username, password FROM member WHERE username = %(user)s'
    mycursor.execute(sql,{"user":user} )
    myresult = mycursor.fetchall() 
    # for x in myresult:     
    if (mycursor.rowcount > 0) :
        return redirect("http://127.0.0.1:3000/error?message=帳號已經被註冊")
    else:
        mycursor = mydb.cursor()
        sql='INSERT INTO member(name, username, password) VALUES(%s, %s, %s)'
        val=(name, user, pwd)
        mycursor.execute(sql,val)
        mydb.commit()
        return redirect('/')

#註冊後回首頁 #index.html -> signin.route
@app.route('/signin', methods =['POST'])
def signin():
    user = request.form['username']
    pwd = request.form['password']
    #紀錄使用者
    session["username"]= user
    session["password"]= pwd

    mycursor = mydb.cursor()
    sql='SELECT name, username, password FROM member WHERE username = %s and password = %s' 
    mycursor.execute(sql,(user,pwd))
    myresult = mycursor.fetchall()
    if  mycursor.rowcount>0 and myresult[0][1] == user and myresult[0][2] == pwd:
        name = request.args.get("name","")
        session['name'] = myresult[0][0]
        #使用者紀錄保持登入狀態
        session['enter'] = 'loginIng'
        return redirect(url_for("member")) 
    else:        
        return redirect("http://127.0.0.1:3000/error?message=帳號、或密碼輸入錯誤") 

#signin.route -> member.route
@app.route('/member')
def member():
    #假設使用者紀錄保持登入狀況，會導向前端，取出name值
    if "loginIng" == session['enter']:
        name = session['name'] 
        return render_template("member.html",name = name)
    else:
    #沒有使用者紀錄，回到首頁
        return redirect('/')
    

@app.route('/error')
def error():
    data = request.args.get('message',"")
    return render_template("error.html", data = data)
    
@app.route('/signout',)
def signout():
     session['enter'] = 'close'
     return redirect('/')


if __name__ == "__main__":
    app.run(port=3000,debug=True)

