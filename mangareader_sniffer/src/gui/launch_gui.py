'''
Created on 30 juil. 2013

@author: gtheurillat
'''


import sys, time, locale, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from src.gui.gui import Ui_GroupBox
from threading import Thread
from time import sleep
from src.controller.mr_proxy import MangaReader_Proxy

class MyStream(object):
    
    def __init__(self, logText):
        ""
        self.myLogText = logText
        
        
    
    def write(self, text):
        # Add text to a QTextEdit...
        self.myLogText.appendPlainText(text)
        #QCoreApplication.processEvents
    
class EmittingStream(QObject):

    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class ConvertionYDP_GUI(QGroupBox):
    ""
    def __init__(self, parent=None):
        ""
        super (ConvertionYDP_GUI, self).__init__(parent)
        
        self.mr_proxy = MangaReader_Proxy() 
        self.createWidget()
        
        #self.ui.verticalLayout_2.setm
        
        self.param_data = {}
        self.msgBox = None
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
    
    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
    
    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.ui.logText.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.ui.logText.setTextCursor(cursor)
        self.ui.logText.ensureCursorVisible()
    
    def createWidget(self):
        ""
        self.ui = Ui_GroupBox()
        self.ui.setupUi(self)
        
       
        self.ui.listChapters2.setSelectionMode(QAbstractItemView.MultiSelection)
        
        #set des slot pour les boutons
        self.ui.showDetailsButton.clicked.connect(self._show_serie_details)
        self.ui.outputButton.clicked.connect(self._browse_outputfolder)
        self.ui.runButton.clicked.connect(self._start_generation)
        
        self._create_list_serie_alpha()
        self._recup_list_series()
        
        self.connect(self.ui.select_unselectChapters, SIGNAL('stateChanged(int)'), self._onSelectUnselectChapters)
        self.connect(self.ui.logText, SIGNAL('textChanged()'), self._onUpdateLog)
        self.connect(self.ui.progressBar, SIGNAL('valueChanged(int)'), self._update_bar);

        
        self.ui.outputText.setAcceptDrops(True);
        self.ui.outputText.installEventFilter(self)
        
        #rediection de la sortie standard vers un inputtext de log
        self.ui.logText.setReadOnly(True)
        self.ui.logText.clear()
        
        #sys.stdout = MyStream(self.ui.logText)
        #sys.stderr = MyStream(self.ui.logText) 
    
    def _update_bar(self, value):
        ""
        print value
        self.progressbar.setValue(value)
    
    def _onUpdateLog(self):
        ""
        QApplication.processEvents
        
    
    def _create_list_serie_alpha(self):
        ""
        alphas = ["-- ALL --", "#","+","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    
        list_alpha = QStringList()
        for alpha in alphas:
            list_alpha.append(alpha)
        self.ui.listLetters.insertItems(0, list_alpha)
        
        self.connect(self.ui.listLetters, SIGNAL('activated(QString)'), self.combo_chosen)

    def _onSelectUnselectChapters(self, state):
        ""
        
        
        

    def combo_chosen(self, text):
        """
        Handler called when a distro is chosen from the combo box
        """
        self._recup_list_serie_by_alpha(text)
    
    def _recup_list_serie_by_alpha(self, alpha):
        ""
        list_items = QStringList()
        for item in self.list:
            if item[0] == alpha or alpha == "-- ALL --":
                list_items.append(item)
                
        self.ui.listSerie.clear()
        self.ui.listSerie.insertItems(0, list_items)
        self.ui.listSerie.installEventFilter(self)
        
    
    def _recup_list_series(self):
        ""
        self.list = self.mr_proxy.get_list_series()
        list_items = QStringList()
        for item in self.list:
            list_items.append(item)
        self.ui.listSerie.insertItems(0, list_items)
    
    def thread_progressbar(self):
        ""
        value = 0
        while self.res == -255:
            if value >= 100:
                value = 0
            self._update_bar(value)
            value += 25
            sleep(0.25)
        

    def eventFilter(self, object, event):
        if (object is self.ui.outputText):
            if (event.type() == QEvent.DragEnter):
                if event.mimeData().hasUrls():
                    event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
                    print "accept"
                else:
                    event.ignore()
                    print "ignore"
            if (event.type() == QEvent.Drop):
                if event.mimeData().hasUrls():   # if file or link is dropped
                    urlcount = len(event.mimeData().urls())  # count number of drops
                    url = event.mimeData().urls()[0]   # get first url
                    object.setText(url.path()[1:])   # assign first url to editline
                    #event.accept()  # doesnt appear to be needed
            return False # lets the event continue to the edit
        return False


    def _show_serie_details(self):
        #fname = QFileDialog.getExistingDirectory(self, 'Select input file')
        serie_selected = self.ui.listSerie.currentText() 
        if serie_selected != "":
            print "[INFO] : Recuperation des chapitres de la serie '{0}'".format(serie_selected)
            model = QStandardItemModel()
            list_chapters = self.mr_proxy.get_chapters_list(str(serie_selected))
            print "[INFO] : {0} chapitres sont disponibles pour cette serie.".format(len(list_chapters))
            for chapter in list_chapters:
                newItem = QListWidgetItem(chapter.replace('\n',''))
                newItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                newItem.setCheckState(Qt.Unchecked)
                self.ui.listChapters2.addItem(newItem)
                
            map_serie_details = self.mr_proxy.get_serie_details(str(serie_selected))
            if len(map_serie_details) > 0:
                self.ui.serie_titre.setText(map_serie_details.get("Name", ""))
                self.ui.serie_titre_alternatif.setText(map_serie_details.get("Alternate Name:", ""))
                self.ui.serie_realease_year.setText(map_serie_details.get("Year of Release:", ""))
                #self.ui.serie_status.setText(map_serie_details.get("Status:", None))
                self.ui.serie_auteur.setText(map_serie_details.get("Author:", ""))
                self.ui.serie_reading_direction.setText(map_serie_details.get("Reading Direction:", ""))
                self.ui.serie_genre.setText(map_serie_details.get("Genre:", ""))
                self.ui.serie_artiste.setText(map_serie_details.get("Artist:", ""))
                
            
        else:
            print "[WARNING] Veuillez selectionner une serie!"
        
    def _browse_outputfolder(self):
        fname = QFileDialog.getExistingDirectory(self, 'Select output folder')
        if fname:
            self.ui.outputText.setText(fname)
            
    def _start_generation(self):
        outputext = self.ui.outputText.text()  
        
        chapters_selected = []
        for index in xrange(self.ui.listChapters2.count()):
            if self.ui.listChapters2.item(index).checkState() == Qt.Checked:
                chapters_selected.append(str(self.ui.listChapters2.item(index).text()))
            
        print chapters_selected
#        self._show_loader()
        #self._show_ok()
        #self._show_ko()
        #self._show_echec()
        if len(chapters_selected) > 0:
            if outputext != "" and outputext != None and os.path.exists(outputext):
                self.res = -255
                thread = Thread(target = self.thread_run, args = (chapters_selected, outputext))
                thread.start()
                
                #if self.res == 0:
                #    self._show_ok()
                #else:
                #    self._show_echec()
                
            else:
                print "[WARNING] Absence de repertoire de sortie ou mauvais repertoire"
        else:
            print "[WARNING] Aucune chapitre selectionne"
            
    def thread_run(self, chapters_selected, outputext):
        ""
        print "C'est parti pour la recuperation de {0} chapitre".format(len(chapters_selected))
        self.ui.progressBar.setValue(0)
        self.mr_proxy.setProgressBar(self.ui.progressBar)
        self.res = self.mr_proxy.import_images_from_chapters(chapters_selected, str(outputext))
        self.ui.progressBar.setValue(100)
        
    
    def _start_convertion(self, input_file, output_folder):
        ""
        
        if os.path.exists(input_file) and os.path.exists(output_folder):
            
            
            
            self.res = -255
            
            #on demarre le thread de la progressbar
            self._update_bar(0);
            #thread = Thread(target = self.thread_progressbar, args = ())
            #thread.start()
            
            
            #res = proxy.start()
            #for i in range(0,10):
            #    print "{0} / 10".format(i)
            #    sleep(2);
            
            #self.res = 0
            
            self.res = 0
            
            if self.res == 0:
                self._show_ok()
            elif self.res < 0:
                self._show_ko()
            elif self.res > 0:
                self._show_echec()
                
            self._update_bar(100);
        else:
            print "[ERREUR] Merci de verifier l'existance du fichiers xcel d'entree et du repertoire de sortie."
    
    def _update_bar(self, val):
        self.ui.progressBar.setValue(val)   
    
    
    def _show_loader(self):
        self.msgBox = QMessageBox(self)
        self.msgBox.setText("Exportation des notes en cours...");
        self.msgBox.setInformativeText("Merci de patienter");
        self.msgBox.setStandardButtons(QMessageBox.Cancel);
        
        icon = QPixmap("images/loader.jpg")
        self.msgBox.setIconPixmap(icon)
        self.msgBox.show()
         
    def _show_ko(self):
        self.msgBox = QMessageBox(self)
        self.msgBox.setText("L'exportation des notes a ECHOUEE");
        self.msgBox.setInformativeText("Veuillez consulter le fichier de log pour de plus ample informations");
        self.msgBox.setStandardButtons(QMessageBox.Ok);
        
        icon = QPixmap("images/KO.png")
        self.msgBox.setIconPixmap(icon)
        self.msgBox.show()
        
    def _show_ok(self):
        self.msgBox = QMessageBox(self)
        self.msgBox.setText("L'exportation des notes a ete un succes");
        self.msgBox.setInformativeText("Merci et a bientot");
        self.msgBox.setStandardButtons(QMessageBox.Ok);
        
        icon = QPixmap("images/OK.png")
        self.msgBox.setIconPixmap(icon)
        self.msgBox.show()
        
    def _show_echec(self):
        self.msgBox = QMessageBox(self)
        self.msgBox.setText("L'exportation des notes a ete un succes MAIS certains warnings sont apparus")
        self.msgBox.setStandardButtons(QMessageBox.Ok);
        
        icon = QPixmap("images/ECHEC.png")
        self.msgBox.setIconPixmap(icon)
        self.msgBox.show()
    
    
   
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = ConvertionYDP_GUI()
    myapp.show()
    sys.exit(app.exec_())