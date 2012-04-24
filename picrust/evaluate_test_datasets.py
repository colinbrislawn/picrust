#!/usr/bin/env python
# File created on April 10  2012
from __future__ import division

__author__ = "Jesse Zaneveld"
__copyright__ = "Copyright 2012, The PICRUST project"
__credits__ = ["Jesse Zaneveld"]
__license__ = "GPL"
__version__ = "1.4.0-dev"
__maintainer__ = "Jesse Zaneveld"
__email__ = "zaneveld@gmail.com"
__status__ = "Development"

from numpy import  array,ravel
from copy import copy
from cogent.maths.stats.test import correlation 
from cogent.maths.stats.distribution import tprob,t_high
from biom.table import table_factory




def evaluate_test_dataset(observed_table,expected_table):
    """ evaluate the correlation between an observed and expected
    biom table.

    Returns data points for a scatter plot of observed v. expected values,
    and a dict of correlations keyed by method (each containing the r value,
    then the probability) 
    """
    # identify the overlapping otus that can be used to predict metagenomes 
    overlapping_ids = list(set(observed_table.ObservationIds) &
                            set(expected_table.ObservationIds))
    #print "dir(observed_table):\n",dir(observed_table)
    #print overlapping_ids

    if len(overlapping_ids) < 1:
        raise ValueError,\
         "No ids are in common  between the observed and expected tables, so no evaluations can be performed."

    # create lists to contain filtered data - we're going to need the data in 
    # numpy arrays, so it makes sense to compute this way rather than filtering
    # the tables
    obs_data = []
    exp_data = []

    # build lists of filtered data
    for obs_id in overlapping_ids:
        obs_data.append(observed_table.observationData(obs_id))
        exp_data.append(expected_table.observationData(obs_id))

    #print obs_data
    #print exp_data
    flat_obs_data = ravel(array(obs_data))
    flat_exp_data = ravel(array(exp_data))
    #print flat_obs_data
    #print flat_exp_data

    #GET THE SCATTER PLOT POINTS
    scatter_data_points =\
      zip(flat_obs_data,flat_exp_data)
    
    # CALCULATE CORRELATIONS
    correlations = {}

    
    pearson_r,pearson_t_prob =\
      correlation(flat_obs_data,flat_exp_data)
    
    correlations["pearson"] = (pearson_r,pearson_t_prob)
    
    spearman_r,spearman_t_prob =\
      spearman_correlation(flat_obs_data,flat_exp_data)
    
    correlations["spearman"] = (spearman_r,spearman_t_prob)
    
     
    return scatter_data_points,correlations     


def convert_vals_to_spearman_ranks(vals):
    """Return the rank of each val in list for Spearman rank correlation
    vals -- a list of floats

    Ranks will be returned in the same order as the entered values.
    Calculating rank:  if there are no ties, rank is just position in the ordered
    list.  If there are ties, then the rank is equal to the mean of all tied ranks
    """
    
    #In order to find ranks, we need to 
    #sort values from largest to smallest
    ordered_vals = sorted(vals,reverse=True)
    

    #Next we need to generate a mapping between 
    #each value and its rank using the sorted
    #list, so that we can apply it to the original 
    #list
    
    val_to_rank = {}
    for i,val1 in enumerate(ordered_vals):
        
        #Get indices (numbering from 1 not 0) of all occurences of value
        ranks= [j+1 for j,val2 in enumerate(ordered_vals) if val2 == val1]
        
        #The overall rank is always the mean of the list of ranks
        rank = float(sum([r for r in ranks]))/float(len(ranks))
        
        val_to_rank[val1] = rank

    result = []
    for val in vals:
        result.append(val_to_rank[val])

    return result

def calc_spearman_t(r,n,tails='two-tailed',eps=1e-10):
    """Calculate the t value, and probability for Spearman correlation
    
    Equation from Wikipedia article on Spearman rank correlation:
    http://en.wikipedia.org/wiki/Spearman's_rank_correlation_coefficient
    
    TODO:  verify with additional / published sources.
    TODO:  want to find the correct handling for the 
    case of perfect correlation
    """
    #Right now I subtract an arbitrarily tiny
    #epsilon if r is exactly 1.0 to prevent divide-by-zero
    #errors.  

    if r == 1.0:
        r = r-eps
    
    t = r*(((n-2)/(1.0-r**2))**0.5)
    
    if tails == 'two-tailed':
        prob = tprob(t,n-2)
    elif tails == 'high':
        prob = t_high(t,n-2)
    elif tails == 'low':
        prob = t_low(t,n-2)
    else:
        raise RuntimeError("Valid prob. methods are 'two-tailed','high',and 'low'")

    return prob

        
def spearman_correlation(x_array,y_array,tails = 'two-tailed'):
    """calculate the Spearman rank correlation for x and y
    
    x_array -- a 1D NumPy array
    y_array -- a 1D NumPy array
    """
    
    #Convert absolute values to ranks
    x_ranks = convert_vals_to_spearman_ranks(x_array)
    y_ranks = convert_vals_to_spearman_ranks(y_array)
    
    #Now we get r by performing Pearson correlation
    #on the rank data.
    r, pearson_prob = correlation(x_ranks, y_ranks)
    
    #However, the conversion to ranks affects the prob
    #so we need the corrected version of the t statistic
    #not the generic version used by Pearson correlation
    spearman_t_prob =\
      calc_spearman_t(r,n=len(x_array),tails=tails)

    
    #return r,spearman_t_prob
    return r,spearman_t_prob


