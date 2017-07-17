import numpy as np
from numpy import exp
from numpy import pi
from numpy import sqrt
from numpy import log
import numpy.testing as nut
import sympy as sp
import scipy.integrate as si
import mpmath as mp
import sympy

x, xp, y, yp, dl = sp.symbols('x xp y yp dl')

#Definition of mathematical objects


    #Definition of the transformation matrices

def MatrixFlight(L):                                                   # For a flight path of length
    return np.array([[1,-L,0],[0,1,0],[0,0,1]])

def MatrixMonoPlane(b, ThetaB):                                         # For a perfect flat crystal monochromator
    return np.array([[b,0,0],[0,1/b,(1-1/b)*np.tan(ThetaB)],[0,0,1]])

def MatrixMonoBent(b, Fc, ThetaB):                                     # For a perfect curved crystal monochromator (meridionally and sagitally focusing)
    return np.array([[b,0,0],[1/Fc,1/b,(1-1/b)*np.tan(ThetaB)],[0,0,1]])

def MatrixMonoMosaic(ThetaB):                                             # For a mosaic monochromator
    return np.array([[1,0,0],[0,-1,2*np.tan(ThetaB)],[0,0,1]])

def MatrixMirrorPlane(IncAng, Sigma, Lambda, Delta):                      # For the plane mirror
    return exp(-(4*pi*np.sin(IncAng)*Sigma/Lambda)**2)*np.array([[1,0,0],[Delta,1,0],[0,0,1]])

def MatrixMirror(IncAng, Sigma, Lambda, Delta, Fm, S):                      # For the bent and toroidal mirrors
    return exp(-(4*pi*np.sin(IncAng)*Sigma/Lambda)**2)*np.array([[1,0,0],[(1+S*Fm*Delta)/Fm,1,0],[0,0,1]])

def MatrixCompLensPara(F):                                                 # For the compound refractive lenses with parabolic holes
    return np.array([[1,0,0],[1/F,1,0],[0,0,1]])

def MatrixCompLensCirc(Coef, F):                                           # For the compound refractive lenses with circular holes
    return np.array([[1,0,0],[Coef/F,1,0],[0,0,1]])

def MatrixMultilayer(Fmu):                                                  # For the multilayer
    return np.array([[1,0,0],[1/Fmu,1,0],[0,0,1]])

    #Definition of the beam source

def SourceXXP(x, xp, SigmaXSource=1e-1, SigmaXPSource=3e-5):
    return sp.exp(-( (x/SigmaXSource)**2 + (xp/SigmaXPSource)**2) / 2 )
def SourceYYP(y, yp, SigmaYSource=1e-2, SigmaYPSource=1e-4, GammaSource=0):
    return sp.exp( -( (y/SigmaYSource)**2 + ((yp-GammaSource*y)/SigmaYPSource)**2)/2 )
def SourceLambda(dl, SigmaSLambda=1e-3):
    return sp.exp(-(dl)**2/2/SigmaSLambda**2)

    #Definition of the acceptance windows of the optical parts

def cotan(x):
    return 1/np.tan(x)

def AcceptanceSlit(y, Aperture, calctype):                                                           #Slit acceptance
    if calctype==0:
        return sqrt(6/pi) / sqrt(6*log(2)/pi) * sp.exp( -(y/Aperture)**2/2*12)
    if calctype==1:
        return 1/sqrt(6*log(2)/pi)*sp.exp(-y**2/(2*Aperture**2/2/pi))
    else:
        return 'the value for calctype is 0 or 1 you pipsqueak !'

def AcceptancePin(y, Diameter):                                                            #Pinhole acceptance
    return sqrt(8/pi) * exp ( -(y/Diameter)**2/2*16 )

def AcceptanceAngleMonoPlane(RMono, RInt, Wd, yp, DeltaLambda, ThetaB):                #Plane monochromator angle acceptance
    return RMono*RInt*sqrt(6/pi)/Wd * exp( -(yp-DeltaLambda*np.tan(ThetaB))**2 / (2*Wd**2/12))

def AcceptanceWaveMonoPlane(DeltaLambda, SigmaYp, ThetaB, Wd):                        #Plane monochromator wave acceptance
    return sqrt(6/pi) * exp( - (DeltaLambda)**2 / (2*(SigmaYp**2+Wd**2/12)*cotan(ThetaB)**2) )

