with open('website/index.html') as f:
    c = f.read()
print('Old paths (../):', c.count('src="../'))
print('New paths (./):', c.count('src="./'))
