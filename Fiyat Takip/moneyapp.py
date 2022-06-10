import mysql.connector
import os, platform, subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from types import BuiltinMethodType
import requests
import smtplib
import time
from bs4 import BeautifulSoup
default_url = "https://www.hepsiburada.com/hous-mobilya-tokyo-acik-ceviz-renk-raf-tasarim-ahsap-kitaplik-p-HBCV000003BHF4"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}
def fiyat_kontrol():
    ##DB bağlantımızı yapıyoruz
    db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="projedb"
      )
    ##tüm linkleri ve diğer doneleri çekiyoruz
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM urunler")
    urunler = cur.fetchall()
    for i in urunler:
        id_db = str(i[0])
        link_db = str(i[1])
        fiyat1_db = str(i[2])
        fiyat2_db = str(i[3])
        fiyat3_db = str(i[4])
        msj_db = str(i[5])

        
        print (link_db)
        check_price(link_db)
    db_connection.commit()


def check_price(url):
    page = requests.get(url,headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find(id='product-name').get_text().strip()
    print(f'Ürünün Adı: {title}')
    span = soup.find(id='offering-price')
    content = span.attrs.get('content')
    price = float(content)
    print(f'Ürünün Fiyatı: {price}')
    
    db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="projedb"
      )
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM urunler where link='"+str(url)+"'") ## ilgili url'deki bilgileri çekiyoruz
    urunler = cur.fetchall()
    db_connection.commit()

    
    fiyat1 = float(urunler[0][2])
    fiyat2 = float(urunler[0][3])
    fiyat3 = float(urunler[0][4])
    msj = str(urunler[0][5])
    bot_token = 'Telegram Bot Token'
    bot_chatID = 'Telegram ID'

    if price==0:
        print("Ürün Satıştan Kaldırılmış...\n",str(url))
    else:
        if fiyat1==0:
            
            db_cursor = db_connection.cursor()
            test_sorgu = "UPDATE urunler SET fiyat1='"+str(price)+"' where link ='"+str(url)+"'"        ## yeni eklenmiş ürüne fiyatını yazdıralım
              
            db_cursor.execute(test_sorgu)
            send_text = 'https://api.telegram.org/bot'+bot_token+'/sendMessage?chat_id='+bot_chatID+'&parse_mode=Markdown&text=Yeni Ürün takibi Başladı\n'+str(url)
            response = requests.get(send_text)
        if round(float(fiyat1),2) != round(float(price),2):
            db_cursor = db_connection.cursor()
            test_sorgu = "UPDATE urunler SET fiyat1='"+str(price)+"' where link ='"+str(url)+"'"        ## fiyat takibine giren ürünün güncel fiyat karşılaştırması eşit değilse fiyat2 ye yazdıralım ve msj gönderelim
          
            db_cursor.execute(test_sorgu)
            
            send_text = 'https://api.telegram.org/bot'+bot_token+'/sendMessage?chat_id='+bot_chatID+'&parse_mode=Markdown&text=Ürün Fiyatında Değişiklik Var\n'+str(url)+'\nÜrün Fiyatı: '+str(price)
            response = requests.get(send_text)

    db_connection.commit()

def send_mail(title):
    sender = 'emreemir352935@gmail.com'
    receiver = 'emreemir353529@gmail.com'
    try:
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.ehlo()
        server.starttls()
        server.login(sender, 'cdzaqxrqawzokbgy')
        subject = title + 'istedigin fiyata dustu'
        body = 'Bu linkten gidebilirsin ->' + url
        mailContent = f'To:{receiver}\n From:{sender}\nSubject:{subject}\n\n{body}'
        server.sendmail(sender,receiver,mailContent)
        print('Mail Gönderildi.')
    except smtplib.SMTPException as e:
        print(e)
    finally:
        server.quit()
     
while(1):
     fiyat_kontrol()

     time.sleep(10)
