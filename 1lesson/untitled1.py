import csv

from ping3 import ping

domens = ['youtube.com',"web.telegram.org","profi.ru","vk.com","sky.pro","drive.google.com","mail.google.com","yandex.ru","kwork.ru","baserow.io"]
RTT={}
RTT_par={}
RTT_max_par={}
RTT_min_par={}
lost={}
results=[]
for domen in domens:
    rtt_list =[]
    for j in range(4):
      a = ping(domen, timeout=2)
      if a != None:
        rtt_list.append(a)
    RTT[domen] = rtt_list
    if RTT[domen]:
      RTT_par[domen] = sum(RTT[domen]) / len(RTT[domen])
    else:
      RTT_par[domen] = None
    lost[domen]= 100*((4- len(RTT[domen]))/4)
    if RTT[domen]:
      RTT_max_par[domen] = max(RTT[domen])
    else:
      RTT_max_par[domen] = None
    if RTT[domen]:
      RTT_min_par[domen] = min(RTT[domen])
    else:
      RTT_min_par[domen] = None
    results.append({
      'domain': domen,
      'avg_rtt_sec': RTT_par[domen],
      'max_rtt_sec': RTT_max_par[domen],
      'loss_pct': lost[domen],
      'min_rtt_sec': RTT_min_par[domen]
    })
filednames=['domain','avg_rtt_sec','max_rtt_sec','loss_pct','min_rtt_sec']
with open("spisok.csv","w") as spis:
  writer = csv.DictWriter(spis,fieldnames=filednames)
  writer.writeheader()
  writer.writerows(results)





