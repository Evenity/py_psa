import numpy as np
from numpy import exp
from numpy import pi
from numpy import sqrt
from numpy import log
import numpy.testing as nut
import scipy.integrate as si
import mpmath as mp
import matplotlib.pylab as plt

#DEFINITION OF MATHEMATICAL OBJECTS
#Definition of the transformation matrices

def matrixFlight(L):                                                       # For a flight path of length
    return np.array([[1,-L,0],[0,1,0],[0,0,1]])

def matrixMonoPlane(b, ThetaB):                                         # For a perfect flat crystal monochromator
    return np.array([[b,0,0],[0,1/b,(1-1/b)*np.tan(ThetaB)],[0,0,1]])

def matrixMonoBent(b, Fc, ThetaB):                                     # For a perfect curved crystal monochromator (meridionally and sagitally focusing)
    return np.array([[b,0,0],[1/Fc,1/b,(1-1/b)*np.tan(ThetaB)],[0,0,1]])

def matrixMonoMosaic(ThetaB):                                             # For a mosaic monochromator
    return np.array([[1,0,0],[0,-1,2*np.tan(ThetaB)],[0,0,1]])

def matrixMirrorPlane(IncAng, Sigma, Lambda, Delta):                      # For the plane mirror
    return exp(-(4*pi*np.sin(IncAng)*Sigma/Lambda)**2)*np.array([[1,0,0],[Delta,1,0],[0,0,1]])

def matrixMirror(IncAng, Sigma, Lambda, Delta, Fm, S):                      # For the bent and toroidal mirrors
    return exp(-(4*pi*np.sin(IncAng)*Sigma/Lambda)**2)*np.array([[1,0,0],[(1+S*Fm*Delta)/Fm,1,0],[0,0,1]])

def matrixCompLensPara(F):                                                 # For the compound refractive lenses with parabolic holes
    return np.array([[1,0,0],[1/F,1,0],[0,0,1]])

def matrixCompLensCirc(Coef, F):                                           # For the compound refractive lenses with circular holes
    return np.array([[1,0,0],[Coef/F,1,0],[0,0,1]])

def matrixMultilayer(Fmu):                                                  # For the multilayer
    return np.array([[1,0,0],[1/Fmu,1,0],[0,0,1]])

#Definition of the beam source

def sourceXXP(x, xp, SigmaXSource, SigmaXPSource):
    return exp(-( (x/SigmaXSource)**2 + (xp/SigmaXPSource)**2) / 2 )
def sourceYYP(y, yp, SigmaYSource, SigmaYPSource, GammaSource):
    return exp( -( (y/SigmaYSource)**2 + ((yp-GammaSource*y)/SigmaYPSource)**2)/2 )
def sourceLambda(dl, SigmaSLambda):
    return exp(-dl**2/2/SigmaSLambda**2)

#Definition of the acceptance windows of the optical parts

def cotan(x):
    return 1/np.tan(x)

def acceptanceSlit(y, Aperture, calctype):                                                           #Slit acceptance
    if calctype==0:
        return sqrt(6/pi) / sqrt(6*log(2)/pi) * exp( -(y/Aperture)**2/2*12)
    if calctype==1:
        return 1/sqrt(6*log(2)/pi)*exp(-y**2/(2*Aperture**2/2/pi))
    else:
        return 'the value for calctype is 0 or 1 you pipsqueak !'

def acceptancePin(y, Diameter):                                                            #Pinhole acceptance
    return sqrt(8/pi) * exp ( -(y/Diameter)**2/2*16 )

def acceptanceAngleMonoPlane(yp, DeltaLambda, ThetaB, Wd, RMono, RInt):                #Plane monochromator angle acceptance
    return RMono*RInt*sqrt(6/pi)/Wd * exp( -(yp-DeltaLambda*np.tan(ThetaB))**2 / (2*Wd**2/12))

def acceptanceWaveMonoPlane(DeltaLambda, SigmaYp, ThetaB, Wd):                        #Plane monochromator wave acceptance
    return sqrt(6/pi) * exp( - (DeltaLambda)**2 / (2*(SigmaYp**2+Wd**2/12)*cotan(ThetaB)**2) )

def acceptanceAngleMonoMosaic(yp, DeltaLambda, ThetaB, eta, RInt):                       #Mosaic monochromator angular acceptance
    return RInt*sqrt(6/pi)/eta * exp(- (yp-DeltaLambda*np.tan(ThetaB))**2 / eta**2 /2 )

def acceptanceWaveMonoMosaic(DeltaLambda, SigmaYp, ThetaB, eta):                        #Mosaic monochromator wave acceptance
    return sqrt(6/pi) * exp( - (DeltaLambda)**2 / 2 /((SigmaYp**2+eta**2)*cotan(ThetaB)**2))

