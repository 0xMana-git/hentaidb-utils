import ehentai_comicinfo
import requests
import cfg
import dict2xml

# API compliant with https://github.com/ccloli/e-hentai-db
def gdata_params_from_id(id : int, token : str):
    return {
  "id" : id,
  "token" : token
}


# https://exhentai.org/g/1901491/fcdc0a73b8/
# sample url
def gdata_params_from_url(url : str):
    return gdata_params_from_id(*ehentai_comicinfo.get_id_token_from_url((url)))



def request_comicinfo_fromurl(url : str, api_url : str = "http://localhost:8880") -> str:
    res = requests.get(api_url + "/api/g", proxies=cfg.proxies, params=gdata_params_from_url(url))
    meta = ehentai_comicinfo.response_to_metadata_dict(res.json()["gmetadata"][0], url)

    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" + dict2xml.dict2xml(meta, indent=" ")


def request_comicinfo_fromid(id : int, token : str, api_url : str = "http://localhost:8880") -> str:
    url = f"https://exhentai.org/g/{id}/{token}/"
    return request_comicinfo_fromurl(api_url, url)



def get_language_of_entry(entry : dict) -> str:
    for tag in entry["tags"]:
        if len(tag.split(":")) == 1:
            continue
        tt = tag.split(":")[0]
        tv = tag.split(":")[1]
        if tt != "language":
            continue
        if tv == "translated":
            continue
        return tv
    return "japanese"


def get_lang_priority(lang : str) -> int:
    if not lang in cfg.preferred_lang_order:
        return 0
    return cfg.preferred_lang_order[lang]

def get_entry_lang_priority(entry : dict):
    return get_lang_priority(get_language_of_entry(entry))

#TODO: refactor this shit
def request_comicinfo_from_search_query(query_str : str, api_url : str = "http://localhost:8880"):
    res = requests.get(api_url + "/api/search", proxies=cfg.proxies, params={
        "keyword" : query_str,
        "limit" : 20
    })
    res_list = res.json()["data"]
    if len(res_list) == 0:
        raise LookupError("Entry not found")
    #default 0:
    picked_entry = res_list[0]
    picked_lang_priority = get_entry_lang_priority(picked_entry)
    for entry in res_list:  
        prio = get_entry_lang_priority(entry)
        if prio > picked_lang_priority:
            picked_lang_priority = prio
            picked_entry = entry
    return ehentai_comicinfo.response_to_metadata_dict(entry, ehentai_comicinfo.get_url_from_id_token(entry["gid"], entry["token"]))
        
        

