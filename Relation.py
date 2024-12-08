import struct

from pageId import PageId
from Record import Record
from RecordId import RecordId


class Relation:

    def __init__(self, relationName, nbCollumn, colInfoList, tailleVar, bufferManager, headerPageId):
        self.relationName = relationName
        self.nbCollumn = nbCollumn
        self.col_info_list = colInfoList
        self.tailleVar = tailleVar
        self.bufferManager = bufferManager
        self.headerPageId = headerPageId

    def getNbCollumn(self):
        return self.nbCollumn

    def getCol_info_list(self):
        return self.col_info_list

    def getBufferManager(self):
        return self.bufferManager

    def getHeaderPageId(self):
        return self.headerPageId

    def writeRecordToBuffer(self, record, buff, pos):
        posRel = pos
        if not self.tailleVar:  # Mode fixe
            index = 0
            for col in self.col_info_list:
                match col.colType:
                    case "INT":
                        buff[posRel:posRel + 4] = struct.pack('i', record[index])
                        posRel += 4
                        index += 1
                    case "FLOAT":
                        buff[posRel:posRel + 4] = struct.pack('f', record[index])
                        posRel += 4
                        index += 1
                    case "CHAR(T)":
                        T = col.size  # On suppose que la taille T est définie dans col.size
                        value = record[index].ljust(T, '$')[:T]  # Remplir avec '$' si nécessaire
                        buff[posRel:posRel + T] = value.encode('utf-8')
                        posRel += T
                        index += 1
                    case "VARCHAR(T)":
                        T = col.size  # Taille maximale de VARCHAR
                        value = record[index][:T]  # Tronquer si la chaîne est plus grande que T
                        actual_length = len(value)
                        buff[posRel:posRel + 4] = struct.pack('i', actual_length)  # Longueur réelle
                        buff[posRel + 4:posRel + 4 + actual_length] = value.encode('utf-8')
                        posRel += 4 + actual_length
                        index += 1

            return posRel - pos

        else:  # Mode variable
            posRel1 = pos + self.nbCollumn * 4  # Position pour les valeurs des colonnes
            index = 0
            for col in self.col_info_list:
                match col.colType:
                    case "INT":
                        buff[posRel:posRel + 4] = struct.pack('i', 4)  # Taille de l'entier
                        buff[posRel1:posRel1 + 4] = struct.pack('i', record[index])
                        posRel += 4
                        posRel1 += 4
                        index += 1
                    case "FLOAT":
                        buff[posRel:posRel + 4] = struct.pack('i', 4)  # Taille du float
                        buff[posRel1:posRel1 + 4] = struct.pack('f', record[index])
                        posRel += 4
                        posRel1 += 4
                        index += 1
                    case "CHAR(T)":
                        T = col.size  # Taille maximale pour CHAR(T)
                        value = record[index].ljust(T, '$')[:T]  # Remplir avec '$' si nécessaire
                        buff[posRel:posRel + 4] = struct.pack('i', T)  # Taille fixe pour CHAR(T)
                        buff[posRel1:posRel1 + T] = value.encode('utf-8')
                        posRel += 4
                        posRel1 += T
                        index += 1
                    case "VARCHAR(T)":
                        T = col.size  # Taille maximale pour VARCHAR(T)
                        value = record[index][:T]  # Tronquer si nécessaire
                        actual_length = len(value)
                        buff[posRel:posRel + 4] = struct.pack('i', actual_length)  # Taille réelle
                        buff[posRel1:posRel1 + actual_length] = value.encode('utf-8')
                        posRel += 4
                        posRel1 += actual_length
                        index += 1

            return posRel1 - pos