def acceptanceAngleMonoBent(y, yp, DeltaLambda, Alpha, ThetaB, Wd, r, RMono, RInt):    #Curved monochromator angle acceptance
    return RMono*RInt*sqrt(6/pi)/Wd * exp( - (yp-y/r/np.sin(ThetaB+Alpha)-DeltaLambda*np.tan(ThetaB))**2/(2*Wd**2/12))

def acceptanceWaveMonoBent(DeltaLambda, ThetaB, DistanceFromSource, Wd, SigmaSource):  #Curved monochromator wave acceptance
    return sqrt(6/pi) * exp( -(DeltaLambda)**2 / (2*cotan(ThetaB)**2*((SigmaSource/DistanceFromSource)**2+Wd**2/12))   )

def acceptanceCompLensPara(x, Radius, Distance, Sigma):                                          #Compound refractive lense with parabolic holes acceptance
    return exp( -(x**2+Radius*Distance)/2/Sigma**2)

def acceptanceCompLensCirc(x, Radius, Distance, Sigma, FWHM):                                    #Compound refractive lense with circular holes acceptance
    return exp( -x**2/2/Sigma**2 -x**2*FWHM**2/8/Radius**2/Sigma**2 -x**2*FWHM**4/16/Sigma**2/Radius**4 -Radius*Distance/2/Sigma**2  )

def acceptanceAngleMulti(y, yp, DeltaLambda, ThetaML, Rml, Rowland, Ws):                #Multilayer angle acceptance
    return Rml*8/3*sqrt(log(2)/pi) * exp( -(-yp-y/Rowland/np.sin(ThetaML)-DeltaLambda*np.tan(ThetaML))**2*8*log(2)/2/Ws**2 )

def acceptanceWaveMulti(DeltaLambda, ThetaML, DistanceFromSource, Ws, SigmaSource):     #Multilayer wave acceptance
    return sqrt(6/pi) * exp( -(DeltaLambda)**2/2/((SigmaSource/DistanceFromSource)**2+Ws**2/8/log(2))/cotan(ThetaML)**2)


# Useful functions for the calculation part

def propagateMatrixList(x, xp, y, yp, dl, SigmaXSource, SigmaXPSource, SigmaYSource, SigmaYPSource, GammaSource, MatTabX, MatTabY, ListObject, bMonoX, bMonoY):
    # initiating variables, copies of the arrays are created
    MX = MatTabX.copy()
    MY = MatTabY.copy()
    MatTempX = np.array([x,xp,dl])
    MatTempY = np.array([y, yp, dl])
    # the case of single propagation has to be done separately because of a pb of range
    if len(MX)==1:
        MatTempX = np.dot(MX[0], MatTempX)
        MatTempY = np.dot(MY[0], MatTempY)
        NewSourceX = sourceXXP(MatTempX[0], MatTempX[1], SigmaXSource, SigmaXPSource)
        NewSourceY = sourceYYP(MatTempY[0], MatTempY[1], SigmaYSource, SigmaYPSource, GammaSource)
    # now we do the general case
    else :
        #first matrix multiplication
        for i in range(len(MX)-1, -1, -1):
            MatTempX = np.dot(MX[i], MatTempX)
            MatTempY = np.dot(MY[i], MatTempY)
        NewSourceX = sourceXXP(MatTempX[0], MatTempX[1], SigmaXSource, SigmaXPSource)
        NewSourceY = sourceYYP(MatTempY[0], MatTempY[1], SigmaYSource, SigmaYPSource, GammaSource)
        del MX[0]
        del MY[0]
        k = 0
        #we are going to do our matrix product, then apply the acceptance if needed and calculate the new resulting
        # source. Once this is done, we erase the two first matrices and do this again until our arrays are empty
        while MX!=[] and MY!=[]:
            for i in range(len(MX)-1,-1,-1):
                MatTempX = np.array([x, xp, dl])
                MatTempY = np.array([y, yp, dl])
                MatTempX = np.dot(MX[i],MatTempX)
                MatTempY = np.dot(MY[i], MatTempY)
            if ListObject[k][0] == 'Slit':
                NewSourceX = NewSourceX * acceptanceSlit(MatTempX[0], ListObject[k][1], ListObject[k][4])
                NewSourceY = NewSourceY * acceptanceSlit(MatTempY[0], ListObject[k][2], ListObject[k][4])
            elif ListObject[k][0] == 'MonoPlaneVertical':
                NewSourceY = NewSourceY * acceptanceAngleMonoPlane(MatTempY[1], MatTempY[2], ListObject[k][1], ListObject[k][2], ListObject[k][3], ListObject[k][4])
                NewSourceY = NewSourceY * acceptanceWaveMonoPlane(MatTempY[2], bMonoY*SigmaYPSource, ListObject[k][1], ListObject[k][2])
            elif ListObject[k][0] == 'MonoPlaneHorizontal':
                NewSourceX = NewSourceX * acceptanceAngleMonoPlane(MatTempX[1], MatTempX[2], ListObject[k][1], ListObject[k][2], ListObject[k][3], ListObject[k][4])
                NewSourceX = NewSourceX * acceptanceWaveMonoPlane(MatTempX[2], bMonoX*SigmaXPSource, ListObject[k][1], ListObject[k][2])
            k = k +1
            del MX[0:2]
            del MY[0:2]
    return [NewSourceX, NewSourceY]

