import json
import os
import shutil


with open('test.json') as json_file:
	data = json.load(json_file)

links = data["links"]

start_subnet = 1
end_subnet = 30



#fonction to distribute automatically ipv6 address 
def distribute():
	i=1
	while i <= len(links):
		
		original_string = "192.168.a."
		subnet = original_string.replace("a", str(i))
		
		n = 1
		for router in links[i-1]:
			interface_address = subnet + str(n)
			n+=1
			for inter in links[i-1][router]:
				links[i-1][router][inter] = interface_address
				#print(str(links[i-1][router]) + " has the address " + links[i-1][router][inter])
		i+=1
	return links

links=distribute()
print(links)
	
#fonction for output ipv6 address automatically		
def address(routername, intername):
	i=1
	while i <= len(links):
		for key, router in links[i-1].items():
			if str(key)==routername:
				for key, inter in router.items():
					if str(key)==intername:
						#f.write(f'ipv6 address {inter}/64\n')
						str1=f"{inter}" 
						return str1
		i+=1
#fonction for print subnet corresponding	
def network(routername):
	i=1
	while i <= len(links):
		
		original_string = "192.168.a."
		subnet = original_string.replace("a", str(i))
		
		n = 1
		for key, router in links[i-1].items():
			network= subnet
			if str(key)==routername:
				f.write(f" network {network}/64\n")
		i+=1
	
#fonction for print if there exist protocole rip or ospf
def RipOspf(routername,intername):
	for router in data['routers']:
		if router['name']==routername:
			for interface in router['interfaces']:
				if interface['name']==intername:
					if 'RIP' in interface:
						 f.write(" ipv6 rip " + interface['RIP'] + " enable\n")
					if 'OSPF' in interface:
						 f.write(" ipv6 ospf 1 area "+ interface['OSPF']+ "\n")
					
#print if il exist ospf interface
def ifOspf(routername):
	for router in data['routers']:
		if router['name']==routername:
			rid=str(router['router_id'])
			for interface in router['interfaces']:
					if 'OSPF' in interface:
						 f.write("ipv6 router ospf "+interface['OSPF'] +"\n")
						 f.write(" router-id "+ rid+ "\n")
						 if 'AS' in interface:
						 	f.write("redistribute bgp "+interface['AS']+"\n")
						 break
					if 'RIP' in interface:
						 f.write("ipv6 router rip " +interface['RIP']+"\n")
						 f.write("redistribute connected\n")
						 break

#print bgp neighbor from each interface (without loopback)
def neighbor(routername,ASfind):
	add = []
	for router in data['routers']:
		if router['name']!=routername:
			for interface in router['interfaces']:
				if 'AS' in interface and interface['AS']==ASfind:
					add.append(address(router['name'],interface['name']))
					#f.write("bgp neighbor "+ str(add)+" remote-as "+ str(ASfind)+ " \n")
					#f.write("bgp neighbor "+ str(add)+" activate \n")
	return add

def findloop(routername, ASfind):
	for router in data['routers']:
		if router['name']!=routername and router['AS']==ASfind:
			for interface in router['interfaces']:
				if interface['name']=="Loopback0":
					f.write(" neighbor "+ interface['address']+" remote-as "+ router['AS']+ "\n")
					f.write(" neighbor "+interface['address']+ " update-source "+ interface['name']+"\n")
		if 'EBGP' in router and router['EBGP']==routername:
			for interface in router['interfaces']:
				if interface['name']=="Loopback0":
					f.write(" neighbor "+ interface['address']+" remote-as "+ router['AS']+ "\n")
					f.write(" neighbor "+interface['address']+ " update-source "+ interface['name'] +"\n")
				#elif 'AS' in interface:
				if interface['name']==router['EBGPinter']:
					a=address(router['name'],interface['name'])
					f.write(" neighbor "+ str(a) +" remote-as "+ router['AS']+ "\n")
				
					
def activate(routername, ASfind):
	for router in data['routers']:
		if router['name']!=routername and router['AS']==ASfind:
			for interface in router['interfaces']:
				if interface['name']=="Loopback0":
					f.write(" neighbor "+ interface['address']+" activate\n")
		if 'EBGP' in router and router['EBGP']==routername:
			for interface in router['interfaces']:
				if interface['name']=="Loopback0":
					f.write(" neighbor "+ interface['address']+" activate\n")
				#elif 'AS' in interface:
				if interface['name']==router['EBGPinter']:
					a=address(router['name'],interface['name'])
					f.write(" neighbor "+ str(a) +" activate\n")

	
#create cfg file
for router in data['routers']:
	with open("i"+router['name'] +"_startup-config" + ".cfg", "w") as f:
				
		#the head unchangeable part
		f.write("!\n")
		f.write("!\n")
		f.write("version 15.2\n")
		f.write("service timestamps debug datetime msec\n")
		f.write("service timestamps log datetime msec\n")
		f.write("!\n")
		f.write("hostname R"+router['name']+"\n")
		f.write("!\n")
		f.write("boot-start-marker\n")
		f.write("boot-end-marker\n")
		f.write("!\n")
		f.write("!\n")
		f.write("no aaa new-model\n")
		f.write("no ip icmp rate-limit unreachable\n")
		f.write("ip cef\n")
		f.write("!\n")
		f.write("!\n")
		f.write("no ip domain lookup\n")
		f.write("ipv6 unicast-routing\n")
		f.write("ipv6 cef\n")
		f.write("!\n")
		f.write("!\n")
		f.write("multilink bundle-name authenticated\n")
		f.write("!\n")
		f.write("ip tcp synwait-time 5\n")
		f.write("! \n")
		f.write("!\n")


