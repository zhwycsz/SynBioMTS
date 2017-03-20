import re
import numpy as np
import sklearn
from scipy import stats,polyfit
from __future__ import division


class statistics(object):

    def __init__(self):
        pass

    def corr(self,x,y,name="Pearson"):
        # Linear or rank correlation
        # Returns:
        #   r,rho, or tau (float) = the test statistic
        #   pvalue (float) = the p-value for the test

        assert len(x)==len(y), "Arrays x & y must be of equal length to calculate correlation statistics."

        if name == "Pearson":
            (r,pvalue) = stats.pearsonr(x,y)
            return r,pvalue

        elif name == "Spearman":
            (rho,pvalue) = stats.spearmanr(x,y)
            return rho,pvalue

        elif name == "Kendall":
            (tau,pvalue) = stats.kendalltau(x,y)
            return tau,pvalue

        else:
            error = "The {} correlation is not available. \
            Please use 'Pearson', 'Spearman', or 'Kendall.'".format(name)
            ValueError(error)

    def vartest2(self,x,y,alpha=0.05,test="F"):
        # Two-sample F-test/Barlett-test/Levene-test for equal variances
        # Returns:
        #   h (bool)  = test decision, True if the test rejects the null hypothesis
        #   S (float) = the test statistic
        #   pvalue (float) = the p-value for significance of test decision

        if test == "F":
            df1 = len(x)-1
            df2 = len(y)-1
            statistic = np.var(x)/np.var(y) # stat = F
            pvalue = stats.f.sf(stat, df1, df2)

        elif test == "Barlett":
            (statistic,pvalue) = stats.bartlett(x,y)

        elif test == "Levene":
            (statistic,pvalue) = stats.levene(x,y)
        else:
            error = "The {}-test for equal variances is not available. \
            Please use 'F', 'Barlett', or 'Levene'.".format(test)
            ValueError(error)

        h = pvalue < alpha
        # add confidence interval calculation later
        return (h,statistic,pvalue)

    def ttest2(self,x,y,alpha=0.05):
        # Two sample t-test
        # Returns:
        #   h (bool)  = test decision, True if the test rejects the null hypothesis
        #   t (float) = the test statistic
        #   pvalue (float) = the p-value for significance of test decision

        (t,pvalue) = stats.ttest_ind(x,y,equal_var=False,nan_policy='omit')
        h = pvalue < alpha
        return (h,t,pvalue)

    def fit_linear_model(self,x,y,slope=None):
        # Linear least squares (LSQ) linear regression (polynomial fit of degree=1)
        # Returns:
        #   m (float) = slope of linear regression line of form (y = m*x + b)
        #   b (float) = intercept of linear regression line

        assert len(x)==len(y), "Arrays x & Y must be of equal length to fit linear regression model."

        if slope == None:
            (m,b) = polyfit(x,y,deg=1)

        else:
            LSQ = lambda b: np.sum( (y-(slope*x+b))**2.0 )
            res = minimize(LSQ,x0=1,bounds=None)
            (m,b) = (slope,res.x[0])

        # calculate significance of linear regression
        # self.ANOVA()
        
        return (m,b)

    def ANOVA(self,X,y,coeffs):
        # Univariate linear regression tests
        # Quick linear model for sequentially testing the effect of many regressors
        # Using scikit learn's Feature selection toolbox
        # Returns:
        #   F (array) = F-values for regressors
        #   pvalues (array) = p-values for F-scores

        # Compute regressors as product of predictors and the coeffs of a model
        (m,n) = np.shape(X)
        M = np.transpose( [list(coeffs)*m] )
        mX = np.multipy(M,X)

        (F,pvalues) = sklearn.feature_selection.f_regression(mX,y)
        return (F,pvalues)

    def mad(self,x):
        # Median absolute deviation
        # Returns:
        #   MAD (float) = the median absolute deviation of the values in X
        #   diff (list) = a list of deviations of the values in X from the median of X
        median = np.median(x)
        diff = np.absolute(x - median)
        MAD = np.median(diff)
        return (MAD,diff)

    '''Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and Handle Outliers",
    The ASQC Basic References in Quality Control: Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.'''  
    def find_outliers(self,x,threshold=2):
        # Outlier detection method using Iglewicz & Hoaglin's modified Z-score
        # Returns a list of bools, where True is an outlier
        (MAD,diff) = self.mad(x)
        M = 0.6745 * diff / MAD
        outliers = M > threshold
        return outliers

    def empirical_cdf(self):
        # both raw count and probability
        pass

    def auroc(self,predictions,observations,cutoff=None,n=50):
        # Calculate ROC curve and the area under the curve (auc)
        # Returns:
        #   auroc (float) = area under the ROC curve
        #   fpr (array) = false positive rates, where fpr[i] is the FPR at threshold, thresholds[i]
        #   tpr (array) =  true positive rates, where tpr[i] is the TPR at threshold, thresholds[i]
        #   thresholds (array) = thresholds from ROC curve

        # define outcomes as TRUE/FALSE defined by cutoff
        if cutoff == None: cutoff = np.median(outcomes)
        outcomes = (observations > cutoff)

        # preallocate arrays and define n-many threshodls
        fpr = np.zeros(n)
        tpr = np.zeros(n)
        thresholds = np.linspace(min(observations)-2,max(observations)+2,n)

        for i in xrange(0,n):

            threshold = thresholds[i]
            scores = prediction > threshold

            # calculate confusion matrix
            a = sum(scores & outcomes)
            b = sum(scores & ~outcomes)
            c = sum(~scores & outcomes)
            d = sum(~scores & ~outcomes)            

            # calculate fpr and tpr for each threshold
            fpr[i] = b/(b+d)
            tpr[i] = a/(a+c)

        # Add (0,0) and (1,1) data points if not captured by thresholds
        # Sort fpr and tpr arrays

        # Could also use scikit learn roc_curve and roc_auc_score functions
        # sklearn.metrics.roc_curve

        # Calculate area under the ROC curve
        auroc = np.trapz(tpr,fpr)

        return auroc,fpr,tpr,thresholds

    def normKLdiv(self,data,b):
        # Calculate normalized Kullback-Leibler divergence
        # normKLdiv uses data and calculates the normKLdiv relative to a random model (Q) over bin range (-b,b)
        # Returns:
        #   NKLdiv (float)   = normalized Kullback-Leibler divergence
        #   KLdiv (float)    = KL-divergence
        #   KLdivmax (float) = KL-divergence for a perfect model (dirac delta fxn)

        (P,x) = self.pdist(data,b)
        Pmax = np.zeros(len(x))
        Pmax[0] = 1.0
        Q = np.ones(len(x))/len(x)
        KLdiv = self.entropy(P,Q)
        KLdivmax = self.entropy(Pmax,Q)
        NKLdiv = D_KL/D_KL_max

        return (NKLdiv,KLdiv,KLdivmax)

    def pdist(self,data,b,nbins=100,make_outliers_rand=True):
        # Calculate the discrete probability distribution function of a set of data
        # Defined over the range (-b,b) with nbins
        # ignore_outliers (bool) = if True ignore outliers, if False add random error to pdf
        # Returns:
        #   pdf (array) = discrete pdf with probability of event i as pdf[i]
        #   x (array) = midpoints of the bins of the histogram that defines pdf

        # remove outliers outside of range (-b,b)
        data2 = data[~(np.abs(data) > b)]

        # calculate Pset (the pdf of the set of data points within the range)
        edges = np.linspace(-b,b,nbins+1)
        Pset = np.histogram(data2,edges,density=True)
        fset = len(data2)/len(error)
        x = (edges[0:-1]+edges[1:])/2

        if make_outliers_rand:
            # calculate Poutliers (pdf corresponding to random guesses)
            Pout = np.ones(len(x))/len(x)
            fout = 1 - fset
            pdf = fset*Pset + fout*Pout
        else:
            pdf = Pset

        return (pdf,x)

    def entropy(self,pk,qk=None,base=None):
        # Calculate the entropy of a distribution for given probability values
        # pk (array) = probability distribution of a discrete distribution
        # qk (array) = pdf of a second sequence with which pk is compared against
        # base (float) = the logarithmic base to use (default=e)
        # Returns:
        #   S (float) = Shannon entropy if qk is None else Kullback-Leibler divergence
        return stats.entropy(pk,qk,base)

    def model_capacity(self,Hseq,mu,sigma,error):
        # Calculate model capacity (MC)
        # Inputs:
        #   Hseq (float)       = total Shannon sequence entropy for the genetic system
        #   mu, sigma (arrays) = mean and standard deviations of system outcomes with mu[i] and sigma[i] as the mean and std of outcome i
        #   error (array)      = model error for system outcomes (of equal length of mu & sigma)
        # Returns:
        #   MC (float)      = model capacity in bits
        #   Hmodel (float)  = Shannon entropy of the model error distribution
        #   Hrandom (float) = Shannon entropy of a random model error distribution
        #   N (float)       = number of distinguishable outcomes
        #   CV (float)      = coefficient of variation of system outcomes

        # calculate N-distinguishable outcomes
        CV = mean( sigma/mu )
        N = 1000.0 if CV == 0.0 else N = np.round((max(np.log10(mu))-min(np.log10(mu)))/np.log10(1+CV))

        # calculate Hmodel
        pdf,_ = self.pdist(error,b=4,nbins=N)
        Hmodel = self.entropy(pdf)
        
        # calculate Hrandom
        pdf,_ = self.pdist(np.array([np.inf]),b=4,nbins=N)
        Hrandom = self.entropy(pdf)

        # calculate MC
        MC = Hseq*(N-1)*(1-Hmodel/Hrandom)

        return (MC,Hmodel,Hrandom,N,CV)