def sourceFinale(SigmaXSource, SigmaXPSource, SigmaYSource, SigmaYPSource, SigmaSLambda, GammaSource, MatTabX, MatTabY, ListObject, SourceI, bMonoX, bMonoY):
    IXXP = lambda x, xp, dl : propagateMatrixList(x, xp, 0, 0, dl, SigmaXSource, SigmaXPSource, SigmaYSource, SigmaYPSource, GammaSource, MatTabX, MatTabY, ListObject, bMonoX, bMonoY)[0]
    IYYP = lambda y, yp, dl : propagateMatrixList(0, 0, y, yp, dl, SigmaXSource, SigmaXPSource, SigmaYSource, SigmaYPSource, GammaSource, MatTabX, MatTabY, ListObject, bMonoX, bMonoY)[1]
    ISigma = lambda dl : sourceLambda(dl, SigmaSLambda) * SourceI
    return IXXP,IYYP, ISigma

def calculateLimits(IXXP, IYYP, ISigma):
    # We need to minimize calculation time and maximize precision and avoid empty
    # sampling. So we determine the boundaries of our gaussians with a quick algorithm.
    IotaX = 10 ** -8
    while IXXP(IotaX, 0, 0) > 10 ** -15 * IXXP(0, 0, 0):
        IotaX = IotaX * 2
    IotaX = IotaX * 2

    IotaXp = 10 ** -8
    while IXXP(0, IotaXp, 0) > 10 ** -15 * IXXP(0, 0, 0):
        IotaXp = IotaXp * 2
    IotaXp = IotaXp * 2

    IotaY = 10 ** -8
    while IYYP(IotaY, 0, 0) > 10 ** -15 * IYYP(0, 0, 0):
        IotaY = IotaY * 2
    IotaY = IotaY * 2

    IotaYp = 10 ** -8
    while IYYP(0, IotaYp, 0) > 10 ** -15 * IYYP(0, 0, 0):
        IotaYp = IotaYp * 2
    IotaYp = IotaYp * 2

    IXint = lambda x, xp, dl : IXXP(x, xp, dl) * ISigma(dl)
    IYint = lambda y, yp, dl : IYYP(y, yp, dl) * ISigma(dl)

    IotaYdl = 10 ** -8
    while IYint(0, 0, IotaYdl) > 10 ** -15 * IYint(0, 0, 0):
        IotaYdl = IotaYdl * 2

    IotaXdl = 10 ** -8
    while IXint(0, IotaXdl, 0) > 10 ** -15 * IXint(0, 0, 0):
        IotaXdl = IotaXdl * 2

    return [IotaX, IotaXp, IotaY, IotaYp, IotaXdl, IotaYdl]

def comparisonSourceBoundaries(IXXP, IYYP, ISigma, SigmaXSource, SigmaXPSource, SigmaYSource, SigmaYPSource, SigmaSLambda):
    [IotaX, IotaXp, IotaY, IotaYp, IotaXdl, IotaYdl] = calulateLimits(IXXP, IYYP, ISigma)
    print('Integration limits divided by the source Sigmas :',
          [IotaX / SigmaXSource, IotaY / SigmaYSource, IotaXp / SigmaXPSource, IotaYp / SigmaYPSource,
           IotaXdl / SigmaSLambda, IotaYdl / SigmaSLambda])

def calculateBetterLimits(f, Eval, SigmaSource1, SigmaSource2, Epsilon ):
    Iota1 = SigmaSource1
    Iota2 = SigmaSource2
    while si.quad(f, -Iota1, Iota1, args=(Iota2, Eval))[0] / f(0, 0, 0) > Epsilon:
        Iota2 = Iota2 * 2
    fPerm = lambda x, y, z: f(y, x, z)
    while si.quad(fPerm, -Iota2, Iota2, args=(Iota1, Eval))[0] / f(0, 0, 0) > Epsilon:
        Iota1 = Iota1 * 2
    return Iota1, Iota2

def calculateUltimatelyBetterLimitsLikeSuperAwesomeLimitsAndWayBetterthanCalculateBetterLimits(f, SigmaSource1, SigmaSource2, SigmaSource3, Epsilon):
    [Iota1, Iota2] = calculateBetterLimits(f, 0, SigmaSource1, SigmaSource2, Epsilon)
    fPerm1 = lambda x, y, z : f(y, z, x)
    [Iota3, Iota4] = calculateBetterLimits(fPerm1, Iota2/4, SigmaSource2, SigmaSource3, Epsilon)
    fPerm2 = lambda x, y, z : f(x, z, y)
    [Iota5, Iota6] = calculateBetterLimits(fPerm2, Iota1/4, SigmaSource1, SigmaSource3, Epsilon)
    if Iota1 < Iota5:
        Iota1 = Iota5
    if Iota2 < Iota3:
        Iota2 = Iota4
    if Iota4 < Iota6:
        Iota4 = Iota6
    print('The marvelous Iotas are :', Iota1, Iota2, Iota4)
    return Iota1, Iota2, Iota4

