import importlib.util, sys
from pathlib import Path
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.cluster import KMeans as SkKM, DBSCAN as SkDB, MeanShift as SkMS, SpectralClustering as SkSC, HDBSCAN as SkHD
from sklearn.mixture import GaussianMixture as SkGM
from sklearn.metrics import adjusted_rand_score, silhouette_samples
ROOT=Path('.')
def load(path):
    spec=importlib.util.spec_from_file_location(path.replace('/','_').replace('-','_'),ROOT/path/'python/solution.py')
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
B='machine-learning/unsupervised-learning/clustering/'
checks=[]
def check(name,cond,detail=''):
    checks.append((name,bool(cond),detail)); print(('PASS ' if cond else 'FAIL ')+name, detail)
rng=np.random.default_rng(44)
centers=np.array([[0,0],[6,0],[3,6.]]); X=np.vstack([c+rng.normal(scale=0.6,size=(25,2)) for c in centers]); truth=np.repeat([0,1,2],25)
# KMeans: explicit init -> compare with sklearn Lloyd
init=X[[0,30,60]]
km=load(B+'k-means').KMeans(3,init=init,n_init=1).fit(X); sk=SkKM(3,init=init,n_init=1,algorithm='lloyd',tol=0).fit(X)
check('KMeans explicit-init centers vs sklearn Lloyd',np.allclose(np.sort(km.cluster_centers_,axis=0),np.sort(sk.cluster_centers_,axis=0),atol=1e-8))
check('KMeans inertia equals hand SSE and sklearn',abs(km.inertia_-sum(((X[km.labels_==j]-km.cluster_centers_[j])**2).sum() for j in range(3)))<1e-9 and abs(km.inertia_-sk.inertia_)<1e-8)
check('KMeans fixed point: labels are nearest centers; centers are means',np.array_equal(km.labels_,np.argmin(((X[:,None]-km.cluster_centers_[None])**2).sum(2),1)) and all(np.allclose(km.cluster_centers_[j],X[km.labels_==j].mean(0)) for j in range(3)))
# Agglomerative vs scipy for 4 linkages (heights + labels ARI==1)
Xs=X[::3]
for method in ['single','complete','average','ward']:
    ag=load(B+'agglomerative-hierarchical-clustering').AgglomerativeClustering(3,linkage=method).fit(Xs)
    Z=linkage(Xs,method=method)
    check(f'Agglomerative {method} merge heights == scipy',np.allclose(ag.distances_,Z[:,2],atol=1e-10) and adjusted_rand_score(ag.labels_,fcluster(Z,3,'maxclust'))==1.0,f'max h diff {np.max(np.abs(ag.distances_-Z[:,2])):.1e}')
