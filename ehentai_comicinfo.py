    import requests
import urllib
import dict2xml
import datetime


def gdata_payload_from_id(id : int, token : str):
    return {
  "method": "gdata",
  "gidlist": [
      [id, token]
  ],
  "namespace": 1
}

# https://exhentai.org/g/1901491/fcdc0a73b8/
# sample url
def gdata_payload_from_url(url : str):
    id = int(url.split("/")[4])
    token = url.split("/")[5]
    return gdata_payload_from_id(id, token)


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

def response_to_metadata_dict(resp_json : dict, url : str) -> dict:
    resp_meta = resp_json["gmetadata"][0]
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
            "LanguageISO" : language,
            "Translated" : "Yes" if is_translated else "No"
        }
    }


def request_comicinfo_fromurl(api_url : str, url : str) -> str:
    res = requests.post(api_url, proxies=proxies, json=gdata_payload_from_url(url))
    meta = response_to_metadata_dict(res.json(), url)

    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + dict2xml.dict2xml(meta, indent=" ")
def request_comicinfo_fromid(api_url : str, id : int, token : str):
    url = f"https://exhentai.org/g/{id}/{token}/"
    return request_comicinfo_fromurl(api_url, url)