def simpleIntegralDenullification(f, k, Iota):
    Eval = k
    Integral = si.quad(f, -Iota, Iota, args=(0, Eval))[0]
    if Integral == 0.0:
        while Integral == 0.0:
            Eval = Eval / 2
            Integral = si.quad(f, -Iota, Iota, args=(0, Eval))[0]
        Eval = Eval / 4
    return Eval

def doubleIntegralDenullification(f, k, Iota1, Iota2):
    #
    Eval = k
    Integral = si.nquad(f, [[-Iota1, Iota1], [-Iota2, Iota2]], args=(Eval,))[0]
    if Integral == 0.0:
        while Integral == 0.0:
            Eval = Eval / 2
            Integral = si.nquad(f, [[-Iota1, Iota1], [-Iota2, Iota2]], args=(DlEval,))[0]
        Eval = Eval / 4
    return Eval

def sigmaCalc(Eval, ValueExponent, ValueA):
    return 1 / 2 / sqrt(2 * np.log(2)) * sqrt(4 * log(2) * Eval**2 / -log(ValueExponent / ValueA))

def plotXXP(IXXP, IotaX, IotaXp):
    x = np.linspace(-IotaX, IotaX, 100)
    xp = np.linspace(-IotaXp, IotaXp, 100)
    X = np.outer(x, np.ones_like(xp))
    XXP = np.zeros_like(X)

    for ix, xval in enumerate(x):
        for ixp, xpval in enumerate(xp):
            XXP[ix, ixp] = IXXP(xval, xpval, 0)

    print("Integral of XXP", XXP.sum() * (x[1] - x[0]) * (xp[1] - xp[0]))

    print("XXP shape", XXP.shape)

    fig = plt.figure()

    # cmap = plt.cm.Greys
    plt.imshow(XXP.T, origin='lower', extent=[x[0], x[-1], xp[0], xp[-1]], cmap=None, aspect='auto')
    plt.colorbar()
    ax = fig.gca()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    plt.title("TITLE")
    plt.show()

    plt.plot(x, XXP.sum(axis=1))
    plt.title("INT vs x")
    plt.show()
    plt.plot(xp, XXP.sum(axis=0))
    plt.title("INT vs xp")
    plt.show()

def plotYYP(IYYP, IotaY, IotaYp):
    y = np.linspace(-IotaY, IotaY, 100)
    yp = np.linspace(-IotaYp, IotaYp, 100)
    Y = np.outer(y, np.ones_like(yp))
    YYP = np.zeros_like(Y)

    for ix, xval in enumerate(y):
        for ixp, xpval in enumerate(yp):
            YYP[ix, ixp] = IYYP(xval, xpval, 0)

    print("Integral of XXP", YYP.sum() * (y[1] - y[0]) * (yp[1] - yp[0]))

    print("XXP shape", YYP.shape)

    fig = plt.figure()

    # cmap = plt.cm.Greys
    plt.imshow(YYP.T, origin='lower', extent=[y[0], y[-1], yp[0], yp[-1]], cmap=None, aspect='auto')
    plt.colorbar()
    ax = fig.gca()
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    plt.title("TITLE")
    plt.show()

    plt.plot(y, YYP.sum(axis=1))
    plt.title("INT vs y")
    plt.show()
    plt.plot(yp, YYP.sum(axis=0))
    plt.title("INT vs yp")
    plt.show()

