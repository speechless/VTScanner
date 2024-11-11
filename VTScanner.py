import requests
from colorama import Fore,init,deinit
from http import HTTPStatus
import click
from bs4 import BeautifulSoup as bs

allURLs = []
toDoURLs = []
toDoNext=[]

@click.command()
@click.option('-u',required=True,type=str,help="URL of the target")
@click.option('-d',required=False,type=int,default=2,show_default=True, help='Depth of getting a page through another.')
@click.option('-r',required=False,is_flag=True, default=False,show_default=True,help='Allow requests to follow redirects.')
@click.option('-o',required=False,is_flag=True, default=False,show_default=True,help='Allow requests to change of website during scanning.')

def main(u,r,d,o):
    """
    Sends multiple HTTP requests to help detection of Verb Tampering.

    Checks if there are other pages on this page and do the same.

    Some methods like TRACE or CONNECT are not tested here.
    """
    #Variables
    url=u
    redirects=r
    depth=d
    outside=o

    sendRequests(url,redirects)
    getLinksPage(url,toDoURLs)
    for i in range(depth):
        analyzer(url,redirects,outside)
    
#To get depth
def analyzer(url,redirects,outside):
    for u in toDoURLs:
        if u[0]=='/' or (u[:7]!='http://' and u[:8]!='https://'):
            if u[0]=='/':
                updatedURL=url+u[1:]
            else:
                updatedURL=url+u
            sendRequests(updatedURL,redirects)
            getLinksPage(updatedURL,toDoNext)
        elif outside == True:
            sendRequests(u,redirects)
            getLinksPage(u,toDoNext) 
    toDoURLs.clear()
    for i in toDoNext:
        toDoURLs.append(i)
    toDoNext.clear()

#get href(s) of the page
def getLinksPage(url,tab):
    page = requests.get(url)
    parser = bs(page.content, 'html.parser')
    hrefs= parser.find_all('a',href=True)

    for i in hrefs:
        link=i['href']
        if link not in ['/','',' ','#']:
            if link not in allURLs : 
                allURLs.append(link)
                tab.append(link)

#Verb Tampering
def sendRequests(url,F_allow_redirects):
    Reqs=[]
    order=["GET","POST","PUT","DELETE","HEAD","OPTIONS"]
    Reqs.append(requests.get(url,allow_redirects=F_allow_redirects))
    Reqs.append(requests.post(url,allow_redirects=F_allow_redirects))
    Reqs.append(requests.put(url,allow_redirects=F_allow_redirects))
    Reqs.append(requests.delete(url,allow_redirects=F_allow_redirects))
    Reqs.append(requests.head(url,allow_redirects=F_allow_redirects))
    Reqs.append(requests.options(url,allow_redirects=F_allow_redirects))

    print("URL : "+url)
    
    for r in range(len(Reqs)) :
        status_code = Reqs[r].status_code
        status_enum = HTTPStatus(status_code)
        status_name = status_enum.name
        init(autoreset=True)
        if status_enum.is_informational :
            print(Fore.WHITE+order[r]+" "+str(Reqs[r].status_code)+" - "+status_name)
        elif status_enum.is_success :
            print(Fore.GREEN+order[r]+" "+str(Reqs[r].status_code)+" - "+status_name)
        elif status_enum.is_redirection :
            print(Fore.YELLOW+order[r]+" "+str(Reqs[r].status_code)+" - "+status_name)
        elif status_enum.is_client_error :
            print(Fore.RED+order[r]+" "+str(Reqs[r].status_code)+" - "+status_name)
        elif status_enum.is_server_error :
            print(Fore.MAGENTA+order[r]+" "+str(Reqs[r].status_code)+" - "+status_name)
        else:
            print(Fore.BLUE+order[r]+" "+Reqs[r].status_code)
        deinit()
    print()
    

if __name__ == '__main__':
    main()





