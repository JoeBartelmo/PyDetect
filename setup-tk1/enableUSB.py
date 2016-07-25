data = None
with open('/boot/extlinux/extlinux.conf', 'r+') as file:
	data=file.read()
	data = data.replace("usb_port_owner_info=0", "usb_port_owner_info=2")
	file.seek(0)
	file.write(data)
	file.truncate()
	file.close()
	print data