def plotAnything(f, Iota1, Iota2, Iota3, Eval, Var):
    #f is a 3 variable function, if you want to plot :
        # 1st and 2nd variable : Var = 12
        # 2nd and 3rd variable : Var = 23
        # 1st and 3rd variable : Var = 13

    u = np.linspace(-Iota1, Iota1, 100)
    v = np.linspace(-Iota2, Iota2, 100)
    w = np.linspace(-Iota3, Iota3, 100)
    X = np.outer(u, np.ones_like(v))
    Y = np.outer(v, np.ones_like(w))
    Z = np.outer(u, np.ones_like(w))

    if Var == 12:
        Matrix = np.zeros_like(X)
        for ix, xval in enumerate(u):
            for ixp, xpval in enumerate(v):
                Matrix[ix, ixp] = f(xval, xpval, Eval)
                print("Integral of Matrix", Matrix.sum() * (u[1] - u[0]) * (v[1] - v[0]))

                print("Matrix shape", Matrix.shape)

                fig = plt.figure()

                # cmap = plt.cm.Greys
                plt.imshow(Matrix.T, origin='lower', extent=[u[0], u[-1], v[0], v[-1]], cmap=None, aspect='auto')
                plt.colorbar()
                ax = fig.gca()
                ax.set_xlabel("X")
                ax.set_ylabel("Y")

                plt.title("TITLE")
                plt.show()

                plt.plot(u, Matrix.sum(axis=1))
                plt.title("INT vs Variable1")
                plt.show()
                plt.plot(v, Matrix.sum(axis=0))
                plt.title("INT vs Variable2")
                plt.show()
                return
    elif Var == 23:
        Matrix = np.zeros_like(Y)
        for ix, xval in enumerate(v):
            for ixp, xpval in enumerate(w):
                Matrix[ix, ixp] = f(Eval, xval, xpval)
                print("Integral of Matrix", Matrix.sum() * (v[1] - v[0]) * (w[1] - w[0]))

                print("Matrix shape", Matrix.shape)

                fig = plt.figure()

                # cmap = plt.cm.Greys
                plt.imshow(Matrix.T, origin='lower', extent=[v[0], v[-1], w[0], w[-1]], cmap=None, aspect='auto')
                plt.colorbar()
                ax = fig.gca()
                ax.set_xlabel("X")
                ax.set_ylabel("Y")

                plt.title("TITLE")
                plt.show()

                plt.plot(v, Matrix.sum(axis=1))
                plt.title("INT vs Variable1")
                plt.show()
                plt.plot(w, Matrix.sum(axis=0))
                plt.title("INT vs Variable2")
                plt.show()
                return
    elif Var == 13:
        Matrix = np.zeros_like(Z)
        for ix, xval in enumerate(u):
            for ixp, xpval in enumerate(w):
                Matrix[ix, ixp] = f(xval, Eval, xpval)
                print("Integral of Matrix", Matrix.sum() * (u[1] - u[0]) * (w[1] - w[0]))

                print("Matrix shape", Matrix.shape)

                fig = plt.figure()

                # cmap = plt.cm.Greys
                plt.imshow(Matrix.T, origin='lower', extent=[u[0], u[-1], w[0], w[-1]], cmap=None, aspect='auto')
                plt.colorbar()
                ax = fig.gca()
                ax.set_xlabel("X")
                ax.set_ylabel("Y")

                plt.title("TITLE")
                plt.show()

                plt.plot(u, Matrix.sum(axis=1))
                plt.title("INT vs Variable1")
                plt.show()
                plt.plot(w, Matrix.sum(axis=0))
                plt.title("INT vs Variable2")
                plt.show()
                return
    else:
        print("Var can only take the values 12, 23 or 13. Try again bro !")
        return 0


# Where the magic happens...

