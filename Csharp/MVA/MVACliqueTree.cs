namespace MVA
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    public class MVACliqueTree
    {
        public class MVANode : HashSet<int>
        {
            public MVANode()
            : base()
            {

            }
            public MVANode(IEnumerable<int> collection)
            : base(collection)
            {
            }
        }

        public class MVAEdge
        {
            public MVAEdge(int node1, int node2, HashSet<int> seperator, int seperatorWeight)
            {
                this.Node1 = node1;
                this.Node2 = node2;
                this.Seperator = seperator;
                this.SeperatorWeight = seperatorWeight;
            }

            public int Node1 { get; set; }
            public int Node2 { get; set; }
            public HashSet<int> Seperator { get; set; }
            public int SeperatorWeight { get; set; }
        }

        public int MaximalCliques { get; set; }
        public int Edges { get; set; }
        public List<MVAEdge> EdgesList { get; set; }
        public List<int> Cardinalities { get; set; }
        public List<MVANode> Cliques { get; set; }

        public MVACliqueTree()
        {
            this.MaximalCliques = 0;
            this.Edges = 0;
            this.EdgesList = new List<MVAEdge>();
            this.Cardinalities = new List<int>();
            this.Cliques = new List<MVANode>();
        }

        public void MergeCliques(int upperBound, Random random)
        {
            var disSet = new MVA.UnionFind<int>();
            for (int i = 0; i < this.MaximalCliques; i++)
            {
                var tmp = disSet[i];
            }

            var finalEdges = new List<MVAEdge>();

            while (this.EdgesList.Count > 0 && this.Edges < upperBound)
            {
                var rndEdgeI = random.Next(this.EdgesList.Count);
                var rndEdge = this.EdgesList[rndEdgeI];
                this.EdgesList.RemoveAt(rndEdgeI);

                int i = disSet[rndEdge.Node1], j = disSet[rndEdge.Node2];
                var edges_a = this.Cardinalities[i] - rndEdge.SeperatorWeight;
                var edges_b = this.Cardinalities[j] - rndEdge.SeperatorWeight;
                if (this.Edges + (edges_a * edges_b) <= upperBound)
                {
                    var mergedIndex = disSet.Union(rndEdge.Node1, rndEdge.Node2);
                    if (mergedIndex != i)
                    {
                        // Union find merged in j
                        var tmp = i;
                        i = j;
                        j = tmp;
                    }

                    this.Cliques[i].UnionWith(this.Cliques[j]);
                    this.Cardinalities[i] = edges_a + edges_b + rndEdge.SeperatorWeight;
                    this.Cliques[j] = null;
                    this.Cardinalities[j] = 0;
                    this.Edges += edges_b * edges_a;
                    this.MaximalCliques -= 1;
                }
                else
                {
                    finalEdges.Add(rndEdge);
                }
            }

            this.EdgesList.AddRange(finalEdges);
        }

        public static MVACliqueTree ExpandCliques(int n, Random random)
        {
            var cliqueTree = new MVACliqueTree()
            {
                Cliques = new List<MVANode>() { new MVANode() },
                Cardinalities = new List<int>() { 1 },
                MaximalCliques = 1
            };

            for (int u = 0; u < n; u++)
            {
                var i = random.Next(cliqueTree.MaximalCliques);
                var t = random.Next(1, cliqueTree.Cardinalities[i] + 1);
                if (t == cliqueTree.Cardinalities[i])
                {
                    // expand old 
                    cliqueTree.Cliques[i].Add(u);
                    cliqueTree.Cardinalities[i]++;
                }
                else
                {
                    var seperator = RandomSample<int>(cliqueTree.Cliques[i], t, random);
                    var newNode = new MVANode() { u };
                    newNode.UnionWith(seperator);
                    cliqueTree.Cliques.Add(newNode);
                    cliqueTree.MaximalCliques++;
                    cliqueTree.Cardinalities.Add(t + 1);
                    cliqueTree.EdgesList.Add(new MVAEdge(i, cliqueTree.MaximalCliques - 1, new HashSet<int>(seperator), t));
                }

                cliqueTree.Edges += t;
            }

            return cliqueTree;
        }

        public static T[] RandomSample<T>(IEnumerable<T> population, int k, Random random)
        {
            var pool = population.ToList();
            var n = pool.Count;
            var result = new T[n];
            for (int i = 0; i < k; i++)
            {
                var j = random.Next(0, n - i);
                result[i] = pool[j];
                pool[j] = pool[n - i - 1];
            }

            return result;
        }
    }
}