import requests
import dict2xml
import datetime
import cfg

def gdata_payload_from_id(id : int, token : str):
    return {
  "method": "gdata",
  "gidlist": [
      [id, token]
  ],
  "namespace": 1
}

def get_id_token_from_url(url : str) -> tuple:
    return (int(url.split("/")[4]), url.split("/")[5])


def get_url_from_id_token(id : int, token : str) -> str:
    return f"https://exhentai.org/g/{id}/{token}/"

# https://exhentai.org/g/1901491/fcdc0a73b8/
# sample url
def gdata_payload_from_url(url : str):
    
    return gdata_payload_from_id(*get_id_token_from_url((url)))


LANGUAGE_ISO_LOOKUP = {
    "english" : "en",
    "japanese" : "ja",
    "chinese" : "zh"
}
def list_to_tag_string(ls : list) -> str:
    out = ""
    for element in ls:
        out += str(element)
        out += ", "
    return out[:-2]

def response_to_metadata_dict(resp_meta : dict, url : str) -> dict:
    post_time = datetime.datetime.fromtimestamp(int(resp_meta["posted"]))
    character_tag = []
    parody_tag = []
    misc_tag = []
    writer_tag = []
    group_tag = []
    language = "na"
    is_translated = False
    for tag in resp_meta["tags"]:
        # type
        tt = tag.split(":")[0]
        # value
        tv = tag.split(":")[1]
        if tt == "character":
            character_tag.append(tv)
        elif tt == "language":
            if tv == "translated":
                is_translated = True
            else:
                language = LANGUAGE_ISO_LOOKUP[tv]
        elif tt == "parody":
            parody_tag.append(tv)
        elif tt == "artist":
            writer_tag.append(tv)
        elif tt == "group":
            group_tag.append(tv)
        else:
            misc_tag.append(tv)
        

    return {
        "ComicInfo" : {
            "Manga" :  "Yes",
            "Title" : resp_meta["title"],
            "EHentaiId" : resp_meta["gid"],
            "EHentaiToken" : resp_meta["token"],
            "Summary" : resp_meta["title_jpn"],
            "PageCount" : resp_meta["filecount"],
            "URL" : url,
            "Genre" : resp_meta["category"],
            "BlackAndWhite" : "Yes",
            "Year" : post_time.year,
            "Month" : post_time.month,
            "Day" : post_time.day,
            "Series" : list_to_tag_string(parody_tag),
            "Characters" : list_to_tag_string(character_tag),    
            "Tags" : list_to_tag_string(misc_tag),
            "Writer" : list_to_tag_string(writer_tag),
            "Publisher" : list_to_tag_string(group_tag),
            "EHTags" : list_to_tag_string(resp_meta["tags"]),
            "LanguageISO" : language,
            "Translated" : "Yes" if is_translated else "No"
        }
    }


def request_comicinfo_fromurl(url : str, api_url : str = "https://api.e-hentai.org/api.php") -> str:
    res = requests.post(api_url, proxies=cfg.proxies, json=gdata_payload_from_url(url))
    meta = response_to_metadata_dict(res.json()["gmetadata"][0], url)

    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + dict2xml.dict2xml(meta, indent=" ")


def request_comicinfo_fromid(id : int, token : str, api_url : str = "https://api.e-hentai.org/api.php"):
    url = get_url_from_id_token(id, token)
    return request_comicinfo_fromurl(api_url, url)

