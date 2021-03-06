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
        public static readonly int[] Vertices = new int[] { 1000, 2500, 5000, 10000, 50000 , 100000 };

        public static readonly double[][] KFactor = new double[][]{
            new double[] {0.02, 0.05, 0.08, 0.18, 0.33},  // 1000
            new double[] {0.01, 0.04, 0.07, 0.13, 0.36},  // 2500
            new double[] {0.01, 0.04, 0.07, 0.1, 0.36},  // 5000
            new double[] {0.009, 0.03, 0.06, 0.09, 0.33},  // 10000
            new double[] {0.007, 0.01, 0.036, 0.082, 0.12},  // 50000
            new double[] { 0.004, 0.01, 0.02, 0.03, 0.04 }  // 100000
        };

        // public static readonly int[] Vertices = new int[] { 5 };

        // public static readonly double[][] KFactor = new double[][]{
        //     new double[] {0.57},  // 50
        // };

        private Stats InitializeRunStats(int n, int k)
        {
            var stats = new Stats();
            stats.Parameters["Algorithm"] = "Shet";
            stats.Parameters["n"] = n.ToString(System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["k"] = k.ToString(System.Globalization.CultureInfo.InvariantCulture);
            stats.Parameters["n/k"] = ((float)n / k).ToString(System.Globalization.CultureInfo.InvariantCulture);
            stats.Times["treeTime"] = new List<double>();
            stats.Times["subTreesTime"] = new List<double>();
            stats.Times["ctreeTime"] = new List<double>();
            stats.Times["Total"] = new List<double>();
            stats.Output["edgeDensity"] = new List<double>();
            stats.Output["CC"] = new List<double>();
            stats.Output["Mem"] = new List<double>();
            return stats;
        }

        public TreeStatistics SHETBFSStatistics(long edges, IEnumerable<TreeNode> tree)
        {
            var count = tree.Count();
            var avgDegree = 2.0 * (count - 1) / count;
            var tStats = new TreeStatistics();
            var visited = new HashSet<TreeNode>();
            var stack = new Stack<TreeNode>();
            var root = tree.First();
            var farthestNode = root;
            stack.Push(root);
            while (stack.Count > 0)
            {
                var clique = stack.Pop();
                visited.Add(clique);
                var degree = 0;
                foreach (var child in clique.Adjoint.Where(c => (c.State == NodeState.Valid || c.State == NodeState.NewCC) && !visited.Contains(c)))
                {
                    child.Height = clique.Height + 1;
                    degree++;
                    stack.Push(child);
                    // calculate for each edge
                    tStats.NumEdges++;
                    var seperatorCount = clique.CliqueList.Intersect(child.CliqueList).Count();
                    tStats.SumWeight += seperatorCount;
                    tStats.MaxWeight = Math.Max(tStats.MaxWeight, seperatorCount);
                    tStats.MinWeight = tStats.MinWeight == 0 ? seperatorCount : Math.Min(tStats.MinWeight, seperatorCount);

                    if (!tStats.DistributionWeight.ContainsKey(seperatorCount))
                    {
                        tStats.DistributionWeight[seperatorCount] = 1;
                    }
                    else
                    {
                        tStats.DistributionWeight[seperatorCount] += 1;
                    }
                }

                var size = clique.CliqueList.Count;
                tStats.Num++;
                tStats.Width = Math.Max(tStats.Width, degree);
                tStats.Height = Math.Max(tStats.Height, clique.Height);
                tStats.DegreesVar += (degree - avgDegree) * (degree - avgDegree);
                tStats.MaxSize = Math.Max(tStats.MaxSize, size);
                tStats.MinSize = tStats.MinSize == 0 ? clique.CliqueList.Count : Math.Min(tStats.MinSize, clique.CliqueList.Count);
                tStats.SumSize += clique.CliqueList.Count;

                if (!tStats.DistributionSize.ContainsKey(size))
                {
                    tStats.DistributionSize[size] = 1;
                }
                else
                {
                    tStats.DistributionSize[size] += 1;
                }

                if (clique.Height > farthestNode.Height)
                {
                    farthestNode = clique;
                }
            }

            tStats.MaxCliqueDistribution = ((tStats.MaxSize * (tStats.MaxSize - 1)) / 2.0) / edges;
            tStats.AvgSize = tStats.SumSize / (double)tStats.Num;
            tStats.AvgWeight = tStats.SumWeight / (double)tStats.NumEdges;

            // run a second bfs from farthest vertex to get the diameter
            farthestNode.Height = 0;
            visited = new HashSet<TreeNode>();
            stack = new Stack<TreeNode>();
            stack.Push(farthestNode);
            while (stack.Count > 0)
            {
                var clique = stack.Pop();
                visited.Add(clique);
                foreach (var child in clique.Adjoint.Where(c => (c.State == NodeState.Valid || c.State == NodeState.NewCC) && !visited.Contains(c)))
                {
                    child.Height = clique.Height + 1;
                    stack.Push(child);
                }

                tStats.Diameter = Math.Max(tStats.Diameter, clique.Height);
            }

            return tStats;
        }

        private void CalculateRunStatistics(long n, long edges, List<TreeNode> tree, Stats stats)
        {
            long maxEdges = ((long)n * (n - 1)) / 2L;
            var validCliques = tree.Where(x => x.State == NodeState.Valid || x.State == NodeState.NewCC);
            stats.Edges.Add(edges);
            stats.Output["edgeDensity"].Add(Convert.ToDouble(Decimal.Divide((decimal)edges, (decimal)maxEdges)));
            stats.Output["CC"].Add(validCliques.Where(x => x.State == NodeState.NewCC).Count());
            stats.CliqueTrees.Add(this.SHETBFSStatistics(edges, validCliques));

            var proc = System.Diagnostics.Process.GetCurrentProcess();
            stats.Output["Mem"].Add(proc.WorkingSet64 / (1024.0 * 1024.0));
        }

        public void PrintRunStatistics(Stats stats)
        {
            Console.WriteLine($"Edges: {stats.Edges.Last()} - {stats.Output["edgeDensity"].Last()}");
            Console.WriteLine($"CC: {stats.Output["CC"].Last()}");
            Console.WriteLine($"Clique tree:");

            Console.WriteLine($"\tMax clique distr.: {stats.CliqueTrees.Last().MaxCliqueDistribution}");

            Console.WriteLine($"\tNum: {stats.CliqueTrees.Last().Num}");
            Console.WriteLine($"\tMin: {stats.CliqueTrees.Last().MinSize}");
            Console.WriteLine($"\tMax: {stats.CliqueTrees.Last().MaxSize}");
        }

        public List<Stats> MergeStatistics(List<Stats> stats)
        {
            var allStats = new List<Stats>();
            foreach (var stat in stats)
            {
                var finalStats = new Stats()
                {
                    Parameters = stat.Parameters
                };

                allStats.Add(finalStats);

                foreach (var key in stat.Times.Keys)
                {
                    finalStats.Times[key] = TreeStatistics.AverageStd(stat.Times[key]);
                }

                finalStats.Edges = TreeStatistics.AverageStd(stat.Edges);

                foreach (var key in stat.Output.Keys)
                {
                    finalStats.Output[key] = TreeStatistics.AverageStd(stat.Output[key]);
                }

                finalStats.CliqueTrees = TreeStatistics.AvgStdTreeStats(stat.CliqueTrees);
            }

            return allStats;
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

                        long edges = 0;
                        using (var sw = new Watch(stats.Times["ctreeTime"]))
                        {
                            edges = CliqueTree.ConvertToGraph(tree, n);
                        }

                        stats.Times["Total"].Add(stats.Times["treeTime"].Last() + stats.Times["subTreesTime"].Last() + stats.Times["ctreeTime"].Last());

                        Console.WriteLine($"Generate tree time: {stats.Times["treeTime"].Last()} s");
                        Console.WriteLine($"Subtrees time: {stats.Times["subTreesTime"].Last()} s");
                        Console.WriteLine($"Convert clique tree time: {stats.Times["ctreeTime"].Last()} s");
                        this.CalculateRunStatistics(n, edges, tree, stats);
                        this.PrintRunStatistics(stats);
                        Console.WriteLine("------------------ End Run --------------------");
                    }

                    var runStats = this.MergeStatistics(new List<Stats>() { stats });
                    ExcelReporter.ExcelReporter.CreateSpreadsheetWorkbook($"ShetMem_{n}_{kfactor}", runStats);
                }
            }

            return this.MergeStatistics(allStats);
        }
    }
}