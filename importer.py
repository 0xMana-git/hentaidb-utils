import sqlite3
import zipfile
import os 
import xml.etree.ElementTree as ET
import xmltodict



db_path = "./database.db"
gallery_root = "E:/Archives/Doujins/"
infos = []


#fields: 
#id - primary ket
#name - str
#nhentai id - int(may not exist)
#pages - int

#tags - str
#characters - str
#parody - str
#artist(s) - str
#group(s) - str

#language - str
#upload time - date(text)

table_spec = """hentai(
    id INTEGER,
    name TEXT,
    nhentai_id INTEGER,
    pages INTEGER,  
    tags TEXT,
    characters TEXT,
    parody TEXT,
    artists TEXT,
    groups TEXT,
    language TEXT,
    date TEXT
    );"""


table_create_cmd = "CREATE TABLE IF NOT EXISTS " + table_spec




database = sqlite3.connect(db_path)
database_cursor = database.cursor()

def date_add_padding(m_d : str) -> str:
    if(len(m_d) == 2):
        return m_d
    return "0" + m_d
def serialize_list(lst : list) -> str:
    out = ""
    if type(lst) != list:
        return lst
    for e in lst:
        out += e + " "
    return out[:-1]
def xml_entry_to_db_entry(xml_entry : dict) -> dict:
    date_str = f"""{xml_entry["Year"]}-{date_add_padding(xml_entry["Month"])}-{date_add_padding(xml_entry["Day"])}"""
    entry = {
        "name" : xml_entry["Title"],
        "nhentai_id" : xml_entry["NhentaiId"],
        "pages" : xml_entry["PageCount"],
        "tags" : xml_entry["Tags"],
        "characters" : xml_entry["Characters"],
        "parody" : xml_entry["Series"],
        "artists" : xml_entry["Writer"],
        "groups" : "Placeholder",
        "language" : xml_entry["LanguageISO"],
        "date" : date_str

    }
    for k in entry.keys():
        entry[k] = serialize_list(entry[k])
    return entry


def db_entry_to_insert_cmd(db_entry : dict) -> tuple:
    insert_keys = "INSERT INTO hentai("
    insert_values_str = ("VALUES(" + "?, " * len(db_entry))[:-2] + ")"
    insert_values = []
    for key in db_entry.keys():
        insert_keys += key + ","
        insert_values.append(db_entry[key])

    insert_keys = insert_keys[:-1] + ")"
    return (insert_keys + insert_values_str, tuple(insert_values))



def insert_to_db(entry : dict, db : sqlite3.Cursor = database_cursor):
    cmd = db_entry_to_insert_cmd(xml_entry_to_db_entry(entry))
    db.execute(cmd[0], cmd[1])

#database.execute("DROP TABLE hentai")
database.execute(table_create_cmd)

for root, dirs, files in os.walk(gallery_root):
    for file in files:
        if file.endswith(".cbz") or file.endswith(".zip"):
            try: 
                zip = zipfile.ZipFile(root + file)
                info_str = zip.read("ComicInfo.xml")
                
                infos.append(xmltodict.parse(info_str.decode("utf-8")))
            except KeyError:
                print(f"Cannot find ComicInfo.xml in {root + file}" )



for entry in infos:
    insert_to_db(entry["ComicInfo"])

print(database.execute("SELECT * FROM hentai").fetchall())

database.commit()