"""Elitist binary genetic search: tournaments,uniform crossover,bit-flip mutation."""
import importlib.util
from pathlib import Path
import sys

import numpy as np

_spec=importlib.util.spec_from_file_location('atlas_b10_support',Path(__file__).resolve().parents[2]/'support.py')
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=support;_spec.loader.exec_module(support)


def tournament_selection(fitness,contestants):
    values=np.asarray(fitness);selected=np.asarray(contestants)
    if values.ndim!=1 or not 2<=len(values)<=64 or values.dtype.kind not in 'iuf':
        raise ValueError('finite real fitness vector of length2..64 required')
    values=np.array(values,dtype=float,copy=True)
    if not np.isfinite(values).all() or np.any(np.abs(values)>1e100):
        raise ValueError('fitness outside finite objective bounds')
    if (selected.ndim!=1 or selected.dtype.kind not in 'iu' or not 1<=len(selected)<=len(values)
            or np.any(selected<0) or np.any(selected>=len(values)) or len(np.unique(selected))!=len(selected)):
        raise ValueError('distinct valid contestant indices required')
    return min((int(i) for i in selected),key=lambda i:(values[i],i))


def uniform_crossover(first,second,mask):
    a=support.bits(first);b=support.bits(second,dimension=len(a));choice=np.asarray(mask)
    if choice.shape!=a.shape or choice.dtype.kind!='b':
        raise ValueError('boolean crossover mask must match parent shape')
    return np.where(choice,a,b),np.where(choice,b,a)


def bit_flip_mutation(value,mask):
    bits=support.bits(value);choice=np.asarray(mask)
    if choice.shape!=bits.shape or choice.dtype.kind!='b':
        raise ValueError('boolean mutation mask must match bit string')
    return bits ^ choice.astype(np.int64)


class GeneticAlgorithm:
    def __init__(self,population_size=16,crossover_rate=.8,mutation_rate=.05,
                 tournament_size=2,elite_count=1,random_state=0):
        self.population_size,self.crossover_rate,self.mutation_rate=population_size,crossover_rate,mutation_rate
        self.tournament_size,self.elite_count,self.random_state=tournament_size,elite_count,random_state
        self._settings()

    def _settings(self):
        support.integer(self.population_size,'population_size',2,64)
        support.integer(self.tournament_size,'tournament_size',2,self.population_size)
        support.integer(self.elite_count,'elite_count',1,self.population_size-1)
        support.integer(self.random_state,'random_state',0,2**32-1)
        support.real(self.crossover_rate,'crossover_rate',0.,1.)
        support.real(self.mutation_rate,'mutation_rate',0.,1.)

    def _select(self,fitness,rng):
        contestants=rng.permutation(len(fitness))[:int(self.tournament_size)]
        return tournament_selection(fitness,contestants)

    @support.numerical
    def minimize(self,fun,n_bits,*,initial_population=None,max_generations=100,target_value=None,stagnation_generations=None):
        self._settings();d=support.integer(n_bits,'n_bits',1,32)
        support.integer(max_generations,'max_generations',1,1000)
        if self.population_size+(self.population_size-self.elite_count)*max_generations>20000:
            raise ValueError('population/generation fitness budget exceeds20000')
        if target_value is not None:target_value=support.real(target_value,'target_value',-1e100,1e100)
        if stagnation_generations is not None:support.integer(stagnation_generations,'stagnation_generations',1,max_generations)
        rng=np.random.default_rng(self.random_state)
        if initial_population is None:
            population=rng.integers(0,2,size=(int(self.population_size),d),dtype=np.int64)
        else:
            a=np.asarray(initial_population)
            if a.shape!=(self.population_size,d) or a.dtype.kind not in 'biu' or np.any((a!=0)&(a!=1)):
                raise ValueError('initial population must be population_size-by-n_bits binary matrix')
            population=np.array(a,dtype=np.int64,copy=True)
        fitness=np.array([support.objective(fun,x) for x in population])
        nfev=len(population);history=[float(fitness.min())];stagnant=generations=0;status='generation-budget'
        converged=bool(target_value is not None and history[-1]<=target_value)
        while generations<max_generations and not converged:
            elite_indices=np.argsort(fitness,kind='stable')[:int(self.elite_count)]
            new_population=[population[i].copy() for i in elite_indices]
            new_fitness=[float(fitness[i]) for i in elite_indices]
            while len(new_population)<self.population_size:
                first=population[self._select(fitness,rng)];second=population[self._select(fitness,rng)]
                if rng.random()<self.crossover_rate:
                    children=uniform_crossover(first,second,rng.random(d)<.5)
                else:children=(first.copy(),second.copy())
                for child in children:
                    if len(new_population)==self.population_size:break
                    child=bit_flip_mutation(child,rng.random(d)<self.mutation_rate)
                    new_population.append(child);new_fitness.append(support.objective(fun,child));nfev+=1
            population=np.array(new_population,dtype=np.int64);fitness=np.array(new_fitness)
            best=float(fitness.min());stagnant=stagnant+1 if best>=history[-1] else 0
            history.append(best);generations+=1
            converged=bool(target_value is not None and best<=target_value)
            if not converged and stagnation_generations is not None and stagnant>=stagnation_generations:
                status='stagnation';break
        if converged:status='target-reached'
        index=int(np.argmin(fitness))
        return support.OptimizationResult(population[index].copy(),float(fitness[index]),generations,nfev,status,converged,
            np.array(history),dict(population=population.copy(),fitness=fitness.copy(),stagnant_generations=stagnant,
                                   target_value=target_value,fitness_evaluations=nfev))
