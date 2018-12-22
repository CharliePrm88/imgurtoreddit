from flask import Flask, abort, request, flash, redirect, url_for, render_template
import requests,requests.auth, urllib, json, os
from base64 import b64encode
from werkzeug.utils import secure_filename

CLIENT_ID = "19BlIR44gVazLw" # Reddit ID
CLIENT_SECRET = "VqJTL4uJE4ysw22m-GLv8wQQ1U8" # Reddit Secret ID
REDIRECT_URI = "http://localhost:5000/IMGURtoRedditApp" #Reddit redirect dopo oAuth2
USER_AGENT = {"User-Agent": "RC2018"} #Reddit vuole che sia incorporato altrimenti ti blocca
IMGUR_CLIENT_ID = 'Client-ID 9833ef015fd6205' #imgur ID
UPLOAD_FOLDER = 'UPLOAD_FOLDER' #cartella di upload del file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) #estensioni utilizzabili su IMGUR
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def homepage():
    return render_template("home.html",make_authorization_url=make_authorization_url()) #renderizza la relativa pagina nella cartella templates 

def make_authorization_url(): #prepara il link di autorizzazione (Usato nella homepage)
    params = {"client_id": CLIENT_ID,
              "response_type": "code",
              "state": "abcdefg", 
              "redirect_uri": REDIRECT_URI, #se non corrisponde a quello dichiarato nella console di reddit non funziona
              "duration": "temporary", #per lo scope (leggi dopo) utilizzato (postare link su reddit) l'utente può concedere l'accesso per massimo un'ora
              "scope": "submit"}
    url = "https://ssl.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)
    return url


def allowed_file(filename): #questa funzione verifica che il file è della estensione corretta
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/IMGURtoRedditApp', methods=['GET','POST'])
def IMGURtoRedditApp():
    if request.method == 'GET':
        return render_template("IMGURtoRedditApp.html")

    #POST
    if request.method == 'POST':
        error = request.args.get('error', '')#se c'è un errore nel link per qualche motivo.....
        if error:
            return "Error: " + error #ritorna errore con il tipo dell'errore
        access_token = request.args.get('access_token','')
        if not access_token:
            code = request.args.get('code') #altrimenti prendi il codice dal link e richiedi il token
            access_token = get_token(code)
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
            linkIMGUR = sendToIMGURAPI(path) #invio il file su imgur
            if os.path.exists(path): #verifico che il file esiste nella cartella di UPLOAD 
                os.remove(path)      #quindi essendo appena stato inviato, lo elimino mantenendo pulito il server
            risposta = submit_link(access_token, title, subreddit, linkIMGUR) #infine invio il link su reddit!
            return redirect(url_for('ok', access_token=access_token)) #let's party!
        else: #i campi sono tutti required, questo else funziona solo con l'accesso via CURL nel caso l'utente dimentica di inserire qualcosa
            return redirect(url_for('errore', access_token=access_token))

def get_token(code): #prendo il token
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET) #compongo il link
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = USER_AGENT
    response = requests.request('POST',"https://ssl.reddit.com/api/v1/access_token", 
                             auth=client_auth,
                             headers=headers,
                             data=post_data) #lo invio
    token_json = json.loads(response.text) #recupero il token dalla risposta in json
    return token_json['access_token'] 

def sendToIMGURAPI(photo): #questa funzione invia la foto sul servizio IMGUR
    urlImgur = 'https://api.imgur.com/3/image' #compongo il link
    payloadImgur = {'image': b64encode(open(photo, 'rb').read()) }
    files = {}
    headersImgur = {
  'Authorization': IMGUR_CLIENT_ID
    }
    responseImgur = requests.request('POST', urlImgur, headers = headersImgur, data = payloadImgur, files = files, allow_redirects=False) #lo invio
    data = json.loads(responseImgur.text) #trasformo la stringa in un oggetto json
    urlFoto = data['data']['link'] #recupero il link della foto da pubblicare su reddit
    return urlFoto
    
def submit_link(access_token, title, subreddit, url ): #questa funzione invia un link su reddit a un prescelto subreddit
    header = USER_AGENT
    header.update({"Authorization": "bearer " + access_token})
    data = {"title": title, "url":url, "sr": subreddit, "kind":"link", "api_type": "json"}
    response = requests.request('POST', "https://oauth.reddit.com/api/submit", data=data, headers=header)
    print(response.text)#dovrebbe stampare la risposta del server sulla console
    return response.text

@app.route("/Errore")
def errore():
    return render_template("errore.html")

@app.route("/ok")
def ok():
    return render_template("ok.html")
 
#pagina deprecata: per l'accesso via CURL usare -F esempio: curl -X POST -F "Title=test" -F "Subreddit=test" -F "file=@nome-del-File.jpg" http://127.0.0.1:5000/IMGURtoRedditApp dopo aver fatto oauth
#@app.route("/APIpost", methods=['POST'])
#def apiPost():
#   file = request.files['myimage']
#   if file and allowed_file(file.filename):
#       file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#   return "Saved file: "+ file.filename + "Campo Utente" + request.values.get('text')
 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