def AcceptanceAngleMonoMosaic(RInt, eta, yp, DeltaLambda, ThetaB):                       #Mosaic monochromator angular acceptance
    return RInt*sqrt(6/pi)/eta * exp(- (yp-DeltaLambda*np.tan(ThetaB))**2 / eta**2 /2 )

def AcceptanceWaveMonoMosaic(DeltaLambda, SigmaYp, eta, ThetaB):                        #Mosaic monochromator wave acceptance
    return sqrt(6/pi) * exp( - (DeltaLambda)**2 / 2 /((SigmaYp**2+eta**2)*cotan(ThetaB)**2))

def AcceptanceAngleMonoBent(RMono, RInt, Wd,yp, y, r, ThetaB, Alpha, DeltaLambda ):    #Curved monochromator angle acceptance
    return RMono*RInt*sqrt(6/pi)/Wd * exp( - (yp-y/r/np.sin(ThetaB+Alpha)-DeltaLambda*np.tan(ThetaB))**2/(2*Wd**2/12))

def AcceptanceWaveMonoBent(DeltaLambda, ThetaB, SigmaSource, DistanceFromSource, Wd):  #Curved monochromator wave acceptance
    return sqrt(6/pi) * exp( -(DeltaLambda)**2 / (2*cotan(ThetaB)**2*((SigmaSource/DistanceFromSource)**2+Wd**2/12))   )

def AcceptanceCompLensPara(x, Radius, Distance, Sigma):                                          #Compound refractive lense with parabolic holes acceptance
    return exp( -(x**2+Radius*Distance)/2/Sigma**2)

def AcceptanceCompLensCirc(x, Sigma, FWHM, Radius, Distance):                                    #Compound refractive lense with circular holes acceptance
    return exp( -x**2/2/Sigma**2 -x**2*FWHM**2/8/Radius**2/Sigma**2 -x**2*FWHM**4/16/Sigma**2/Radius**4 -Radius*Distance/2/Sigma**2  )

def AcceptanceAngleMulti(Rml, yp, y, Rowland, ThetaML, DeltaLambda, Ws):                #Multilayer angle acceptance
    return Rml*8/3*sqrt(log(2)/pi) * exp( -(-yp-y/Rowland/np.sin(ThetaML)-DeltaLambda*np.tan(ThetaML))**2*8*log(2)/2/Ws**2 )

def AcceptanceWaveMulti(DeltaLambda, SigmaSource, DistanceFromSource, Ws, ThetaML):     #Multilayer wave acceptance
    return sqrt(6/pi) * exp( -(DeltaLambda)**2/2/((SigmaSource/DistanceFromSource)**2+Ws**2/8/log(2))/cotan(ThetaML)**2)


#Testing the functions


    #Testing the matrices

def testMatrixMonoPlane():
    print(">> MatFlatMono in test")
    b=0.8
    ThetaB=1.0
    Mat=np.array([[0.8,0,0],[0,1.25,-0.389352],[0,0,1]])
    print(Mat.shape)
    result = MatrixMonoPlane(b,ThetaB)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMonoPlane())

def testMatrixMonoBent():
    print(">> MatCurvMono in test")
    b = 0.8
    Fc = 2
    ThetaB = 1.0
    Mat = np.array([[0.8, 0, 0], [0.5, 1.25, -0.389352], [0, 0, 1]])
    print(Mat.shape)
    result = MatrixMonoBent(b, Fc, ThetaB)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMonoBent())

def testMatrixMonoMosaic():
    print(">> MatMosMono in test")
    ThetaB = 1.0
    Mat = np.array([[1, 0, 0], [0, -1, 2*np.tan(1)], [0, 0, 1]])
    print(Mat.shape)
    result = MatrixMonoMosaic(ThetaB)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMonoMosaic())

def testMatrixMirrorPlane():
    print(">> MatFlatMirr in test")
    Sigma = 0.02
    IncAng = 30
    Lambda = 1
    Delta = 5
    Mat = np.array([[0.9402, 0, 0], [4.701, 0.9402, 0], [0, 0, 0.9402]])
    print(Mat.shape)
    result = MatrixMirrorPlane(IncAng, Sigma, Lambda, Delta)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMirrorPlane())

