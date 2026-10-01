"""Unduh korpus artikel Wikipedia nyata dalam bahasa Indonesia dan Inggris."""

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ARTICLES_PER_LANGUAGE = 15
MINIMUM_CHARACTERS = 500
USER_AGENT = "HybridComputingCoursework/1.0 (educational word-count benchmark)"
SEARCH_TERMS = {
    "id": ("Indonesia", "sejarah", "sains", "budaya", "geografi", "teknologi"),
    "en": ("science", "history", "culture", "geography", "technology", "literature"),
}


class ArticleTextParser(HTMLParser):
    """Ambil teks isi artikel HTML sambil melewati navigasi dan skrip."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "header", "footer", "noscript"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "header", "footer", "noscript"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def fetch_search_results(language, query):
    """Cari judul artikel dengan API REST Wikimedia."""
    parameters = urllib.parse.urlencode({"q": query, "limit": 50})
    url = f"https://{language}.wikipedia.org/w/rest.php/v1/search/page?{parameters}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8")).get("pages", [])


def fetch_article_text(language, key):
    """Unduh HTML halaman dan ekstrak teks artikel menggunakan parser bawaan."""
    encoded_key = urllib.parse.quote(key, safe="")
    url = f"https://{language}.wikipedia.org/w/rest.php/v1/page/{encoded_key}/html"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = ArticleTextParser()
    parser.feed(html)
    return " ".join(parser.parts), url


def download_language(language, output_dir):
    """Simpan 15 artikel berbeda; hentikan dengan pesan jelas bila gagal."""
    saved = []
    seen_titles = set()
    results = []
    seen_keys = set()
    try:
        for query in SEARCH_TERMS[language]:
            results.extend(fetch_search_results(language, query))
    except (OSError, TimeoutError, urllib.error.URLError) as error:
        raise RuntimeError(
            f"Gagal mencari artikel Wikipedia {language}: {error}. "
            "Periksa koneksi atau letakkan minimal 30 file .txt secara manual di b3/data_wc."
        ) from error

    for result in results:
        key = result.get("key", "")
        title = result.get("title", "").strip()
        if not key or title in seen_titles or key in seen_keys:
            continue
        seen_titles.add(title)
        seen_keys.add(key)
        try:
            text, source_url = fetch_article_text(language, key)
        except (OSError, TimeoutError, urllib.error.URLError):
            continue
        if len(text) >= MINIMUM_CHARACTERS:
            destination = output_dir / f"{language}_wiki_{len(saved) + 1:03d}.txt"
            destination.write_text(f"{title}\n\n{text}\n", encoding="utf-8")
            saved.append((title, len(text)))
            with (output_dir / "corpus_sources.csv").open("a", encoding="utf-8") as source_file:
                source_file.write(f'"{language}","{title.replace(chr(34), chr(34) * 2)}","{source_url}"\n')
        if len(saved) == ARTICLES_PER_LANGUAGE:
            break
        time.sleep(0.25)  # MODIFIED: beri jarak antarunduhan ke layanan publik.

    if len(saved) < ARTICLES_PER_LANGUAGE:
        raise RuntimeError(
            f"Hanya {len(saved)} artikel {language} yang memenuhi syarat; "
            "butuh 15 per bahasa agar korpus campuran berisi sedikitnya 30 file."
        )
    return saved


def main():
    """Buat korpus 30 artikel nyata dan tampilkan daftar ringkasnya."""
    output_dir = Path(__file__).resolve().parent / "data_wc"
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = {}
    for language in ("id", "en"):
        files = sorted(output_dir.glob(f"{language}_wiki_*.txt"))
        articles = []
        for path in files:
            content = path.read_text(encoding="utf-8", errors="ignore")
            title, _, text = content.partition("\n\n")
            if len(text) >= MINIMUM_CHARACTERS:
                articles.append((path, title.strip(), len(text)))
        existing[language] = articles

    # MODIFIED: gunakan korpus valid yang sudah diunduh agar pengulangan tidak terkena rate limit.
    if all(len(existing[language]) >= ARTICLES_PER_LANGUAGE for language in ("id", "en")):
        with (output_dir / "corpus_sources.csv").open("w", newline="", encoding="utf-8") as source_file:
            writer = csv.writer(source_file)
            writer.writerow(("language", "title", "source_url"))
            for language in ("id", "en"):
                for _, title, _ in existing[language][:ARTICLES_PER_LANGUAGE]:
                    key = urllib.parse.quote(title.replace(" ", "_"), safe="()")
                    writer.writerow((language, title, f"https://{language}.wikipedia.org/wiki/{key}"))
        total_bytes = sum(path.stat().st_size for language in existing for path, _, _ in existing[language][:ARTICLES_PER_LANGUAGE])
        print("Korpus valid 30 artikel sudah tersedia; tidak perlu mengunduh ulang.")
        print(f"Lokasi: {output_dir}")
        print(f"Total ukuran file korpus: {total_bytes} byte")
        for language in ("id", "en"):
            for _, title, size in existing[language][:ARTICLES_PER_LANGUAGE]:
                print(f"[{language}] {title} ({size} karakter teks)")
        return

    # MODIFIED: siapkan ulang atribusi saat korpus baru diunduh.
    (output_dir / "corpus_sources.csv").write_text(
        '"language","title","source_url"\n', encoding="utf-8"
    )
    downloaded = []
    for language in ("id", "en"):
        articles = download_language(language, output_dir)
        downloaded.extend((language, title, size) for title, size in articles)

    total_bytes = sum(path.stat().st_size for path in output_dir.glob("*_wiki_*.txt"))
    print(f"Diunduh {len(downloaded)} artikel dari Wikipedia (id.wikipedia.org dan en.wikipedia.org).")
    print(f"Lokasi: {output_dir}")
    print(f"Total ukuran file korpus: {total_bytes} byte")
    for language, title, size in downloaded:
        print(f"[{language}] {title} ({size} karakter teks)")


if __name__ == "__main__":
    main()