# DBSCAN vs sklearn
db=load(B+'dbscan').DBSCAN(eps=1.0,min_samples=4).fit(X); sd=SkDB(eps=1.0,min_samples=4).fit(X)
check('DBSCAN labels == sklearn (ARI 1, same noise set)',adjusted_rand_score(db.labels_,sd.labels_)==1.0 and np.array_equal(db.labels_==-1,sd.labels_==-1) and np.array_equal(db.core_sample_indices_,sd.core_sample_indices_),f'noise {np.sum(db.labels_==-1)}/{np.sum(sd.labels_==-1)}')
# HDBSCAN vs sklearn HDBSCAN (same self-inclusive min_samples convention)
hd=load(B+'hdbscan').HDBSCAN(min_cluster_size=8).fit(X); sh=SkHD(min_cluster_size=8).fit(X)
check('HDBSCAN labels vs sklearn HDBSCAN (ARI)',adjusted_rand_score(hd.labels_,sh.labels_)==1.0 and np.array_equal(hd.labels_==-1,sh.labels_==-1),f'ARI {adjusted_rand_score(hd.labels_,sh.labels_):.4f} noise {np.sum(hd.labels_==-1)}/{np.sum(sh.labels_==-1)} probs maxdiff {np.max(np.abs(np.sort(hd.probabilities_)-np.sort(sh.probabilities_))):.2e}')
# hand: core distance = distance to (min_samples-1)th other neighbor; MST total weight equals scipy single linkage sum on mutual reachability
from scipy.spatial.distance import squareform
D=np.sqrt(((X[:,None]-X[None])**2).sum(2)); core=np.sort(D,1)[:,7]; MR=np.maximum(np.maximum(D,core[:,None]),core[None,:])
Zs=linkage(squareform(MR,checks=False),'single')
check('HDBSCAN MST weight == scipy single-linkage on mutual reachability',abs(hd.minimum_spanning_tree_[:,2].sum()-Zs[:,2].sum())<1e-9 and np.allclose(np.sort(hd.single_linkage_tree_[:,2]),Zs[:,2]))
# GMM vs sklearn with identical initialization
means0=X[[0,30,60]]; cov0=np.cov((X-X.mean(0)).T,bias=True)+1e-6*np.eye(2)
gm=load(B+'gaussian-mixture-models').GaussianMixture(3,means_init=means0,tol=1e-12,max_iter=500).fit(X)
sg=SkGM(3,means_init=means0,weights_init=np.full(3,1/3),precisions_init=np.repeat(np.linalg.inv(cov0)[None],3,0),tol=1e-12,max_iter=500,reg_covar=1e-6).fit(X)
check('GMM means/covariances/weights vs sklearn (same init)',np.allclose(gm.means_,sg.means_,atol=1e-6) and np.allclose(gm.covariances_,sg.covariances_,atol=1e-6) and np.allclose(gm.weights_,sg.weights_,atol=1e-6))
check('GMM mean log-likelihood vs sklearn score',abs(gm.score(X)-sg.score(X))<1e-8 and abs(gm.bic(X)-sg.bic(X))<1e-6)
check('GMM log-likelihood monotone nondecreasing',np.all(np.diff(gm.log_likelihood_history_)>=-1e-10))
# Mean shift vs sklearn (all-seed flat kernel, same stopping tol)
ms=load(B+'mean-shift').MeanShift(bandwidth=2.0).fit(X); sm=SkMS(bandwidth=2.0,bin_seeding=False).fit(X)
check('MeanShift centers vs sklearn',ms.cluster_centers_.shape==sm.cluster_centers_.shape and np.allclose(np.sort(ms.cluster_centers_,0),np.sort(sm.cluster_centers_,0),atol=1e-6) and adjusted_rand_score(ms.labels_,sm.labels_)==1.0,f'{len(ms.cluster_centers_)} vs {len(sm.cluster_centers_)}')
# Spectral: properties + ARI vs truth, exact recovery on block-diagonal affinity
sc=load(B+'spectral-clustering').SpectralClustering(3,gamma=0.5).fit(X)
v=sc.eigenvectors_[:,0]; d=np.sqrt(sc.degree_); 
check('Spectral top eigenvalue 1 with eigenvector ∝ sqrt(degree)',abs(sc.all_eigenvalues_[0]-1)<1e-10 and np.allclose(np.abs(v/np.linalg.norm(v)),d/np.linalg.norm(d),atol=1e-8) and np.all(sc.all_eigenvalues_<=1+1e-10))
check('Spectral recovers planted clusters (ARI 1) and matches sklearn ARI',adjusted_rand_score(sc.labels_,truth)==1.0 and adjusted_rand_score(SkSC(3,gamma=0.5,random_state=0).fit(X).labels_,sc.labels_)==1.0)
Wb=np.zeros((6,6)); Wb[np.ix_([0,1,2],[0,1,2])]=1; Wb[np.ix_([3,4],[3,4])]=1; Wb[5,5]=0; Wb[5,[3,4]]=0.0; np.fill_diagonal(Wb,0); Wb[5,4]=Wb[4,5]=1
sp=load(B+'spectral-clustering').SpectralClustering(2,affinity='precomputed').fit(Wb)
check('Spectral precomputed block graph exact partition',np.array_equal(sp.labels_,[0,0,0,1,1,1]) and abs(sp.normalized_cut_)<1e-12)
# Divisive DIANA hand example in 1-D: {0,1,2, 10,11, 30}
Xd=np.array([[0.],[1],[2],[10],[11],[30]])
dv=load(B+'divisive-hierarchical-clustering').DivisiveClustering(2).fit(Xd)
check('DIANA first split isolates most-dissimilar point 30',set(dv.splits_[0]['right'])=={5} and dv.splits_[0]['splinter_seed']==5 and dv.splits_[0]['diameter']==30.0)
dv3=load(B+'divisive-hierarchical-clustering').DivisiveClustering(3).fit(Xd)
check('DIANA second split separates {0,1,2} from {10,11}',set(map(tuple,[sorted(np.flatnonzero(dv3.labels_==j)) for j in range(3)]))=={(0,1,2),(3,4),(5,)})
# metrics vs sklearn
mm=importlib.util.spec_from_file_location('cm',ROOT/B/'metrics.py'); mod=importlib.util.module_from_spec(mm); mm.loader.exec_module(mod)
check('ARI vs sklearn',abs(mod.adjusted_rand_index(truth,km.labels_)-adjusted_rand_score(truth,km.labels_))<1e-12 and abs(mod.adjusted_rand_index(truth,db.labels_)-adjusted_rand_score(truth,db.labels_))<1e-12)
check('silhouette_samples vs sklearn',np.allclose(mod.silhouette_samples(X,km.labels_),silhouette_samples(X,km.labels_),atol=1e-10))
print('\nSUMMARY',sum(c[1] for c in checks),'/',len(checks),'passed')
