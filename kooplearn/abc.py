from __future__ import annotations
import abc
import os
from typing import Optional, Union, Callable

import numpy as np


# Abstract base classes defining the interface to implement when extending kooplearn
class BaseModel(abc.ABC):
    @abc.abstractmethod
    def fit(self, data: np.ndarray):
        """Fit the model to the data.

        Args:
            data (np.ndarray): Batch of context windows of shape ``(n_samples, context_len, *features_shape)``. The length of the lookforward and lookback windows will be inferred from the context window length and the :attr:`lookback_len` attribute.
        """
        pass

    @abc.abstractmethod
    def predict(self, data: np.ndarray, t: int = 1, observables: Optional[Union[Callable, np.ndarray]] = None):
        """
        Predicts the state or, if the system is stochastic, its expected value :math:`\mathbb{E}[X_t | X_0 = X]` after ``t`` instants given the initial conditions ``X = data[:, self.lookback_len:, ...]`` being the lookback slice of ``data``.
        
        If ``observables`` are not ``None``, returns the analogue quantity for the observable instead.

        Args:
            data (numpy.ndarray): Initial conditions to predict. Array of context windows with shape ``(n_init_conditions, context_len, *features_shape)`` whose trailing dimensions match the dimensions of the data used in :func:`fit`.
            t (int): Number of steps to predict (return the last one).
            observables (callable, numpy.ndarray or None): Callable, array of context windows of shape ``(n_init_conditions, context_len, *obs_features_shape)`` or ``None``. If array, it must be the observable evaluated at the training data. If ``None`` returns the predictions for the state.

        Returns:
           The predicted (expected) state/observable at time :math:`t`, shape ``(n_init_conditions, n_obs_features)``.
        """
        pass

    @abc.abstractmethod
    def eig(self, eval_left_on: Optional[np.ndarray] = None, eval_right_on: Optional[np.ndarray] = None):
        """
        Returns the eigenvalues of the Koopman/Transfer operator and optionally evaluates left and right eigenfunctions.

        Args:
            eval_left_on (numpy.ndarray or None): Array of context windows on which the left eigenfunctions are evaluated, shape ``(n_samples, context_len, *features_shape)``.
            eval_right_on (numpy.ndarray or None): Array of context windows on which the right eigenfunctions are evaluated, shape ``(n_samples, context_len, *features_shape)``.

        Returns:
            Eigenvalues of the Koopman/Transfer operator, shape ``(rank,)``. If ``eval_left_on`` or ``eval_right_on``  are not ``None``, returns the left/right eigenfunctions evaluated at ``eval_left_on``/``eval_right_on``: shape ``(n_samples, rank)``.
        """
        pass

    @abc.abstractmethod
    def save(self, path: os.PathLike):
        pass
    
    @classmethod
    @abc.abstractmethod
    def load(path: os.PathLike):
        pass

    @abc.abstractmethod
    def modes(self, data: np.ndarray, observables: Optional[Union[Callable, np.ndarray]] = None):
        """
        Computes the mode decomposition of arbitrary observables of the Koopman/Transfer operator at the states defined by ``data``.
        
        Informally, if :math:`(\\lambda_i, \\xi_i, \\psi_i)_{i = 1}^{r}` are eigentriplets of the Koopman/Transfer operator, for any observable :math:`f` the i-th mode of :math:`f` at :math:`x` is defined as: :math:`\\lambda_i \\langle \\xi_i, f \\rangle \\psi_i(x)`. See :footcite:t:`Kostic2022` for more details.

        Args:
            data (numpy.ndarray): Initial conditions to compute the modes on. See :func:`predict` for additional details.
            observables (callable, numpy.ndarray or None): Callable, array of context windows of shape ``(n_samples, context_len, *obs_features_shape)`` or ``None``. If array, it must be the desired observable evaluated on the *lookforward slice* of the training data. If ``None`` returns the predictions for the state.
        Returns:
            Modes of the system at the states defined by ``data``. Array of shape ``(rank, n_samples, ...)``.
        """
        pass

    @property
    @abc.abstractmethod
    def is_fitted(self) -> bool:
        """Check if the model is fitted.

        Returns:
            bool: Returns ``True`` if the model is fitted, ``False`` otherwise.
        """
        pass

    @property
    @abc.abstractmethod
    def lookback_len(self) -> int:
        """Length of the lookback window associated to the contexts. Upon fitting, the dimension of the lookforward window will be inferred from the context window length and this attribute. Moreover, shape checks against this attribute will be performed on the data passed to :func:`fit`, :func:`predict`, :func:`eig` and :func:`modes`.

        Returns:
            int: Length of the lookback window associated to the contexts.
        """
        pass

class FeatureMap(abc.ABC):
    """Abstract Base Class for feature maps. The :func:`__call__` method must accept a batch of context windows of shape ``(n_samples, context_len, *features_shape)`` and return a batch of features of shape ``(n_samples, out_features)``.

    .. warning::

        A feature map should return a two dimensional array. Though this is not a strict condition, models such as :class:`kooplearn.models.ExtendedDMD`, :class:`kooplearn.models.KernelDMD` and :class:`kooplearn.models.DeepEDMD` will automatically flatten the results. 
    """
    @abc.abstractmethod
    def __call__(self, data: np.ndarray) -> np.ndarray:
        pass

class TrainableFeatureMap(FeatureMap):
    @abc.abstractmethod
    def fit(self, *a, **kw) -> None:
        """Fit the feature map to the data.
        """
        pass
    
    @property
    @abc.abstractmethod
    def is_fitted(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def lookback_len(self) -> int:
        """Length of the lookback window associated to the contexts. Upon fitting, the dimension of the lookforward window will be inferred from the context window length and this attribute.

        Returns:
            int: Length of the lookback window associated to the contexts.
        """
        pass
