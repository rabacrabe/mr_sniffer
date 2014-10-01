import urllib2
from lxml import etree
import lxml.html as lh
import os
import shutil
import sys
from PyQt4.QtCore import *

class Html_Images_Proxy(object):
    ""
    
    def __init__(self):
        ""
    
    def stealStuff(self, file_path,file_mode,url):
        from urllib2 import Request, urlopen, URLError, HTTPError
        
        #create the url and the request
        
        req = Request(url)
        print(url)
        # Open the url
        try:
            f = urlopen(req)
            
            # Open our local file for writing
            local_file = open(file_path, "w" + file_mode)
            #Write to our local file
            local_file.write(f.read())
            local_file.close()
            
        #handle errors
        except HTTPError, e:
            print("[HTTP Error] :",e.code , url)
        except URLError, e:
            print("[URL Error] :",e.reason , url)

    def _get_and_save_img(self, new_name, img_url):
        ""
        
        try:
            src = urllib2.urlopen(img_url)
        except urllib2.HTTPError, e:
            print("[ERREUR] : {0}".format(e))
            pass
        else:
            dst = open(new_name, 'w');
            shutil.copyfileobj(src, dst)
    
    def _get_image_path_from_page(self, chapter_num, page_num):
        ""
        #if len(page_num) == 1:
        #    page_num = "0{0}".format(page_num)
        #return "{0}/{1}/{2}.jpg".format("http://www.lecture-en-ligne.com/images/mangas/{0}".format(m_tab_name.get(manga_number, None)), chapter_num.split(" ")[-1], page_num)
       
        return None
    
    def import_image_from_page(self, url_page, page_number, output_folder):
        doc=lh.parse(urllib2.urlopen(url_page))
        
        for img in doc.iter('img'):
            attr = img.attrib
            if attr.has_key("id"):
                if attr.get("id") == "img":
                    url_img = attr.get("src")
                    if url_img != "":
                        new_name = "{0}.jpg".format(page_number)
                        #self._get_and_save_img(new_name, url_img)
        