def hseq(self,sequences,align="left",positions=None):
    # Calcualte total Shannon sequence entropy
    # Returns:
    #   hseq 

    sequences = [seq.upper().replace("U","T") for seq in sequences[:]]
    exp = re.compile('[ATGC]')
    if any([exp.match(seq) is None for seq in sequences]):
        raise ValueError("Invalid letters found in sequences. Only ATGCU accepted.")

    maxseqlen = max([len(seq) for seq in sequence_list])
    samelen   = all([len(sequences[0])==len(seq) for seq in sequences[1:]])

    if   align == "left" and not samelen:
        # align sequences to left and buffer right with Xs
        sequences = [seq+"X"*(maxseqlen-len(seq)) for seq in sequences[:]]

    elif align == "right" and not samelen:
        # align sequences to the right by buffering left with Xs
        sequences = ["X"*(maxseqlen-len(seq))+seq for seq in sequences[:]]

    elif align == "positions":
        # align sequences at alignment_positions and buffer both ends with Xs

        if positions == None:
            raise Exception("Provide positions if align=='positions'")

        lefts     = [len(seq[0:pos]) for seq,pos in zip(sequences,alignment_positions)]
        rights    = [len(seq[pos:]) for seq,pos in zip(sequences,alignment_positions)]
        maxleft   = max(lefts)
        maxright  = max(rights)
        sequences = ["X"*(maxleft-lenl)+seq+"X"*(maxright-lenr) for lenl,seq,lenr in zip(lefts,sequences[:],rights)]
    
    else:
        ValueError("align cannot be {}. Please use 'left','right',or'positions'".format(align))

    assert all(len(sequences[0])==len(seq) for seq in sequences[1:]), "Bug in hseq, sequences aren't the same length."

    # tabulate frequency of each nt at each position
    if samelen: alphabet = 'ATCG'
    else:       alphabet = 'ATCGX'
    counts = {key: np.zeros(maxseqlen) for key in alphabet}

    for seq in sequences:
        for i,c in enumerate(seq):
            counts[c][i] += 1
    
    pkList = [[counts[c][i]/maxseqlen for c in alphabet] for i in xrange(maxseqlen)]

    # calcualte Shannon entropy at each position and total Shannon entropy (hseq)
    S = [self.entropy(pk,base=2) for pk in pkList]
    hseq = sum(S)

    return hseq,S
