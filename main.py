from flask import Flask, abort, request, flash, redirect, url_for
import requests,requests.auth, urllib, json, os
from base64 import b64encode
from werkzeug.utils import secure_filename
 
CLIENT_ID = "19BlIR44gVazLw" # Reddit ID
CLIENT_SECRET = "VqJTL4uJE4ysw22m-GLv8wQQ1U8" # Reddit Secret ID
REDIRECT_URI = "http://localhost:5000/IMGURtoRedditApp" #Reddit redirect dopo oAuth2
USER_AGENT = {"User-Agent": "RC2018"} #Reddit vuole che sia incorporato altrimenti ti blocca
IMGUR_CLIENT_ID = 'Client-ID 9833ef015fd6205'
UPLOAD_FOLDER = '/home/charlie/Scrivania/KM/UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
@app.route('/')
def homepage():
    text = 'Per prima cosa, <a href="%s">Autenticati via Reddit</a>'
    return text % make_authorization_url()
 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
def make_authorization_url():
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": "abcdefg",
              "redirect_uri": REDIRECT_URI, #se non corrisponde a quello dichiarato nella console di reddit non funziona
              "duration": "temporary",
              "scope": "submit"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
    return url
 
@app.route('/IMGURtoRedditApp', methods=['GET','POST'])
def reddit_callback():
    if request.method == 'GET':
        error = request.args.get('error', '')
        if error:
            return "Error: " + error
        code = request.args.get('code')
        global access_token
        access_token = get_token(code)
        return '''
  <!doctype html>
  <title>IMGUR to Reddit App</title>
  <body>
  <h1>IMGUR to Reddit App</h1>
  <form method=post enctype=multipart/form-data>
    Titolo del post: <input type=text name=Title required><br>
    Subreddit: <input type=text name=Subreddit required><br>
    File Da Inviare: <input type=file name=file required><br>
    <input type=submit value=Invia>
  </form>
  </body>
  '''
 
    #POST
    if request.method == 'POST':
        # controlla se il file è del tipo ammesso
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('errore')) # se non lo è fa il redirect sulla pagina di errore
        file = request.files['file']
        title = request.form['Title']
        subreddit = request.form['Subreddit']
        # sono tutti required però un occchiatina in più non fa male...inoltre verifico che il file è del tipo giusto
        if title and subreddit and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = app.config['UPLOAD_FOLDER'] + '/' + filename
            linkIMGUR = sendToIMGURAPI(path) #imvio il file su imgur
            if os.path.exists(path): #verifico che il file esiste nella cartella di UPLOAD
                os.remove(path)      #quindi essendo appena stato inviato, lo elimino mantenendo pulito il server
            risposta = submit_link(access_token, title, subreddit, linkIMGUR) #infine invio il link su reddit!
            return redirect(url_for('ok')) #let's party!
        else: #i campi sono tutti required, questo else funziona solo con l'accesso via CURL nel caso l'utente dimentica di inserire qualcosa
            return redirect(url_for('errore'))
 
def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = USER_AGENT
    response = requests.request('POST',"https://ssl.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             headers=headers,
                             data=post_data)
    token_json = json.loads(response.text)
    print(token_json)
    return token_json['access_token']
   
def submit_link(access_token, title, subreddit, url ):
    header = USER_AGENT
    header.update({"Authorization": "bearer " + access_token})
    data = {"title": title, "url":url, "sr": subreddit, "kind":"link", "api_type": "json"}
    response = requests.request('POST', "https://oauth.reddit.com/api/submit", data=data, headers=header)
    print(response.text)#dovrebbe stampare la risposta del server sulla console
    return response.text
 
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
   <h3>Ricorda: non è possibile inviare su reddit due post nell'arco di 10 minuti</h3>
  </body>'''
 
def sendToIMGURAPI(photo):
    urlImgur = 'https://api.imgur.com/3/image'
    payloadImgur = {'image': b64encode(open(photo, 'rb').read()) }
    files = {}
    headersImgur = {
  'Authorization': IMGUR_CLIENT_ID
    }
    responseImgur = requests.request('POST', urlImgur, headers = headersImgur, data = payloadImgur, files = files, allow_redirects=False)
    data = json.loads(responseImgur.text)
    urlFoto = data['data']['link']
    return urlFoto
 
#pagina deprecata: per l'accesso via CURL usare -F esempio: curl -X POST -F "Title=test" -F "Subreddit=test" -F "file=@nome-del-File.jpg" http://127.0.0.1:5000/IMGURtoRedditApp dopo aver fatto oauth
#@app.route("/APIpost", methods=['POST'])
#def apiPost():
#   file = request.files['myimage']
#   if file and allowed_file(file.filename):
#       file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#   return "Saved file: "+ file.filename + "Campo Utente" + request.values.get('text')
 
 
if __name__ == '__main__':
    app.run(debug=True, port=5000)
