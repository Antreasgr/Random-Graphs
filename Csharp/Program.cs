﻿using System;
using System.Collections.Generic;
using System.Linq;
using static SHET.TreeNode;

namespace SHET
{
    public static class SHET
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

        static void Main(string[] args)
        {
            for (int nIndex = 0; nIndex < Vertices.Length; nIndex++)
            {
                var n = Vertices[nIndex];
                foreach (var kfactor in KFactor[nIndex])
                {
                    var k = (int)(n * kfactor);
                    k = Math.Max(1, k);
                    k = Math.Min((int)(n / 2), k);

                    Console.WriteLine("------------------ Begin Run --------------------");
                    Console.WriteLine($"n:{n} \t k:{k} \t");
                    var random = new Random();
                    var sw = new System.Diagnostics.Stopwatch();
                    sw.Start();
                    var tree = TreeNode.GenerateTree(n, random);

                    for (int i = 0; i < n; i++)
                    {
                        TreeNode.SubTreeGeneration(tree, k, i, random);
                    }
                    var edges = CliqueTree.ConvertToGraph(tree, n);
                    sw.Stop();

                    var validCliques = tree.Where(x => x.State == NodeState.Valid || x.State == NodeState.NewCC);

                    Console.WriteLine($"Total time: {sw.Elapsed.TotalSeconds}");
                    Console.WriteLine($"Edges: {edges}");
                    Console.WriteLine($"Clique tree:");
                    Console.WriteLine($"\tNum: {validCliques.Count()}");
                    Console.WriteLine($"\tMin: {validCliques.Min(x => x.CliqueList.Count)}");
                    Console.WriteLine($"\tMax: {validCliques.Max(x => x.CliqueList.Count)}");
                    Console.WriteLine("------------------ End Run --------------------");
                    
                }
            }
        }
    }
}
