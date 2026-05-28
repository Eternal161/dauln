import asyncio
import json
from playwright.async_api import async_playwright

# 💡 Link chương 1 bộ truyện Dậu muốn hút:
START_URL = "https://docln.sbs/truyen/20569-trung-sinh-2000-thanh-mai-giao-hoa-18-tuoi/c155831-chuong-1-nu-hon-lam-ca-lop-ngo-ngang"

async def hut_truyen():
    html_content = """
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Times New Roman', serif; line-height: 1.6; max-width: 800px; margin: auto; padding: 20px; font-size: 18px; color: #000000; background-color: #ffffff; }
            h2 { color: #2c3e50; text-align: center; margin-top: 50px; page-break-before: always; }
            p { text-indent: 20px; text-align: justify; margin-bottom: 15px; }
        </style>
    </head>
    <body>
    """

    async with async_playwright() as p:
        print("🚀 Khởi động trình duyệt ngầm trên hệ thống GitHub...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        current_url = START_URL
        chuong_so = 1

        while current_url:
            print(f"⏳ Bot đang hút dữ liệu chương {chuong_so}...")
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(2000) # Chờ 2 giây tải chữ chống Cloudflare

                # Lấy tiêu đề chương
                tieu_de_loc = page.locator(".title-top h4, .title-item").first
                tieu_de = await tieu_de_loc.text_content()
                if not tieu_de: tieu_de = f"Chương {chuong_so}"

                # Lấy nội dung chữ
                noi_dung_loc = page.locator("#chapter-content")
                noi_dung = await noi_dung_loc.inner_html()
                
                html_content += f"<h2>{tieu_de.strip()}</h2>\n"
                html_content += noi_dung + "\n"

                # Tìm nút sang chương tiếp theo
                nut_next = page.locator("a:has-text('Chương sau'), a.rd_sd-button_item.rd_top-right").last
                
                if await nut_next.is_visible() and await nut_next.get_attribute("href") != "#":
                    href = await nut_next.get_attribute("href")
                    current_url = href if href.startswith("http") else f"https://docln.sbs{href}"
                    chuong_so += 1
                else:
                    print("✅ Đã thu thập đến trang cuối cùng của bộ truyện!")
                    current_url = None

            except Exception as e:
                print(f"❌ Xảy ra sự cố ngắt quãng tại chương {chuong_so}: {e}")
                break

        # 📄 TỰ ĐỘNG BIẾN THÀNH FILE PDF XỊN XÒ TỪ CODE
        print("📄 Đang tiến hành đóng gói và xuất bản file PDF...")
        html_content += "</body></html>"
        await page.set_content(html_content)
        await page.pdf(
            path="thanh_mai_giao_hoa_full.pdf", 
            format="A4", 
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
        )
        print("✅ Đã xuất bản file 'thanh_mai_giao_hoa_full.pdf' thành công!")
        await browser.close()

    # 📝 TỰ ĐỘNG ĐẺ FILE LN.JSON ĐỂ SÁNG TV ĐỌC ĐƯỢC LUÔN
    print("📝 Cập nhật sơ đồ cấu hình dữ liệu mạng cho Sáng TV...")
    ln_data = {
        "comics": [
            {
                "title": "Trùng Sinh 2000: Thanh Mai Giao Hoa 18 Tuổi",
                "thumb_url": "https://docln.sbs/images/books/20569.jpg",
                "status": "Full PDF",
                "pdf_url": "https://raw.githubusercontent.com/Eternal161/dauln/main/thanh_mai_giao_hoa_full.pdf"
            }
        ]
    }
    with open("ln.json", "w", encoding="utf-8") as f:
        json.dump(ln_data, f, ensure_ascii=False, indent=4)
    print("✅ Đã tạo cấu trúc file 'ln.json' thành công!")

if __name__ == "__main__":
    asyncio.run(hut_truyen())
