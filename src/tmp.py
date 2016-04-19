s = '0x4E000x4e02'
s = r'\u4E00\u4E02'

l = s.strip().split(['\\u', '0x']['0x' in s])[1:]

l2 = ''.join([unichr(int(x, 16)).encode('utf-8') for x in l])

u2c = lambda s: ''.join([unichr(int(x, 16)).encode('utf-8')
                         for x in s.strip().split(['\\u', '0x']['0x' in s])[1:]])

print l, l2
print u2c(s)