def readFromBuffer(self, record, buff, pos):
    if self.tailleVar == False:
        posRel = pos
        index = 0
        for col in self.col_info_list:
            match col.colType:
                case "INT":
                    record[index] = struct.unpack('i', buff[posRel:posRel + 4])[0]
                    posRel += 4
                    index += 1
                case "FLOAT":
                    record[index] = struct.unpack('i', buff[posRel:posRel + 4])[0]
                    posRel += 4
                    index += 1
                case "CHAR(T)":
                    # il faut trouver un moyen de savoir la taille T du char
                    index += 1
                case "VARCHAR(T)":
                    # il faut trouver un moyen de savoir la taille T du char
                    index += 1

        return posRel - pos
    else:
        posRel = pos  # la on vas incrire les tailles des cols
        posRel1 = pos + self.nbCollumn * 4  # la c'est les valeurs des cols
        index = 0
        for col in self.col_info_list:
            match col.colType:
                case "INT":
                    record[index] = struct.unpack('i', buff[posRel1:posRel1 + 4])[0]
                    posRel += 4
                    posRel1 += 4
                    index += 1
                case "FLOAT":
                    record[index] = struct.unpack('i', buff[posRel1:posRel1 + 4])[0]
                    posRel += 4
                    posRel1 += 4
                    index += 1
                case "CHAR(T)":
                    taille = struct.unpack('i', buff[posRel:posRel + 4])[0]
                    text = struct.unpack(f'{taille}s', buff[posRel1:posRel1 + taille])[0]
                    for i in range(taille):
                        if text[i] != '$':
                            val = val + text[i]
                    record[index] = val
                    posRel += 4
                    posRel1 += posRel1 + taille
                    index += 1
                case "VARCHAR(T)":
                    taille = struct.unpack('i', buff[posRel:posRel + 4])[0]
                    record[index] = struct.unpack(f'{taille}s', buff[posRel1:posRel1 + taille])[0]
                    posRel += 4
                    posRel1 += posRel1 + taille
                    index += 1
        return posRel1 - pos

def addDataPage(self):
        bufferManager = self.bufferManager
        nb_octets_restant = bufferManager.disk_manager.getDBC().get_pageSize()
        nouvelle_page = bufferManager.disk_manager.AllocPage()

        headerPage = bufferManager.getPage(self.headerPageId)
        nb_pages = headerPage.read_int(0) or 0  # Si None, on initialise à 0
        nb_pages += 1
        headerPage.write_int(0, nb_pages)

        next_offset = 4 + (nb_pages - 1)*12

        # Écriture des informations sur la nouvelle page
        headerPage.write_int(next_offset, nouvelle_page.file_idx)
        headerPage.write_int(next_offset + 4, nouvelle_page.page_idx)
        headerPage.write_int(next_offset + 8, nb_octets_restant - 8)

        # Libération de la page d'en-tête
        bufferManager.free_page(self.header_page_id, flush=True)

        # Étape 4 : Préparation de la nouvelle page de données
        data_page = bufferManager.getPage(nouvelle_page)
        data_page.write_int(nb_octets_restant - 4, 0)
        data_page.write_int(nb_octets_restant - 8, 0)
        bufferManager.FreePage(nouvelle_page, flush=True)

        # Étape 5 : Flush des buffers
        bufferManager.flush_buffers()


def getFreeDataPageId(self, sizeRecord):
    # Accéder à bufferManager pour obtenir la page d'en-tête
    bufferManager = self.bufferManager
    headerPage = bufferManager.getPage(self.headerPageId)

    # Lire le nombre de pages de données existantes
    nb_pages = headerPage.read_int(0) or 0  # Si None, on initialise à 0

    # Parcourir toutes les pages de données enregistrées
    for i in range(nb_pages):
        offset = 4 + i * 12  # Calcul de l'offset de la page

        # Lire l'espace restant dans la page
        available_space = headerPage.read_int(offset + 8)
        if available_space is None:
            continue

        # Vérifier si le record peut être inséré dans cette page
        if sizeRecord + 8 <= available_space:
            # Construire le PageId à partir des informations de la page
            file_idx = headerPage.read_int(offset)
            page_idx = headerPage.read_int(offset + 4)
            page = PageId(file_idx, page_idx)

            # Libérer la page d'en-tête
            bufferManager.freePage(self.headerPageId, flush=False)
            return page

    # Si aucune page ne convient, on libère la page d'en-tête et on retourne None
    bufferManager.freePage(self.headerPageId, flush=False)
    return None

