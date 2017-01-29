"""
"""
import logging
import numpy as np
from skopt.core.utils import get_logger, normalise
from skopt.core.utils import flatten, flatten_two
from skopt.core.tasks import SetTask

DEFAULT_GLOBAL_COST_FUNC = "rms"

def abserr(ref, model):
    """Return the per-element difference model and reference.
    """
    rr = np.asarray(ref)
    mm = np.asarray(model)
    assert rr.shape == mm.shape, (rr.shape, mm.shape)
    return mm - ref

def relerr(ref, model):
    """Return the per-element relative difference between model and reference.

    To handle cases where `ref` vanish, and possibly `model` vanish
    at the same time, we:

        * translate directly a vanishing absolute error into vanishing
          relative error (where both `ref` and `model` vanish.

        * take the model as a denominator, thus yielding 1, where
          `ref` vanishes but `model` is non zero
    """
    rr = np.asarray(ref)
    mm = np.asarray(model)
    # get deviations
    err = abserr(rr, mm)
    # fix the denominator
    denom = rr
    denom[rr == 0.] = mm[rr == 0.]
    # assert 0 absolute error even for 0 denominator
    rele = np.zeros(err.shape)
    rele[err != 0] = err[err != 0] / denom[err != 0]
    return rele

def cost_RMS(ref, model, weights, errf=abserr):
    """Return the weighted-RMS deviation"""
    assert np.asarray(ref).shape == np.asarray(model).shape
    assert np.asarray(ref).shape == np.asarray(weights).shape
    err2 = errf(ref, model) ** 2
    rms = np.sqrt(np.sum(weights*err2))
    return rms

def eval_objectives(objectives):
    """
    """
    fitness = np.array([objv() for objv in objectives])
    return fitness

# ----------------------------------------------------------------------
# Function mappers
# ----------------------------------------------------------------------
# use small letters for the function names; make sure
# the input parser coerces any capitalisation in advance

# cost functions
costf = {"rms": cost_RMS, }

# error types
errf = {"abs": abserr, "rel": relerr, "abserr": abserr, "relerr": relerr,}
# ----------------------------------------------------------------------


class Evaluator (object):
    """
    __Evaluator__

    The evaluator is the only thing visible to the optimiser.  
    It has several things to do:  

    1. Accept a list (or dict?) of parameter values (or key-value pairs),
       and an iteration number (or a tuple: (generation,particle_index)).
    2. Update tasks (and underlying models) with new parameter values.
    3. Execute the tasks to obtain model data with the new parameters.
    5. Evaluate fitness for individual objectives.
    6. Evaluate global fitness (cost) and return the value. It may be 
       good to also return the max error, to be used as a stopping criterion.
    """   
    def __init__(self, objectives, tasks, costf=costf[DEFAULT_GLOBAL_COST_FUNC],
                 utopia = None,
                 verbose=False, logger=logging.getLogger(__name__), **kwargs):
        self.objectives = objectives
        self.weights = normalise([oo.weight for oo in objectives])
        self.tasks = tasks
        self.costf = costf
        if utopia is None:
            self.utopia = np.zeros(len(self.objectives))
        else:
            assert len(utopia) == len(objectives), (len(utopia), len(objectives))
            self.utopia = utopia
        self.verbose = verbose
        self.logger = logger
    
    def evaluate(self, parameters, iteration=None):
        """Evaluate the global fitness of a given point in parameter space.

        This is the only object accessible to the optimiser.

        Args:
            parameters (list or dict): current point in design/parameter space
            iteration: (int or tupple): current iteration or current 
                generation and individual index within generation

        Return:
            fitness (float): global fitness of the current design point
        """
        # Update models with new parameters.
        # Updating the models should be the first task in the tasks list,
        # but user may decide to omit it in some situations (e.g. if only
        # interested in evaluating the set of models, not optimising).
        jj = 0
        task = self.tasks[jj]
        if isinstance(task, SetTask):
            if parameters is None:
                self.logger.warning('Omitting task 1 due to None parameters:')
                self.logger.debug(task)
            else:
                task(parameters, iteration)
            jj = 1
        # Get new model data by executing the rest of the tasks
        for ii, task in enumerate(self.tasks[jj:]):
            kk = ii + jj
            try:
                task()
            except:
                self.logger.critical('\nEvaluation FAILED at task {}:\n{}'.format(kk+1, task))
                raise
        # Evaluate individual fitness for each objective
        self.objvfitness = eval_objectives(self.objectives)
        ref = self.utopia
        # evaluate global fitness
        cost = self.costf(ref, self.objvfitness, self.weights)
        return np.atleast_1d(cost)

    def __call__(self, parameters, iteration=None):
        return self.evaluate(parameters, iteration)