def testMatrixMirror():
    print(">> MatMirr in test")
    Sigma = 0.02
    IncAng = 30
    Lambda = 1
    Delta = 5
    Fm = 10
    S =0.1
    Mat = np.array([[0.9402, 0, 0], [0.56412, 0.9402, 0], [0, 0, 0.9402]])
    print(Mat.shape)
    result = MatrixMirror(IncAng, Sigma, Lambda, Delta, Fm, S)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMirror())

def testMatrixCompLensPara():
    print(">> MatParaLens in test")
    F=12.3
    Mat = np.array([[1, 0, 0], [0.0813008, 1, 0], [0, 0, 1]])
    print(Mat.shape)
    result = MatrixCompLensPara(F)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixCompLensPara())

def testMatrixCompLensCirc():
    print(">> MatCircLens in test")
    F = 12.3
    Coef = 0.4
    Mat = np.array([[1, 0, 0], [0.0325203, 1, 0], [0, 0, 1]])
    print(Mat.shape)
    result = MatrixCompLensCirc(Coef, F)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixCompLensCirc())

def testMatrixMultilayer():
    print(">> MatMulti in test")
    Fmu = 15.1
    Mat = np.array([[1, 0, 0], [0.0662252, 1, 0], [0, 0, 1]])
    print(Mat.shape)
    result = MatrixMultilayer(Fmu)
    print("Mistakes ?", nut.assert_array_almost_equal(Mat, result, decimal=5))
print(testMatrixMultilayer())

    #Testing the source

def testSourceXXP():
    print(">> SourceX in test")
    x = 0.5
    xp = 2
    Source = 0.605773
    result = SourceXXP(x, xp, SigmaXSource=10, SigmaXPSource=2)
    print(Source, result)
    print("Mistakes ?", nut.assert_almost_equal(Source, result, decimal=5))
print(testSourceXXP())

def testSourceYYP():
    print(">> SourceY in test")
    y = 0.5
    yp = 2
    Source = 0.753897
    result = SourceYYP(y, yp, SigmaYSource=10, SigmaYPSource=2, GammaSource=1)
    print(Source, result)
    print("Mistakes ?", nut.assert_almost_equal(Source, result, decimal=5))
print(testSourceYYP())

def testSourceLambda():
    print(">> SourceLambda in test")
    DeltaLambda = 4
    Source = 0.278037
    result = SourceLambda(DeltaLambda, SigmaSLambda=2.5)
    print(Source, result)
    print("Mistakes ?", nut.assert_almost_equal(Source, result, decimal=5))
print(testSourceLambda())

    #Testing the acceptances

def testAcceptanceSlit():
    print(">> AccSlit in test")
    y = 2
    Aperture = 75
    Acceptance = 1.19601
    result = AcceptanceSlit(y, Aperture, 0)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
    result2 = AcceptanceSlit(y, Aperture, 1)
    Acceptance2=0.867194
    print(Acceptance2, result2)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance2, result2, decimal=5))
print(testAcceptanceSlit())

def testAcceptancePin():
    print(">> AccPinh in test")
    y = 2
    Diameter = 75
    Acceptance = 1.58672
    result = AcceptancePin(y, Diameter)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptancePin())

def testAcceptanceAngleMonoPlane():
    print(">> AccMonoPlanAng in test")
    RMono = 0.91
    RInt = 0.2
    Wd = 103.2
    yp = 0.001
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 0.00214474
    result = AcceptanceAngleMonoPlane(RMono, RInt, Wd, yp, DeltaLambda, ThetaB)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceAngleMonoPlane())

def testAcceptanceWaveMonoPlane():
    print(">> AccMonoPlanWav in test")
    Wd = 103.2
    SigmaYp = 0.001
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 1.21616
    result = AcceptanceWaveMonoPlane(DeltaLambda, SigmaYp, ThetaB, Wd)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceWaveMonoPlane())

def testAcceptanceAngleMonoMosaic():
    print(">> AccMonoMosaAng in test")
    RMono = 0.91
    RInt = 0.2
    eta = 103.2
    yp = 0.001
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 0.00264987
    result = AcceptanceAngleMonoMosaic(RInt, eta, yp, DeltaLambda, ThetaB)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceAngleMonoMosaic())

def testAcceptanceWaveMonoMosaic():
    print(">> AccMonoMosaWav in test")
    eta = 103.2
    SigmaYp = 0.001
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 1.36733
    result = AcceptanceWaveMonoMosaic(DeltaLambda, SigmaYp, eta, ThetaB)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceWaveMonoMosaic())

