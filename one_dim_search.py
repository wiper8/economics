def one_dim_search(f, XBAR, alpha0, d, alphaBAR):
    A=0
    R=0
    CFLG=0
    KL=-10**30
    FA=f(XBAR)
    CTR=0
    B=min(alpha0, alphaBAR)
    while True:
        alpha = B
        FB = f(XBAR + alpha*d)
        if FB <= FA and SLPFLG != 1:
            break
        else:
            B=B/2
            KL=FB

    C=2*B
    CFLG=1
    