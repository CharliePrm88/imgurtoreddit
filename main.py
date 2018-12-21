import os, requests,json
#from base64 import b64encode
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from base64 import b64encode
UPLOAD_FOLDER = '/home/charlie/Scrivania/KM/UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # controlla se il file è del tipo ammesso
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('errore')) # se non lo è fa il redirect sulla pagina di errore
        file = request.files['file']
        username = request.form['Username']
        password = request.form['Password']
        subreddit = request.form['Subreddit']
        # if user does not select file, browser also
        # submit an empty part without filename
        if username and password and subreddit and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #la riga seguente genera un errore - serve a passare da FileStorage a stringa
            linkIMGUR = sendToIMGURAPI(b64encode(file.read()))
            print(username)
            print(password)
            print(subreddit)
            print(linkIMGUR)
            return redirect(url_for('ok'))
        else: #i campi sono tutti required, questo else funziona solo con l'accesso via CURL nel caso l'utente dimentica di inserire qualcosa
            return redirect(url_for('errore'))
 
    #Se la chiamata è GET
    return '''
   <!doctype html>
   <title>IMGUR to Reddit App</title>
   <body>
   <h1>IMGUR to Reddit App</h1>
   <form method=post enctype=multipart/form-data>
     Username: <input type=text name=Username required><br>
     Password: <input type=password name=Password required><br>
     Subreddit: <input type=text name=Subreddit required><br>
     File Da Inviare: <input type=file name=file required><br>
     <input type=submit value=Invia>
   </form>
   </body>
   '''
 
@app.route("/Errore")
def errore():
    return '''<!doctype html>
   <title>IMGUR to Reddit App</title>
   <body>
   <h1>Errore!</h1>
   <p>Il file selezionato non è ammesso.<br>File ammessi: .png - .jpg - .jpeg - .gif<br>
   <a href="/">Ritorna alla pagina di upload</a>    
   </p>    
   </form>
   </body>
'''
@app.route("/ok")
def ok():
    return '''<!doctype html>
   <title>IMGUR to Reddit App</title>
   <body>
   <h1>File correttamente inviato</h1>
   <a href="/">Invia un altro file!</a>
   </body>'''
 
def sendToIMGURAPI(photo):
    urlImgur = 'https://api.imgur.com/3/image'
    payloadImgur = {'image': photo }
    files = {}
    headersImgur = {
  'Authorization': 'Client-ID 9833ef015fd6205'
    }
    responseImgur = requests.request('POST', urlImgur, headers = headersImgur, data = payloadImgur, files = files, allow_redirects=False)
    data = json.loads(responseImgur.text)
    print(data)
    urlFoto = data['data']['link']
    return urlFoto
 
#pagina deprecata: per l'accesso via CURL usare -F esempio: curl -X POST -F "Username=stefano" -F "Password=Lontra" -F "Subreddit=pics" -F "file=@ok.jpg" http://127.0.0.1:5000/
#@app.route("/APIpost", methods=['POST'])
#def apiPost():
#   file = request.files['myimage']
#   if file and allowed_file(file.filename):
#       file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#   return "Saved file: "+ file.filename + "Campo Utente" + request.values.get('text')
 
if __name__ == "__main__":
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.run(debug=True)
