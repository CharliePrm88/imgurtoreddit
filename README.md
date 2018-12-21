# imgurtoreddit
Progetto Reti Di Calcolatori 2018

IMGUR to Reddit App
Questa applicazione permette l'invio di immagini sul servizio <a href=https://apidocs.imgur.com/>Imgur</a> (API n°1) ed il successivo repost del link su <a href=https://www.reddit.com/dev/api> reddit</a> (API n2 con oAuth2 - entrambi i siti sono commerciali)!
reddit (si scrive tutto minuscolo!) è un sito di social news che permette l'invio ed il commento da parte degli utenti di link.
Generalmente quando il link è una foto, gli utenti si appoggiano al servizio Imgur per postare la foto, reperire il link e pubblicarlo sul prescelto subreddit (le sezioni di reddit). Con questa app, la magia avviene tutta automaticamente!
 
Il codice è scritto in Python3 con l'ausilio di <a href=http://flask.pocoo.org/>Flask</a> un web microframework che permette la creazione di webserver tramite l'utilizzo di decoratori.
 
ISTRUZIONI:
1. Scaricare l'intera repository
2. installare flask:
    su Windows: dopo aver installato python3 (>=3.4) con la utility pip, aprire un prompt in modalità amministratore e scrivere
                pip install flask (Attenzione: se sullo stesso pc è installato anche python2 potrebbero andare in conflitto, si rimanda
                alla documentazione ufficiale)
    su Debian-based Distro (Debian, Ubuntu, Mint etc): sudo apt-get install python3-flask
    su Arch-linux: sudo pacman -S python3-flask
3. inserire la proprio chiave reddit, la propria chiave segreta reddit, la propria chiave Imgur nel file main.py
4. avviare da terminale (prompt dei comandi su windows): python3 main.py (python main.py su windows)
5. collegarsi al link fornito dal server (default: 127.0.0.1:5000)
 
PROCEDURA:
<ol>
<li>Per iniziare fai il login su reddit tramite il link fornito dal server</li>
<li>compila il form</li>
<li>clicca su invia</li>
 </ol>
semplice e pulito! Dopo alcuni secondi (dipende dalla grandezza della foto e dalla potenza della tua linea in upload) troverai la foto pubblicata sul tuo profilo reddit.
 
ATTENZIONE:
<ol><li>reddit è molto severo nel permettere l'accesso da parte di app di terze parti. Non puoi pubblicare più di una foto ogni 10 minuti (probabilmente per evitare la creazione di spam bot)</li>
<li>reddit raccomanda (you Must - che più che raccomanda si traduce in "lo devi fare") l'utilizzo del subreddit "test" per effettuare appunto dei test. Pertanto se utilizzi quest'app per scopi didattici, per piacere rispetta la regola!</li>
 </ol>
 
Il codice è quasi totalmente commentato, ma se ci fosse il bisogno di ulteriori chiarimenti, scriveteci!
Testato su Ubuntu Mate 18.04, Arch Linux e Windows 10.
