from time import perf_counter
n = 10000
kq = []
check = [True]*n
def xuli(n):
    for i in range(2,n):
        for j in range(i*i,n,i):
            check[j]=False
    for i in range(2,n):
        if check[i]:
            kq.append(i)
    print(kq)
bt = perf_counter()
kt = perf_counter()
xuli(n)
print(kt-bt)