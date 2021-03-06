namespace MVA
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Helpers;
    using SHET;
    using Statistics;
    using static SHET.TreeNode;

    public class MVAMain : SHET
    {
        public static new readonly long[] Vertices = new long[] { 1000, 2500, 5000, 10000, 50000, 100000 };
        public static readonly double[] EdgeDensity = new double[] { 0.1, 0.33, 0.5, 0.75, 0.99 };

        private Stats InitializeRunStats(long n, double ed)
        {
            var stats = new Stats();
            stats.Parameters["Algorithm"] = "MVA";
            stats.Parameters["n"] = n.ToString(System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["edgeDensity"] = ed.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
            stats.Times["ExpandCliques"] = new List<double>();
            stats.Times["MergeCliques"] = new List<double>();
            stats.Times["Total"] = new List<double>();
            stats.Output["EdgeDensity"] = new List<double>();
            stats.Output["Mem"] = new List<double>();
            return stats;
        }

        public TreeStatistics MVABFSStatistics(long n, MVACliqueTree tree)
        {
            // convert to SHET data structure for the statistics
            var dict = new Dictionary<int, TreeNode>();
            foreach (var edge in tree.EdgesList)
            {
                foreach (var node in new int[] { edge.Node1, edge.Node2 })
                {
                    if (!dict.ContainsKey(node))
                    {
                        dict[node] = new TreeNode(node)
                        {
                            State = edge.SeperatorWeight == 0 ? NodeState.NewCC : NodeState.Valid,
                            CliqueList = tree.Cliques[node].ToList()
                        };
                    }
                }

                dict[edge.Node1].Adjoint.Add(dict[edge.Node2]);
                dict[edge.Node2].Adjoint.Add(dict[edge.Node1]);
            }

            var shetTree = dict.Values.ToList();

            var tmpSHET = new SHET();
            return tmpSHET.SHETBFSStatistics(tree.Edges, shetTree);
        }

        private void CalculateRunStatistics(long n, MVACliqueTree tree, Stats stats)
        {
            var maxEdges = (n * (n - 1)) / 2;
            stats.Edges.Add(tree.Edges);
            stats.Output["EdgeDensity"].Add((double)tree.Edges / maxEdges);
            var proc = System.Diagnostics.Process.GetCurrentProcess();
            stats.Output["Mem"].Add(proc.WorkingSet64 / (1024.0 * 1024.0));

            stats.CliqueTrees.Add(this.MVABFSStatistics(n, tree));
        }

        public new void PrintRunStatistics(Stats stats)
        {
            Console.WriteLine($"Edges: {stats.Edges.Last()} - {stats.Output["EdgeDensity"].Last()}");
            Console.WriteLine($"Clique tree:");

            Console.WriteLine($"\tMax clique distr.: {stats.CliqueTrees.Last().MaxCliqueDistribution}");

            Console.WriteLine($"\tNum: {stats.CliqueTrees.Last().Num}");
            Console.WriteLine($"\tMin: {stats.CliqueTrees.Last().MinSize}");
            Console.WriteLine($"\tMax: {stats.CliqueTrees.Last().MaxSize}");
        }

        public List<Stats> RunMVA(int runs)
        {
            var allStats = new List<Stats>();
            for (int nIndex = 0; nIndex < Vertices.Length; nIndex++)
            {
                var n = Vertices[nIndex];
                foreach (var ed in EdgeDensity)
                {
                    var edgesBound = ed * ((n * (n - 1)) / 2L);
                    var stats = this.InitializeRunStats(n, ed);
                    allStats.Add(stats);

                    for (int r = 0; r < runs; r++)
                    {
                        Console.WriteLine("------------------ Begin Run --------------------");
                        Console.WriteLine($"n:{n} \t ed:{ed.ToString("F2")} \t edgesBound: {edgesBound}");

                        var random = new Random();

                        MVACliqueTree tree = null;
                        using (var sw = new Watch(stats.Times["ExpandCliques"]))
                        {
                            tree = MVACliqueTree.ExpandCliques(n, random);
                        }
                        using (var sw = new Watch(stats.Times["MergeCliques"]))
                        {
                            tree.MergeCliques((long)edgesBound, random);
                        }

                        stats.Times["Total"].Add(stats.Times["ExpandCliques"].Last() + stats.Times["MergeCliques"].Last());
                        Console.WriteLine($"Expand Cliques: {stats.Times["ExpandCliques"].Last()} s");
                        Console.WriteLine($"Merge Cliques: {stats.Times["MergeCliques"].Last()} s");
                        this.CalculateRunStatistics(n, tree, stats);
                        this.PrintRunStatistics(stats);
                        Console.WriteLine("------------------ End Run --------------------");
                    }
                }
            }

            return this.MergeStatistics(allStats);
        }
    }
}