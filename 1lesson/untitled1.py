import csv

from ping3 import ping


domains = ['youtube.com',"web.telegram.org","profi.ru","vk.com","sky.pro","drive.google.com","mail.google.com","yandex.ru","kwork.ru","baserow.io"]
RTT={}
RTT_par={}
RTT_max_par={}
RTT_min_par={}
lost={}
results=[]
for domain in domains:
    rtt_list =[]
    for _ in range(4):
      rtt = ping(domain, timeout=2)
      if rtt != None:
        rtt_list.append(rtt)
    RTT[domain] = rtt_list
    if RTT[domain]:
      RTT_par[domain] = sum(RTT[domain]) / len(RTT[domain])
    else:
      RTT_par[domain] = None
    lost[domain]= 100*((4- len(RTT[domain]))/4)
    if RTT[domain]:
      RTT_max_par[domain] = max(RTT[domain])
    else:
      RTT_max_par[domain] = None
    if RTT[domain]:
      RTT_min_par[domain] = min(RTT[domain])
    else:
      RTT_min_par[domain] = None
    results.append({
      'domain': domain,
      'avg_rtt_sec': RTT_par[domain],
      'max_rtt_sec': RTT_max_par[domain],
      'loss_pct': lost[domain],
      'min_rtt_sec': RTT_min_par[domain]
    })
    
fieldnames=['domain','avg_rtt_sec','max_rtt_sec','loss_pct','min_rtt_sec']
with open("list.csv","w") as info:
  writer = csv.DictWriter(info,fieldnames=fieldnames)
  writer.writeheader()
  writer.writerows(results)





