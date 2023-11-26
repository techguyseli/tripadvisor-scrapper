from bs4 import BeautifulSoup
import subprocess
from pathlib import Path


class AttractionLinkDownloader:

    def __init__(self, link_pre:str, link_suff:str, last_pagination:int,
                 pagination:int=0, pagination_incr:int=30,
                 download_path:str="./out") -> None:
        self.link_pre = link_pre
        self.link_suff = link_suff

        self.last_pagination = last_pagination
        self.pagination = pagination
        self.pagination_incr = pagination_incr

        self.download_path = Path(download_path)
        self.temp_page_path = self.download_path / "page.html"
        self.links_path = self.download_path / "links.txt"


    def _get_pagination_link(self, increment:bool=False) -> str:
        pagination_str = "" if self.pagination==0 else "oa" + str(self.pagination) + "-"
        link = self.link_pre + pagination_str + self.link_suff
        if increment:
            self.pagination += self.pagination_incr 
        return link


    def _precleenup(self) -> None:
        if not self.download_path.exists():
            self.download_path.mkdir(parents=True, exist_ok=True)
        if self.links_path.exists():
            self.links_path.unlink()


    def _postcleanup(self) -> None:
        if self.temp_page_path.exists():
            self.temp_page_path.unlink()


    def download(self) -> None:
        print("Performing pre-cleanup...")
        self._precleenup()

        print("Downloading attractions' links...")
        while self.pagination <= self.last_pagination:
            print("\tPagination:", self.pagination, "/", self.last_pagination)
            pagination_link = self._get_pagination_link(increment=True)

            print("\t\tRequesting the page...")
            command = "wget " + pagination_link + ' -O ' + str(self.temp_page_path)
            subprocess.run(command, shell=True, 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
            print("\t\tPage downloaded.")

            print("\t\tParsing the page...")
            soup = BeautifulSoup(open(self.temp_page_path, 'r').read(), "html.parser")
            places_links = soup.find_all("div", class_="PgLKC")
            places_links = [place for place in places_links if "yzLvM" not in place.get('class', [])]
            places_links = ["https://www.tripadvisor.com/" + linkk.find("a")['href'] for linkk in places_links]
            
            with open(self.links_path, 'a') as f:
                [f.write(linkk + '\n') for linkk in places_links]
            print("\t\tPagination", self.pagination - self.pagination_incr, ": links downloaded.")

        print("Performing post-clean-up...")
        self._postcleanup()
        print("Links downloaded successfully at", str(self.links_path))