#print ip address and interface part
		for interface in router['interfaces']:
			if interface['name'] == "Loopback0":
				f.write(f"interface {interface['name']}\n")
				f.write(f" no ip address\n")
				f.write(" ipv6 address " + interface['address'] + "/64\n")
				f.write(f" ipv6 enable\n")
				RipOspf(router['name'],interface['name'])
				f.write(f"!\n")
			
			elif interface['name'] == "FastEthernet0/0":
				f.write(f"interface {interface['name']}\n")
				f.write(f" no ip address\n")
				f.write(f" duplex full\n")    #exception for inter f0/0
				#f.write(f" ipv6 address {interface['ipv6_address']}/{interface['subnet_mask']}\n")
				d=str(address(router['name'],interface['name']))
				f.write(" ipv6 address " + d + "/64\n")
				f.write(f" ipv6 enable\n")
#fonction to check if it contained rip or ispf
				RipOspf(router['name'],interface['name'])
				f.write(f"!\n")
				f.write(f"!\n")
			else:
				f.write(f"interface {interface['name']}\n")
				if 'AS' in interface:
					f.write(f" no ip address\n")
					f.write(f" negotiation auto\n")
					
#address(router['name'],interface['name'])
					d=str(address(router['name'],interface['name']))
					f.write(" ipv6 address " + d + "/64\n")
					

					f.write(f" ipv6 enable\n")
					##f.write(f" ipv6 rip 1 enable\n")
					RipOspf(router['name'],interface['name'])
					f.write(f"!\n")
					f.write(f"!\n")
				else:
					f.write(f" no ip address\n")
					f.write(f" shutdown\n")
					f.write(f" negotiation auto\n")
					f.write(f"!\n")
					f.write(f"!\n")	
	
		f.write(f"!\n")
		f.write(f"!\n")
		f.write(f"!\n")
		ifOspf(router['name'])
		f.write(f"!\n")
		f.write(f"!\n")
			
		#write bgp neighbor		
		f.write("router bgp "+ router['AS']+"\n")			
		f.write(f" bgp router-id {router['router_id']}\n")
		f.write(f" bgp log-neighbor-changes\n")
		f.write(f" no bgp default ipv4-unicast\n")
		
#fonction to print bgp neighbor (without loopback version)
		'''for interface in router['interfaces']:
			if 'AS' in interface:
				add=neighbor(router['name'], interface['AS'])
				for adds in add:
					f.write("bgp neighbor "+ str(adds)+" remote-as "+ interface['AS']+ " \n")
				break'''
#fonction with loopback interface
		findloop(router['name'],router['AS'])
		
		
		f.write(f"!\n")	
		f.write(f"!\n")	
		f.write(f"!\n")	
		f.write(f"address-family ipv4\n")	
		f.write(f"exit-address-family\n")	
		f.write(f"!\n")	
		f.write(f"address-family ipv6\n")
		for interface in router['interfaces']:
			if 'OSPF' in interface:
				f.write(" redistribute ospf "+interface['OSPF']+"\n")	
				break
			if'RIP' in interface:
				f.write(" redistribute rip "+interface['RIP']+"\n")
				break
#Fonction to print network related to router
		network(router['name'])
#fonction activate neighbor bgp without loopback version
		'''for interface in router['interfaces']:
			if 'AS' in interface:
				add=neighbor(router['name'], interface['AS'])
				for adds in add:
					f.write("bgp neighbor "+ str(adds)+" activate \n")
				break'''
		activate(router['name'],router['AS'])
		
		f.write(f"exit-address-family\n")	 
		f.write(f"!\n")	
		f.write(f"ip forward-protocol nd\n")	
		f.write(f"!\n")	
		f.write(f"no ip http server\n")	
		f.write(f"no ip http secure-server\n")	
		f.write(f"!\n")	
		
#write for rip or ospf
		ifOspf(router['name'])
		

		#the end unchangeable part
		f.write("!\n")
		f.write("control-plane\n")
		f.write("!\n")
		f.write("!\n")
		f.write("line con 0\n")
		f.write(" exec-timeout 0 0\n")
		f.write(" privilege level 15\n")
		f.write(" logging synchronous\n")
		f.write(" stopbits 1\n")
		f.write("line aux 0\n")
		f.write(" exec-timeout 0 0\n")
		f.write(" privilege level 15\n")
		f.write(" logging synchronous\n")
		f.write(" stopbits 1\n")
		f.write("line vty 0 4\n")
		f.write(" login\n")
		f.write("!\n")
		f.write("!\n")
		f.write("end\n")

#file_list = ["R1.cfg","R2.cfg","R3.cfg"]
root_dir = "project-files"

n = 1
while n<=14:
	src=f"i{n}_startup-config.cfg"
	for root, dirs, files in os.walk(root_dir):
		for file in files:
			if file == src:
				dst = os.path.join(root, file)
				shutil.copy2(src, dst)
				break

	n+=1








