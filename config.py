# !/urs/bin/python3
import json

from datetime import datetime
now = datetime.now()
from math import floor

#fonction pour ouvrir et lire le fichier json 
def open_file(_file) :
	# Opening JSON file
	f = open(_file)
	  
	# returns JSON object as a dictionary
	data = json.load(f)
	f.close()
	return data


filename=str(input('File name? -->')) #le nom de fichier json
json_object = open_file(filename)


def write_file() :
    script="!\n\n!\n!Last configuration change at "+now.strftime("%H:%M:%S")+" UTC "+now.strftime("%a %b %d %Y")+"\n!\n"
    script+="version 15.2\n"
    script+="service timestamps debug datetime msec\n"
    script+="service timestamps log datetime msec\n"
    script+="!\nhostname "+r['hostname']+"\n!\n"
    script+="boot-start-marker\n"
    script+="boot-end-marker\n!\n!\n!\n"
    script+="no aaa new-model\n"
    script+="no ip icmp rate-limit unreachable\n"
    script+="ip cef\n!\n!\n!\n!\n!\n!\n"
    script+="no ip domain lookup\n"
    script+="ipv6 unicast-routing\n"
    script+="ipv6 cef\n!\n!\n"
    script+="multilink bundle-name authenticated\n"
    script+="!\n!\n!\n!\n!\n!\n!\n!\n!\n"
    script+="ip tcp synwait-time 5\n"
    script+="!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n!\n"
    
    for x in r['interfaces']:
        script+="interface "+str(x['interface_name'])+"\n"
        script+=" no ip address\n"
        
        if str(x['interface_name'])=="Loopback1":
            script+=" ipv6 address "+str(r['id'])+"::"+str(r['id'])+"/128\n"
            
        elif str(x['interface_name'])=="FastEthernet0/0":
            script+=" duplex full\n"
            script+=" ipv6 address 2001:192:"+str(r['AS_number'])+":"
            if r['id']<x['link']:
                script+=str(r['id'])+str(x['link'])
            else:
                script+=str(x['link'])+str(r['id'])
            
            script+="::"+str(r['id'])+"/64\n"
            
        elif r['border_router']!=0 and x['border_interface']!=0 :
        #elif r['border_router']!=0 and str(x['interface_name'])=="GigabitEthernet1/0" and x['border_interface']!=0 :
            script+=" negotiation auto\n"
            border_subnet="2001:192:"
            
            if r['id']<x['link']:
                border_subnet+=str(floor(r['id']/10))+str(floor(x['link']/10))+":"
            else:
                border_subnet+=str(floor(x['link']/10))+str(floor(r['id']/10))+":"
                
            if r['id']<x['link']:
                border_subnet+=str(r['id'])+str(x['link'])
            else:
                border_subnet+=str(x['link'])+str(r['id'])
            border_subnet+="::"
            
            script+=" ipv6 address "+border_subnet+str(r['id'])+"/64\n"
        else:
            script+=" negotiation auto\n"
            script+=" ipv6 address 2001:192:"+str(r['AS_number'])+":"
            if r['id']<x['link']:
                script+=str(r['id'])+str(x['link'])
            else:
                script+=str(x['link'])+str(r['id'])
            
            script+="::"+str(r['id'])+"/64\n"
        
        script+=" ipv6 enable\n"
         
        if r['IGP_protocol']=="ospf":
            script+=" ipv6 ospf "+str(r['id'])+" area 0\n"
            if x['ospf_cost_apply']!=0:
                script+=" ipv6 ospf cost "+str(x['ospf_cost'])+"\n"
        elif r['IGP_protocol']=="rip":
            script+=" ipv6 rip "+r['rip_process_name']+" enable\n"
        script+="!\n"
        
        
        
    if r['bgp_apply']!=0 :
        script+="router bgp "+str(r['AS_number'])+"\n"
        script+=" bgp router-id "
        script+=str(r['id'])
        for x in range(3):
            script+="."+str(r['id'])
        script+="\n"
        script+=" bgp log-neighbor-changes\n"
        script+=" no bgp default ipv4-unicast\n"
        

        for y in json_object['routers'] :
            if (y['AS_number']==r['AS_number'] and y['id']!=r['id']):
                script+=" neighbor "+str(y['id'])+"::"+str(y['id'])+" remote-as "+str(y['AS_number'])+"\n"
                script+=" neighbor "+str(y['id'])+"::"+str(y['id'])+" update-source Loopback1\n"
         
        if r['border_router']!=0:
            for x in r['ebgp']['neighbors']:
                script+=" neighbor "+border_subnet+str(x['id'])+" remote-as "+str(floor(x['id']/10))+"\n"
        script+=" !\n"
        script+=" address-family ipv4\n"
        script+=" exit-address-family\n"
        script+=" !\n"
        
        script+=" address-family ipv6\n"
        if r['border_router']!=0:
            if r['IGP_protocol']=="rip":
                script+="  redistribute rip "+r['rip_process_name']+"\n"
            elif r['IGP_protocol']=="ospf":
                script+="  redistribute ospf "+str(r['id'])+"\n"
                
            script+="  network 2001:192:"+str(r['AS_number'])+"::/48\n"
            script+="  network "+border_subnet+"/64\n"
            script+="  aggregate-address 2001:192:"+str(r['AS_number'])+"::/48 summary-only\n"
            script+="  aggregate-address "+border_subnet+"/64 summary-only\n"
            
            
        
        
        
        for y in json_object['routers'] :
            if (y['AS_number']==r['AS_number'] and y['id']!=r['id']):
                script+="  neighbor "+str(y['id'])+"::"+str(y['id'])+" activate\n"
                
        
        
        if r['border_router']!=0:
            for x in r['ebgp']['neighbors']:
                script+="  neighbor "+border_subnet+str(x['id'])+" activate\n"
                
        if r['border_router']!=0 and r['local_pref']['metric_apply']!=0:
            for x in r['local_pref']['link']:
                script+="  neighbor "+border_subnet+str(x['id'])+" route-map "+x['name']+" "+x['direction']+"\n"
        
        script+=" exit-address-family\n!\n"
        script+="ip forward-protocol nd\n!\n!\n"
        script+="no ip http server\n"
        script+="no ip http secure-server\n!\n"

        if r['IGP_protocol']=="ospf":
            script+="ipv6 router ospf "+str(r['id'])+"\n"
            script+=" router-id "
            script+=str(r['id'])
            for x in range(3):
                script+="."+str(r['id'])
            script+="\n"
            script+=" redistribute connected\n"
        elif r['IGP_protocol']=="rip":
            script+="ipv6 router rip "+ r['rip_process_name']+"\n"
            script+=" redistribute connected\n"
            
        if r['border_router']!=0 and r['local_pref']['metric_apply']!=0:
            for x in r['local_pref']['link']:
                script+="!\n!\nroute-map "+x['name']+" permit 10\n"
                script+=" set local-preference 400\n"
        script+="!\n!\n!\n!\ncontrol-plane\n!\n!\n"
        script+="line con 0\n"
        script+=" exec-timeout 0 0\n"
        script+=" privilege level 15\n"
        script+=" logging synchronous\n"
        script+=" stopbits 1\n"
        script+="line aux 0\n"
        script+=" exec-timeout 0 0\n"
        script+=" privilege level 15\n"
        script+=" logging synchronous\n"
        script+=" stopbits 1\n"
        script+="line vty 0 4\n"
        script+=" login\n!\n!\nend"
    return script		
			
#print(write_file())
for r in json_object['routers'] :
    
    #ecrire dans le fichier json
    destination=r['hostname']+".cfg"
    with open(destination, "w") as outfile:
        outfile.write(write_file())