def beamGeoSize(IXXP,IYYP,ISigma, SigmaXPSource, SigmaYPSource, SigmaSLambda):  # the two next functions are similar to this model
    # creating the functions to integrate, we need to redo this every time because the integration functions integrate
    # using the order in which the parameters are input, like it will integrate Ix in this order : xp, dl and then x
    Ix = lambda xp, dl, x : IXXP(x, xp, dl)
    Iy = lambda yp, dl, y : IYYP(y, yp, dl)
    #Now we get ze integration boundaries
    [IotaX, IotaXp, IotaY, IotaYp, IotaXdl, IotaYdl] = calculateLimits(IXXP, IYYP, ISigma)
    # Again, to minimize integration, we calculate the integrals of I = Ix*Iy*Idl separately, do do that, we need to
    # check that either Ix or Iy does not depend on dl, thus the next test
    if Ix(0,0,0) == Ix(0,100,0): #we check the dependancy on dl, Ix being similar to a gaussian (the bijectivity of a gaussian
        # on the interval [0, +inf[ makes this test valid)
        print("Lambda is affected to y")
        IYint = lambda yp, dl, y : Iy(yp, dl, y) * ISigma(dl)
        # we are going to do 4 integrations : along xp and dl with x = {0,10**-2}, along yp and dl with y = {0,10**-2}
        # we can do that since the integrals can be separated, and it takes less time to calculate. Adding a parameter
        # to a numerical integration multiplies the execution time by approx 300.
        # args(0,10**-2) sets the values of dl and x to 0 and 10**-2
        XEval = 10**-2
        YEval = 10**-2
        #integral denullification section : Python does not have an infinite precision and sometimes the integrals are
        # too small to be calculated and so the result is 0, which is not acceptable. So we calculate them again using
        # a different evaluation. Here, we change the evaluation preemptively with the 2 following functions
        XEval = simpleIntegralDenullification(Ix, XEval, IotaXp)
        YEval = doubleIntegralDenullification(IYint, YEval, IotaYp, IotaYdl)
        # integrations
        IxIntegrated_0 = si.quad(Ix, -IotaXp, IotaXp, args=(0, 0))[0]    #xp is integrated
        IxIntegrated_E2 = si.quad(Ix, -IotaXp, IotaXp, args=(0, XEval))[0]

        IotaYpBetter = calculateBetterLimits(IYint, YEval, SigmaYPSource, SigmaSLambda, 10**-5)[0]
        IotaYdlBetter = calculateBetterLimits(IYint, YEval, SigmaYPSource, SigmaSLambda, 10**-5)[1]
        print('IotaYdlBetter is :', IotaYdlBetter, 'and IotaYpBetter is :', IotaYpBetter)

        IyIntegrated_0 = si.nquad(IYint, [[-IotaYpBetter, IotaYpBetter], [-IotaYdlBetter, IotaYdlBetter]], args=(0,))[0]
        IyIntegrated_E2 = si.nquad(IYint, [[-IotaYpBetter, IotaYpBetter],[-IotaYdlBetter, IotaYdlBetter]], args=(YEval,))[0]

        print('Value of the integrals : ', IxIntegrated_0, IxIntegrated_E2, IyIntegrated_0, IyIntegrated_E2)
        # we now have our integrals, we just need both Sigmas
        ValueAX = IxIntegrated_0 * IyIntegrated_0
        print('ValueAX :', ValueAX)
        ValueAY = ValueAX
        ValueExponentX = IyIntegrated_0 * IxIntegrated_E2
        ValueExponentY = IxIntegrated_0 * IyIntegrated_E2
        print('ValueExponentY is :', ValueExponentY)
        SigmaX = sigmaCalc(XEval, ValueExponentX, ValueAX)
        SigmaY = sigmaCalc(YEval, ValueExponentY, ValueAY)

    elif Iy(0,0,0) == Iy(0,100,0):
        # If we arrive here, this means Ix depended of dl, so we do exactly the same thing as in the previous paragraph,
        # but with Iy
        print("Lambda is affected to x")
        IXint = lambda xp, dl, x: Ix(xp, dl, x) * ISigma(dl)
        print('The integration limits are :', [IotaXp, IotaYp, IotaXdl])
        XEval = 10**-2
        YEval = 10**-2
        # integral denullification section
        XEval = doubleIntegralDenullification(IXint, XEval, IotaXp, IotaXdl)
        YEval = simpleIntegralDenullification(Iy, YEval, IotaYp)
        # integrations
        IyIntegrated_0 = si.quad(Iy, -IotaYp, IotaYp, args=(0, 0))[0]
        IyIntegrated_E2 = si.quad(Iy, -IotaYp, IotaYp, args=(0, YEval))[0]

        IotaXpBetter = calculateBetterLimits(IXint, XEval, SigmaXPSource, SigmaSLambda, 10 ** -5)[0]
        IotaXdlBetter = calculateBetterLimits(IXint, XEval, SigmaXPSource, SigmaSLambda, 10 ** -5)[1]
        print('IotaXdlBetter is :', IotaXdlBetter, 'and IotaXpBetter is :', IotaXpBetter)

        IxIntegrated_0 = si.nquad(IXint, [[-IotaXpBetter, IotaXpBetter], [-IotaXdlBetter, IotaXdlBetter]], args=(0,))[0]
        IxIntegrated_E2 = si.nquad(IXint, [[-IotaXpBetter, IotaXpBetter], [-IotaXdlBetter, IotaXdlBetter]], args=(XEval,))[0]
        print('Value of the integrals : ',IyIntegrated_0, IyIntegrated_E2, IxIntegrated_0, IxIntegrated_E2)
        #simple calculation part
        ValueAX = IxIntegrated_0 * IyIntegrated_0
        print(ValueAX)
        ValueAY = ValueAX
        ValueExponentX = IyIntegrated_0 * IxIntegrated_E2
        ValueExponentY = IxIntegrated_0 * IyIntegrated_E2
        SigmaX = sigmaCalc(XEval, ValueExponentX, ValueAX)
        SigmaY = sigmaCalc(YEval, ValueExponentY, ValueAY)

    else:
        print("Computation time too long, DeltaLambda variation on both axis -> not possible")
        return 0

    return [SigmaX, SigmaY]