def writeRecordToDataPage(self, record, pageId):
    bufferManager = self.bufferManager
    page_size = bufferManager.getDiskManager().getDbConfig().getPageSize()

    # Emprunter la page de données
    page = bufferManager.getPage(pageId)

    # Lire la position libre sur la page
    position_libre = page.read_int(page_size - 4) or 0  # Si None, initialiser à 0

    # Écrire l'enregistrement dans la page
    taille_record = self.writeRecordToBuffer(record, page, position_libre)

    # Lire le nombre de records présents
    nb_slot = page.read_int(page_size - 8) or 0  # Si None, initialiser à 0

    # Mise à jour de la page (nombre de records et position libre)
    page.write_int(page_size - 8, nb_slot + 1)
    page.write_int(page_size - 4, position_libre + taille_record)

    # Calculer la taille du couple (position, taille)
    taille_pos = nb_slot * 8

    # Écrire le couple (position, taille) dans la page
    page.write_int(page_size - 8 - taille_pos - 8, position_libre)
    page.write_int(page_size - 8 - taille_pos - 4, taille_record)

    # Calculer la taille totale du record avec le couple
    taille_totale = taille_record + 8

    # Mettre à jour l'en-tête de la page dans le buffer
    headerPage = bufferManager.getPage(self.headerPageId)
    for i in range(headerPage.read_int(0) or 0):
        offset = 4 + i * 12
        file_idx = headerPage.read_int(offset)
        page_idx = headerPage.read_int(offset + 4)
        if file_idx == pageId.getFileIdx() and page_idx == pageId.getPageIdx():
            tmp = headerPage.read_int(offset + 8) or 0
            headerPage.write_int(offset + 8, tmp - taille_totale)

    # Libérer les pages (données et en-tête)
    bufferManager.freePage(pageId, flush=True)
    bufferManager.freePage(self.headerPageId, flush=True)

    # Effectuer un flush pour garantir que toutes les modifications sont écrites
    bufferManager.flushBuffers()

    # Retourner l'identifiant du record (RecordId)
    return RecordId(pageId, page_size - 8 - taille_pos - 8)

def getRecordsInDataPage(self, pageId):
    bufferManager = self.bufferManager

    # Créer une liste pour stocker les records
    liste_de_records = []

    # Obtenir la taille de la page
    page_size = bufferManager.getDiskManager().getDbConfig().getPageSize()

    # Lire la page de données à partir du buffer
    page = bufferManager.getPage(pageId)

    # Lire le nombre d'enregistrements dans la page
    nb_record = page.read_int(page_size - 8) or 0

    pos = 0

    # Lire chaque record dans la page
    for _ in range(nb_record):
        record = Record([])  # Créer un record vide, à remplir après

        # Lire l'enregistrement depuis le buffer
        pos += self.readFromBuffer(record, page, pos)

        # Ajouter le record à la liste
        liste_de_records.append(record)

    # Libérer la page après lecture
    bufferManager.freePage(pageId, flush=False)

    # Retourner la liste des records
    return liste_de_records

def getDataPages(self):
    # Liste pour stocker les PageIds
    liste_pages = []

    # Accéder au BufferManager
    bufferManager = self.bufferManager

    # Lire la Header Page
    headerPage = bufferManager.getPage(self.headerPageId)

    # Obtenir le nombre de pages de données
    nb_pages = headerPage.read_int(0) or 0  # Si la valeur est None, on considère qu'il n'y a pas de pages

    # Parcourir chaque page pour récupérer les informations
    for i in range(nb_pages):
        # Calculer l'offset pour lire le file_idx et le page_idx
        offset = 4 + i * 12

        # Lire les indices du fichier et de la page
        file_idx = headerPage.read_int(offset)
        page_idx = headerPage.read_int(offset + 4)

        # Créer un nouvel objet PageId et l'ajouter à la liste
        if file_idx is not None and page_idx is not None:
            liste_pages.append(PageId(file_idx, page_idx))

    # Libérer la Header Page
    bufferManager.freePage(self.headerPageId, flush=False)

    # Retourner la liste des PageIds
    return liste_pages

def insertRecord(self, record):
    # Obtenir la taille d'une page depuis le gestionnaire de disque
    page_size = self.bufferManager.disk_manager.getDBC().get_pageSize()

    # Création d'un buffer temporaire pour calculer la taille du record
    byte_buffer = bytearray(page_size)
    buffer_record = memoryview(byte_buffer)  # Équivaut à un ByteBuffer en Python

    # Calculer la taille du record
    taille_record = self.writeRecordToBuffer(record, buffer_record, 0)

    # Trouver une page avec suffisamment d'espace pour insérer le record
    data_page = self.getFreeDataPageId(taille_record)

    # Si aucune page n'a assez d'espace, en créer une nouvelle
    if data_page is None:
        self.addDataPage()
        # Réessayer de trouver une page avec suffisamment d'espace
        data_page = self.getFreeDataPageId(taille_record)

    # Insérer le record dans la page de données et retourner son RecordId
    return self.writeRecordToDataPage(record, data_page)