class MangaReader_Proxy(object):
    def __init__(self):
        ""
        self.addr_base = "http://www.mangareader.net"
        self.serie_name = ""
        self.map_serie_link = {}
        self.map_chapter_link = {}
        self.imgproxy = Html_Images_Proxy()
        
    def setProgressBar(self, progress):
        self.progressbar = progress

    def _update_bar(self, value):
        ""
        print value
        self.progressbar.setValue(value)
    
    def import_images_from_chapters(self, list_chapters, output_folder):
        by_chapter = 100 / len(list_chapters)
        for chapter_name in list_chapters:
            print("[INFO] : Recuperation du chapitre '{0}'".format(chapter_name))
            
            try:
                
                chapter_addr = "{0}{1}".format(self.addr_base, self.map_chapter_link.get(chapter_name))
                pages_map_addr = self._get_chapter_pages(chapter_addr)
                
                print("[INFO] : il y a {0} pages dans le chapitre '{1}'".format(len(pages_map_addr), chapter_name))
                
                if len(pages_map_addr) > 0:
                    by_page = by_chapter / len(pages_map_addr)
                    newrep_chapter = os.path.join(output_folder, self.serie_name, chapter_name.replace(":", "-"))
                    if not os.path.exists(newrep_chapter):
                        os.makedirs(newrep_chapter, 0755)
                    print("[INFO] : Creation du repertoire '{0}'".format(newrep_chapter))
                    i = 0
                    compteur = 0
                    for titre, addr in pages_map_addr.iteritems():
                        i +=1
                        url_page = "{0}{1}".format(self.addr_base, addr)
                        self.imgproxy.import_image_from_page(url_page, titre, newrep_chapter)
                        print("[INFO] : Recuperation de la page '{0}' ({1}/{2})".format(titre, i, len(pages_map_addr)))
                        compteur+=by_page
                        self._update_bar(compteur)
                    return 0
            except Exception,e :
                print("[ERREUR] : Lors de la recuperation des images du chapitre {0}".format(chapter_name))
                print("[ERREUR] : {0}".format(e))
            
    def _get_chapter_pages(self, chapter_addr):
        
        try:
            page_url = "{0}".format(chapter_addr)
            doc=lh.parse(urllib2.urlopen(page_url))
            
            chapter_pages_list = {}
            for select in doc.iter('div'):
                attr = select.attrib
                if attr.has_key("id"):
                    if attr.get("id") == "selectpage":
                        pages = select.findall("select/option")
                        for page in pages:
                            page_attr = page.attrib
                            if page_attr.has_key("value"):
                                url_page = page_attr.get("value")
                                titre_page = page.text_content()
                                num_page = titre_page
                                chapter_pages_list[num_page] = url_page
            
            
            return chapter_pages_list
        except Exception, e:
            print("[ERREUR] : lors de la recuperation des pages du chapitre")
            print("[ERREUR] : {0}".format(e))
    
    def get_serie_details(self,titre_serie):
        map_details = {}
       
        addr_url = "{0}{1}".format(self.addr_base, self.map_serie_link.get(titre_serie))
        self.serie_name = titre_serie
        try:
            doc=lh.parse(urllib2.urlopen(addr_url))
            for div in doc.iter('div'):
                attr = div.attrib
                if attr.has_key("id"):
                    if attr.get("id") == "mangaproperties":
                        #print(etree.tostring(div, pretty_print=True))
                        for tr in div.findall("table/tr"):
                            td = tr.find("td")
                            td_attr = td.attrib
                            if td_attr.has_key("class"):
                                if td_attr.get("class") == "propertytitle":
                                    property_name = td.text
                                    
                                    td_2 = td.getnext()
                                    property_value = td_2.text
                                    
                                    map_details[property_name] = property_value
        except Exception, e:
            print("[ERREUR] : lors de la recuperation des details de la serie")
            print("[ERREUR] : {0}".format(e))    
        return map_details
    
    def get_list_series(self):
        list_series = []
        
        addr_url = "{0}/{1}".format(self.addr_base, "alphabetical")
        
        try:
        
            doc=lh.parse(urllib2.urlopen(addr_url))
            for select in doc.iter('div'):
                attr = select.attrib
                if attr.has_key("class"):
                    if attr.get("class") == "series_alpha":
                        titre_categorie = select.find("h2/a").text_content()
                        
                        children = select.findall("ul/li")
                        for child in children:
                            child_link = child.find("a")
                            child_link_attr = child_link.attrib
                            if child_link_attr.has_key("href"):
                                addr_serie = child_link_attr.get("href")
                                titre_serie = child_link.text_content()
                                if titre_serie != "" and addr_serie != "":
                                    self.map_serie_link[titre_serie] = addr_serie
                                    list_series.append(titre_serie)
                                else:
                                    print("[EREUR] : Probleme avec le recuperation de la serie: {0} ({1})".format(titre_serie, addr_serie))
        except Exception, e:
            print("[ERREUR] : lors de la recuperation de la liste des series disponibles")
            print("[ERREUR] : {0}".format(e))
        return list_series
    
    def get_chapters_list(self, titre_serie):
        list_chapter = []
       
        addr_url = "{0}{1}".format(self.addr_base, self.map_serie_link.get(titre_serie))
        self.serie_name = titre_serie
        try:
            doc=lh.parse(urllib2.urlopen(addr_url))
            for select in doc.iter('div'):
                attr = select.attrib
                if attr.has_key("id"):
                    if attr.get("id") == "chapterlist":
        
                        for td in select.iterfind("table/tr/td"):
        
                            link_chapter = td.find("a")
                            if link_chapter is not None:
                                link_chapter_attr = link_chapter.attrib
                                if link_chapter_attr.has_key("href"):
                                    addr_chapter = link_chapter_attr.get("href")
                                    titre_chapter = td.text_content()
                                    
                                    if titre_chapter != "" and addr_chapter != "":
                                        self.map_chapter_link[titre_chapter.replace('\n','')] = addr_chapter
                                        list_chapter.append(titre_chapter.replace('\n',''))
                
            return list_chapter
        except Exception, e:
            print("[ERREUR] : lors de la recuperation des chapitre disponible pour la serie '{0}'".format(titre_serie))
            print("[ERREUR] : {0}".format(e))
    
    