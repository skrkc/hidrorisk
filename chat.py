"""Arac cagirabilen HidroRisk asistani (komut satiri).

Dongu cok basit:
kullanici sorar -> model ya cevap verir ya da bir arac cagirir
-> araci biz calistirir, sonucu modele geri veririz
-> model nihai cevabi yazar

Kullanim:
python chat.py
"""

import argparse

import ollama_client
import tools


MAX_TOOL_ROUNDS = 5  # sonsuz arac dongusune karsi emniyet freni


SYSTEM_PROMPT = """Sen HidroRisk adinda Turkce konusan bir hidroloji ve hidrolik on degerlendirme asistanisin.

Elinde 4 arac var:

- calculate_peak_runoff: Rasyonel Yontem ile pik yuzeysel akis debisini hesaplar.

- check_channel_capacity: Manning denklemi ile dikdortgen acik kanal kapasitesini hesaplar ve verilen tasarim debisine gore yeterliligini kontrol eder.

- calculate_spi: Aylik yagis verisi iceren CSV dosyasindan secilen zaman olceginde Standartlastirilmis Yagis Indisi (SPI) hesaplar.

- plot_spi_series: Aylik yagis verisi iceren CSV dosyasindan secilen zaman olceginde SPI zaman serisi grafigi olusturur ve PNG dosyasi olarak kaydeder.

- internet_search: Guncel bilgi, standart, mevzuat veya genel bilgi icin internette arama yapar.

KURALLAR:

- Sayisal bir hidroloji veya hidrolik hesabi icin uygun arac varsa hesabi kendin tahmin etme, ilgili araci kullan.

- Hesap icin gerekli bir parametre eksikse deger uydurma. Kullanicidan eksik bilgiyi iste.

- Manning n katsayisi, kanal egimi, yagis siddeti, akim katsayisi gibi muhendislik girdilerini kullanici vermediyse kendin secme.

- Bir yagis serisinin kurak veya nemli oldugunu soylemeden once SPI hesabi gerekiyorsa calculate_spi aracini kullan.

- Aracin dondurdugu sayisal sonucu esas al ve sonucu degistirme.

- Guncel veya dis kaynaktan dogrulanmasi gereken bilgiler icin internet_search aracini kullan.

- Selamlasma, sohbet ve kavramsal sorular icin arac cagirmana gerek yok.

- Kanal yeterliligi sorularinda arac sonucu YETERLI ise cevaba "Evet", YETERSIZ ise "Hayir" diye basla. Sonucla celisen bir ifade kullanma.

- Arac sonucundaki teknik terimleri anlamlarini degistirecek sekilde yeniden adlandirma. Ornegin "uniform akis" ifadesini aynen koru.

- SPI sonucunu yorumlarken yalnizca toolun belirttigi son tarihteki sinifi soyle. Tum veri serisinin genel olarak kurak, nemli, normal veya dengeli oldugunu soyleme ve gelecege yonelik devam edecegi anlamina gelen yorum yapma.

- Kullanici SPI grafigi, cizim, plot veya gorsellestirme isterse plot_spi_series aracini kullan. Grafik veya cizim sonucu olusturuldugunda dosya yolunu kullaniciya bildir.

- Kullanici internet_search icin belirli bir sonuc sayisi isterse max_results degerini ayni sayi olarak kullan.

- internet_search aracinin dondurdugu kaynak basliklarini ve URL'leri aynen kullan. Basliklari yeniden adlandirma, URL'leri degistirme veya arac sonucunda bulunmayan kaynak ekleme.

- internet_search araci yalnizca baslik ve URL donduruyorsa kaynaklarin icerigi hakkinda ek aciklama uretme. Yalnizca arac sonucunda gercekten bulunan bilgileri aktar.

- Herhangi bir arac cagrildiktan sonra nihai cevabi arac sonucuna dayandir. Aracin dondurmedigi sayisal deger, kaynak, URL veya teknik sonuc ekleme.

- HidroRisk bir on degerlendirme asistanidir; sonuclari nihai muhendislik projesi veya resmi onay olarak sunma.
"""


parser = argparse.ArgumentParser(
    description="Ollama tabanli HidroRisk asistani."
)

parser.add_argument(
    "--chat-model",
    default=ollama_client.CHAT_MODEL,
    help="Ollama sohbet modeli",
)

args = parser.parse_args()


def run_tool_calls(tool_calls: list[dict]) -> list[dict]:
    """Modelin istedigi araclari calistirir ve sonuclari mesaj formatinda dondurur."""

    messages = []

    for call in tool_calls:
        name = call["function"]["name"]
        arguments = call["function"].get("arguments") or {}

        print(f"\n[TOOL] {name}({arguments})")

        function = tools.TOOLS.get(name)

        if function is None:
            output = f"'{name}' adinda bir arac yok."
        else:
            try:
                output = function(**arguments)
            except Exception as exc:  # arac hatasi sohbeti bitirmesin
                output = f"Arac calistirilamadi: {exc}"

        messages.append(
            {
                "role": "tool",
                "tool_name": name,
                "content": output,
            }
        )

    return messages


print("=" * 60)
print("                         HIDRORISK")
print("          Yerel Hidroloji ve Hidrolik Risk Asistani")
print("=" * 60)
print()
print(f"Model : {args.chat_model}")
print()
print("Araclar:")
print("  [1] Pik Debi Hesabi")
print("  [2] Acik Kanal Kapasitesi")
print("  [3] SPI Kuraklik Analizi")
print("  [4] SPI Grafik Olusturma")
print("  [5] Internet Aramasi")
print()
print("Cikmak icin: cik")
print("-" * 60)
print()


messages = [{"role": "system", "content": SYSTEM_PROMPT}]


while True:
    try:
        question = input("Siz > ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if not question:
        continue

    if question.lower() in {"cik", "cık", "çık", "çik", "exit", "quit"}:
        break

    messages.append({"role": "user", "content": question})

    try:
        for _ in range(MAX_TOOL_ROUNDS):
            message = ollama_client.chat(
                messages,
                model=args.chat_model,
                tools=tools.TOOL_SCHEMAS,
            )

            messages.append(message)

            tool_calls = message.get("tool_calls")

            if not tool_calls:
                break

            messages.extend(run_tool_calls(tool_calls))

    except RuntimeError as exc:
        print(f"\nHata: {exc}\n")
        continue

    print(f"\nHidroRisk > {(message.get('content') or '').strip()}\n")
print("-" * 60)