def calculate_accuracy_stats_from_observations(obs,exp,verbose=False):
    """Return statistics derived from the confusion matrix
    obs -- a list of floats representing observed values
    exp -- a list of floats for expected values (same order as obs)
    verbose -- print verbose output 
    """
    
    tp,fp,fn,tn =\
      confusion_matrix_from_data(obs,exp,verbose)
    
    result =\
      calculate_accuracy_stats_from_confusion_matrix(tp,fp,fn,tn,verbose)
    return result
    
def calculate_accuracy_stats_from_confusion_matrix(tp,fp,fn,tn,verbose=False):
    """Calculate accuracy,sensitivity,specificity,etc from the number of true positives,false positives,false negatives, and true negatives
    
    tp -- number of true positives
    fp -- number of false positives
    fn -- number of false negatives
    tn -- number of true negatives
    verbose -- print verbose output
    """

    n = sum([tp,fp,tn,fn])
    results ={} 
    results['positive_predictive_value'] = tp/(tp+fp) # == precision
    results['sensitivity'] =  tp/(tp+fn) # == TPR, hit rate, recall
    results['specificity'] =  tn/(tn+fp) # == 1- FPR, TNR
    results['false_positive_rate'] = fp/(fp+tn)
    results['accuracy'] = (tp + tn)/n  

    return results
    
def confusion_matrix_from_data(obs,exp,verbose=False):
    """Return the number of true_positive,false_positive,false_negatives,false_positives from paired lists of observed and expected values


    obs -- a list of floats representing observed values
    exp -- a list of floats for expected values (same order as obs)
    verbose -- print verbose output 
    """
    tp_indices,fp_indices,fn_indices,tn_indices =\
      confusion_matrix_results_by_index(obs,exp,verbose)
    #print obs,exp
    #print tp_indices,fp_indices,fn_indices,tn_indices 
    tp = float(len(tp_indices))
    fp = float(len(fp_indices))
    fn = float(len(fn_indices))
    tn = float(len(tn_indices)) 
    #print tp,fp,fn,tn 
    return tp,fp,fn,tn

def confusion_matrix_results_by_index(obs,exp,verbose=False):
    """Return indices in obs that are true positives, false positives, false negatives or true negatives

    
    obs -- a list of floats representing observed values
    exp -- a list of floats for expected values (same order as obs)
    verbose -- print verbose output 
    
    All values >= 1 are considered presence and scored
    identically.  0s are scored as absence.
    """
    
    tp_indices =\
        [i for i,f in enumerate(obs) if exp[i] >= 1 and obs[i]>=1]
    
    fp_indices =\
        [i for i,f in enumerate(obs) if exp[i] == 0 and obs[i]>=1]

    fn_indices =\
        [i for i,f in enumerate(obs) if exp[i] >= 1 and obs[i]==0]

        
    tn_indices =\
        [i for i,f in enumerate(obs) if exp[i] == 0 and obs[i]==0]
    

    return tp_indices,fp_indices,fn_indices,tn_indices

def roc_analysis(trials):
    """Perform ROC analysis for a set of trials, each a list of obs,exp values"""
    points = roc_points(trials)
    area_under_the_curve = roc_auc(trials)
    return points,area_under_the_curve


def roc_points(trials):
    """get points for a roc curve from lists of paired observed and expected values
    trials -- a list of (obs,exp) tuples, where obs and exp are lists of observed vs. expected data values
    
    Returns a list of points on the ROC curve in x,y format, with the False Positive Rate (FPR, 1-specificity) on the x axis, and the True Positive Rate (sensitivity) on the y axis."""
    points = []
    #print trials
    for obs,exp in trials:
        curr_result = calculate_accuracy_stats_from_observations(obs,exp)
        x = curr_result["false_positive_rate"]
        y = curr_result["sensitivity"]
        points.append((x,y))
    #print points
    return points

def roc_auc(points):
    """Get the ROC Area Under the Curve given a list of obs,exp values for trials
    trials -- a list of (obs,exp) tuples, where obs and exp are lists of observed vs. expected data values
    
    This is the average prob. of ranking a random positive above a random negative.
    """

    #points = roc_points(trials)
    ordered_points = sorted(points)
    G = gini_coefficient(points)
    #print "G:",G
    area_under_the_curve = (G+1.0)/2.0 
    #print "AUC:",area_under_the_curve
    return area_under_the_curve
 

def gini_coefficient(points):
    """Calculate the Gini coefficient using trapezoidal approximations
    
    trials -- a list of (obs,exp) tuples, where obs and exp are lists of observed vs. expected data values

    """
    points = sorted(points)
    indices_to_consider = [(i,i-1) for i in range(1,len(points))]
    #print indices_to_consider
    #print points
    X,Y = zip(*points)
    #print X,Y
    gini = 1.0 - \
      sum([float((X[k]-X[k_minus_one])*(Y[k]+Y[k_minus_one])) for k,k_minus_one in indices_to_consider])
                
    return gini