def testAcceptanceAngleMonoBent():
    print(">> AccMonoCurvAng in test")
    RMono = 0.91
    RInt = 0.2
    Wd = 103.2
    yp = 0.001
    y = 8
    r = 9
    Alpha = 0.5
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 0.00218093
    result = AcceptanceAngleMonoBent(RMono, RInt, Wd, yp, y, r, ThetaB, Alpha, DeltaLambda)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceAngleMonoBent())

def testAcceptanceWaveMonoBent():
    print(">> AccMonoCurvWav in test")
    Wd = 103.2
    SigmaSource = 5.5
    DistanceFromSource = 0.001
    DeltaLambda = 0.2
    ThetaB = 33
    Acceptance = 1.38197
    result = AcceptanceWaveMonoBent(DeltaLambda, ThetaB, SigmaSource, DistanceFromSource, Wd)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceWaveMonoBent())

def testAcceptanceCompLensPara():
    print(">> AccLensPara in test")
    x = 2
    Radius = 75
    Distance = 22.2
    Sigma = 33.3
    Acceptance = 0.471162
    result = AcceptanceCompLensPara(x, Radius, Distance, Sigma)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceCompLensPara())

def testAcceptanceCompLensCirc():
    print(">> AccLensCirc in test")
    x = 2
    Radius = 75
    Distance = 22.2
    FWHM = 43.3
    Sigma = 33.3
    Acceptance = 0.471079
    result = AcceptanceCompLensCirc(x, Sigma, FWHM, Radius, Distance)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceCompLensCirc())

def testAcceptanceAngleMulti():
    print(">> AccMultAng in test")
    Rml = 200
    yp = 0.03
    y = 22.2
    Rowland = 443.3
    ThetaML = 1
    DeltaLambda = 1
    Ws = 0.7
    Acceptance = 0.0000541429
    result = AcceptanceAngleMulti(Rml, yp, y, Rowland, ThetaML, DeltaLambda, Ws)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceAngleMulti())

def testAcceptanceWaveMulti():
    print(">> AccMultWav in test")
    ThetaML = 1
    DeltaLambda = 1
    Ws = 0.7
    DistanceFromSource = 22
    SigmaSource = 45
    Acceptance = 1.04044
    result = AcceptanceWaveMulti(DeltaLambda, SigmaSource, DistanceFromSource, Ws, ThetaML)
    print(Acceptance, result)
    print("Mistakes ?", nut.assert_almost_equal(Acceptance, result, decimal=5))
print(testAcceptanceWaveMulti())


# todo Simplest example : propagation

z0 = 20000
Flight_paths_in_order = [z0]
MatTab = [MatrixFlight(z0)]
dlBoundaries = [-10**-6,10**-6]
CoefMonoX = 1
CoefMonoY = 1
CoefAtten = 1
SourceI = 1e25

def MatCreation():
    MatTempX = np.array([x,xp,dl])
    MatTempY = np.array([y, yp, dl])
    MatTempX = np.dot(MatrixFlight(z0),MatTempX)
    MatTempY = np.dot(MatrixFlight(z0), MatTempY)
    return [MatTempX,MatTempY]
print(">>>>>>>" , MatCreation())

def NewSource():
    MatTempX = MatCreation()[0]
    MatTempY = MatCreation()[1]
    NewSourceX = SourceXXP(MatTempX[0], MatTempX[1])
    NewSourceY = SourceYYP(MatTempY[0], MatTempY[1])
    return [NewSourceX, NewSourceY]
print(">>>>>>>>>>>>>>",NewSource())

