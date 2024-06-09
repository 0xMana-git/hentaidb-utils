import zipfile
import ehentai_comicinfo
import os
import shutil
import cfg

#packs original archives into cbzs that follow a unified naming convention and stuff


def pad_page_id(id : int) -> str:
    id_str = str(id)
    return '0' * (3 - len(id_str)) + id_str
    




def repack_zip(src : str, add_comicinfo = False, lookup_comicinfo = False, comicinfo_path = False, ehentai_url : str = ""):
    
    temp_dir = "./repack_tmp/"
    temp_archive = "repack_temp_archive"
    archive_name = src.split(".")[0]
    with zipfile.ZipFile(src, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    ctr = 1
    for fname in os.listdir(temp_dir):
        ext = "." + fname.split(".")[1]
        target_name = pad_page_id(ctr) + ext
        if fname != target_name:
            os.rename(temp_dir + fname, temp_dir + target_name)
        ctr += 1
    if add_comicinfo:
        if lookup_comicinfo:
            comicinfo = ehentai_comicinfo.request_comicinfo_fromurl(ehentai_url)
            with open(temp_dir + "ComicInfo.xml", "w", encoding="utf-8") as f:
                f.write(comicinfo)
        else:
            #not implmeneted, cba rn
            pass
    shutil.make_archive(temp_archive, "zip", temp_dir)
    id, token = ehentai_comicinfo.get_id_token_from_url(ehentai_url)
    os.rename(temp_archive + ".zip", f"[e-hentai][{id}]{archive_name}.cbz")
    shutil.rmtree(temp_dir)


repack_zip("(C91) [Fuka Fuka (Sekiya Asami)] Clever ED Manga (Kari) Pre Ban (Qualidea Code) [English] [Rupee].zip", add_comicinfo=True, lookup_comicinfo=True, ehentai_url="https://exhentai.org/g/2449179/5251f99591/")

