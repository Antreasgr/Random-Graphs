namespace SHET
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using Helpers;
    using Statistics;
    using static global::SHET.TreeNode;

    public class SHET
    {
        public static readonly int[] Vertices = new int[] { 50, 100, 500, 1000, 2500, 5000, 10000 };

        public static readonly double[][] KFactor = new double[][]{
            new double[] {0.03, 0.1, 0.2, 0.32, 0.49},  // 50
            new double[] {0.04, 0.1, 0.22, 0.33, 0.49},  // 100
            new double[] {0.02, 0.05, 0.08, 0.2, 0.40},  // 500
            new double[] {0.02, 0.05, 0.08, 0.18, 0.33},  // 1000
            new double[] {0.01, 0.04, 0.07, 0.13, 0.36},  // 2500
            new double[] {0.01, 0.04, 0.07, 0.1, 0.36},  // 5000
            new double[] {0.009, 0.03, 0.06, 0.09, 0.33}  // 10000
        };

        // public static readonly int[] Vertices = new int[] { 5 };

        // public static readonly double[][] KFactor = new double[][]{
        //     new double[] {0.57},  // 50
        // };

        private Stats InitializeRunStats(int n, int k)
        {
            var stats = new Stats();
            stats.Parameters["n"] = n.ToString();
            stats.Parameters["k"] = k.ToString();
            stats.Parameters["n/k"] = ((float)n / k).ToString();
            stats.Times["treeTime"] = new List<double>();
            stats.Times["subTreesTime"] = new List<double>();
            stats.Times["ctreeTime"] = new List<double>();
            stats.Output["edges"] = new List<double>();
            stats.Output["edgeDensity"] = new List<double>();
            stats.Output["CC"] = new List<double>();
            return stats;
        }

        private void CalculateRunStatistics(int n, int edges, List<TreeNode> tree, Stats stats)
        {
            var maxEdges = (n * (n - 1)) / 2;
            var validCliques = tree.Where(x => x.State == NodeState.Valid || x.State == NodeState.NewCC);
            stats.Output["edges"].Add(edges);
            stats.Output["edgeDensity"].Add((double)edges / maxEdges);
            stats.Output["CC"].Add(validCliques.Where(x => x.State == NodeState.NewCC).Count());
            var max = (double)validCliques.Max(x => x.CliqueList.Count);
            stats.CliqueTrees.Add(new TreeStatistics()
            {
                Num = validCliques.Count(),
                MinSize = validCliques.Min(x => x.CliqueList.Count),
                MaxSize = (int)max,
                MaxCliqueDistribution = ((max * (max - 1)) / 2) / edges
            });
        }

        public void PrintRunStatistics(Stats stats)
        {
            Console.WriteLine($"Edges: {stats.Output["edges"].Last()} - {stats.Output["edgeDensity"].Last()}");
            Console.WriteLine($"CC: {stats.Output["CC"].Last()}");
            Console.WriteLine($"Clique tree:");

            Console.WriteLine($"\tMax clique distr.: {stats.CliqueTrees.Last().MaxCliqueDistribution}");

            Console.WriteLine($"\tNum: {stats.CliqueTrees.Last().Num}");
            Console.WriteLine($"\tMin: {stats.CliqueTrees.Last().MinSize}");
            Console.WriteLine($"\tMax: {stats.CliqueTrees.Last().MaxSize}");
        }

        public List<Stats> RunSHET(int runs)
        {
            var allStats = new List<Stats>();
            for (int nIndex = 0; nIndex < Vertices.Length; nIndex++)
            {
                var n = Vertices[nIndex];
                foreach (var kfactor in KFactor[nIndex])
                {
                    var k = (int)(n * kfactor);
                    k = Math.Max(1, k);
                    k = Math.Min((int)(n / 2), k);

                    var stats = this.InitializeRunStats(n, k);
                    allStats.Add(stats);

                    for (int r = 0; r < runs; r++)
                    {
                        if ((2 * k) - 1 > n)
                        {
                            throw new Exception("chordal gen parameter k must be lower than n/2");
                        }

                        Console.WriteLine("------------------ Begin Run --------------------");
                        Console.WriteLine($"n:{n} \t k:{k} \t");
                        var random = new Random();

                        var tree = new List<TreeNode>();
                        using (var sw = new Watch(stats.Times["treeTime"]))
                        {
                            tree = TreeNode.GenerateTree(n, random);
                        }

                        using (var sw = new Watch(stats.Times["subTreesTime"]))
                        {
                            for (int i = 0; i < n; i++)
                            {
                                TreeNode.SubTreeGeneration(tree, k, i, random);
                            }
                        }

                        int edges = 0;
                        using (var sw = new Watch(stats.Times["ctreeTime"]))
                        {
                            edges = CliqueTree.ConvertToGraph(tree, n);
                        }

                        Console.WriteLine($"Generate tree time: {stats.Times["treeTime"].Last()} s");
                        Console.WriteLine($"Subtrees time: {stats.Times["subTreesTime"].Last()} s");
                        Console.WriteLine($"Convert clique tree time: {stats.Times["ctreeTime"].Last()} s");
                        this.CalculateRunStatistics(n, edges, tree, stats);
                        this.PrintRunStatistics(stats);
                        Console.WriteLine("------------------ End Run --------------------");
                    }
                }
            }

            return allStats;
        }
    }
}