def BeamGeoSize():
    Ix = lambda up, ddl, u: NewSource()[0].subs([(x, u), (xp, up), (dl, ddl)])
    print('Ix is :', Ix(xp, dl, x))
    Iy = lambda vp, ddl, v: NewSource()[1].subs([(y, v), (yp, vp), (dl, ddl)])
    print('Iy is :', Iy(yp, dl, y))
    IYint = lambda vp, ddl, v: Iy(vp, ddl, v) * SourceLambda(ddl, SigmaSLambda=1e-3) * SourceI
    print('IYint is :', IYint(yp, dl, y))
    # we are going to do 4 integrations : along xp and dl with x = {0,10**-2}, along yp and dl with y = {0,10**-2}
    # we can do that since the integrals can be separated, and it takes less time to calculate. Adding a parameter
    # to a numerical integration multiplies the execution time by approx 300.
    # args(0,10**-2) sets the values of dl and x to 0 and 10**-2
    IxIntegrated_0 = si.quad(Ix, -10 ** -6, 10 ** -6, args=(0, 0))[0]    #up is integrated
    IxIntegrated_E2 = si.quad(Ix, -10 ** -6, 10 ** -6, args=(0, 10 ** -2))[0]
    IyIntegrated_0 = si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
    IyIntegrated_E2 = si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -2,))[0]
    print(IxIntegrated_0, IxIntegrated_E2, IyIntegrated_0, IyIntegrated_E2)
    ValueAX = IxIntegrated_0 * IyIntegrated_0
    print(ValueAX)
    ValueAY = ValueAX
    ValueExponentX = IyIntegrated_0 * IxIntegrated_E2
    ValueExponentY = IxIntegrated_0 * IyIntegrated_E2
    SigmaX = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -log(ValueExponentX / ValueAX))
    SigmaY = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -log(ValueExponentY / ValueAY))
    return [SigmaX, SigmaY]
print(BeamGeoSize())

def BeamAngularSize():
    Ixp = lambda u, ddl, up: NewSource()[0].subs([(x, u), (xp, up), (dl, ddl)])
    print('Ixp is :', Ixp(x, dl, xp))
    Iyp = lambda v, ddl, vp: NewSource()[1].subs([(y, v), (yp, vp), (dl, ddl)])
    print('Iyp is :', Iyp(y, dl, yp))
    IYpint = lambda v, ddl, vp: Iyp(v, ddl, vp) * SourceLambda(ddl, SigmaSLambda=1e-4) * SourceI
    print('IYint is :', IYpint(y, dl, yp))
    IxpIntegrated_0 = si.quad(Ixp, -10 ** -6, 10 ** -6, args=(0, 0))[0]
    IxpIntegrated_E6 = si.quad(Ixp, -10 ** -6, 10 ** -6, args=(0, 10 ** -6))[0]
    IypIntegrated_0 = si.nquad(IYpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
    IypIntegrated_E6 = si.nquad(IYpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -6,))[0]
    print(IxpIntegrated_0, IxpIntegrated_E6, IypIntegrated_0, IypIntegrated_E6)
    ValueAXp = IxpIntegrated_0 * IypIntegrated_0
    print(ValueAXp)
    ValueAYp = ValueAXp
    ValueExponentXp = IypIntegrated_0 * IxpIntegrated_E6
    ValueExponentYp = IxpIntegrated_0 * IypIntegrated_E6
    SigmaXp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentXp / ValueAXp))
    SigmaYp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentYp / ValueAYp))
    return [SigmaXp, SigmaYp]
print(BeamAngularSize())

def Sigma1_MaxFluxL_FluxPhi():
    Ix = lambda u, up, ddl: NewSource()[0].subs([(x, u), (xp, up), (dl, ddl)])
    print('Ix is :',Ix(x, xp, dl))
    Iy = lambda v, vp, ddl: NewSource()[1].subs([(y, v), (yp, vp), (dl, ddl)])
    IYint = lambda v, vp, ddl: Iy(v, vp, ddl) * SourceLambda(ddl, SigmaSLambda=1e-4) * SourceI
    IxIntegrated = si.nquad(Ix, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
    print('IxIntegrated is :', IxIntegrated)
    # ValueAL needs dl = 0, so we set it to 0 during the integration
    ValueAL = IxIntegrated * si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
    print(" ValueAL gives :", ValueAL)
    # ValueExponentL needs dl = 10**-3, so we set it to 10**-3 during the integration
    ValueExponentL = IxIntegrated * si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -3,))[0]
    print(" ValueExponentL gives :", ValueExponentL)
    Sigma = 1 / 2 / sqrt(2 * np.log(2)) * sqrt(4 * log(2) / -log(ValueExponentL / ValueAL) / 10 ** 6)
    MaxFluxL = ValueAL
    FluxPhi = IxIntegrated * \
              si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6], [dlBoundaries[0], dlBoundaries[1]]])[0]
    FluxPhi = CoefAtten * CoefMonoX * CoefMonoY * FluxPhi
    return Sigma, MaxFluxL, FluxPhi
