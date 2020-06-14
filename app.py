from flask import Flask
from flask_restful import Api, Resource, reqparse
from bs4 import BeautifulSoup
import requests
import urllib.request
import json

app = Flask(__name__)
api = Api(app)

baseURL="https://animegun.hu/"
titleList=[]
titleInfos=[]

def cat(catName):
    URL=baseURL+"category/"+catName+"/page/"+str(1);
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    pageNum=str(soup.findAll('a',class_='page-numbers')).split(',')
    db=1
    for y in pageNum:
        if y.find("<a class=\"page-numbers\"") != -1:
            db+=1
    i=1
    my_json_stringList=[]
    while i <=db:
        URL=baseURL+"category/"+catName+"/page/"+str(i);
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        divContent = soup.findAll('div',class_='columns postbox')
        for x in divContent:
            title=x.find('a')["title"]
            titleURL=x.find('a')["href"]
            titlePic=x.find('img')["src"]
            my_json_stringList.append(json.dumps({
                'cim ':title,
                'anime urlje ': titleURL,
                'anime icon ': titlePic
            }))
        i+=1
    return my_json_stringList

def titlePage(nameUrl):
    response = requests.get("https://animegun.hu/"+nameUrl)
    soup=BeautifulSoup(response.text,"html.parser")
    title=str(soup.find('h1')).replace('<h1 class=\"entry-title\">','').replace('</h1>','')
    info=str(soup.findAll('td',class_='right')).replace(',','\n').replace('<td class=\"right\">','').replace('</td>','').replace('<em>','').replace('</em>','').replace('<b>','').replace('</b>','').replace('<strong>','').replace('</strong>','').replace('[','').replace(']','').split('\n')
    contentRAW=list(filter(None, str(response.text).replace('<table>',';').replace('<tbody>',';').replace('<tr>',';').replace('<td>',';').replace('</table>',';').replace('</tbody>',';').replace('</tr>',';').replace('</td>',';').split(';')))
    i=0
    description=""
    while i<len(contentRAW):
        if "<strong>Ismertető:</strong>" in contentRAW[i]:
              description=contentRAW[i+1]
              break
        i+=1
    temp=str(soup.findAll('a')).replace(',', '\n').split('\n')
    links=[]
    for x in temp:
        if "wordpress" in x:
            break
        if "<a data-wpel-link=\"external\" href=" in x:
            link=x.replace('<a data-wpel-link=\"external\" href=\"','').replace(' rel=\"external noopener noreferrer\" target=\"_blank\">','').replace(' ','').split('\"')
            links.append(link[0])
    return {'Cim:': title, 'Eredet cim' : info[0], 'Angol cim' : info[1], 'Egyeb cimek': info[2], 'tipus' : info[3]+"-"+info[4], 'hossz': info[5], 'datum' :info[6],'Ismerteto': description, 'linkek': links }


def search(searchText):
    URL=baseURL+"?s="+searchText;
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    if "Ilyen Anime nincs Kohai" in soup:
        return "Ilyen Anime nincs Kohai"
    else:
        pageNum=str(soup.findAll('a',class_='page-numbers')).split(',')
        db=1
        for y in pageNum:
            if y.find("<a class=\"page-numbers\"") != -1:
                db+=1
        i=1
        my_json_stringList=[]
        while i <=db:
            URL=baseURL+"page/"+str(i)+"?s="+searchText;
            response = requests.get(URL)
            soup = BeautifulSoup(response.text, "html.parser")
            divContent = soup.findAll('div',class_='columns postbox')
            for x in divContent:
                if x.find('a')['href']!=baseURL+"hibajelentes/":
                    title=x.find('a')["title"]
                    titleURL=x.find('a')["href"]
                    titlePic=x.find('img')["src"]
                    my_json_stringList.append(json.dumps({
                            'cim ':title,
                            'anime urlje ': titleURL,
                            'anime icon ': titlePic
                        }))
            i+=1
        return my_json_stringList

class AnimeGun(Resource):
    def get(self,reqType='',startLetter='',animePageInfo='',searchText=''):
        if reqType == "search":
            return search(searchText), 200
        if reqType == "StartLetter":
            return cat(startLetter), 200
        if reqType == "AnimeInfoPage":
            return titlePage(animePageInfo), 200
        return "Hiba valamit beneztel Senpai", 404

api.add_resource(AnimeGun, "/animegun/<string:reqType>&&<string:startLetter>&&<string:animePageInfo>&&<string:searchText>")
if __name__ == '__main__':
    app.run(debug=True)