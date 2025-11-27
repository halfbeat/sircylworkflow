import csv
from io import StringIO

CSV = """"Asiento";",Estado";"Fecha de distribucion";"Fecha de registro";"Nº de registro";"Origen";"Destino";"Materia";"Fecha de estado"
"93129867";"ARCHIVADO";"2025-05-26 11:02:03+02:00";"2025-02-28 13:37:20+01:00";"202580000000025";"REGISTRO GENERAL DE LA ACCYL";"CN=SIRCYL_PRE@DIST_810,OU=Perfiles Aplicaciones,OU=Groups,OU=Administración Autonómica,OU=JCYL,DC=jcyl,DC=red";"EGM";"2025-06-16 10:57:45+02:00"
"""

def test_read_csv_from_string():
    f = StringIO(CSV)
    reader = csv.reader(f, delimiter=';', quotechar='"')
    for row in reader:
        print(row)