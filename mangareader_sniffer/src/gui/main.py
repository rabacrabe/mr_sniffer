# -*- coding: utf8 -*-
'''
Created on 17 sept. 2014

@author: gtheurillat
'''


from PyQt4 import QtGui, QtCore
import sys, os
from src.controller.mr_proxy import MangaReader_Proxy




class Main_Gui(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow,self).__init__()
        self.setWindowTitle(u"MagaReader Sniffer")
        
        window_icon = QtGui.QIcon("images/icon.ico") 
        self.setWindowIcon(window_icon) 
        
        self.mr_proxy = MangaReader_Proxy() 
        
        
        myQWidget = QtGui.QWidget()
        self.myMainBoxLayout = QtGui.QVBoxLayout()
        
        self.create_series_selections_part()
        
        myQWidget.setLayout(self.myMainBoxLayout)
        self.setCentralWidget(myQWidget)
#         myBoxLayout = QtGui.QHBoxLayout()
#         self.myBoxLayoutNomsG = QtGui.QVBoxLayout()
#         self.myBoxLayoutNomsD = QtGui.QVBoxLayout()
#         myQWidget.setLayout(myBoxLayout)
#         self.setCentralWidget(myQWidget)

        
       
#         self.listPhotos = DropPhotosList()
#         self.del_etiquette = False
#        
#         #on cree le menu
#         self.createMenu()
#        
#         #on rempli les donnee
#         #mapPhotos = self.get_photosMap()
#         #self.fillin_data(mapPhotos)
#         
#         
#         
#         
#         self.listPhotos.setIconSize(QtCore.QSize(200, 150))
#         self.listPhotos.setFlow(QtGui.QListView.LeftToRight)
#         self.listPhotos.setWrapping(True)
#         self.listPhotos.setResizeMode(QtGui.QListView.Adjust);
#         #self.listPhotos.setTextElideMode(QtCore.Qt.ElideMiddle);
#         self.listPhotos.setViewMode(QtGui.QListView.IconMode)
#         self.listPhotos.setAcceptDrops(True)
# #         self.setMovement(QtGui.QListView.Static);
#         font = QtGui.QFont('SansSerif', 15)
#         
#         font.setBold(True)
# 
#         self.listPhotos.setFont(font)
#         
#         self.listPhotos.setLayoutD(self.myBoxLayoutNomsD)
#         self.listPhotos.setLayoutG(self.myBoxLayoutNomsG)
#         self.listPhotos.setMode(self.del_etiquette)
#         self.listPhotos.setStyleSheet("background:#34277D;")
#         
#         
#         
#         myBoxLayout.addLayout(self.myBoxLayoutNomsG)      
#         myBoxLayout.addWidget(self.listPhotos)
#         myBoxLayout.addLayout(self.myBoxLayoutNomsD)     


        #myMainBoxLayout.addLayout(myBoxLayout)

    def create_series_selections_part(self):
        ""
        seriesLayoutPart = QtGui.QHBoxLayout()
        
        label_serie = QtGui.QLabel()
        label_serie.setText(u"Series")
        seriesLayoutPart.addWidget(label_serie)
        
        self.listLetters = QtGui.QComboBox()
        self._create_list_serie_alpha()
        seriesLayoutPart.addWidget(self.listLetters)
        
        self.listSerie = QtGui.QComboBox()
        seriesLayoutPart.addWidget(self.listSerie)
        
        showDetailsButton = QtGui.QPushButton()
        showDetailsButton.setText("Show serie chapters")
        showDetailsButton.clicked.connect(self._show_serie_details)
        seriesLayoutPart.addWidget(showDetailsButton)
        
        self.myMainBoxLayout.addLayout(seriesLayoutPart)
    
    def _create_list_serie_alpha(self):
        ""
        alphas = ["-- ALL --", "#","+","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    
        list_alpha = QtCore.QStringList()
        for alpha in alphas:
            list_alpha.append(alpha)
        self.listLetters.insertItems(0, list_alpha)
        
        self.connect(self.listLetters, QtCore.SIGNAL('activated(QString)'), self.combo_chosen)
 
    def combo_chosen(self, text):
        """
        Handler called when a distro is chosen from the combo box
        """
        self._recup_list_serie_by_alpha(text)
    
    def _recup_list_serie_by_alpha(self, alpha):
        ""
        list_items = QtCore.QStringList()
        for item in self.listLetters:
            if item[0] == alpha or alpha == "-- ALL --":
                list_items.append(item)
                
        self.listSerie.clear()
        self.listSerie.insertItems(0, list_items)
        self.listSerie.installEventFilter(self)
 
    def _show_serie_details(self):
        #fname = QFileDialog.getExistingDirectory(self, 'Select input file')
        serie_selected = self.ui.listSerie.currentText() 
        if serie_selected != "":
            print "[INFO] : Recuperation des chapitres de la serie '{0}'".format(serie_selected)
            model = QtGui.QStandardItemModel()
            list_chapters = self.mr_proxy.get_chapters_list(str(serie_selected))
            print "[INFO] : {0} chapitres sont disponibles pour cette serie.".format(len(list_chapters))
            for chapter in list_chapters:
                newItem = QtGui.QListWidgetItem(chapter.replace('\n',''))
                newItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                newItem.setCheckState(QtCore.Qt.Unchecked)
                self.ui.listChapters2.addItem(newItem)
        else:
            print "[WARNING] Veuillez selectionner une serie!"
 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog_1 = Main_Gui()
    dialog_1.show()
    dialog_1.resize(480,320)
    sys.exit(app.exec_())
