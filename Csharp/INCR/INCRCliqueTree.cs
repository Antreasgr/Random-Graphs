namespace INCR
{
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Linq;
    using MVA;

    public class INCRCliqueTree
    {
        public class INCRNode : List<int>
        {
            public INCRNode()
            : base()
            {
            }

            public INCRNode(IEnumerable<int> collection)
            : base(collection)
            {
            }
        }

        public class INCREdge
        {
            public INCREdge(int node1, int node2, List<int> seperator, int seperatorWeight)
            {
                this.Node1 = node1;
                this.Node2 = node2;
                this.Seperator = seperator;
                this.SeperatorWeight = seperatorWeight;
            }

            public int Node1 { get; set; }
            public int Node2 { get; set; }
            public List<int> Seperator { get; set; }
            public int SeperatorWeight { get; set; }
        }

        public int MaximalCliques { get; set; }
        public long Edges { get; set; }
        public List<INCREdge> EdgesList { get; set; }
        public List<int> Cardinalities { get; set; }
        public List<INCRNode> Cliques { get; set; }

        public INCRCliqueTree()
        {
            this.MaximalCliques = 0;
            this.Edges = 0;
            this.EdgesList = new List<INCREdge>();
            this.Cardinalities = new List<int>();
            this.Cliques = new List<INCRNode>();
        }

        public long SplitEdgesK(long upperBound, long n, Random random, int k = 1)
        {
            var loops = 0;
            var disSet = new MVA.UnionFind<int>();
            for (int i = 0; i < this.MaximalCliques; i++)
            {
                var tmp = disSet[i];
            }

            while (this.EdgesList.Count > 0 && this.Edges < upperBound)
            {
                loops++;
                var rndEdgeI = random.Next(this.EdgesList.Count);
                var rndEdge = this.EdgesList[rndEdgeI];
                int i = disSet[rndEdge.Node1], j = disSet[rndEdge.Node2];

                var xSep = new HashSet<int>(this.Cliques[i]);
                xSep.ExceptWith(rndEdge.Seperator);

                var ySep = new HashSet<int>(this.Cliques[j]);
                ySep.ExceptWith(rndEdge.Seperator);

                if (xSep.Count == 0 && ySep.Count == 0)
                {
                    throw new Exception("Not a valid clique tree");
                }
                else if (xSep.Count <= k || ySep.Count <= k)
                {
                    // merge x,y
                    var edgesAdded = xSep.Count * ySep.Count;
                    var mergedIndex = disSet.Union(rndEdge.Node1, rndEdge.Node2);
                    if (mergedIndex != i)
                    {
                        // Union find merged in j
                        var tmp = i;
                        i = j;
                        j = tmp;
                    }
                    this.Cliques[i].Union(this.Cliques[j]);
                    this.Cardinalities[i] += ySep.Count;
                    this.Cliques[j] = null;
                    this.Cardinalities[j] = 0;
                    this.Edges += edgesAdded;
                    this.MaximalCliques--;
                    this.EdgesList.RemoveAt(rndEdgeI);
                }
                else if (xSep.Count <= k)
                {
                    // merge x,z
                    var yLen = random.Next(1, ySep.Count);
                    var yRandom = ySep.Take(yLen);

                    this.Cliques[i].AddRange(yRandom);
                    this.Cardinalities[i] += yLen;
                    this.EdgesList[rndEdgeI].Seperator.Union(yRandom);
                    this.EdgesList[rndEdgeI].SeperatorWeight += yLen;
                }
                else if (ySep.Count <= k)
                {
                    //merge y,z
                    var xLen = random.Next(1, xSep.Count);
                    var xRandom = xSep.Take(xLen);

                    this.Cliques[i].AddRange(xRandom);
                    this.Cardinalities[i] += xLen;
                    this.EdgesList[rndEdgeI].Seperator.Union(xRandom);
                    this.EdgesList[rndEdgeI].SeperatorWeight += xLen;
                }
                else
                {
                    // make new z node
                    var xLen = random.Next(1, xSep.Count);
                    var yLen = random.Next(1, ySep.Count);

                    var xRandom = xSep.Take(xLen);
                    var yRandom = ySep.Take(yLen);

                    var z = new INCRNode(xRandom);
                    z.AddRange(yRandom);
                    z.AddRange(rndEdge.Seperator);

                    var edgesAdded = xLen * yLen;
                    this.Cliques.Add(z);
                    this.Cardinalities.Add(xLen + yLen + rndEdge.SeperatorWeight);

                    var sep1 = new List<int>(xRandom);
                    sep1.AddRange(rndEdge.Seperator);
                    this.EdgesList.Add(new INCREdge(rndEdge.Node1, this.Cliques.Count - 1, sep1, edgesAdded + rndEdge.SeperatorWeight));

                    var sep2 = new List<int>(yRandom);
                    sep2.AddRange(rndEdge.Seperator);
                    this.EdgesList.Add(new INCREdge(rndEdge.Node2, this.Cliques.Count - 1, sep2, edgesAdded + rndEdge.SeperatorWeight));

                    this.MaximalCliques++;
                    this.Edges += edgesAdded;
                    this.EdgesList.RemoveAt(rndEdgeI);
                }
            }

            foreach (var edge in this.EdgesList)
            {
                edge.Node1 = disSet[edge.Node1];
                edge.Node2 = disSet[edge.Node2];
            }

            return loops;
        }

        public static INCRCliqueTree GenerateKTree(long n, int k, Random random)
        {
            var node = new INCRNode(Enumerable.Range(0, k + 1));
            var cliqueTree = new INCRCliqueTree()
            {
                MaximalCliques = 1,
                Edges = k * (k + 1) / 2,
                Cardinalities = new List<int>() { k + 1 },
                Cliques = new List<INCRNode>() { node }
            };

            for (int u = 1; u < n - k; u++)
            {
                var i = random.Next(cliqueTree.MaximalCliques);
                var y = random.Next(cliqueTree.Cardinalities[i]);
                var sep = cliqueTree.Cliques[i].Where((x, ii) => ii != y);
                var newSep = new List<int>(sep);
                var newNode = new INCRNode(sep);
                newNode.Add(u + k);

                cliqueTree.Cliques.Add(newNode);
                cliqueTree.Cardinalities.Add(k + 1);
                cliqueTree.MaximalCliques++;
                cliqueTree.Edges += k;
                cliqueTree.EdgesList.Add(new INCREdge(i, cliqueTree.Cliques.Count - 1, newSep, k));
            }

            return cliqueTree;
        }
    }
}