namespace INCR
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Helpers;
    using MVA;
    using Statistics;

    public class INCRMain : SHET.SHET
    {
        public static new readonly long[] Vertices = new long[] { /* 1000, 2500, 5000, 10000,*/ 50000, 100000 };
        public static readonly double[] EdgeDensity = new double[] { 0.1, 0.33, 0.5, 0.75, 0.99 };

        private Stats InitializeRunStats(long n, double ed, double k, double ktreeK, double kEdges)
        {
            var stats = new Stats();
            stats.Parameters["Algorithm"] = "INCR";
            stats.Parameters["n"] = n.ToString(System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["edgeDensity"] = ed.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["k"] = k.ToString("F2");
            stats.Parameters["ktreeK"] = ktreeK.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["kEdges"] = kEdges.ToString("F2", System.Globalization.CultureInfo.InvariantCulture);

            stats.Times["GenerateKTree"] = new List<double>();
            stats.Times["SplitEdgesK"] = new List<double>();
            stats.Times["Total"] = new List<double>();
            stats.Output["EdgeDensity"] = new List<double>();
            return stats;
        }

        private void CalculateRunStatistics(long n, INCRCliqueTree tree, Stats stats)
        {
            var maxEdges = (n * (n - 1)) / 2L;
            stats.Edges.Add(tree.Edges);
            stats.Output["EdgeDensity"].Add((double)tree.Edges / maxEdges);
            var mvaAlgo = new MVAMain();
            stats.CliqueTrees.Add(mvaAlgo.MVABFSStatistics(n, tree));
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

        public List<Stats> RunINCR(int runs, double edgesToAdd)
        {
            var allStats = new List<Stats>();
            for (int nIndex = 0; nIndex < Vertices.Length; nIndex++)
            {
                var n = Vertices[nIndex];
                foreach (var ed in EdgeDensity)
                {
                    var edgesBound = ed * ((n * (n - 1)) / 2L);
                    var k = Math.Max(1, edgesToAdd * edgesBound);
                    var ktreeK = 1.0 / 2 * (2 * n - 1 - Math.Sqrt(((2 * n - 1) * (2 * n - 1)) - (8 * edgesBound)));
                    ktreeK = (int)(Math.Floor(ktreeK));
                    var kEdges = (n - ktreeK - 1) * ktreeK + (ktreeK * (ktreeK + 1) / 2);
                    long ktreeK1 = (long)ktreeK + 1;
                    var kEdges1 = (n - ktreeK1 - 1) * ktreeK1 + (ktreeK1 * (ktreeK1 + 1) / 2);

                    var stats = this.InitializeRunStats(n, ed, k, ktreeK, kEdges);
                    allStats.Add(stats);

                    for (int r = 0; r < runs; r++)
                    {
                        Console.WriteLine("------------------ Begin Run --------------------");
                        Console.WriteLine($"n:{n} \t ed:{ed.ToString("F2")} \t edgesBound: {edgesBound}");
                        Console.WriteLine($"k:{k} \t kTree:{ktreeK.ToString("F2")} \t kEdges: {kEdges}({edgesBound - kEdges})");
                        Console.WriteLine($"kTree + 1:{ktreeK1.ToString("F2")} \t kEdges + 1: {kEdges1}({edgesBound - kEdges1})");

                        var random = new Random();

                        INCRCliqueTree tree = null;
                        using (var sw = new Watch(stats.Times["GenerateKTree"]))
                        {
                            tree = INCRCliqueTree.GenerateKTree(n, (int)ktreeK, random);
                        }
                        
                        using (var sw = new Watch(stats.Times["SplitEdgesK"]))
                        {
                            tree.SplitEdgesK((int)edgesBound, random, (int)k);
                        }

                        stats.Times["Total"].Add(stats.Times["GenerateKTree"].Last() + stats.Times["SplitEdgesK"].Last());
                        Console.WriteLine($"Generate K-Tree: {stats.Times["GenerateKTree"].Last()} s");
                        Console.WriteLine($"Split Edges K: {stats.Times["SplitEdgesK"].Last()} s");
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