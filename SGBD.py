import DiskManager
import BufferManager
import DBManager
import ColInfo
import Relation
import DBConfig

class SGBD:
    
    def __init__(self, dbConfig):  
        self.dbConfig = dbConfig
        self.diskManager = DiskManager(dbConfig)  
        self.bufferManager = BufferManager(dbConfig,self.diskManager)
        self.dbManager = DBManager(dbConfig) 
        self.diskManager.loadState()
        self.dbManager.loadState()

    def ProcessCreateDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.Createdatabase(nom)

    def ProcessSetCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.SetCurrentDatabase(nom)
    
    def ProcessAddTableToCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2] #recuperer le nom
        table = cmd.split()[3] #recupere les cols
        table = table[1:len(table)-1] #eliminer les ()
        tableCol = table.split(",")  #pour les infos des cols
        cols = [] #list to pass to the relation constructer
        var = False
        for i in range(len(tableCol)):
            cols[i].add(ColInfo(tableCol[i].split(":")[0],tableCol[i].split(":")[1]))
            if(tableCol[i].split(":")[1].startsWith("VARCHAR")):
                var = True
        relation = Relation(nom,len(tableCol),cols,var)
        self.dbManager.AddTableToCurrentDatabase(relation)

    def ProcessGetTableFromCurrentDatabaseCommand(self, cmd):
        for table in self.dbManager.active_database.tables:
            self.dbManager.GetTableFromCurrentDatabase(table.nom_table)

    def ProcessRemoveTableFromCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.RemoveTableFromCurrentDatabase(nom)

    def ProcessRemoveDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.RemoveDatabase(nom)

    def ProcessRemoveTablesFromCurrentDatabaseCommand(self, cmd):
        self.dbManager.RemoveTablesFromCurrentDatabase()

    def ProcessRemoveDatabasesCommand(self, cmd):
        self.dbManager.RemoveDatabases()

    def ProcessListDatabasesCommand(self, cmd):
        self.dbManager.ListDatabases()

    def run(self):
        print("Welcome dans notre SGBD. Tapez une commande ou 'QUIT' pour quitter.")
        while True:
            try:
                # Affiche le prompt "?" et récupère l'entrée du user
                cmd = input("? ").strip()
                if cmd.upper() == "QUIT":
                    print("Sauvegarde de l'état.")
                    self.dbManager.SaveState()
                    print("Ciao !")
                    break  # Quitte la boucle pour arrêter l'application (pas tres cool d'utiliser ça mais bon)

                # Analyse la commande et appelle la méthode appropriée
                action = cmd.split()[0].upper()
                if action == "CREATE" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessCreateDatabaseCommand(cmd)
                elif action == "SET" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessSetCurrentDatabaseCommand(cmd)
                elif action == "CREATE" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessAddTableToCurrentDatabaseCommand(cmd)
                elif action == "GET" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessGetTableFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessRemoveTableFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessRemoveDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "TABLES":
                    self.ProcessRemoveTablesFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "DATABASES":
                    self.ProcessRemoveDatabasesCommand(cmd)
                elif action == "LIST" and cmd.split()[1].upper() == "DATABASES":
                    self.ProcessListDatabasesCommand(cmd)
                elif action == "LIST" and cmd.split()[1].upper() == "TABLES":
                    self.dbManager.ListTablesInCurrentDatabase()  # Appelle directement depuis dbManager
                else:
                    print("Commande non reconnue :(")
            except Exception as e:
                print(f"Erreur lors du traitement de la commande : {e}")



    def main(self, path):
        dbConfig = DBConfig.load_db_config(path)
        sgbd = SGBD(dbConfig)
        sgbd.run()