def beamAngularSize(IXXP, IYYP, ISigma, SigmaXSource, SigmaYSource, SigmaSLambda):
    #creating the functions to integrate
    Ixp = lambda x, dl, xp : IXXP(x, xp, dl)
    Iyp = lambda y, dl, yp : IYYP(y, yp, dl)
    [IotaX, IotaXp, IotaY, IotaYp, IotaXdl, IotaYdl] = calculateLimits(IXXP, IYYP, ISigma)
    #dl dependancy check on Ixp
    if Ixp(0, 0, 0) == Ixp(0, 100, 0):
        print("Lambda is affected to y")
        IYpint = lambda y, dl, yp : Iyp(y, dl, yp) * ISigma(dl)
        #Integrations
        XpEval = 10**-6
        YpEval = 10**-6
        XpEval = simpleIntegralDenullification(Ixp, XpEval, IotaX)
        YpEval = doubleIntegralDenullification(IYpint, YpEval, IotaY, IotaYdl)
        IxpIntegrated_0 = si.quad(Ixp, -IotaX, IotaX, args=(0, 0))[0]
        IxpIntegrated_E6 = si.quad(Ixp, -IotaX, IotaX, args=(0, XpEval))[0]

        IotaYBetter = calculateBetterLimits(IYpint, YpEval, SigmaYSource, SigmaSLambda, 10 ** -5)[0]
        IotaYdlBetter = calculateBetterLimits(IYpint, YpEval, SigmaYSource, SigmaSLambda, 10 ** -5)[1]
        print('IotaYdlBetter is :', IotaYdlBetter, 'and IotaYBetter is :', IotaYBetter)

        IypIntegrated_0 = si.nquad(IYpint, [[-IotaYBetter, IotaYBetter], [-IotaYdlBetter, IotaYdlBetter]], args=(0,))[0]
        IypIntegrated_E6 = si.nquad(IYpint, [[-IotaYBetter, IotaYBetter], [-IotaYdlBetter, IotaYdlBetter]], args=(YpEval,))[0]
        print('Value of the integrals : ', IxpIntegrated_0, IxpIntegrated_E6, IypIntegrated_0, IypIntegrated_E6)

        #Simple calculation part
        ValueAXp = IxpIntegrated_0 * IypIntegrated_0
        print(ValueAXp)
        ValueAYp = ValueAXp
        ValueExponentXp = IypIntegrated_0 * IxpIntegrated_E6
        ValueExponentYp = IxpIntegrated_0 * IypIntegrated_E6
        SigmaXp = sigmaCalc(XpEval, ValueExponentXp, ValueAXp)
        SigmaYp = sigmaCalc(YpEval, ValueExponentYp, ValueAYp)
        SigmaXpMilliRad = SigmaXp * 10**6
        SigmaYpMilliRad = SigmaYp * 10**6
        return [SigmaXpMilliRad, SigmaYpMilliRad]
    #Dl dependancy check on Iyp
    elif Iyp(0,0,0) == Iyp(0,100,0):
        print("Lambda is affected to x")
        IXpint = lambda x, dl, xp: Ixp(x, dl, xp) * ISigma(dl)
        print('Integration limits are :', [IotaX, IotaY, IotaXdl])
        # Integrations
        XpEval = 10**-6
        YpEval = 10**-6
        XpEval = doubleIntegralDenullification(IXpint, XpEval, IotaX, IotaXdl)
        YpEval = simpleIntegralDenullification(Iyp, YpEval, IotaY)
        IypIntegrated_0 = si.quad(Iyp, -IotaY, IotaY, args=(0, 0))[0]
        IypIntegrated_E6 = si.quad(Iyp, -IotaY, IotaY, args=(0, YpEval))[0]

        IotaXBetter = calculateBetterLimits(IXpint, XpEval, SigmaXSource, SigmaSLambda, 10 ** -5)[0]
        IotaXdlBetter = calculateBetterLimits(IXpint, XpEval, SigmaXSource, SigmaSLambda, 10 ** -5)[1]
        print('IotaXdlBetter is :', IotaXdlBetter, 'and IotaXBetter is :', IotaXBetter)

        IxpIntegrated_0 = si.nquad(IXpint, [[-IotaXBetter, IotaXBetter], [-IotaXdlBetter, IotaXdlBetter]], args=(0,))[0]
        IxpIntegrated_E6 = si.nquad(IXpint, [[-IotaXBetter, IotaXBetter], [-IotaXdlBetter, IotaXdlBetter]], args=(XpEval,))[0]
        print('Value of the integrals : ',IxpIntegrated_0, IxpIntegrated_E6, IypIntegrated_0, IypIntegrated_E6)
        # Simple calculation part
        ValueAXp = IxpIntegrated_0 * IypIntegrated_0
        print(ValueAXp)
        ValueAYp = ValueAXp
        ValueExponentXp = IypIntegrated_0 * IxpIntegrated_E6
        ValueExponentYp = IxpIntegrated_0 * IypIntegrated_E6
        SigmaXp = sigmaCalc(XpEval, ValueExponentXp, ValueAXp)
        SigmaYp = sigmaCalc(YpEval, ValueExponentYp, ValueAYp)
        SigmaXpMilliRad = SigmaXp * 10**6
        SigmaYpMilliRad = SigmaYp * 10**6
        return [SigmaXpMilliRad, SigmaYpMilliRad]
    else:
        print("Computation time too long, DeltaLambda variation on both axis -> not possible")
        return 0

