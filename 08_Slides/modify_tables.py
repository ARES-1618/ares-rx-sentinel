import sys
from bs4 import BeautifulSoup
import re

def main():
    filepath = 'ARES_RX_Sentinel_Presentation.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Find slide 6 (Threat Model)
    slide_6 = soup.find('div', id='slide-6')
    if slide_6:
        table = slide_6.find('table', class_='data-table')
        if table:
            # Header
            thead_tr = table.find('thead').find('tr')
            ths = thead_tr.find_all('th')
            # 6 cols: ID, Kategori Serangan, Karakteristik Stimulus, Target Host, Lapisan Detektor, Respons Silikon
            # Reduce to 4: [ID], [Nama Serangan + Stimulus], [Lapisan Detektor], [Respons Silikon]
            ths[1].string = "Nama Serangan & Stimulus"
            ths[2].decompose() # Remove Karakteristik Stimulus
            ths[3].decompose() # Remove Target Host
            
            # Body
            for tr in table.find('tbody').find_all('tr'):
                tds = tr.find_all('td')
                # Combine td[1], td[2]
                tds[1].append(soup.new_tag('br'))
                tds[1].append(soup.new_string(tds[2].text.strip()))
                tds[2].decompose()
                tds[3].decompose()

    # Find slide 15 (Verification Results)
    slide_15 = soup.find('div', id='slide-15')
    if slide_15:
        table = slide_15.find('table', class_='data-table')
        if table:
            # 11 columns in original
            # thead_tr = table.find('thead').find_all('tr')[1] # the second TR has the headers usually, or maybe it's just 1 TR. Let's find all TH
            # ths = thead_tr.find_all('th') if thead_tr else table.find('thead').find('tr').find_all('th')
            # wait, let's just find the first TR in thead
            thead_tr = table.find('thead').find('tr')
            ths = thead_tr.find_all('th')
            
            # Original headers usually: [0]Vektor, [1]Skenario, [2]Total Siklus, [3]Siklus Fault, [4]Latch Cycle, [5]T_latch, [6]T_isolate, [7]Bus Out, [8]Status, ... wait let's check
            # I will just keep by index. I need: [Vektor], [Skenario], [Total Siklus], [Siklus Fault], [Bus Out], [Status]
            # Since I don't know exact indexes, I will match by text
            keep_headers = ['Vektor', 'Skenario', 'Total Siklus', 'Siklus Fault', 'Bus Out', 'Status']
            keep_indices = []
            for i, th in enumerate(ths):
                text = th.text.strip()
                if any(k.lower() in text.lower() for k in keep_headers):
                    keep_indices.append(i)
            
            # Remove from headers
            for i, th in reversed(list(enumerate(ths))):
                if i not in keep_indices:
                    th.decompose()
            
            # Remove from body
            for tr in table.find('tbody').find_all('tr'):
                tds = tr.find_all('td')
                for i, td in reversed(list(enumerate(tds))):
                    if i not in keep_indices:
                        td.decompose()
                        
            # Add callout
            table_container = table.find_parent('div', class_='table-container')
            callout = soup.new_tag('div', **{'class': 'callout callout-info mt-2'})
            strong = soup.new_tag('strong')
            strong.string = "Catatan:"
            callout.append(strong)
            callout.append(soup.new_string(" T_latch = 1 cycle, T_isolate = 0 cycles untuk SEMUA vektor AV01–AV08"))
            table_container.insert_after(callout)

    # Find slide 4 (Literature Gap)
    slide_4 = soup.find('div', id='slide-4')
    if slide_4:
        table = slide_4.find('table', class_='data-table')
        if table:
            # We want to split this table into 2 parts. 
            # Top part: Sumbu Evaluasi 1-4 (rows 0-3 in tbody)
            # Bottom part: Sumbu 5-6 (rows 4-5 in tbody) with styling row-highlight
            
            thead = table.find('thead')
            # Shorten header names
            ths = thead.find('tr').find_all('th')
            ths[1].string = "SW ISR"
            ths[2].string = "Bus Firewall"
            ths[3].string = "Crypto Engine"
            ths[4].string = "WuRx"
            ths[5].string = "ARES-RX"
            
            tbody = table.find('tbody')
            trs = tbody.find_all('tr')
            
            table2 = soup.new_tag('table', **{'class': 'data-table mt-2'})
            thead2 = soup.new_tag('thead')
            tr_head = soup.new_tag('tr')
            for th in ths:
                new_th = soup.new_tag('th')
                new_th.string = th.text
                tr_head.append(new_th)
            thead2.append(tr_head)
            table2.append(thead2)
            
            tbody2 = soup.new_tag('tbody')
            
            for tr in trs[4:]:
                tr['class'] = 'row-highlight'
                tbody2.append(tr.extract())
            
            table2.append(tbody2)
            
            table_container = table.find_parent('div', class_='table-container')
            table_container.append(table2)

    # Find slide 19 (CTA)
    slide_19 = soup.find('div', id='slide-19')
    if slide_19:
        # Tambahkan efek animated neon border/glow pada container utama
        # I will add an inline style to the slide-body or the slide itself, or just replace classes.
        # Actually, let's wrap the slide body with a border.
        slide_body = slide_19.find('div', class_='slide-body')
        if slide_body:
            slide_body['style'] = 'animation: glow-pulse 3s infinite alternate; border: 1px solid var(--accent-cyan); border-radius: 12px; padding: 1.5rem; background: rgba(0, 212, 255, 0.03);'
        
        # Buat 4 keunggulan utama tampil dalam layout lebih visual (icon + teks besar)
        ul = slide_19.find('ul', class_='bullet-list')
        if ul:
            ul['style'] = 'display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'
            for li in ul.find_all('li'):
                li['style'] = 'background: var(--bg-card); padding: 1rem; border-radius: 8px; border: 1px solid var(--accent-green); display: flex; flex-direction: column; text-align: center;'
                # Make strong text larger
                strong = li.find('strong')
                if strong:
                    strong['style'] = 'font-size: 1.1rem; color: var(--accent-green); margin-bottom: 0.5rem;'
        
        # Tambahkan highlight box berwarna cyan yang lebih menonjol untuk Call to Action
        # Look for the card containing Call to Action
        card_gold = slide_19.find('div', class_='card-gold')
        if card_gold:
            card_gold['class'] = 'card' # remove gold to make it cyan-based
            card_gold['style'] = 'border-color: var(--accent-cyan); box-shadow: 0 0 20px var(--accent-cyan); background: rgba(0, 212, 255, 0.08);'
            title = card_gold.find('h3')
            if title:
                title['class'] = 'card-title cyan'
                title.string = "🚀 Mengawal Kedaulatan Digital Indonesia"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == '__main__':
    main()
