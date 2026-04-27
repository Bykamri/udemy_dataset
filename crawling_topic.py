import asyncio
import threading
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    print("="*60)
    print("🚀 Memulai Scraping Seluruh Topik")
    print("="*60)

    all_topics = set()

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        urls_to_mine = [
            "https://www.udemy.com/",         
            "https://www.udemy.com/sitemap/"  
        ]

        for url in urls_to_mine:
            print(f"[*] Topics Crawling from: {url}")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)

                extracted_topics = await page.evaluate("""
                    () => {
                        let topics = new Set();

                        let links = document.querySelectorAll('a[href*="/topic/"], a[href*="/courses/"]');
                        links.forEach(link => {
                            let text = link.innerText.trim();
                            if (text && text.length > 1 && text.length < 60 && !text.toLowerCase().includes('all') && !text.toLowerCase().includes('view')) {
                                topics.add(text);
                            }
                        });

                        let nextData = document.getElementById('__NEXT_DATA__');
                        if (nextData) {
                            try {
                                let ssrJson = JSON.parse(nextData.innerText);
                                let findTopics = (obj) => {
                                    if (!obj || typeof obj !== 'object') return;
                                    if (obj.url && (obj.url.includes('/topic/') || obj.url.includes('/courses/'))) {
                                        let title = obj.title || obj.name;
                                        if (title && title.length > 1 && title.length < 60) {
                                            topics.add(title.trim());
                                        }
                                    }
                                    Object.values(obj).forEach(findTopics);
                                };
                                findTopics(ssrJson);
                            } catch(e) {}
                        }
                        return Array.from(topics);
                    }
                """)

                all_topics.update(extracted_topics)
                print(f"    [+] Ditemukan sementara: {len(all_topics)} topik unik.")

            except Exception as e:
                print(f"    [!] Gagal memuat {url}: {e}")

        await browser.close()

    if not all_topics:
        print("\n[❌] Gagal menemukan topik apa pun.")
        return

    print(f"\n[*] Mengurutkan {len(all_topics)} topik dan menyimpan ke .txt...")
    sorted_topics = sorted(list(all_topics))
    file_name = "udemy_list_topics.txt"

    with open(file_name, "w", encoding="utf-8") as file:
        for index, topic in enumerate(sorted_topics, 1):
            file.write(f"{index}. {topic}\n")

    print("\n✅ PROSES SELESAI!")
    print(f"📄 File berhasil disimpan dengan nama: {file_name}")

def run_in_new_loop():
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

thread = threading.Thread(target=run_in_new_loop)
thread.start()
thread.join()