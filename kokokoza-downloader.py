from email import header
import os
import subprocess
from dataclasses import replace
import requests
from bs4 import BeautifulSoup as bs

# CONFIGURATION

program_name = "" #For example "kagakukiso" or "nihonshi"
save_directory = "" #For example "/Users/user/Desktop/"
download_start = 1 #Download from this chapter
download_end = 40 #to this chapter

if download_start >= 1:
    for x in range(download_start, (download_end + 1)) :

        if (x < 10):
            episode_number = "chapter00" + str(x)
        else:
            episode_number = "chapter0" + str(x)

        archive_link = "https://www.nhk.or.jp/kokokoza/tv/" + program_name + "/archive/"
        master_link = "https://nhks-vh.akamaihd.net/i/kokokoza/mov/tv/" + program_name + "/"
        nhk_page_link = archive_link + episode_number + ".html"

        header = { 'Accept-Language': 'ja' }
        page_request = requests.get(nhk_page_link, headers=header)
        page_content = page_request.content

        soup_parser = bs(page_content, "html.parser")

        nhk_page_title = str(soup_parser.find("title"))
        nhk_page_title = nhk_page_title.replace("<title>", "")
        nhk_page_title = nhk_page_title.replace("</title>", "")
        temp_index = nhk_page_title.index("第")
        nhk_page_title = nhk_page_title[temp_index:]

        #nhk_page_title = ""

        ul_movie = soup_parser.find("ul", attrs={"id": "movie"})

        chapter_titles = []
        video_links = []

        for chapter in ul_movie.find_all("li"):
            fig_caption = str(chapter.find('figcaption'))
            fig_caption = fig_caption.replace("<figcaption>", "")
            fig_caption = fig_caption.replace("</figcaption>", ".mp4")
            chapter_titles.append(fig_caption)

            img_src = str(chapter.find("img").get("src"))
            img_src = img_src.replace("thumbnail/", master_link)
            img_src = img_src.replace("jpg", "mp4/master.m3u8")
            video_links.append(img_src)

        mypath = save_directory + nhk_page_title
        if not os.path.isdir(mypath):
            os.makedirs(mypath)

        bash_file_name = mypath + "/download.sh"

        with open(bash_file_name, "w") as f:
            f.write("#! /bin/bash\n")

            for i in range(len(chapter_titles)):
                f.write("ffmpeg -analyzeduration 5G -i '" + video_links[i] + "' -c copy '" + mypath + "/(AAC)" + str(i + 1) + "." + chapter_titles[i] + "' &\n" )

            f.write("wait\n")
            f.write("echo 'GOOD JOB PIRATE! THE FILES ARE SAFE!'\n")

            for i in range(len(chapter_titles)):
                f.write("ffmpeg -i '" + mypath + "/(AAC)" + str(i + 1) + "." + chapter_titles[i] + "' -c:v copy -acodec mp3 '" + mypath + "/" + str(i + 1) + "." + chapter_titles[i] + "' &\n" )
            
            f.write("wait\n")
            f.write("echo 'VIDEO FILES CONVERTED!'\n")

            for i in range(len(chapter_titles)):
                f.write("rm '" + mypath + "/(AAC)" + str(i + 1) + "." + chapter_titles[i] + "' &\n")

            f.write("wait\n")
            f.write("echo 'AAC VIDEO FILES DELETED!'\n")

        os.system("chmod u+x '" + bash_file_name + "'")
        subprocess.call(bash_file_name)

        sub_code = str(ul_movie.find("li").find("img").get("src"))
        sub_code = sub_code[10:20]

        for i in range(len(chapter_titles)):
            URL = archive_link + "vtt/" + sub_code + str(i + 1) + ".vtt"
            response = requests.get(URL)
            URL = URL.replace(archive_link + "vtt/", "")
            open(mypath + "/" + URL, "wb").write(response.content)