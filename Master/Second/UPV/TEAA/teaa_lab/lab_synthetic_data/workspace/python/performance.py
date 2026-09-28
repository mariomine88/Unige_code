import pandas
from matplotlib import pyplot

save_figures_on_file = False # True


#df = pandas.read_csv('docs/performance.csv', sep = ';')
df = pandas.read_csv('/tmp/performance.csv', sep = ';')
df.sort_values(by = ['cluster_type', 'block_size'], inplace = True)

df_k = df[df.cluster_type == 'local']
df_k = df_k.pivot(index = 'codebook_size', columns = ['cluster_type', 'block_size'], values = 'seconds')
df_k.plot(kind = 'bar',
            ylabel = 'seconds',
            title = 'Performance of a local cluster with 14 workers in a single node\ndepending on the block size for different codebook sizes',
            figsize = (12, 8))
pyplot.tight_layout()
if save_figures_on_file:
    pyplot.savefig('figures/performance_local_cluster.svg', format = 'svg')
else:
    pyplot.show()

df_k = df[df.cluster_type == 'kubernetes']
df_k = df_k.pivot(index = 'codebook_size', columns = ['cluster_type', 'block_size'], values = 'seconds')
df_k.plot(kind = 'bar',
            ylabel = 'seconds',
            title = 'Performance of a Kubernetes cluster with 70 workers and 5 nodes\ndepending on the block size for different codebook sizes',
            figsize = (12, 8))
pyplot.tight_layout()
if save_figures_on_file:
    pyplot.savefig('figures/performance_kubernetes_cluster.svg', format = 'svg')
else:
    pyplot.show()

df_bs = df[df.block_size == 1000]
df_bs = df_bs.pivot(index = 'codebook_size', columns = ['cluster_type', 'block_size'], values = 'seconds')
df_bs.plot(kind = 'bar',
            title = 'Comparative using a local cluster vs a Kubernetes one',
            ylabel = 'seconds',
            figsize = (12, 8))
pyplot.tight_layout()
if save_figures_on_file:
    pyplot.savefig('figures/comparative_local_vs_kubernetes_clusters.svg', format = 'svg')
else:
    pyplot.show()


#df.plot(x = 'codebook_size', y = 'seconds', kind = 'bar')
#pyplot.show()
#df.plot.bar(x = 'codebook_size', y = 'seconds', title = "The second one")
#pyplot.show()
