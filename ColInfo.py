class ColInfo:
    def __init__(self, colNom, colType):
        self.colNom=colNom
        self.colType = colType

    def get_colNom(self):
        return self.colNom

    def get_colType(self):
        return self.colType

    def __str__(self):
        return f"{self.colNom}:{self.colType}"
