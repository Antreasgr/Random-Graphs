namespace MVA
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Helpers;
    using Statistics;

    public class MVAMain
    {
        public static readonly int[] Vertices = new int[] { 50, 100, 500, 1000, 2500, 5000, 10000 };
        public static readonly double[] EdgeDensity = new double[] { 0.1, 0.33, 0.5, 0.75, 0.99 };

        private Stats InitializeRunStats(int n, double ed)
        {
            var stats = new Stats();
            stats.Parameters["n"] = n.ToString();
            stats.Parameters["edgeDensity"] = ed.ToString("F2");
            stats.Times["ExpandCliques"] = new List<double>();
            stats.Times["MergeCliques"] = new List<double>();
            stats.Times["Total"] = new List<double>();
            stats.Output["Edges"] = new List<double>();
            stats.Output["EdgeDensity"] = new List<double>();
            return stats;
        }

        private void CalculateRunStatistics(int n, MVACliqueTree tree, Stats stats)
        {
            var maxEdges = (n * (n - 1)) / 2;
            stats.Output["Edges"].Add(tree.Edges);
            stats.Output["EdgeDensity"].Add((double)tree.Edges / maxEdges);
            var validCliques = tree.Cliques.Where(c => c != null && c.Count > 0);
            var max = validCliques.Max(c => c.Count);
            stats.CliqueTrees.Add(new TreeStatistics()
            {
                Num = validCliques.Count(),
                MaxSize = max,
                MinSize = validCliques.Min(c => c.Count),
                AvgSize = validCliques.Average(c => c.Count),
                MaxCliqueDistribution = ((max * (max - 1)) / 2) / (double)tree.Edges
            });
        }

        public void PrintRunStatistics(Stats stats)
        {
            Console.WriteLine($"Edges: {stats.Output["Edges"].Last()} - {stats.Output["EdgeDensity"].Last()}");
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
                    var edgesBound = ed * ((n * (n - 1)) / 2);
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
                            tree.MergeCliques((int)edgesBound, random);
                        }

                        Console.WriteLine($"Expand Cliques: {stats.Times["ExpandCliques"].Last()} s");
                        Console.WriteLine($"Merge Cliques: {stats.Times["MergeCliques"].Last()} s");
                        this.CalculateRunStatistics(n, tree, stats);
                        this.PrintRunStatistics(stats);
                        Console.WriteLine("------------------ End Run --------------------");
                    }
                }
            }
            return allStats;
        }
    }
}