def sigma1_MaxFluxL_FluxPhi(IXXP, IYYP, ISigma, SigmaXPSource, SigmaYPSource, SigmaXSource, SigmaYSource, SigmaSLambda, CoefAtten, CoefMonoX, CoefMonoY):
    #creating the functions to integrate
    Ix = lambda x, xp, dl: IXXP(x, xp, dl)
    Iy = lambda y, yp, dl: IYYP(y, yp, dl)
    [IotaX, IotaXp, IotaY, IotaYp, IotaXdl, IotaYdl] = calculateLimits(IXXP, IYYP, ISigma)

    if Ix(0, 0, 0) == Ix(0, 0, 100):       #first dependancy check
        print("Lambda is affected to y")
        # last integration boundary needed and function creation
        IYint = lambda y, yp, dl: Iy(y, yp, dl) * ISigma(dl)
        #Integrations
        DlEval = 10**-3
        DlEval = doubleIntegralDenullification(IYint, DlEval, IotaY, IotaYp)
        print('Lambda will be evaluated at :', DlEval)

        IxIntegrated = si.nquad(Ix, [[-IotaX, IotaX], [-IotaXp, IotaXp]], args=(0,))[0]

        IotaYBetter = calculateBetterLimits(IYint, DlEval, SigmaYSource, SigmaYPSource, 10 ** -5)[0]
        IotaYpBetter = calculateBetterLimits(IYint, DlEval, SigmaYSource, SigmaYPSource, 10 ** -5)[1]
        print('IotaYBetter is :', IotaYBetter, 'and IotaYpBetter is :', IotaYpBetter)

        IyIntegrated_0 = si.nquad(IYint, [[-IotaYBetter, IotaYBetter], [-IotaYpBetter, IotaYpBetter]], args=(0,))[0]
        IyIntegrated_E3 = si.nquad(IYint, [[-IotaYBetter, IotaYBetter], [-IotaYpBetter,IotaYpBetter]], args=(DlEval,))[0]

        print('IxIntegrated is :', IxIntegrated, 'Other values :', IyIntegrated_0,IyIntegrated_E3 )
        #simple calculation part
        ValueAL = IxIntegrated * IyIntegrated_0
        print(" ValueAL gives :", ValueAL)
        ValueExponentL = IxIntegrated * IyIntegrated_E3
        print(" ValueExponentL gives :", ValueExponentL)
        Sigma = sigmaCalc(DlEval, ValueExponentL, ValueAL)
        MaxFluxL = ValueAL
        # calculation of the flux
        [IotaYBest, IotaYpBest, IotaYdlBest] = calculateUltimatelyBetterLimitsLikeSuperAwesomeLimitsAndWayBetterthanCalculateBetterLimits(IYint, SigmaYSource, SigmaYPSource, SigmaSLambda, 10**-5)
        FluxPhi = si.nquad(IYint, [[-IotaYBest, IotaYBest], [-IotaYpBest, IotaYpBest], [-IotaYdlBest, IotaYdlBest]])
        print(FluxPhi)
        FluxPhi = IxIntegrated * FluxPhi[0]
        FluxPhi = CoefAtten * CoefMonoX * CoefMonoY * FluxPhi

    elif Iy(0, 0, 0) == Iy(0, 0, 100):
        IXint = lambda x, xp, dl: Ix(x, xp, dl) * ISigma(dl)
        # Integrations
        DlEval = 10 ** -3
        DlEval = doubleIntegralDenullification(IXint, DlEval, IotaX, IotaXp)
        print('Lambda will be evaluated at :', DlEval)
        IyIntegrated = si.nquad(Iy, [[-IotaY, IotaY], [-IotaYp, IotaYp]], args=(0,))[0]

        IotaXBetter = calculateBetterLimits(IXint, DlEval, SigmaXSource, SigmaXPSource, 10 ** -5)[0]
        IotaXpBetter = calculateBetterLimits(IXint, DlEval, SigmaXSource, SigmaXPSource, 10 ** -5)[1]
        print('IotaXBetter is :', IotaXBetter, 'and IotaXpBetter is :', IotaXpBetter)

        IxIntegrated_0 = si.nquad(IXint, [[-IotaXBetter, IotaXBetter], [-IotaXpBetter, IotaXpBetter]], args=(0,))[0]
        IxIntegrated_E3 = si.nquad(IXint, [[-IotaXBetter, IotaXBetter], [-IotaXpBetter, IotaXpBetter]], args=(DlEval,))[0]
        print('IxIntegrated is :', IxIntegrated_0)

        # simple calculation part
        ValueAL = IxIntegrated_0 * IyIntegrated
        print(" ValueAL gives :", ValueAL)
        ValueExponentL = IyIntegrated * IxIntegrated_E3
        print(" ValueExponentL gives :", ValueExponentL)
        Sigma = sigmaCalc(DlEval, ValueExponentL, ValueAL)
        MaxFluxL = ValueAL
        # calculation of the flux
        FluxPhi = si.nquad(IXint, [[-IotaX/2, IotaX/2], [-IotaXp/2, IotaXp/2], [-IotaXdl/2, IotaXdl/2]])
        print(FluxPhi)
        FluxPhi = IyIntegrated * FluxPhi[0]
        FluxPhi = CoefAtten * CoefMonoX * CoefMonoY * FluxPhi

    else:
        print("Computation time too long, DeltaLambda variation on both axis -> not possible")
        return 0

    return Sigma, MaxFluxL, FluxPhi














