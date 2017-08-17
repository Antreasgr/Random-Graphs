using System;
using System.Collections.Generic;
using System.Linq;
using static SHET.TreeNode;

namespace SHET
{
    public class CliqueTree
    {
        public static long ConvertToGraph(List<TreeNode> tree, int n)
        {
            var seen = new bool[n];

            var visited = new HashSet<TreeNode>();
            var queue = new Queue<TreeNode>();
            var edges = 0L;
            queue.Enqueue(tree[0]);

            while (queue.Count > 0)
            {
                var clique = queue.Dequeue();
                visited.Add(clique);
                foreach (var child in clique.Adjoint.Where(c => !visited.Contains(c)))
                {
                    queue.Enqueue(child);
                }

                edges += AddClique(clique, ref seen);
            }

            return edges;
        }

        public static long AddClique(TreeNode node, ref bool[] seen, bool Add = true)
        {
            var newEdges = 0L;
            var oldVertices = new List<int>();
            var newVertices = new List<int>();
            foreach (var c in node.CliqueList)
            {
                if (!seen[c])
                {
                    newVertices.Add(c);
                    seen[c] = true;
                }
                else
                {
                    oldVertices.Add(c);
                }
            }

            if (newVertices.Count > 0)
            {
                newEdges = ((newVertices.Count * (newVertices.Count - 1)) / 2) + oldVertices.Count * newVertices.Count;
                // if (Add)
                // {
                //     var count = 0;
                //     for (int i = 0; i < newVertices.Count; i++)
                //     {
                //         for (int j = i + 1; j < newVertices.Count; j++)
                //         {
                //             count++;
                //             // addEdge(newVertices[i], newVertices[j]);
                //         }

                //         foreach (var v2 in oldVertices)
                //         {
                //             count++;
                //             // addEdge(newVertices[i], node2)
                //         }
                //     }
                // }

                if (oldVertices.Count > 0)
                {
                    node.State = NodeState.Valid;
                    return newEdges;
                }
                else
                {
                    node.State = NodeState.NewCC;
                    return newEdges;
                }
            }

            if (oldVertices.Count > 0)
            {
                node.State = NodeState.Dummy;
                return newEdges;
            }

            node.State = NodeState.Empty;
            return newEdges;
        }
    }
}