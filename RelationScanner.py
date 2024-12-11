from IRecordIterator import IRecordIterator
from Record import Record

class RelationScanner(IRecordIterator):
    def __init__(self, relation):
        """
        Initialisation du RelationScanner.
        :param relation: Instance de la classe Relation représentant la table à scanner.
        """
        self.relation = relation
        self.data_pages = relation.getDataPages()  # Obtenir les pages contenant les données
        self.current_page_index = 0  # Indice de la page actuelle
        self.current_record_index = 0  # Indice du record actuel dans la page
        self.current_page_records = []  # Cache des records de la page actuelle

        # Charger la première page si disponible
        if self.data_pages:
            self._load_page(self.data_pages[self.current_page_index])

    def _load_page(self, page_id):
        """
        Charge les records de la page spécifiée dans le cache.
        :param page_id: Identifiant de la page à charger.
        """
        self.current_page_records = self.relation.getRecordsInDataPage(page_id)
        self.current_record_index = 0  # Réinitialise le pointeur des records

    def GetNextRecord(self):
        """
        Retourne le prochain record et avance le curseur.
        :return: Un objet Record ou None si aucun record restant.
        """
        if self.current_record_index < len(self.current_page_records):
            # Retourner le prochain record dans la page actuelle
            record = self.current_page_records[self.current_record_index]
            self.current_record_index += 1
            return record

        # Passer à la page suivante si disponible
        self.current_page_index += 1
        if self.current_page_index < len(self.data_pages):
            self._load_page(self.data_pages[self.current_page_index])
            return self.GetNextRecord()  # Récursivement essayer la nouvelle page

        # Aucun record restant
        return None

    def Close(self):
        """
        Libère les ressources utilisées par le scanner.
        """
        self.data_pages = []
        self.current_page_records = []
        self.current_page_index = 0
        self.current_record_index = 0
        print("Scanner fermé et ressources libérées.")

    def Reset(self):
        """
        Réinitialise le scanner pour recommencer à parcourir la relation.
        """
        self.current_page_index = 0
        self.current_record_index = 0
        if self.data_pages:
            self._load_page(self.data_pages[0])