print(Sigma1_MaxFluxL_FluxPhi())

# # todo Single slit example
# # number of elements in the device : n
#
# z0 = 10000
# z1 = 12000
# Flight_paths_in_order = [z0,z1]
# AperturSlitX0 = 20
# AperturSlitY0 = 30
# Slit = [AperturSlitX0, AperturSlitY0, np.ones((3, 3)), 0]
# MatTab = [MatrixFlight(z0), Slit[2], MatrixFlight(z1)]
# dlBoundaries = [-10**-6,10**-6]
# CoefMonoX = 1
# CoefMonoY = 1
# CoefAtten = 1
# SourceI = 1e25
#
# def MatCreation():
#     MatTempX = np.array([x,xp,dl])
#     MatTempY = np.array([y, yp, dl])
#     for i in range(len(MatTab)-1,0,-1):
#         MatTempX = np.dot(MatTab[i],MatTempX)
#         MatTempY = np.dot(MatTab[i], MatTempY)
#     return [MatTempX,MatTempY]
# print(">>>>>>>" , MatCreation()[1], np.shape(MatCreation()[0]),np.shape(MatCreation()[1]))
#
# def NewSource():
#     MatTempX = MatCreation()[0]
#     MatTempY = MatCreation()[1]
#     NewSourceX = SourceXXP(MatTempX[0], MatTempX[1])
#     NewSourceY = SourceYYP(MatTempY[0], MatTempY[1])
#     return [NewSourceX, NewSourceY]
# print(NewSource())
#
# del MatTab[0:2]
# MatCreation()
#
# def NewSource2():
#     NewSourceX = NewSource()[0]*AcceptanceSlit(MatCreation()[0][0], Slit[0], Slit[3])
#     NewSourceY = NewSource()[1]*AcceptanceSlit(MatCreation()[1][0], Slit[1], Slit[3])
#     return [NewSourceX, NewSourceY]
# print(">>>>>>", NewSource2())
#
# # Integrations
# # Beam Size
#
# # def IntegralXXP():
# #     NewSourceX = NewSource2()[0]
# #     if sp.diff(NewSourceX, dl) == 0:
# #         return 1
# #     else:
# #         return sp.integrate(NewSourceX, (dl, -np.inf, np.inf))
# # print(IntegralXXP())
# #
# # def IntegralYYP():
# #     NewSourceY = NewSource2()[1]
# #     if sp.diff(NewSourceY, dl) == 0:
# #         return 1
# #     else:
# #         return sp.integrate(NewSourceY, (dl, -np.inf, np.inf))
# # print(IntegralYYP())
#
# def BeamGeoSize():
#     Ix = lambda up, ddl, u: NewSource2()[0].subs([(x, u), (xp, up), (dl, ddl)])
#     print('Ix is :', Ix(xp, dl, x))
#     Iy = lambda vp, ddl, v: NewSource2()[1].subs([(y, v), (yp, vp), (dl, ddl)])
#     print('Iy is :', Iy(y, yp, dl))
#     if sp.diff(Ix(xp, dl, x), dl) == 0:
#         IYint = lambda vp, ddl, v: Iy(vp, ddl, v) * SourceLambda(ddl, SigmaSLambda=1e-3) * SourceI
#         print('IYint is :', IYint(yp, dl, y))
#         #we are going to do 4 integrations : along xp and dl with x = {0,10**-2}, along yp and dl with y = {0,10**-2}
#         #we can do that since the integrals can be separated, and it takes less time to calculate. Adding a parameter
#         #to a numerical integration multiplies the execution time by approx 300.
#         # args(0,10**-2) sets the values of dl and x to 0 and 10**-2
#         IxIntegrated_0 = si.quad(Ix, -10 ** -6, 10 ** -6, args=(0,0))[0]
#         IxIntegrated_E2 = si.quad(Ix, -10 ** -6, 10 ** -6, args=(0,10**-2))[0]
#         IyIntegrated_0 = si.nquad(IYint, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(0,))[0]
#         IyIntegrated_E2 = si.nquad(IYint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10**-2,))[0]
#         print(IxIntegrated_0, IxIntegrated_E2, IyIntegrated_0, IyIntegrated_E2 )
#         ValueAX = IxIntegrated_0 * IyIntegrated_0
#         print(ValueAX)
#         ValueAY = ValueAX
#         ValueExponentX = IyIntegrated_0 * IxIntegrated_E2
#         ValueExponentY = IxIntegrated_0 * IyIntegrated_E2
#         SigmaX = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentX / ValueAX))
#         SigmaY = 1/2/sqrt(2*np.log(2)) * sp.sqrt(4*log(2)*(10**-4)/-sp.log(ValueExponentY/ValueAY))
#         return [SigmaX, SigmaY]
#     elif sp.diff(Iy(yp, dl, y), dl) == 0:
#         IXint = lambda up, ddl, u: Ix(up. ddl, u) * SourceLambda(ddl, SigmaSLambda=1e-4) * SourceI
#         IxIntegrated_0 = si.nquad(IXint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
#         IxIntegrated_E2 = si.nquad(IXint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -2,))[0]
#         IyIntegrated_0 = si.quad(Iy,-10 ** -6, 10 ** -6, args=(0,0))[0]
#         IyIntegrated_E2 = si.quad(Iy,-10 ** -6, 10 ** -6, args=(0, 10**-2))[0]
#         ValueAX = IxIntegrated_0 * IyIntegrated_0
#         ValueAY = ValueAX
#         ValueExponentX = IyIntegrated_0 * IxIntegrated_E2
#         ValueExponentY = IxIntegrated_0 * IyIntegrated_E2
#         SigmaX = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentX / ValueAX))
#         SigmaY = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentY / ValueAY))
#         return [SigmaX, SigmaY]
#     else:
#         print("Computation time too long, DeltaLambda variation on both axis -> not possible")
#         return 0
# # print(BeamGeoSize())
#
#
# # # Angle size of the beam
#
# def BeamAngularSize():
#     Ixp = lambda u, ddl, up: NewSource2()[0].subs([(x, u), (xp, up), (dl, ddl)])
#     print('Ixp is :', Ixp(x, dl, xp))
#     Iyp = lambda v, ddl, vp: NewSource2()[1].subs([(y, v), (yp, vp), (dl, ddl)])
#     print('Iyp is :', Iyp(y, dl, yp))
#     if sp.diff(Ixp(x, dl, xp), dl) == 0:
#         IYpint = lambda v, ddl, vp: Iyp(v, ddl, vp) * SourceLambda(ddl, SigmaSLambda=1e-4) * SourceI
#         print('IYint is :', IYpint(y, dl, yp))
#         IxpIntegrated_0 = si.quad(Ixp, -10 ** -6, 10 ** -6, args=(0, 0))[0]
#         IxpIntegrated_E6 = si.quad(Ixp, -10 ** -6, 10 ** -6, args=(0, 10 ** -6))[0]
#         IypIntegrated_0 = si.nquad(IYpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
#         IypIntegrated_E6 = si.nquad(IYpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -6,))[0]
#         print(IxpIntegrated_0, IxpIntegrated_E6, IypIntegrated_0, IypIntegrated_E6)
#         ValueAXp = IxpIntegrated_0 * IypIntegrated_0
#         print(ValueAXp)
#         ValueAYp = ValueAXp
#         ValueExponentXp = IypIntegrated_0 * IxpIntegrated_E6
#         ValueExponentYp = IxpIntegrated_0 * IypIntegrated_E6
#         SigmaXp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentXp / ValueAXp))
#         SigmaYp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentYp / ValueAYp))
#         return [SigmaXp, SigmaYp]
#     elif sp.diff(Iyp(y, dl, yp), dl) == 0:
#         IXpint = lambda u, ddl, up: Ixp(u, ddl, up) * SourceLambda(ddl, SigmaSLambda=1e-4) * SourceI
#         IxpIntegrated_0 = si.nquad(IXpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(0,))[0]
#         IxpIntegrated_E6 = si.nquad(IXpint, [[-10 ** -6, 10 ** -6], [-10 ** -6, 10 ** -6]], args=(10 ** -6,))[0]
#         IypIntegrated_0 = si.quad(Iyp, -10 ** -6, 10 ** -6, args=(0, 0))[0]
#         IypIntegrated_E6 = si.quad(Iyp, -10 ** -6, 10 ** -6, args=(0, 10 ** -6))[0]
#         ValueAXp = IxpIntegrated_0 * IypIntegrated_0
#         print(ValueAXp)
#         ValueAYp = ValueAXp
#         ValueExponentXp = IypIntegrated_0 * IxpIntegrated_E6
#         ValueExponentYp = IxpIntegrated_0 * IypIntegrated_E6
#         SigmaXp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentXp / ValueAXp))
#         SigmaYp = 1 / 2 / sqrt(2 * np.log(2)) * sp.sqrt(4 * log(2) * (10 ** -4) / -sp.log(ValueExponentYp / ValueAYp))
#         return [SigmaXPmicrorad, SigmaYPmicrorad]
#     else:
#         print("Computation time too long, DeltaLambda variation on both axis -> not possible")
#         return 0
# # print(BeamAngularSize())
#
# #flux
#
# # def Beam():                                                                 # X-ray source, kinda useless
# #     SourceI = 6 * 10**20
# #     return NewSource2()[0]*NewSource2()[1]*SourceLambda(dl, SigmaSLambda=1e-6)*SourceI
#
#
# def Sigma1_MaxFluxL_FluxPhi():
#     Ix = lambda u, up, ddl: NewSource2()[0].subs([(x, u), (xp, up), (dl, ddl)])
#     #nquad only works with a function that has non-global and non-symbol parameters
#     print('Ix is :',Ix(x, xp, dl))
#     Iy = lambda v, vp, ddl: NewSource2()[1].subs([(y, v), (yp, vp), (dl, ddl)])
#     if sp.diff(Ix(x, xp, dl), dl) == 0:
#         #basically, we need to split the expression otherwise it takes too much time to integrate
#         IYint = lambda v, vp, ddl : Iy(v, vp, ddl)*SourceLambda(ddl, SigmaSLambda=1e-4)*SourceI
#         #since Ix doesnt not depend upon dl, args=(0,) sets its value to 0 for the integration and it changes nothing
#         IxIntegrated = si.nquad(Ix, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(0,))[0]
#         print('IxIntegrated is :',IxIntegrated)
#         #ValueAL needs dl = 0, so we set it to 0 during the integration
#         ValueAL= IxIntegrated * si.nquad(IYint, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(0,))[0]
#         print(" ValueAL gives :", ValueAL)
#         #ValueExponentL needs dl = 10**-3, so we set it to 10**-3 during the integration
#         ValueExponentL = IxIntegrated * si.nquad(IYint, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(10**-3,))[0]
#         print(" ValueExponentL gives :", ValueExponentL)
#         Sigma = 1/2/sqrt(2*np.log(2)) * sqrt(4 * log(2) / -log(ValueExponentL / ValueAL) / 10 ** 6)
#         MaxFluxL = ValueAL
#         FluxPhi = IxIntegrated * si.nquad(IYint, [[-10**-6, 10**-6], [-10**-6, 10**-6], [dlBoundaries[0], dlBoundaries[1]]])[0]
#         FluxPhi = CoefAtten * CoefMonoX * CoefMonoY * FluxPhi
#         return Sigma, MaxFluxL, FluxPhi
#     elif sp.diff(Iy(y, yp, dl), dl) == 0:
#         IXint = lambda u, up, ddl : Ix(u, up, ddl)*SourceLambda(ddl, SigmaSLambda=1e-4)*SourceI
#         IyIntegrated = si.nquad(Iy, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(0,))[0]
#         ValueAL = IyIntegrated * si.nquad(IXint, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(0,))[0]
#         print(" ValueAL gives :", ValueAL)
#         ValueExponentL = IyIntegrated * si.nquad(IXint, [[-10**-6, 10**-6], [-10**-6, 10**-6]], args=(10 ** -3,))[0]
#         print(" ValueExponentL gives :", ValueExponentL)
#         Sigma = 1/2/sqrt(2*np.log(2)) * sqrt(4 * log(2) / -log(ValueExponentL / ValueAL) / 10 ** 6)
#         MaxFluxL = ValueAL
#         FluxPhi = IyIntegrated * si.nquad(IXint, [[-10**-6, 10**-6], [-10**-6,10**-6], [dlBoundaries[0], dlBoundaries[1]]])[0]
#         FluxPhi = CoefAtten * CoefMonoX * CoefMonoY * FluxPhi
#         return Sigma, MaxFluxL, FluxPhi
#     else:
#         print("Computation time too long, DeltaLambda variation on both axis -> not possible")
#         return 0
# # print(Sigma1_MaxFluxL_FluxPhi())